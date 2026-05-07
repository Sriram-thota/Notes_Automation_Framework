import allure
import pytest
from faker import Faker
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.environment import config
from pages.login_page import LoginPage
from pages.notes_page import NotesPage
from pages.create_note_page import CreateNotePage

fake = Faker()

@allure.feature("Notes - UI")
@allure.story("Edit Note")
class TestEditNote:

    @pytest.fixture(autouse=True)
    def _login(self, driver):
        LoginPage(driver).login(config.test_email, config.test_password)

    @allure.title("TC-UI-10 | Edit note -> updated title visible in list")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_note_title(self, driver, note_data):
        notes_page  = NotesPage(driver)
        create_page = CreateNotePage(driver)

        # Create note via UI
        notes_page.click_add_note()
        create_page.create_note(**note_data)
        notes_page.wait_for_note_visible(note_data["title"])

        # Click Edit button on the card
        edit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(("xpath", "//button[normalize-space(text())='Edit']"))
        )
        driver.execute_script("arguments[0].click();", edit_btn)

        # Wait for Edit modal — update title field
        new_title = f"Edited {fake.bothify('??-###')}"
        title_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(("xpath", "//input[@placeholder='Title' or @name='title' or contains(@class,'title')]"))
        )
        title_input.clear()
        title_input.send_keys(new_title)

        # Click Save in modal
        save_btn = driver.find_element("xpath", "//button[normalize-space(text())='Save']")
        driver.execute_script("arguments[0].click();", save_btn)

        # Assert updated title visible in list
        assert notes_page.wait_for_note_visible(new_title), (
            f"Updated title '{new_title}' not visible after edit"
        )