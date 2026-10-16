import json
from unittest.mock import Mock

import pytest
from astronverse.browser import CommonForBrowserType
from astronverse.browser.browser_software import BrowserSoftware
from astronverse.browser.core.core_win import BrowserCore


@pytest.mark.parametrize("arguments", [{}, {"activate_window": True}, {"activate_window": False}])
def test_get_current_browser_preserves_activation_by_default_and_allows_read_only(monkeypatch, arguments):
    control = object()
    lookup = Mock(return_value=control)
    activate = Mock()
    monkeypatch.setattr(BrowserCore, "get_browser_control", lookup)
    monkeypatch.setattr(BrowserCore, "browser_top_and_max", activate)
    method = getattr(BrowserSoftware.get_current_obj, "__wrapped__", BrowserSoftware.get_current_obj)
    browser = method(CommonForBrowserType.BTEdge, **arguments)
    assert browser.browser_control is control
    assert browser.browser_type == CommonForBrowserType.BTEdge
    lookup.assert_called_once_with(CommonForBrowserType.BTEdge.value)
    if arguments.get("activate_window", True):
        activate.assert_called_once_with(control)
    else:
        activate.assert_not_called()


def test_failed_activation_still_returns_browser_as_before(monkeypatch):
    control = object()
    monkeypatch.setattr(BrowserCore, "get_browser_control", Mock(return_value=control))
    monkeypatch.setattr(BrowserCore, "browser_top_and_max", Mock(side_effect=RuntimeError("window unavailable")))
    method = getattr(BrowserSoftware.get_current_obj, "__wrapped__", BrowserSoftware.get_current_obj)
    assert method().browser_control is control


def test_activation_switch_is_available_in_component_metadata():
    from astronverse.actionlib.atomic import atomicMg

    atomicMg.register(BrowserSoftware)
    inputs = json.loads(atomicMg.json())["BrowserSoftware.get_current_obj"]["inputList"]
    switch = next(p for p in inputs if p["key"] == "activate_window")
    assert switch["default"] is True
    assert switch["types"] == "Bool"
    assert switch["required"] is False
