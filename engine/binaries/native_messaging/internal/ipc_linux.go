//go:build !windows

package internal

import (
	"errors"
	"fmt"
	"net"
)

// InitIPC is a stub implementation for non-Windows platforms.
// It currently does not support any IPC protocol and always returns an error.
func InitIPC(proto string, config map[string]string) (net.Listener, error) {
	return nil, errors.New(fmt.Sprintf("invalid protocol format: %q", proto))
}
