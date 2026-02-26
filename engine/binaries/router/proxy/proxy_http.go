package proxy

import (
	"bytes"
	"context"
	"crypto/tls"
	"errors"
	"fmt"
	"io"
	"math/rand"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
	"time"
)

// SimpleRpaHttpProxy is an HTTP reverse proxy for RPA traffic.
type SimpleRpaHttpProxy struct {
	options      *Options
	ReverseProxy *httputil.ReverseProxy
}

// NewSimpleRpaHttpProxy creates a SimpleRpaHttpProxy with given options.
func NewSimpleRpaHttpProxy(opts ...Option) *SimpleRpaHttpProxy {
	opt := NewDefault()
	for _, o := range opts {
		o(opt)
	}
	var simpleRpaProxy = &SimpleRpaHttpProxy{
		options: opt,
	}
	simpleRpaProxy.ReverseProxy = simpleRpaProxy.init()
	return simpleRpaProxy
}

// init initializes the underlying httputil.ReverseProxy.
func (p *SimpleRpaHttpProxy) init() *httputil.ReverseProxy {
	return &httputil.ReverseProxy{
		Transport: &SimpleRpaHttpProxyTransport{
			RoundTripper: &http.Transport{
				Proxy: http.ProxyFromEnvironment,
				DialContext: (&net.Dialer{
					Timeout:   200 * time.Second,
					KeepAlive: 200 * time.Second,
				}).DialContext,
				ForceAttemptHTTP2:     true,
				TLSClientConfig:       &tls.Config{InsecureSkipVerify: true},
				DisableKeepAlives:     true,
				MaxIdleConns:          100,
				IdleConnTimeout:       600 * time.Second,
				TLSHandshakeTimeout:   10 * time.Second,
				ExpectContinueTimeout: 1 * time.Second,
			},
			logger:       p.options.logger,
			tryTime:      3,
			trySleepTime: 500 * time.Millisecond,
		},
		ErrorHandler: p.rpaErrorHandler,
		Rewrite: func(req *httputil.ProxyRequest) {
			targetURL := req.In.Context().Value("targetURL").(string)
			target, err := url.Parse(targetURL)
			if err != nil {
				p.options.logger.Errorf("http-proxy: invalid target URL %q: %v", targetURL, err)
				return
			}
			req.SetURL(target)
			req.Out.Host = req.Out.URL.Host
			if req.Out.URL.Path != "/" {
				req.Out.URL.Path = strings.TrimRight(req.Out.URL.Path, "/")
			}
			if req.Out.RequestURI != "/" {
				req.Out.RequestURI = strings.TrimRight(req.Out.RequestURI, "/")
			}
		},
	}
}

// ServeHTTP implements http.Handler and forwards the HTTP request.
func (p *SimpleRpaHttpProxy) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
	targetUrl := p.options.defaultTarget

	// Get route key from request path
	head, err := p.options.targetRegexpFunc(req.URL.Path)
	if err != nil {
		p.rpaErrorHandler(rw, req, err)
		return
	}
	config, ok := p.options.targetConfigMap[strings.Trim(head, "/")]
	if !ok {
		rw.WriteHeader(http.StatusNotFound)
		return
	}
	targetUrl = config.ProxyUrl

	// Add cookies to the request if the route is API.
	// Rewrite request path when needed
	if head == "api" {
		AddCookie(targetUrl, rw, req)
	} else {
		if p.options.defaultRewrite != nil {
			p.options.defaultRewrite(req)
		}
	}

	// Save target URL into request context for later use
	req = req.WithContext(context.WithValue(req.Context(), "targetURL", targetUrl))

	// Forward the request to the target URL.
	p.ReverseProxy.ServeHTTP(rw, req)
}

// rpaErrorHandler writes proxy error to log and client.
func (p *SimpleRpaHttpProxy) rpaErrorHandler(rw http.ResponseWriter, req *http.Request, err error) {
	p.options.logger.Errorf("http-proxy: error: %v", err)
	rw.WriteHeader(http.StatusBadGateway)
}

// SimpleRpaHttpProxyTransport wraps RoundTripper with retry logic.
type SimpleRpaHttpProxyTransport struct {
	http.RoundTripper
	logger Logger

	// Retry configuration
	tryTime      int
	trySleepTime time.Duration
}

// RoundTrip forwards the request and retries on specific system errors.
func (t *SimpleRpaHttpProxyTransport) RoundTrip(req *http.Request) (resp *http.Response, err error) {
	now := time.Now().UnixMilli()
	randBits := rand.Int31n(1000)
	reqID := fmt.Sprintf("%d%03d", now, randBits)

	// Read and buffer request body so it can be retried
	var bodyBytes []byte
	if req.Body != nil {
		bodyBytes, _ = io.ReadAll(req.Body)
		_ = req.Body.Close()
	}
	for i := t.tryTime; i > 0; i-- {
		if len(bodyBytes) > 0 {
			req.Body = io.NopCloser(bytes.NewReader(bodyBytes))
			req.ContentLength = -1
		} else {
			req.Body = nil
			req.ContentLength = 0
		}
		t.logger.Infof("[req:%s] http-proxy: proxying %s %s", reqID, req.Method, req.URL.String())
		resp, err = t.RoundTripper.RoundTrip(req)
		if err != nil {
			var xErr *os.SyscallError
			if errors.As(err, &xErr) {
				t.logger.Errorf("[req:%s] http-proxy: syscall error %v: %v", reqID, xErr, err)
				time.Sleep(t.trySleepTime)
				continue
			} else {
				t.logger.Errorf("[req:%s] http-proxy: RoundTrip error: %v", reqID, err)
				return nil, err
			}
		}
		delete(resp.Header, "Access-Control-Allow-Origin")
		delete(resp.Header, "Access-Control-Allow-Credentials")
		delete(resp.Header, "Access-Control-Expose-Headers")
		return resp, err
	}
	if err != nil {
		t.logger.Errorf("[req:%s] http-proxy: request failed after %d attempts: %v", reqID, t.tryTime, err)
	}
	return resp, err
}
