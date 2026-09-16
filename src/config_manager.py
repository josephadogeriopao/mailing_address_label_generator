"""
Configuration Management Persistence Layer
------------------
Description: Manages reading, validation, writing, and storage rules
             for application settings independently of the UI framework.

Author: Joseph Adogeri
File: config_manager.py
"""

import os
import json

class ConfigManager:
    def __init__(self, config_file="app_config.json"):
        self.config_file = config_file

    def load_config(self) -> dict:
        """Reads complete configuration properties from the JSON file safely."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_setting(self, key: str, value: str):
        """Updates a specific configuration property safely in the storage layer."""
        config = self.load_config()
        config[key] = value
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")
