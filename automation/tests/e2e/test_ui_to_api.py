"""
test_ui_to_api.py — E2E Scenario 1: Create note via UI → validate in API.

Flow:
  1. Login via UI
  2. Create note via UI form
  3. Authenticate via API
  4. GET /notes via API
  5. Assert note exists in API with matching fields
"""

import allure
import pytest

from api_client.auth_client import AuthClient
from api_client.notes_client import NotesClient
from config.environment import config
from pages.create_note_page import CreateNotePage
from pages.login_page import LoginPage
from pages.notes_page import NotesPage


@allure.feature("E2E Hybrid")
@allure.story("UI → API Sync")
class TestUIToAPISync:

    @allure.title("TC-E2E-01 | UI-created note appears in API GET /notes")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_ui_create_note_visible_in_api(self, driver, note_data, api_token):
        """
        Preconditions:
          - Valid user account registered.
          - API token available via session fixture.

        Steps:
          1. Login via UI.
          2. Navigate to Add Note.
          3. Fill form and save.
          4. Call GET /notes via API.
          5. Locate note by title in API response.
          6. Validate all fields match.
        """
        # ── Step 1-3: UI Create ────────────────────────────────────────────
        with allure.step("Login via UI"):
            login_page = LoginPage(driver)
            login_page.login(config.test_email, config.test_password)
            assert login_page.is_login_successful()

        with allure.step("Create note via UI form"):
            notes_page  = NotesPage(driver)
            create_page = CreateNotePage(driver)
            notes_page.click_add_note()
            create_page.create_note(
                title=note_data["title"],
                description=note_data["description"],
                category=note_data["category"],
            )
            assert notes_page.wait_for_note_visible(note_data["title"]), (
                f"Note '{note_data['title']}' not visible in UI after creation"
            )

        # ── Step 4-6: API Validation ──────────────────────────────────────
        with allure.step("Fetch all notes via API and find matching note"):
            client = NotesClient(token=api_token)
            api_note = client.find_note_by_title(note_data["title"])

        with allure.step("Assert fields match between UI input and API response"):
            assert api_note is not None, (
                f"Note '{note_data['title']}' NOT found in API response"
            )
            assert api_note["title"]       == note_data["title"],       "Title mismatch"
            assert api_note["description"] == note_data["description"], "Description mismatch"
            assert api_note["category"]    == note_data["category"],    "Category mismatch"

    @allure.title("TC-E2E-02 | UI-created note has valid metadata in API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ui_created_note_metadata(self, driver, note_data, api_token):
        """API response for a UI-created note must contain id, createdAt, completed."""
        with allure.step("Create note via UI"):
            LoginPage(driver).login(config.test_email, config.test_password)
            notes_page  = NotesPage(driver)
            create_page = CreateNotePage(driver)
            notes_page.click_add_note()
            create_page.create_note(**note_data)
            notes_page.wait_for_note_visible(note_data["title"])

        with allure.step("Validate metadata in API"):
            client   = NotesClient(token=api_token)
            api_note = client.find_note_by_title(note_data["title"])
            assert api_note, "Note not found in API"
            assert "id"        in api_note, "Missing field: id"
            assert "created_at" in api_note, "Missing field: created_at"
            assert "completed" in api_note, "Missing field: completed"
