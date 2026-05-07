import allure
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.environment import config
from pages.login_page import LoginPage
from pages.notes_page import NotesPage
from pages.create_note_page import CreateNotePage

@allure.feature("Notes - UI")
@allure.story("Delete Note via UI")
class TestDeleteNoteUI:

    @pytest.fixture(autouse=True)
    def _login(self, driver):
        LoginPage(driver).login(config.test_email, config.test_password)

    @allure.title("TC-UI-11 | Delete note via UI -> disappears from list")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_note_ui(self, driver, note_data):
        notes_page  = NotesPage(driver)
        create_page = CreateNotePage(driver)

        # Create note via UI
        notes_page.click_add_note()
        create_page.create_note(**note_data)
        notes_page.wait_for_note_visible(note_data["title"])

        # Click Delete button on the card
        delete_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(("xpath", "//button[normalize-space(text())='Delete']"))
        )
        driver.execute_script("arguments[0].click();", delete_btn)

        # Confirm in modal — click the red Delete button
        confirm_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(("xpath", "//div[contains(@class,'modal')]//button[normalize-space(text())='Delete']"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)

        # Assert note gone from list
        assert notes_page.wait_for_note_gone(note_data["title"]), (
            f"Note '{note_data['title']}' still visible after UI deletion"
        )