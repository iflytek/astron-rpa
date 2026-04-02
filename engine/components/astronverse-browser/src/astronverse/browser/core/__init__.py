import platform
import sys

if sys.platform == "win32":
    from astronverse.browser.core.core_win import BrowserCore
elif sys.platform == "darwin":
    from astronverse.browser.core.core_mac import BrowserCore
else:
    raise NotImplementedError(f"Your platform ({platform.system()}) is not supported by browser core.")
