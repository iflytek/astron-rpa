package proxy

import (
	"context"
	"crypto/tls"
	"errors"
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/gorilla/websocket"
)

// SimpleRpaWsProxy is a WebSocket reverse proxy for RPA traffic.
type SimpleRpaWsProxy struct {
	options        *Options
	WsReverseProxy *WsReverseProxy
}

// NewSimpleRpaWsProxy creates a SimpleRpaWsProxy with given options.
func NewSimpleRpaWsProxy(opts ...Option) *SimpleRpaWsProxy {
	opt := NewDefault()
	for _, o := range opts {
		o(opt)
	}
	var simpleRpaProxy = &SimpleRpaWsProxy{
		options:        opt,
		WsReverseProxy: nil,
	}
	simpleRpaProxy.WsReverseProxy = simpleRpaProxy.init()
	return simpleRpaProxy
}

// init initializes the underlying WsReverseProxy.
func (p *SimpleRpaWsProxy) init() *WsReverseProxy {
	proxy := &WsReverseProxy{
		HttpRewrite: func(request *httputil.ProxyRequest) {
			targetURL := request.In.Context().Value("targetURL").(string)
			target, err := url.Parse(targetURL)
			if err != nil {
				p.options.logger.Errorf("ws-proxy: invalid target URL %q: %v", targetURL, err)
				return
			}
			request.SetURL(target)
			request.Out.Host = request.Out.URL.Host
			if request.Out.URL.Path != "/" {
				request.Out.URL.Path = strings.TrimRight(request.Out.URL.Path, "/")
			}
			if request.Out.RequestURI != "/" {
				request.Out.RequestURI = strings.TrimRight(request.Out.RequestURI, "/")
			}
		},
		Log:          p.options.logger,
		ErrorHandler: p.rpaErrorHandler,
		tryTime:      3,
		trySleepTime: 500 * time.Millisecond,
	}
	return proxy
}

// ServeHTTP implements http.Handler and forwards the WebSocket request.
func (p *SimpleRpaWsProxy) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
	targetUrl := p.options.defaultTarget

	// Get route key from request path
	head, err := p.options.targetRegexpFunc(req.URL.Path)
	if err != nil {
		p.rpaErrorHandler(rw, req, fmt.Errorf("error: targetRegexpFunc %s error %w", req.URL.Path, err))
		return
	}
	config, ok := p.options.targetConfigMap[strings.Trim(head, "/")]
	if !ok {
		rw.WriteHeader(http.StatusNotFound)
		return
	}
	targetUrl = config.ProxyUrl

	// Set custom WebSocket message handlers
	p.WsReverseProxy.wsServiceMsgHandler = config.WsServiceMsgHandler
	p.WsReverseProxy.wsClientMsgHandler = config.WsClientMsgHandler

	// Add cookies to the request if the route is API.
	// Rewrite request path when needed
	if head == "api" {
		AddCookie(targetUrl, rw, req)
	} else {
		if p.options.defaultRewrite != nil {
			p.options.defaultRewrite(req)
		}
	}

	// Forward WebSocket request
	req = req.WithContext(context.WithValue(req.Context(), "targetURL", targetUrl))
	p.WsReverseProxy.ServeHTTP(rw, req)
}

// rpaErrorHandler writes WebSocket proxy error to log.
func (p *SimpleRpaWsProxy) rpaErrorHandler(rw http.ResponseWriter, req *http.Request, err error) {
	p.options.logger.Errorf("ws-proxy: error: %v", err)
}

// WsReverseProxy manages WebSocket connections between client and backend.
type WsReverseProxy struct {
	HttpRewrite  func(*httputil.ProxyRequest)
	Log          Logger
	ErrorHandler func(http.ResponseWriter, *http.Request, error)
	// Retry configuration
	tryTime             int
	trySleepTime        time.Duration
	wsClientMsgHandler  func(c context.Context, messageType int, p []byte) (int, []byte, error)
	wsServiceMsgHandler func(c context.Context, messageType int, p []byte) (int, []byte, error)
}

// upGrader upgrades HTTP connections to WebSocket.
var upGrader = websocket.Upgrader{
	ReadBufferSize:  112400,
	WriteBufferSize: 112400,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// ServeHTTP establishes WebSocket connections and starts data piping.
func (p *WsReverseProxy) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
	// Upgrade client HTTP connection to WebSocket
	backend, err := upGrader.Upgrade(rw, req, nil)
	if err != nil {
		p.ErrorHandler(rw, req, fmt.Errorf("error: Upgrade %w", err))
		return
	}
	defer backend.Close()

	// Rewrite outbound HTTP request before dialing upstream
	outReq := req.Clone(context.Background())
	pr := &httputil.ProxyRequest{
		In:  req,
		Out: outReq,
	}
	p.HttpRewrite(pr)
	outReq = pr.Out

	// Remove WebSocket-specific headers that should not be forwarded
	for k, _ := range outReq.Header {
		switch {
		case k == "Upgrade" ||
			k == "Connection" ||
			k == "Sec-Websocket-Key" ||
			k == "Sec-Websocket-Version" ||
			k == "Sec-Websocket-Extensions" ||
			k == "Sec-Websocket-Protocol":
			outReq.Header.Del(k)
		}
	}

	// Connect to upstream WebSocket server with retry
	var (
		conn   *websocket.Conn
		wsErr  error
		dialer = &websocket.Dialer{
			Proxy:            http.ProxyFromEnvironment,
			HandshakeTimeout: 200 * time.Second,
			TLSClientConfig:  &tls.Config{InsecureSkipVerify: true},
		}
	)
	for i := p.tryTime; i > 0; i-- {
		conn, _, wsErr = dialer.Dial(outReq.URL.String(), outReq.Header)
		if wsErr != nil {
			var xErr *os.SyscallError
			if errors.As(wsErr, &xErr) {
				p.Log.Errorf("ws-proxy: syscall error %v: %v", xErr, wsErr)
				time.Sleep(p.trySleepTime)
				continue
			} else {
				p.Log.Errorf("ws-proxy: dial %s error: %v", outReq.URL.String(), wsErr)
				break
			}
		}
		break
	}
	if wsErr != nil {
		p.ErrorHandler(rw, req, fmt.Errorf("ws-proxy: dial %s error: %w", outReq.URL.String(), wsErr))
		return
	}
	defer conn.Close()

	// Log successful WebSocket connection
	p.Log.Infof("ws-proxy: connected %s <-> %s", req.RemoteAddr, outReq.URL.String())

	// Start bidirectional copy between client and backend
	errc := make(chan error, 1)
	spc := switchWsProtocolCopier{
		user:                conn,
		backend:             backend,
		wsClientMsgHandler:  p.wsClientMsgHandler,
		wsServiceMsgHandler: p.wsServiceMsgHandler,
	}
	log := p.Log
	ctx := req.Context()
	go spc.copyFromBackend(ctx, errc, log)
	go spc.copyToBackend(ctx, errc, log)
	err = <-errc

	// Report final error to handler
	p.ErrorHandler(rw, req, fmt.Errorf("ws-proxy: copy loop ended with error: %w", err))
}

// switchWsProtocolCopier copies WebSocket messages between user and backend.
type switchWsProtocolCopier struct {
	user, backend       *websocket.Conn
	wsClientMsgHandler  func(c context.Context, messageType int, p []byte) (int, []byte, error)
	wsServiceMsgHandler func(c context.Context, messageType int, p []byte) (int, []byte, error)
}

// copyFromBackend reads messages from backend and writes to client.
func (c switchWsProtocolCopier) copyFromBackend(ctx context.Context, errc chan<- error, log Logger) {
	var (
		mt      int
		message []byte
		err     error
	)
	for {
		mt, message, err = c.backend.ReadMessage()
		if err != nil {
			log.Errorf("ws-proxy: copyFromBackend ReadMessage error: %v", err)
			break
		}
		if strings.Contains(string(message), "fs同步") {
			continue
		}
		log.Infof("ws-proxy: copyFromBackend recv %d bytes", len(message))
		if c.wsClientMsgHandler != nil {
			mt, message, err = c.wsClientMsgHandler(ctx, mt, message)
			if err != nil {
				log.Errorf("ws-proxy: copyFromBackend handler error: %v", err)
				continue
			}
			if len(message) == 0 {
				// Drop empty messages
				continue
			}
		}
		err = c.user.WriteMessage(mt, message)
		if err != nil {
			log.Errorf("ws-proxy: copyFromBackend WriteMessage error: %v", err)
			break
		}
	}
	errc <- err
}

// copyToBackend reads messages from client and writes to backend.
func (c switchWsProtocolCopier) copyToBackend(ctx context.Context, errc chan<- error, log Logger) {
	var (
		mt      int
		message []byte
		err     error
	)
	for {
		mt, message, err = c.user.ReadMessage()
		if err != nil {
			log.Errorf("ws-proxy: copyToBackend ReadMessage error: %v", err)
			break
		}
		log.Infof("ws-proxy: copyToBackend recv %d bytes", len(message))
		if c.wsServiceMsgHandler != nil {
			mt, message, err = c.wsServiceMsgHandler(ctx, mt, message)
			if err != nil {
				log.Errorf("ws-proxy: copyToBackend handler error: %v", err)
				continue
			}
			if len(message) == 0 {
				// Drop empty messages
				continue
			}
		}
		err = c.backend.WriteMessage(mt, message)
		if err != nil {
			log.Errorf("ws-proxy: copyToBackend WriteMessage error: %v", err)
			break
		}
	}
	errc <- err
}
