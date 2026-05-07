"""
notes_page.py - POM for the Notes list / home screen.
"""

from typing import List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import get_logger

log = get_logger(__name__)


class NotesPage(BasePage):
    # ?? Locators ??????????????????????????????????????????????????????????
    _ADD_NOTE_BTN = (By.XPATH, "//a[contains(@href,'add')] | //button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'NOTE')] | //*[@data-testid='add-note-btn' or @data-testid='add-note-link']")
    _NOTE_CARDS      = (By.CSS_SELECTOR, ".card")
    _NOTE_TITLE      = (By.CSS_SELECTOR, ".card-title")
    _NOTE_CATEGORY   = (By.CSS_SELECTOR, ".badge")
    _SUCCESS_TOAST   = (By.CSS_SELECTOR, ".toast-body")
    _NOTES_CONTAINER = (By.CSS_SELECTOR, ".notes-container, #notes-list")

    NOTES_PATH = "/"

    def open_notes_page(self):
        from config.environment import config
        self.open(config.ui_base_url + self.NOTES_PATH)

    def click_add_note(self):
        self.click(*self._ADD_NOTE_BTN, hint="add note")
        log.info("Clicked Add Note button")

    def get_note_titles(self) -> List[str]:
        self.wait_for_dom_ready()
        elements = self.find_all("xpath", "//div[contains(@class,'card')]//h5 | //div[contains(@class,'card')]//h6 | //div[contains(@class,'card-title')]")
        titles = [el.text.strip() for el in elements if el.text.strip()]
        log.info("Found %d note(s) on UI: %s", len(titles), titles)
        return titles

    def is_note_visible(self, title: str) -> bool:
        return title in self.get_note_titles()

    def get_success_toast_text(self) -> str:
        try:
            return self.get_text(*self._SUCCESS_TOAST)
        except Exception:
            return ""

    def wait_for_note_visible(self, title: str) -> bool:
    # Ensure we are on the notes list page
        from config.environment import config
        if "/notes/app" not in self.driver.current_url or "add" in self.driver.current_url:
            self.open(config.ui_base_url + "/")
            self.wait_for_dom_ready()

        # Search by visible text anywhere on page — avoids card-title selector dependency
        xpath = f"//*[normalize-space(text())='{title}' or contains(normalize-space(text()),'{title}')]"
        try:
            self.wait.until(
                lambda d: len(d.find_elements("xpath", xpath)) > 0
            )
            log.info("Note '%s' appeared in UI [OK]", title)
            return True
        except Exception:
            log.error("Note '%s' did NOT appear in UI [FAIL]", title)
            return False

    def wait_for_note_gone(self, title: str) -> bool:
        xpath = f"//*[normalize-space(text())='{title}' or contains(normalize-space(text()),'{title}')]"
        try:
            self.wait.until(lambda d: len(d.find_elements("xpath", xpath)) == 0)
            log.info("Note '%s' removed from UI [OK]", title)
            return True
        except Exception:
            log.error("Note '%s' still visible in UI after deletion [FAIL]", title)
            return False