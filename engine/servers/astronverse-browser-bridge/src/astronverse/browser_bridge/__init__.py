from enum import Enum


class CommonForBrowserType(Enum):
    """浏览器类型枚举"""

    BTChrome = "chrome"
    BTEdge = "edge"
    BT360SE = "360se"
    BT360X = "360ChromeX"
    BTFirefox = "firefox"
    BTChromium = "chromium"


BROWSER_REGISTER_NAME = {
    CommonForBrowserType.BTChrome.value: "chrome.exe",
    CommonForBrowserType.BTEdge.value: "msedge.exe",
    CommonForBrowserType.BT360SE.value: "360se6.exe",
    CommonForBrowserType.BT360X.value: "360ChromeX.exe",
    CommonForBrowserType.BTFirefox.value: "firefox.exe",
}
