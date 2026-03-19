import json
import os
from PySide6.QtCore import QObject, Signal

class I18nManager(QObject):
    language_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.locales = {}
        self.current_lang = "en" # default to English
        self.load_locales()

    def load_locales(self):
        locales_dir = os.path.join(os.path.dirname(__file__), "..", "locales")
        for file in os.listdir(locales_dir):
            if file.endswith(".json"):
                lang_code = file.split(".")[0]
                try:
                    with open(os.path.join(locales_dir, file), "r", encoding="utf-8") as f:
                        self.locales[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading {file}: {e}")

    def get_text(self, key, *args):
        lang_dict = self.locales.get(self.current_lang, {})
        text = lang_dict.get(key, key)
        if args:
            try:
                return text % args
            except:
                return text
        return text

    def set_language(self, lang_code):
        if lang_code in self.locales and self.current_lang != lang_code:
            self.current_lang = lang_code
            self.language_changed.emit()

i18n = I18nManager()
def _(key, *args):
    return i18n.get_text(key, *args)
