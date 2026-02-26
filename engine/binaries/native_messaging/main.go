package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"native_msg_host/v2/internal"
)

func main() {
	Start()
}

// Start initializes logging, loads IPC config and runs the service loop.
func Start() {
	// open log file
	f, err := os.OpenFile("log.log", os.O_CREATE|os.O_RDWR|os.O_TRUNC, os.ModePerm)
	if err != nil {
		log.Fatalln(fmt.Sprintf("main: failed to open log file: %v", err))
	}
	defer f.Close()

	logger := internal.NewLogger(f)
	ctx, cancel := context.WithCancel(context.Background())

	// load IPC configuration
	ipcKey, err := internal.GetIPCKey()
	if err != nil {
		logger.Errorf(ctx, "main: failed to load IPC key: %v", err)
		os.Exit(1)
	}
	config := map[string]string{
		"ipcKey": ipcKey,
		"proto":  "npipe",
	}
	logger.Infof(ctx, "main: IPC config: %+v", config)

	// start service
	service := internal.NewService(ctx, config, logger)
	go service.Run()
	logger.Infof(ctx, "main: service started")

	// wait for termination signal
	SignalWait()
	logger.Infof(ctx, "main: received termination signal, shutting down")

	// shutdown service
	cancel()
}

// SignalWait blocks until a termination signal is received.
func SignalWait() {
	signCh := make(chan os.Signal, 1)
	done := make(chan bool, 1)
	signal.Notify(signCh, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT)
	go func() {
		_ = <-signCh
		done <- true
	}()
	<-done
}
