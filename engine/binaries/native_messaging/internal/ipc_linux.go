//go:build !windows

package internal

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"strings"
)

// maxUnixSockPath 为 Unix 域套接字路径安全上限（略小于常见 108 字节 sun_path 限制）。
const maxUnixSockPath = 100

// InitIPC 在 Linux / macOS 上使用 Unix 域套接字实现与 Windows named pipe 等价的流式 IPC。
// 协议名 "npipe" 与 Windows 配置保持一致，此处语义为「本地流式 IPC」；亦支持显式 "unix"。
func InitIPC(proto string, config map[string]string) (net.Listener, error) {
	switch proto {
	case "npipe", "unix":
		key := strings.TrimSpace(config["ipcKey"])
		if key == "" {
			return nil, errors.New("error: The parameter ipcKey must exist.")
		}
		sockPath, err := unixSocketPath(key)
		if err != nil {
			return nil, err
		}
		if err := os.Remove(sockPath); err != nil && !os.IsNotExist(err) {
			return nil, fmt.Errorf("remove stale unix socket: %w", err)
		}
		ln, err := net.Listen("unix", sockPath)
		if err != nil {
			return nil, fmt.Errorf("unix socket listen: %w", err)
		}
		return ln, nil
	default:
		return nil, fmt.Errorf("invalid protocol format: %q", proto)
	}
}

func unixSocketPath(ipcKey string) (string, error) {
	dir, err := unixSocketDir()
	if err != nil {
		return "", err
	}
	base := sanitizeForFilename(ipcKey) + ".sock"
	path := filepath.Join(dir, base)
	if len(path) > maxUnixSockPath {
		sum := sha256.Sum256([]byte(ipcKey))
		short := "astra-" + hex.EncodeToString(sum[:8]) + ".sock"
		path = filepath.Join(dir, short)
		if len(path) > maxUnixSockPath {
			return "", fmt.Errorf("unix socket path too long after shortening: %d bytes", len(path))
		}
	}
	return path, nil
}

func unixSocketDir() (string, error) {
	if runtimeDir := os.Getenv("XDG_RUNTIME_DIR"); runtimeDir != "" {
		sub := filepath.Join(runtimeDir, "astra-native-msg")
		if err := os.MkdirAll(sub, 0o700); err == nil {
			return sub, nil
		}
		// 创建失败时退回系统临时目录
	}
	tmp := os.TempDir()
	sub := filepath.Join(tmp, "astra-native-msg")
	if err := os.MkdirAll(sub, 0o700); err != nil {
		return "", fmt.Errorf("mkdir socket dir: %w", err)
	}
	return sub, nil
}

func sanitizeForFilename(s string) string {
	var b strings.Builder
	b.Grow(len(s))
	for _, r := range s {
		switch {
		case r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z', r >= '0' && r <= '9', r == '_', r == '-':
			b.WriteRune(r)
		}
	}
	out := b.String()
	if out == "" {
		return "ipc"
	}
	return out
}
