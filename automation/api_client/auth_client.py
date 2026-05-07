"""
auth_client.py - Handles user registration and login via the Notes API.
"""

import requests

from api_client.base_client import BaseAPIClient
from config.environment import config
from utils.logger import get_logger

log = get_logger(__name__)


class AuthClient(BaseAPIClient):
    _REGISTER = "/users/register"
    _LOGIN    = "/users/login"

    def register(
        self,
        name: str,
        email: str,
        password: str,
    ) -> requests.Response:
        payload = {"name": name, "email": email, "password": password}
        resp = self.post(self._REGISTER, json=payload)
        log.info("Register: %s -> %d", email, resp.status_code)
        return resp

    def login(self, email: str, password: str) -> str:
        """Login and return the auth token."""
        payload = {"email": email, "password": password}
        resp = self.post(self._LOGIN, json=payload, expected_status=200)
        body = self.json(resp)
        token = body.get("data", {}).get("token")
        assert token, f"Token missing in login response: {body}"
        log.info("Login successful - token acquired for %s", email)
        return token

    def login_default(self) -> str:
        """Convenience: login with credentials from config."""
        return self.login(config.test_email, config.test_password)
