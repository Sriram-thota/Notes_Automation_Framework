"""
api_fixture.py - Pytest fixtures for API client with authenticated session.
"""

import pytest

from api_client.auth_client import AuthClient
from api_client.notes_client import NotesClient
from config.environment import config
from utils.logger import get_logger

log = get_logger(__name__)


@pytest.fixture(scope="session")
def api_token() -> str:
    """Session-scoped: login once and reuse the token across all API tests."""
    client = AuthClient()
    token = client.login_default()
    log.info("Session-scoped API token acquired")
    return token


@pytest.fixture(scope="function")
def notes_client(api_token) -> NotesClient:
    """Authenticated NotesClient for each test function."""
    return NotesClient(token=api_token)


@pytest.fixture(scope="function")
def auth_client() -> AuthClient:
    return AuthClient()
