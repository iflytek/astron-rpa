import unittest

from ..browser import ExtensionManager
from ..constants import BrowserType


class Test(unittest.TestCase):
    def test_install(self):
        ex_manager = ExtensionManager(browser_type=BrowserType.CHROME)
        ex_manager.install()

    def test_check_status(self):
        print(ExtensionManager(browser_type=BrowserType.BROWSER_360).check_status())

    def test_kill_browser(self):
        ExtensionManager(browser_type=BrowserType.BROWSER_360).close_browser()

    def test_check_browser(self):
        ex_manager = ExtensionManager(browser_type=BrowserType.BROWSER_360)
        print(ex_manager.check_browser())

    def test_get_support(self):
        print([browser.value.lower() for browser in ExtensionManager.get_support()])
