"""
login_page.py - POM for the Notes App login screen.
URL: https://practice.expandtesting.com/notes/app/login
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import get_logger

log = get_logger(__name__)


class LoginPage(BasePage):
    # ?? Locators ??????????????????????????????????????????????????????????
    _EMAIL_FIELD    = (By.CSS_SELECTOR, "input[data-testid='login-email']")
    _PASSWORD_FIELD = (By.CSS_SELECTOR, "input[data-testid='login-password']")
    _SUBMIT_BTN = (By.XPATH, "//button[@data-testid='login-submit' or @type='submit' or contains(text(),'Login')]")
    _ERROR_TOAST    = (By.CSS_SELECTOR, ".toast-body")
    _NAV_LOGO       = (By.CSS_SELECTOR, "nav .navbar-brand")

    LOGIN_PATH = "/login"

    def open_login_page(self):
        from config.environment import config
        self.open(config.ui_base_url + self.LOGIN_PATH)
        log.info("Opened login page")

    def enter_email(self, email: str):
        self.type_text(*self._EMAIL_FIELD, email)

    def enter_password(self, password: str):
        self.type_text(*self._PASSWORD_FIELD, password)

    def click_submit(self):
        self.click(*self._SUBMIT_BTN)

    def login(self, email: str, password: str):
        self.open_login_page()
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()
        # Wait until URL leaves /login (redirect to dashboard)
        from selenium.webdriver.support import expected_conditions as EC
        self.wait.until(EC.url_contains("/notes/app"))
        self.wait_for_dom_ready()
        log.info("Login submitted for: %s", email)

    def get_error_message(self) -> str:
        return self.get_text(*self._ERROR_TOAST)

    def is_login_successful(self) -> bool:
        """Presence of the navbar brand indicates a successful post-login redirect."""
        return self.is_element_visible(*self._NAV_LOGO)
