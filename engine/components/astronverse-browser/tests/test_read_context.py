from unittest.mock import Mock

from astronverse.browser import CommonForBrowserType
from astronverse.browser.browser_software import BrowserSoftware
from astronverse.browser.core.core_win import BrowserCore


def test_get_current_browser_does_not_activate_or_maximize_another_window(monkeypatch):
    control = object()
    lookup = Mock(return_value=control)
    activate = Mock()
    monkeypatch.setattr(BrowserCore, "get_browser_control", lookup)
    monkeypatch.setattr(BrowserCore, "browser_top_and_max", activate)
    method = getattr(BrowserSoftware.get_current_obj, "__wrapped__", BrowserSoftware.get_current_obj)
    browser = method(CommonForBrowserType.BTEdge)
    assert browser.browser_control is control
    assert browser.browser_type == CommonForBrowserType.BTEdge
    lookup.assert_called_once_with(CommonForBrowserType.BTEdge.value)
    activate.assert_not_called()
