package internal

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/shirou/gopsutil/process"
)

// BrowserRegisterName：各浏览器类型进程名别名。首项为 Windows 典型「*.exe」，只用于推导 ASTRON_*_PIPE；其余用于匹配进程名。
var BrowserRegisterName = map[string][]string{
	"BTChrome": {
		"chrome.exe", "chrome", "google chrome",
		"google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
	},
	"BTEdge": {
		"msedge.exe", "msedge", "microsoft edge",
		"microsoft-edge", "microsoft-edge-stable",
	},
	"BTFirefox": {"firefox.exe", "firefox"},
	"BT360SE":   {"360se6.exe"},
	"BT360X":    {"360ChromeX.exe"},
}

// GetIPCKey 从祖先进程推导管道名。
// 若能识别为表中某浏览器：必须用该组第一项推 key（与 Python/browser_bridge 按 browser_type 推的 ASTRON_CHROME_PIPE 等一致）；
// 若用祖先进程的原始显示名直接推 key，在 macOS 等处可能得到 Google Chrome → 与对端约定的 CHROME 不一致，故此分支不可省。
// 若识别不了：再退回「进程名去扩展名、空格变下划线」生成 key。
func GetIPCKey() (string, error) {
	name, err := deriveAncestorProcessName()
	if err != nil {
		return "", err
	}
	if bt, ok := matchBrowserType(name); ok {
		al := BrowserRegisterName[bt]
		if len(al) == 0 {
			return "", fmt.Errorf("unsupported browser type for IPC: %q", bt)
		}
		return astronPipe(al[0]), nil
	}
	s := stem(name, true)
	if s == "" {
		return "", errors.New("derived IPC key is empty")
	}
	return astronPipeStem(s), nil
}

// stem：基名去掉最后一段扩展名后小写。underscores 为 true 时把空格换成下划线（用于拼接正式 IPC key）。
func stem(s string, underscores bool) string {
	base := filepath.Base(strings.TrimSpace(s))
	if i := strings.LastIndexByte(base, '.'); i > 0 {
		base = base[:i]
	}
	base = strings.TrimSpace(base)
	if underscores {
		base = strings.ReplaceAll(base, " ", "_")
	}
	return strings.ToLower(base)
}

func matchBrowserType(name string) (string, bool) {
	n := stem(name, false)
	for bt, aliases := range BrowserRegisterName {
		for _, a := range aliases {
			if n == stem(a, false) {
				return bt, true
			}
		}
	}
	return "", false
}

func astronPipe(exeOrName string) string {
	return astronPipeStem(stem(exeOrName, true))
}

func astronPipeStem(lowerStem string) string {
	return fmt.Sprintf("ASTRON_%s_PIPE", strings.ToUpper(lowerStem))
}

func deriveAncestorProcessName() (string, error) {
	pid := int32(os.Getpid())
	var last string
	for depth := 0; depth <= 2; depth++ {
		p, err := process.NewProcess(pid)
		if err != nil {
			break
		}
		name, err := p.Name()
		if err == nil && name != "" {
			last = name
			if _, ok := matchBrowserType(name); ok {
				return name, nil
			}
		}
		ppid, err := p.Ppid()
		if err != nil || ppid == 0 || ppid == pid {
			break
		}
		pid = ppid
	}
	if last == "" {
		return "", errors.New("failed to derive ancestor process name")
	}
	return last, nil
}
