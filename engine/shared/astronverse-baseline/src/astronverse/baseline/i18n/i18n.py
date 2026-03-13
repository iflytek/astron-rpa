import gettext
import locale
import os
from pathlib import Path

from astronverse.baseline.config.config import load_user_settings


class I18n:
    def __init__(self, name: str = "null", language: str = None):
        """Initialize internationalization, gracefully handle missing translation files

        Args:
            name: Translation domain name
            language: Language code (e.g., 'zh-CN', 'en-US').
                     If None, will try to read from user settings or use zh-CN as default.
        """

        self.translation = None
        # Load language from user settings if not provided
        self.language = language or load_user_settings().get("language", "zh_CN")

        try:
            current_file = Path(__file__).resolve()
            localedir = current_file.parent.joinpath("translations")

            # Try to load translation for the specified language
            self.translation = gettext.translation(
                name, localedir=str(localedir), languages=[self.language], fallback=True
            )

            # Try to set locale, but don't fail if it's not available
            try:
                # Attempt to set locale dynamically, e.g., 'zh_CN' -> 'zh_CN.UTF-8'
                locale.setlocale(locale.LC_ALL, f"{self.language}.UTF-8")
            except locale.Error:
                pass  # Locale setting is optional

        except Exception as e:
            return

    def gettext(self, message):
        """Get translated text, gracefully handle missing translation keys"""

        if self.translation is None:
            # Optimization for missing translation files
            return message

        try:
            return self.translation.gettext(message)
        except Exception as e:
            return message

    def getlanguage(self):
        return self.language


# Default instance using system language
i18n = I18n("I18n")
_ = i18n.gettext
