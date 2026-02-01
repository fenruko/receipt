import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "printer_name": "",
    "paper_width": 80,
    "paper_height": 200,
    "auto_height": True,
    "fields": [
        {"id": "date", "label": "التاريخ", "type": "text", "enabled": True},
        {"id": "customer_name", "label": "اسم العميل", "type": "text", "enabled": True},
        {"id": "items", "label": "التفاصيل", "type": "textarea", "enabled": True},
        {"id": "total", "label": "المجموع", "type": "text", "enabled": True}
    ],
    "header_text": "فاتورة بيع",
    "footer_text": "شكراً لزيارتكم"
}

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG

    def save_config(self, config=None):
        if config:
            self.config = config
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def get_fields(self):
        return self.config.get("fields", [])

    def set_fields(self, fields):
        self.config["fields"] = fields
        self.save_config()
