"""
conftest.py - Root conftest: shared fixtures, hooks, and plugin configuration.
"""

import pytest
from faker import Faker

# ?? Import all fixtures so Pytest discovers them ??????????????????????????????
from fixtures.api_fixture import api_token, auth_client, notes_client
from fixtures.browser_fixture import driver

fake = Faker()


# ?? Hook: capture test outcome for screenshot-on-failure logic ????????????????

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ?? Shared data fixtures ??????????????????????????????????????????????????????

@pytest.fixture
def note_data() -> dict:
    """Generate unique note payload for each test."""
    return {
        "title":       f"Test Note {fake.bothify('???-###')}",
        "description": fake.sentence(nb_words=10),
        "category":    fake.random_element(["Home", "Work", "Personal"]),
    }


@pytest.fixture
def invalid_note_data() -> dict:
    return {"title": "", "description": "", "category": ""}
