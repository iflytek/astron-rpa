from enum import Enum
from typing import Dict, List

# 与 native_messaging internal/config.go 中 BrowserRegisterName 对齐：
# - 首项用于推导 ipcKey（ASTRON_*_PIPE），须与 Go 端每组第一项一致；
# - 其余为进程名别名，供后续扩展（如与其它模块统一识别逻辑）使用。


class CommonForBrowserType(Enum):
    """浏览器类型枚举"""

    BTChrome = "chrome"
    BTEdge = "edge"
    BT360SE = "360se"
    BT360X = "360ChromeX"
    BTFirefox = "firefox"
    BTChromium = "chromium"


# API 侧 browser_type 字符串 -> ['推导 ipc 名', ...别名]
BROWSER_REGISTER_NAME: Dict[str, List[str]] = {
    CommonForBrowserType.BTChrome.value: [
        "chrome.exe",
        "chrome",
        "google chrome",
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ],
    CommonForBrowserType.BTChromium.value: [
        "chrome.exe",
        "chrome",
        "google chrome",
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ],
    CommonForBrowserType.BTEdge.value: [
        "msedge.exe",
        "msedge",
        "microsoft edge",
        "microsoft-edge",
        "microsoft-edge-stable",
    ],
    CommonForBrowserType.BT360SE.value: ["360se6.exe"],
    CommonForBrowserType.BT360X.value: ["360ChromeX.exe"],
    CommonForBrowserType.BTFirefox.value: ["firefox.exe", "firefox"],
}

