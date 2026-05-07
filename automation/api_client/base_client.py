"""
base_client.py — Reusable HTTP client wrapping requests.Session.
Centralizes headers, timeouts, logging, and response validation.
"""

import time
from typing import Any, Dict, Optional

import allure
import requests

from config.environment import config
from utils.logger import get_logger

log = get_logger(__name__)


class BaseAPIClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or config.api_base_url
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        if token:
            self.set_auth_token(token)

    # ── Auth ──────────────────────────────────────────────────────────────

    def set_auth_token(self, token: str):
        self.session.headers.update({"x-auth-token": token})
        log.debug("Auth token set on session")

    # ── Core HTTP Methods ─────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        expected_status: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        start = time.perf_counter()

        log.info(">> %s %s", method.upper(), url)
        if "json" in kwargs:
            log.debug("   body: %s", kwargs["json"])

        resp = self.session.request(
            method, url, timeout=config.api_timeout, **kwargs
        )
        elapsed = time.perf_counter() - start

        log.info(
            "<< %d %s  [%.3fs]", resp.status_code, resp.reason, elapsed
        )

        # Attach to Allure
        allure.attach(
            f"{method.upper()} {url}\n"
            f"Status: {resp.status_code}  Time: {elapsed:.3f}s\n\n"
            f"{resp.text[:2000]}",
            name=f"{method.upper()} {endpoint}",
            attachment_type=allure.attachment_type.TEXT,
        )

        if expected_status is not None:
            assert resp.status_code == expected_status, (
                f"Expected {expected_status}, got {resp.status_code}. "
                f"Body: {resp.text[:500]}"
            )

        return resp

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)

    # ── Response Helpers ──────────────────────────────────────────────────

    @staticmethod
    def json(response: requests.Response) -> Any:
        try:
            return response.json()
        except Exception as exc:
            raise ValueError(
                f"Response is not JSON. Status: {response.status_code}. "
                f"Body: {response.text[:300]}"
            ) from exc
