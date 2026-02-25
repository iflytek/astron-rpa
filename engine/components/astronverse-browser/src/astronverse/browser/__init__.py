from enum import Enum


class CommonForBrowserType(Enum):
    """浏览器类型枚举"""

    BTChrome = "chrome"
    BTEdge = "edge"
    BT360SE = "360se"
    BT360X = "360ChromeX"
    BTFirefox = "firefox"
    BTChromium = "chromium"


ALL_BROWSER_TYPES = [
    CommonForBrowserType.BTChrome,
    CommonForBrowserType.BTEdge,
    CommonForBrowserType.BT360X,
    CommonForBrowserType.BT360SE,
    CommonForBrowserType.BTFirefox,
    CommonForBrowserType.BTChromium,
]

# 软件名称正则匹配
BROWSER_SOFTWARE_TAG = {
    CommonForBrowserType.BTChrome.value: "chrome",
    CommonForBrowserType.BTEdge.value: "msedge",
    CommonForBrowserType.BT360SE.value: "360se6",
    CommonForBrowserType.BT360X.value: "360ChromeX",
    CommonForBrowserType.BTFirefox.value: "firefox",
    CommonForBrowserType.BTChromium.value: "chromium",
}

# 注册表名称
BROWSER_REGISTER_NAME = {
    CommonForBrowserType.BTChrome.value: "chrome.exe",
    CommonForBrowserType.BTEdge.value: "msedge.exe",
    CommonForBrowserType.BT360SE.value: "360se6.exe",
    CommonForBrowserType.BT360X.value: "360ChromeX.exe",
    CommonForBrowserType.BTFirefox.value: "firefox.exe",
}

# 隐身模式
BROWSER_PRIVATE_MAP = {
    CommonForBrowserType.BTChrome.value: "incognito",
    CommonForBrowserType.BTEdge.value: "inprivate",
}

# window:uia窗口句柄的class_name
BROWSER_UIA_WINDOW_CLASS = {
    CommonForBrowserType.BTChrome.value: (
        "Chrome_WidgetWin_1",
        ["Chrome Legacy Window", "- Google Chrome", " - Chrome"],
        "in",
    ),
    CommonForBrowserType.BTEdge.value: ("Chrome_WidgetWin_1", ["edge"], "last_in"),
    CommonForBrowserType.BT360SE.value: ("360se6_Frame", ["- 360安全浏览器"], "in"),
    CommonForBrowserType.BT360X.value: ("Chrome_WidgetWin_1", ["- 360极速浏览器X"], "in"),
    CommonForBrowserType.BTFirefox.value: ("MozillaWindowClass", ["Firefox"], "in"),
    CommonForBrowserType.BTChromium.value: ("Chrome_WidgetWin_1", ["- Chromium"], "in"),
}

# window:uia网页渲染句柄的class_name
BROWSER_UIA_POINT_CLASS = {
    CommonForBrowserType.BTChrome.value: ("Chrome_RenderWidgetHostHWND", "ClassName"),
    CommonForBrowserType.BTEdge.value: ("Chrome_RenderWidgetHostHWND", "ClassName"),
    CommonForBrowserType.BT360SE.value: ("Chrome_RenderWidgetHostHWND", "ClassName"),
    CommonForBrowserType.BT360X.value: ("Chrome_RenderWidgetHostHWND", "ClassName"),
    CommonForBrowserType.BTFirefox.value: ("tabbrowser-tabpanels", "AutomationId"),
    CommonForBrowserType.BTChromium.value: ("Chrome_RenderWidgetHostHWND", "ClassName"),
}


# ------------浏览器定义结束--------------


class Element:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class CommonForTimeoutHandleType(Enum):
    """超时处理类型枚举"""

    ExecError = "execError"
    StopLoad = "stopLoad"


class WaitElementForStatusFlag(Enum):
    """等待元素状态标志枚举"""

    ElementExists = "y"
    ElementDisappears = "n"


class ButtonForClickTypeFlag(Enum):
    """按钮点击类型标志枚举"""

    Left = "click"
    Double = "dbclick"
    Right = "right"


class ButtonForAssistiveKeyFlag(Enum):
    """辅助按键标志枚举"""

    Nothing = "None"
    Alt = "Alt"
    Ctrl = "Ctrl"
    Shift = "Shift"
    Win = "Win"


class FillInputForFillTypeFlag(Enum):
    """填充输入类型标志枚举"""

    Text = "text"
    Clipboard = "clipboard"
    Credential = "credential"


class ElementAttributeOpTypeFlag(Enum):
    """元素属性操作类型标志枚举"""

    Get = "get"
    Set = "set"
    Del = "del"


class ElementDragDirectionTypeFlag(Enum):
    """元素拖拽方向类型标志枚举"""

    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"


class ElementDragTypeFlag(Enum):
    """元素拖拽类型标志枚举"""

    Start = "start"
    Current = "current"


class BrowserBizCode(Enum):
    """浏览器业务代码枚举"""

    OK = "0000"
    ServerErr = "5001"
    ElemErr = "5002"
    ExecErr = "5003"


class ElementGetAttributeTypeFlag(Enum):
    """元素获取属性类型标志枚举"""

    GetText = "getText"
    GetHtml = "getHtml"
    GetValue = "getValue"
    GetLink = "getLink"
    GetAttribute = "getAttribute"
    GetPosition = "getPosition"
    GetSelection = "getSelection"
    GetStyle = "getStyle"


class ElementGetAttributeHasSelfTypeFlag(Enum):
    """元素获取属性包含自身类型标志枚举"""

    GetElement = "getElement"
    GetText = "getText"
    GetHtml = "getHtml"
    GetValue = "getValue"
    GetLink = "getLink"
    GetAttribute = "getAttribute"
    GetPosition = "getPosition"
    GetSelection = "getSelection"
    GetStyle = "getStyle"


class ElementCheckedTypeFlag(Enum):
    """元素选中类型标志枚举"""

    Checked = "checked"
    UnChecked = "unchecked"
    Reversed = "reversed"


class SelectionPartner(Enum):
    """选择伙伴枚举"""

    Contains = "contains"
    Equal = "equal"
    Index = "index"


class RelativePosition(Enum):
    """相对位置枚举"""

    ScreenLeft = "screenLeft"
    WebPageLeft = "webPageLeft"


class FillInputForInputTypeFlag(Enum):
    """填充输入类型标志枚举"""

    Append = "append"
    Overwrite = "overwrite"


class ScrollbarForXScrollTypeFlag(Enum):
    """滚动条X轴滚动类型标志枚举"""

    Left = "left"
    Right = "right"
    Defined = "defined"


class ScrollbarForYScrollTypeFlag(Enum):
    """滚动条Y轴滚动类型标志枚举"""

    Top = "top"
    Bottom = "bottom"
    Defined = "defined"


class ScreenShotForShotRangeFlag(Enum):
    """截图范围标志枚举"""

    Visual = "visual"
    All = "all"


class DownloadModeForFlag(Enum):
    """下载模式标志枚举"""

    Click = "click"
    Link = "link"


class ScrollbarType(Enum):
    """滚动条类型枚举"""

    Window = "window"
    CustomEle = "customEle"


class ScrollDirection(Enum):
    """滚动方向枚举"""

    Horizontal = "horizontal"
    Vertical = "vertical"


class WebSwitchType(Enum):
    """网页切换类型枚举"""

    URL = "url"
    TITLE = "title"
    TabId = "tabId"


class InputType(Enum):
    """输入类型枚举"""

    Content = "content"
    File = "file"


class TablePickType(Enum):
    """表格选择类型枚举"""

    Row = "row"
    Column = "column"


class LocateType(Enum):
    """定位类型枚举"""

    Xpath = "xpath"
    CssSelector = "cssSelector"
    Text = "text"


class ElementCreateReturnType(Enum):
    """创建元素对象返回类型"""

    SINGLE = "single"  # 单个元素对象
    LIST = "list"  # 元素对象列表


class RelativeType(Enum):
    """相对类型枚举"""

    Child = "child"
    Parent = "parent"
    Sibling = "sibling"


class ChildElementType(Enum):
    """子元素类型枚举"""

    All = "all"
    Index = "index"
    Xpath = "xpath"
    Last = "last"


class SiblingElementType(Enum):
    """兄弟元素类型枚举"""

    All = "all"
    Next = "next"
    Prev = "prev"
