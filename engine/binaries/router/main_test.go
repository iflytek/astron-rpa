package main

import (
	"net/http"
	"testing"
)

func TestIsLocalRequest(t *testing.T) {
	tests := []struct {
		name       string
		remoteAddr string
		want       bool
	}{
		{name: "ipv4 loopback", remoteAddr: "127.0.0.1:12345", want: true},
		{name: "ipv6 loopback", remoteAddr: "[::1]:12345", want: true},
		{name: "loopback without port", remoteAddr: "127.0.0.1", want: true},
		{name: "lan client", remoteAddr: "192.168.1.10:12345", want: false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := &http.Request{RemoteAddr: tt.remoteAddr}
			if got := isLocalRequest(req); got != tt.want {
				t.Fatalf("isLocalRequest(%q) = %v, want %v", tt.remoteAddr, got, tt.want)
			}
		})
	}
}

func TestIsLanAccessiblePath(t *testing.T) {
	tests := []struct {
		path string
		want bool
	}{
		{path: "/executor/run_sync", want: true},
		{path: "/executor/status", want: true},
		{path: "/terminal/ping", want: true},
		{path: "/scheduler/terminal/ping", want: true},
		{path: "/scheduler/executor/run", want: true},
		{path: "/scheduler/executor/stop_current", want: true},
		{path: "/executor/run/extra", want: false},
		{path: "/scheduler/executor/run/extra", want: false},
		{path: "/executor/pip/install", want: false},
		{path: "/executor/health", want: false},
		{path: "/scheduler/browser_connector/browser/health", want: false},
		{path: "/api/robot/health", want: false},
		{path: "/rpa-local-route/health", want: false},
		{path: "/rpa-local-route/registry", want: false},
		{path: "/", want: false},
	}

	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			if got := isLanAccessiblePath(tt.path); got != tt.want {
				t.Fatalf("isLanAccessiblePath(%q) = %v, want %v", tt.path, got, tt.want)
			}
		})
	}
}
