"""
create_note_page.py - POM for the Create/Edit Note form.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage
from utils.logger import get_logger

log = get_logger(__name__)


class CreateNotePage(BasePage):
    # ?? Locators ??????????????????????????????????????????????????????????
    _CATEGORY_SELECT = (By.CSS_SELECTOR, "select[data-testid='note-category']")
    _TITLE_FIELD     = (By.CSS_SELECTOR, "input[data-testid='note-title']")
    _DESC_FIELD      = (By.CSS_SELECTOR, "textarea[data-testid='note-description']")
    _SAVE_BTN        = (By.CSS_SELECTOR, "button[data-testid='note-submit']")
    _CANCEL_BTN      = (By.CSS_SELECTOR, "button[data-testid='note-cancel']")
    _SUCCESS_TOAST   = (By.CSS_SELECTOR, ".toast-body")

    def select_category(self, category: str):
        self.wait_for_visible(*self._CATEGORY_SELECT)
        select = Select(self.driver.find_element(*self._CATEGORY_SELECT))
        select.select_by_visible_text(category)
        log.info("Selected category: %s", category)

    def enter_title(self, title: str):
        self.type_text(*self._TITLE_FIELD, title)

    def enter_description(self, description: str):
        self.type_text(*self._DESC_FIELD, description)

    def click_save(self):
        self.click(*self._SAVE_BTN, hint="save")
        log.info("Clicked Save")

    def create_note(self, title: str, description: str, category: str = "Home"):
        """Full create-note workflow on the form page."""
        self.select_category(category)
        self.enter_title(title)
        self.enter_description(description)
        self.click_save()
        log.info("Created note: title='%s' category='%s'", title, category)

    def get_success_message(self) -> str:
        try:
            return self.get_text(*self._SUCCESS_TOAST)
        except Exception:
            return ""

    def cancel(self):
        self.click(*self._CANCEL_BTN)
