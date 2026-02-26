package proxy

import (
	"net/http"
)

// RpaManagerProxy is the core interface for RPA manager proxies.
type RpaManagerProxy interface {
	ServeHTTP(rw http.ResponseWriter, req *http.Request)
}

// NewRpaManagerProxy creates an HTTP or WebSocket proxy based on type.
func NewRpaManagerProxy(types string, opts ...Option) RpaManagerProxy {
	if types == "ws" {
		return NewSimpleRpaWsProxy(opts...)
	} else {
		return NewSimpleRpaHttpProxy(opts...)
	}
}
