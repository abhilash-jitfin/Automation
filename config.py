import json
import os
from enum import Enum


class Env(Enum):
    PROD = "prod"
    QA = "qa"
    DEV = "dev"


class Config:
    _instance = None
    SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "settings.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load_settings()
        return cls._instance

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "r") as f:
                self.settings = json.load(f)
        else:
            self.settings = {}

    def save_settings(self):
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def set_environment(self, env):
        self.settings["environment"] = env.value
        self.save_settings()

    def get_environment(self):
        return self.settings.get("environment", Env.PROD.value)

    def set_token(self, token):
        self.settings["token"] = token
        self.save_settings()

    def get_token(self):
        return self.settings.get("token")
