import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.language_dialog import LanguagePromptDialog
from core.i18n import i18n
import os

def main():
    app = QApplication(sys.argv)
    
    # Check if this is the first run / check settings for language
    # For simplicity, we just ask on launch if not saved in a config yet.
    # We can use QSettings or a config file. We'll use a simple marker file for now.
    config_file = "app_config.json"
    lang = "en"
    
    import json
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                cfg = json.load(f)
                lang = cfg.get("language", "en")
        except:
            pass
    else:
        # Default to English on first run silently
        with open(config_file, "w") as f:
            json.dump({"language": "en"}, f)

    i18n.set_language(lang)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
