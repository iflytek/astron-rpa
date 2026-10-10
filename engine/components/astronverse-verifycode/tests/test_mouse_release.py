"""Exercise real slider methods without importing desktop or recognition services."""

# Keep these dependency-free regressions runnable with the standard-library test runner.
# ruff: noqa: PT009, PT027

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / "src/astronverse/verifycode"


def load_method(filename, class_name, method_name, namespace):
    tree = ast.parse((SOURCE / filename).read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name)
    method.decorator_list = []
    module = ast.Module(body=[method], type_ignores=[])
    exec(compile(module, filename, "exec"), namespace)  # noqa: S102 - trusted repository source
    return namespace[method_name]


class MouseReleaseTest(unittest.TestCase):
    def setUp(self):
        self.mouse = SimpleNamespace(
            mouseDown=Mock(), mouseUp=Mock(), position=Mock(return_value=SimpleNamespace(x=100))
        )
        self.move = Mock()
        self.clock = SimpleNamespace(sleep=Mock(), monotonic=Mock(return_value=0))
        self.core = SimpleNamespace(
            get_base64_screenshot=Mock(return_value="image"),
            get_api_result=Mock(return_value="100"),
            get_margin_left=Mock(return_value="100"),
            html_drag_plus=Mock(),
        )
        rect = SimpleNamespace(left=0, top=0, width=lambda: 100, height=lambda: 20)
        element = SimpleNamespace(rect=lambda: rect, point=lambda: SimpleNamespace(x=10, y=20))
        self.namespace = {
            "pyautogui": self.mouse,
            "smooth_move": self.move,
            "time": self.clock,
            "sys": sys,
            "random": SimpleNamespace(choice=Mock(return_value=0.2)),
            "VerifyCodeCore": self.core,
            "Locator": SimpleNamespace(locator=Mock(return_value=element)),
            "logger": Mock(),
        }
        self.core.release_left_button = load_method("core.py", "VerifyCodeCore", "release_left_button", self.namespace)
        self.drag = load_method("core.py", "VerifyCodeCore", "html_drag_plus", self.namespace)
        self.slider = load_method("verifycode.py", "VerifyCode", "slider_code", self.namespace)
        self.slider_args = {
            "browser_obj": SimpleNamespace(browser_type=SimpleNamespace(value="chrome")),
            "picture_pick": {"elementData": {}},
            "slider_pick": {"elementData": {}},
            "unmatched_flag": True,
        }

    def test_normal_drag_releases_mouse_at_destination(self):
        self.drag(SimpleNamespace(x=10, y=20), (110, 20))
        self.move.assert_called_with(110, 20, duration=0.2)
        self.mouse.mouseUp.assert_called_once_with(button="left")

    def test_drag_failure_releases_mouse_and_preserves_error(self):
        error = RuntimeError("movement failed")
        self.move.side_effect = [None, error]
        with self.assertRaises(RuntimeError) as caught:
            self.drag(SimpleNamespace(x=10, y=20), (110, 20))
        self.assertIs(caught.exception, error)
        self.mouse.mouseUp.assert_called_once_with(button="left")

    def test_drag_interruption_releases_mouse(self):
        self.clock.sleep.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.drag(SimpleNamespace(x=10, y=20), (110, 20))
        self.mouse.mouseUp.assert_called_once_with(button="left")

    def test_unmatched_slider_releases_on_success(self):
        self.assertEqual(self.slider(**self.slider_args), 100)
        self.mouse.mouseUp.assert_called_once_with(button="left")

    def test_unmatched_slider_releases_when_element_disappears(self):
        error = RuntimeError("element disappeared")
        self.core.get_margin_left.side_effect = error
        with self.assertRaises(RuntimeError) as caught:
            self.slider(**self.slider_args)
        self.assertIs(caught.exception, error)
        self.mouse.mouseUp.assert_called_once_with(button="left")

    def test_nonconverging_slider_times_out_and_releases(self):
        self.core.get_margin_left.side_effect = ["0", "0", RuntimeError("unbounded adjustment")]
        self.clock.monotonic.side_effect = [0, 1, 31]
        with self.assertRaisesRegex(TimeoutError, "30 seconds"):
            self.slider(**self.slider_args)
        self.mouse.mouseUp.assert_called_once_with(button="left")
        self.assertEqual(self.core.get_margin_left.call_count, 2)

    def test_release_failure_preserves_original_drag_error(self):
        original = RuntimeError("movement failed")
        self.move.side_effect = [None, original]
        self.mouse.mouseUp.side_effect = RuntimeError("release failed")
        with self.assertRaises(RuntimeError) as caught:
            self.drag(SimpleNamespace(x=10, y=20), (110, 20))
        self.assertIs(caught.exception, original)
        self.namespace["logger"].exception.assert_called_once()

    def test_release_failure_after_success_is_reported(self):
        self.mouse.mouseUp.side_effect = RuntimeError("release failed")
        with self.assertRaisesRegex(RuntimeError, "release failed"):
            self.drag(SimpleNamespace(x=10, y=20), (110, 20))

    def test_invalid_step_is_rejected_before_mouse_is_pressed(self):
        for step in (0, -1):
            with self.subTest(step=step), self.assertRaisesRegex(ValueError, "mini_step"):
                self.slider(**self.slider_args, mini_step=step)
        self.mouse.mouseDown.assert_not_called()


if __name__ == "__main__":
    unittest.main()
