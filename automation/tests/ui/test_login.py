"""
test_login.py — UI Login test suite.
Covers: successful login, wrong password, empty fields, SQL-injection attempt.
"""

import allure
import pytest

from config.environment import config
from pages.login_page import LoginPage


@allure.feature("Authentication")
@allure.story("UI Login")
class TestLogin:

    @allure.title("TC-UI-01 | Valid credentials → successful login")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_valid_login(self, driver):
        """
        Precondition: Valid registered user credentials.
        Expected: User is redirected to Notes home; nav is visible.
        """
        page = LoginPage(driver)
        page.login(config.test_email, config.test_password)

        assert page.is_login_successful(), (
            "Login failed — navbar brand not visible after submit"
        )

    @allure.title("TC-UI-02 | Invalid password → error toast")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_password(self, driver):
        page = LoginPage(driver)
        page.login(config.test_email, "WrongPassword#999")

        msg = page.get_error_message()
        assert "Incorrect email address or password" in msg or len(msg) > 0, (
            "Expected an error message for wrong credentials"
        )

    @allure.title("TC-UI-03 | Empty email → validation error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_email(self, driver):
        page = LoginPage(driver)
        page.open_login_page()
        page.enter_password(config.test_password)
        page.click_submit()

        # Either browser HTML5 validation or app error
        current_url = page.get_current_url()
        assert "login" in current_url or not page.is_login_successful()

    @allure.title("TC-UI-04 | Empty password → blocked submission")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_password(self, driver):
        page = LoginPage(driver)
        page.open_login_page()
        page.enter_email(config.test_email)
        page.click_submit()
        # Should stay on login page
        assert "login" in page.get_current_url().lower()

    @allure.title("TC-UI-05 | SQL injection in email field → no crash")
    @allure.severity(allure.severity_level.MINOR)
    def test_sql_injection_email(self, driver):
        page = LoginPage(driver)
        page.login("' OR '1'='1", "anything")
        # Should stay on login page — URL is the real check
        assert "login" in page.get_current_url().lower(), (
            "Security issue: SQL injection should not grant access"
        )
