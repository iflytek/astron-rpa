package internal

import (
	"bufio"
	"context"
	"encoding/json"
	"io"
	"net"
	"os"
	"strings"
	"sync"
	"time"
	"errors"
)

type IService interface {
	Run()
}

func NewService(ctx context.Context, config map[string]string, logger Logger) IService {
	return &Service{
		logger:    logger,
		config:    config,
		ctx:       ctx,
		lock:      &sync.Mutex{},
		stdIoConn: NewStdIoConn(),
		stdIoIn:   make(chan []byte, 5),
	}
}

type Service struct {
	logger    Logger
	config    map[string]string
	ctx       context.Context
	lock      sync.Locker
	stdIoConn *StdIoConn
	stdIoIn   chan []byte
}

func (s *Service) Run() {
	// initialize IPC listener
	listener, err := InitIPC(s.config["proto"], s.config)
	if err != nil {
		s.logger.Errorf(s.ctx, "service: init IPC listener failed: %v", err)
		return
	}

	// start goroutine to read from stdin/stdout bridge
	go func() {
		for {
			read, err := s.stdIoConn.Read()
			if err != nil {
				if err == ExitError {
					s.logger.Infof(s.ctx, "service: stdio reader exiting normally: %v", err)
					os.Exit(0)
				}
				s.logger.Errorf(s.ctx, "service: stdio reader error: %v", err)
				return
			}
			msg := string(read)
			s.logger.Infof(s.ctx, "service: received message from stdio: %q", msg)

			// special message: browser queries current IPC key
			var payload map[string]interface{}
			if err := json.Unmarshal(read, &payload); err == nil {
				if t, ok := payload["type"].(string); ok && t == "ASTRON_GET_IPC_KEY" {
					ipcKey := s.config["ipcKey"]
					resp := map[string]interface{}{
						"type": "ASTRON_GET_IPC_KEY",
						"data": ipcKey,
					}
					data, mErr := json.Marshal(resp)
					if mErr != nil {
						s.logger.Errorf(s.ctx, "service: failed to marshal IPC key response: %v", mErr)
					} else {
						s.logger.Infof(s.ctx, "service: replying with IPC key to stdio: %q", string(data))
						_ = s.stdIoConn.Write(data)
					}
					continue
				}
			}

			s.stdIoIn <- read
		}
	}()

	// accept and handle IPC connections
	for {
		conn, err := listener.Accept()
		if err != nil {
			s.logger.Errorf(s.ctx, "service: accept connection failed: %v", err)
			continue
		}
		go func() {
			defer conn.Close()
			for {
				err := s.handleConn(conn)
				if err != nil {
					break
				}
			}
		}()
	}
}

func (s *Service) handleConn(conn net.Conn) error {
	// only handle one request at a time because we are bound to stdin/stdout
	s.lock.Lock()
	defer s.lock.Unlock()

	r := bufio.NewReader(conn)
	msg, err := r.ReadString('\n')
	if err != nil && err != io.EOF {
		s.logger.Errorf(s.ctx, "service: read request from IPC failed: %v", err)
		return err
	}
	if err == io.EOF {
		return err
	}
	newMsg := strings.Replace(msg, "\n", "", -1)
	if len(newMsg) == 0 {
		s.logger.Errorf(s.ctx, "service: received empty request line from IPC: %q", msg)
		return err
	}

	s.logger.Infof(s.ctx, "service: forwarding IPC request to stdio: %q", newMsg)
	err = s.stdIoConn.Write([]byte(newMsg))
	if err != nil {
		s.logger.Errorf(s.ctx, "service: write to stdio failed: %v", err)
		return err
	}

	// read latest response from stdIoIn with timeout (drop request if blocked)
    t := time.After(60)
	var read []byte
	select {
	case read = <-s.stdIoIn:
		// Message received
	case <-t:
		s.logger.Errorf(s.ctx, "service: timeout waiting for stdio response, dropping request")
		return errors.New("timeout waiting for stdio response")
	}

	s.logger.Infof(s.ctx, "service: forwarding stdio response back to IPC: %q", string(read))
	_, err = conn.Write(read)
	if err != nil {
		s.logger.Errorf(s.ctx, "service: write response to IPC failed: %v", err)
		return err
	}
	return nil
}
