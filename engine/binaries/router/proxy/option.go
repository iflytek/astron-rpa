package proxy

import (
	"context"
	"net/http"
	"path"
	"strings"
)

type (
	// Option is a functional option to configure Options.
	Option func(opt *Options)

	// ConfigMap describes proxy configuration for a route key.
	ConfigMap struct {
		// Independent proxy URL for this key
		ProxyUrl string
		// Custom WebSocket client message handler
		WsClientMsgHandler func(ctx context.Context, messageType int, p []byte) (int, []byte, error)
		// Custom WebSocket server message handler
		WsServiceMsgHandler func(ctx context.Context, messageType int, p []byte) (int, []byte, error)
	}

	// Options holds common proxy configuration.
	Options struct {
		// Default proxy target URL
		defaultTarget string
		// Default rewrite rule
		defaultRewrite func(req *http.Request)
		// Function to extract route key from URL path
		targetRegexpFunc func(urlPath string) (string, error)
		// Map of route key to individual proxy configuration
		targetConfigMap map[string]ConfigMap
		// Logger implementation
		logger Logger
	}
)

// NewDefault returns Options with default values.
func NewDefault() *Options {
	return &Options{
		defaultTarget: "",
		defaultRewrite: func(req *http.Request) {
			// Strip first path segment (routing key)
			tempPath := "/" + path.Join(strings.Split(strings.TrimLeft(req.URL.Path, "/"), "/")[1:]...)
			if len(tempPath) == 0 {
				tempPath = "/"
			}
			tempReqUrl := "/" + path.Join(strings.Split(strings.TrimLeft(req.RequestURI, "/"), "/")[1:]...)
			if len(tempReqUrl) == 0 {
				tempReqUrl = "/"
			}
			req.Host = ""
			req.URL.Path = tempPath
			req.RequestURI = tempReqUrl
		},
		targetConfigMap: nil,
		targetRegexpFunc: func(urlPath string) (string, error) {
			// Use first path segment as routing key
			res := strings.Split(strings.TrimLeft(urlPath, "/"), "/")
			return res[0], nil
		},
		logger: new(BaseLogger),
	}
}

// WithDefaultTarget sets the default proxy target URL.
func WithDefaultTarget(defaultTarget string) func(opt *Options) {
	return func(opt *Options) {
		opt.defaultTarget = defaultTarget
	}
}

// WithDefaultRewrite sets the default URL rewrite function.
func WithDefaultRewrite(f func(req *http.Request)) func(opt *Options) {
	return func(opt *Options) {
		opt.defaultRewrite = f
	}
}

// WithTargetConfigMap sets the route-key to proxy-config map.
func WithTargetConfigMap(m map[string]ConfigMap) func(opt *Options) {
	return func(opt *Options) {
		opt.targetConfigMap = m
	}
}

// WithTargetUrlRegexp sets the function that extracts the route key from URL path.
func WithTargetUrlRegexp(f func(urlPath string) (string, error)) func(opt *Options) {
	return func(opt *Options) {
		opt.targetRegexpFunc = f
	}
}

// WithLogger sets the logger implementation.
func WithLogger(logger Logger) func(opt *Options) {
	return func(opt *Options) {
		opt.logger = logger
	}
}
