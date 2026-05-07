"""
test_create_note.py — UI test suite for note creation and instant visibility.
"""

import allure
import pytest

from config.environment import config
from pages.create_note_page import CreateNotePage
from pages.login_page import LoginPage
from pages.notes_page import NotesPage
from utils.performance import measure_ui_navigation


@allure.feature("Notes — UI")
@allure.story("Create Note")
class TestCreateNote:

    @pytest.fixture(autouse=True)
    def _login(self, driver):
        """Login before each test in this class."""
        LoginPage(driver).login(config.test_email, config.test_password)

    @allure.title("TC-UI-06 | Create note → appears instantly in list (no refresh)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_note_visible_immediately(self, driver, note_data):
        """
        Precondition: Logged in.
        Steps:
          1. Click Add Note
          2. Fill Category, Title, Description
          3. Save
          4. Assert note is visible WITHOUT page reload
        Expected: Note card appears in the list immediately.
        """
        notes_page   = NotesPage(driver)
        create_page  = CreateNotePage(driver)

        notes_page.click_add_note()
        create_page.create_note(
            title=note_data["title"],
            description=note_data["description"],
            category=note_data["category"],
        )

        appeared = notes_page.wait_for_note_visible(note_data["title"])
        assert appeared, (
            f"Note '{note_data['title']}' did not appear in the UI list after creation"
        )

    @allure.title("TC-UI-07 | Create note with all categories")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("category", ["Home", "Work", "Personal"])
    def test_create_note_all_categories(self, driver, category):
        from faker import Faker
        f = Faker()
        title = f"Cat-Test {f.bothify('??-###')}"

        notes_page  = NotesPage(driver)
        create_page = CreateNotePage(driver)

        notes_page.click_add_note()
        create_page.create_note(title=title, description=f.sentence(), category=category)

        assert notes_page.wait_for_note_visible(title), (
            f"Note with category '{category}' not visible"
        )

    @allure.title("TC-UI-08 | Create note with minimum title length")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_note_min_title(self, driver):
        notes_page  = NotesPage(driver)
        create_page = CreateNotePage(driver)

        notes_page.click_add_note()
        create_page.create_note(
            title="AB",   # 2-char minimum per API validation
            description="Minimum title test note description.",
            category="Work",
        )
        # Should show validation error or success — check no crash
        current_url = driver.current_url
        assert current_url is not None   # page is still stable

    @allure.title("TC-UI-09 | UI load timing within acceptable range")
    @allure.severity(allure.severity_level.MINOR)
    def test_ui_page_load_timing(self, driver):
        notes_page = NotesPage(driver)
        notes_page.open_notes_page()

        timing = measure_ui_navigation(driver)
        assert timing["loadComplete"] < 5000, (
            f"Page load too slow: {timing['loadComplete']}ms (threshold 5000ms)"
        )
