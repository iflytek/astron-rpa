import gettext
import locale
import os


class I18n:
    def __init__(self, name: str = "null"):
        """Initialize internationalization, gracefully handle missing translation files"""

        self.translation = None
        try:
            localedir = os.path.join(os.getcwd(), "translations")
            self.translation = gettext.translation(name, localedir=localedir, languages=["zh_CN"])
            locale.setlocale(locale.LC_ALL, "zh_CN.UTF-8")
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


_ = I18n("I18n").gettext
