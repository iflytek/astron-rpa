package internal

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/shirou/gopsutil/process"
)

// BrowserRegisterName mirrors the Python-side mapping.
var BrowserRegisterName = map[string]string{
	"BTChrome":  "chrome.exe",
	"BTEdge":    "msedge.exe",
	"BT360SE":   "360se6.exe",
	"BT360X":    "360ChromeX.exe",
	"BTFirefox": "firefox.exe",
}

// GetIPCKey builds the IPC key: ASTRON_<NAME>_PIPE.
func GetIPCKey() (string, error) {
	name, err := deriveAncestorProcessName()
	if err != nil {
		return "", err
	}
	base := sanitizeProcessName(name)
	if len(base) == 0 {
		return "", errors.New("derived IPC key is empty")
	}
	// enforce naming rule: ASTRON_<NAME>_PIPE, where <NAME> is upper-case, sanitized
	key := fmt.Sprintf("ASTRON_%s_PIPE", strings.ToUpper(base))
	return key, nil
}

// deriveAncestorProcessName walks up the process tree (self, parent, grandparent).
// If any process matches a supported browser executable, that name is returned.
// Otherwise, the last non-empty process name within these levels is returned.
func deriveAncestorProcessName() (string, error) {
	pid := int32(os.Getpid())
	var lastName string

	// depth: 0 = self, 1 = parent, 2 = grandparent
	const maxProcessTreeDepth = 2
	for depth := 0; depth <= maxProcessTreeDepth; depth++ {
		p, err := process.NewProcess(pid)
		if err != nil {
			break
		}
		name, err := p.Name()
		if err == nil && name != "" {
			lastName = name
			if _, ok := matchBrowserTypeByProcessName(name); ok {
				return name, nil
			}
		}

		ppid, err := p.Ppid()
		if err != nil || ppid == 0 || ppid == pid {
			break
		}
		pid = ppid
	}
	if lastName == "" {
		return "", errors.New("failed to derive ancestor process name")
	}
	return lastName, nil
}

// matchBrowserTypeByProcessName maps a process name to a browser enum key
// (e.g. "BTChrome") using BrowserRegisterName.
func matchBrowserTypeByProcessName(name string) (string, bool) {
	base := strings.ToLower(filepath.Base(name))
	// strip extension, e.g. "chrome.exe" -> "chrome"
	if i := strings.LastIndexByte(base, '.'); i > 0 {
		base = base[:i]
	}
	for bt, exe := range BrowserRegisterName {
		exeBase := strings.ToLower(filepath.Base(exe))
		if j := strings.LastIndexByte(exeBase, '.'); j > 0 {
			exeBase = exeBase[:j]
		}
		if base == exeBase {
			return bt, true
		}
	}
	return "", false
}

// sanitizeProcessName normalizes a process name for use in IPC keys.
func sanitizeProcessName(name string) string {
	base := filepath.Base(name)
	// drop .exe or other extensions
	if i := strings.LastIndexByte(base, '.'); i > 0 {
		base = base[:i]
	}
	base = strings.TrimSpace(base)
	if base == "" {
		return ""
	}
	// replace spaces with underscores and normalize to lower-case
	base = strings.ReplaceAll(base, " ", "_")
	return strings.ToLower(base)
}
