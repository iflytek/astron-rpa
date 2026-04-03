//go:build windows

package internal

import (
	"errors"
	"fmt"
	"net"

	gw "github.com/bi-zone/go-winio"
)

// InitIPC initializes an IPC listener on Windows based on the given protocol.
func InitIPC(proto string, config map[string]string) (net.Listener, error) {
	switch proto {
	case "npipe":
		if len(config["ipcKey"]) == 0 {
			return nil, errors.New(fmt.Sprintf("error: The parameter ipcKey must exist."))
		}
		pipeName := `\\.\pipe\` + config["ipcKey"]
		return gw.ListenPipe(pipeName, &gw.PipeConfig{
			SecurityDescriptor: "D:(A;;FA;;;WD)",
		})
	default:
		return nil, errors.New(fmt.Sprintf("invalid protocol format: %q", proto))
	}
}
