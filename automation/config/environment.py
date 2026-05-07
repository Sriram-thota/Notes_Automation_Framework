"""
environment.py - Singleton configuration loader.
Merges config.yaml with .env overrides for flexible multi-env support.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance = None
    _cfg = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        path = Path(__file__).parent / "config.yaml"
        with open(path) as f:
            self._cfg = yaml.safe_load(f)

    # ?? UI ????????????????????????????????????????????????????????????????
    @property
    def ui_base_url(self) -> str:
        return os.getenv("UI_BASE_URL", self._cfg["ui"]["base_url"])

    @property
    def browser(self) -> str:
        return os.getenv("BROWSER", self._cfg["ui"]["browser"]).lower()

    @property
    def headless(self) -> bool:
        return os.getenv("HEADLESS", str(self._cfg["ui"]["headless"])).lower() == "true"

    @property
    def explicit_wait(self) -> int:
        return int(os.getenv("EXPLICIT_WAIT", self._cfg["ui"]["explicit_wait"]))

    # ?? API ???????????????????????????????????????????????????????????????
    @property
    def api_base_url(self) -> str:
        return os.getenv("API_BASE_URL", self._cfg["api"]["base_url"])

    @property
    def api_timeout(self) -> int:
        return int(os.getenv("API_TIMEOUT", self._cfg["api"]["timeout"]))

    @property
    def performance_threshold(self) -> float:
        return float(self._cfg["api"]["performance_threshold_sec"])

    # ?? Test Credentials ??????????????????????????????????????????????????
    @property
    def test_email(self) -> str:
        return os.getenv("TEST_EMAIL", self._cfg["test_user"]["email"])

    @property
    def test_password(self) -> str:
        return os.getenv("TEST_PASSWORD", self._cfg["test_user"]["password"])

    @property
    def test_name(self) -> str:
        return os.getenv("TEST_NAME", self._cfg["test_user"]["name"])

    # ?? Reporting ?????????????????????????????????????????????????????????
    @property
    def allure_dir(self) -> str:
        return self._cfg["reporting"]["allure_dir"]

    @property
    def screenshot_dir(self) -> str:
        return self._cfg["reporting"]["screenshot_dir"]

    @property
    def log_dir(self) -> str:
        return self._cfg["reporting"]["log_dir"]

    @property
    def log_level(self) -> str:
        return self._cfg["reporting"]["log_level"]


config = Config()
