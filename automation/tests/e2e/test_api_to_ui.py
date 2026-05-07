"""
test_api_to_ui.py — E2E Scenario 2: Delete note via API → assert gone from UI.

Flow:
  1. Create a note via API (clean state)
  2. Login via UI — verify note IS visible
  3. Delete note via API
  4. Refresh UI
  5. Assert note is NO LONGER visible
"""

import allure
import pytest

from api_client.notes_client import NotesClient
from config.environment import config
from pages.login_page import LoginPage
from pages.notes_page import NotesPage


@allure.feature("E2E Hybrid")
@allure.story("API → UI Sync")
class TestAPIToUISync:

    @allure.title("TC-E2E-03 | API-deleted note disappears from UI after refresh")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_api_delete_reflected_in_ui(self, driver, note_data, api_token):
        """
        Preconditions:
          - Valid user account. API token available.

        Steps:
          1. Create note via API.
          2. Login via UI.
          3. Confirm note is visible in UI.
          4. Delete note via API.
          5. Refresh UI.
          6. Confirm note is no longer visible.
        """
        client = NotesClient(token=api_token)

        # ── Step 1: Create via API ─────────────────────────────────────────
        with allure.step("Create note via API to get a clean testable state"):
            created = client.create_note(**note_data)
            note_id = created["id"]
            allure.attach(
                f"id={note_id}  title='{note_data['title']}'",
                name="Created Note",
                attachment_type=allure.attachment_type.TEXT,
            )

        # ── Step 2-3: Verify on UI ─────────────────────────────────────────
        with allure.step("Login via UI and assert note is visible"):
            notes_page = NotesPage(driver)
            LoginPage(driver).login(config.test_email, config.test_password)
            visible = notes_page.wait_for_note_visible(note_data["title"])
            assert visible, (
                f"Note '{note_data['title']}' should be visible in UI before deletion"
            )

        # ── Step 4: Delete via API ─────────────────────────────────────────
        with allure.step("Delete note via API"):
            deleted = client.delete_note(note_id)
            assert deleted, f"API deletion of note id={note_id} failed"

        # ── Step 5: Refresh UI ─────────────────────────────────────────────
        with allure.step("Refresh the UI notes list"):
            notes_page.refresh()

        # ── Step 6: Assert gone ────────────────────────────────────────────
        with allure.step("Assert deleted note is no longer visible in UI"):
            gone = notes_page.wait_for_note_gone(note_data["title"])
            assert gone, (
                f"Note '{note_data['title']}' still visible in UI after API deletion"
            )

    @allure.title("TC-E2E-04 | Delete all notes via API → UI shows empty state")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_all_leaves_empty_ui(self, driver, api_token):
        """
        Creates 2 notes via API, deletes them all, then asserts the UI list is empty.
        """
        from faker import Faker
        f = Faker()
        client = NotesClient(token=api_token)

        created_ids = []
        titles = []
        with allure.step("Create 2 notes via API"):
            for _ in range(2):
                data = {
                    "title":       f"Cleanup {f.bothify('??-###')}",
                    "description": f.sentence(),
                    "category":    "Work",
                }
                note = client.create_note(**data)
                created_ids.append(note["id"])
                titles.append(data["title"])

        with allure.step("Login and verify notes appear in UI"):
            LoginPage(driver).login(config.test_email, config.test_password)
            notes_page = NotesPage(driver)
            for title in titles:
                assert notes_page.wait_for_note_visible(title)

        with allure.step("Delete all created notes via API"):
            for nid in created_ids:
                client.delete_note(nid)

        with allure.step("Refresh UI and assert notes are gone"):
            notes_page.refresh()
            for title in titles:
                gone = notes_page.wait_for_note_gone(title)
                assert gone, f"Note '{title}' still visible after deletion"
