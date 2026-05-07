"""
base_page.py - Foundation for all Page Objects.

Provides:
  - Smart explicit waits (WebDriverWait + EC)
  - JS-based interactions as fallback
  - Self-healing find_element wrapper
  - Screenshot on any page-level failure
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.environment import config
from utils.logger import get_logger
from utils.retry import retry_on_flaky
from utils.screenshot import capture_screenshot
from utils.self_healing import find_with_healing

log = get_logger(__name__)


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.explicit_wait)

    # ?? Element Finders ???????????????????????????????????????????????????

    def find(self, by: str, value: str, hint: str = "", tag: str = "*"):
        """Self-healing element finder."""
        return find_with_healing(self.driver, by, value, hint=hint, tag=tag)

    def wait_for_visible(self, by: str, value: str):
        return self.wait.until(EC.visibility_of_element_located((by, value)))

    def wait_for_clickable(self, by: str, value: str):
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def wait_for_text_in_element(self, by: str, value: str, text: str) -> bool:
        return self.wait.until(EC.text_to_be_present_in_element((by, value), text))

    def wait_for_presence(self, by: str, value: str):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_invisibility(self, by: str, value: str) -> bool:
        try:
            return self.wait.until(EC.invisibility_of_element_located((by, value)))
        except TimeoutException:
            return False

    def find_all(self, by: str, value: str):
        return self.driver.find_elements(by, value)

    # ?? Actions ???????????????????????????????????????????????????????????

    @retry_on_flaky(max_attempts=3)
    def click(self, by: str, value: str, hint: str = ""):
        el = self.wait_for_clickable(by, value)
        try:
            el.click()
        except Exception:
            log.warning("Standard click failed - falling back to JS click")
            self._js_click(el)

    @retry_on_flaky(max_attempts=3)
    def type_text(self, by: str, value: str, text: str, clear_first: bool = True):
        el = self.wait_for_visible(by, value)
        if clear_first:
            el.clear()
        el.send_keys(text)

    def get_text(self, by: str, value: str) -> str:
        return self.wait_for_visible(by, value).text.strip()

    def get_attribute(self, by: str, value: str, attr: str) -> str:
        return self.wait_for_presence(by, value).get_attribute(attr)

    def is_element_visible(self, by: str, value: str) -> bool:
        try:
            return self.wait_for_visible(by, value).is_displayed()
        except TimeoutException:
            return False

    def is_element_present(self, by: str, value: str) -> bool:
        try:
            self.wait_for_presence(by, value)
            return True
        except TimeoutException:
            return False

    # ?? JavaScript Executor ???????????????????????????????????????????????

    def _js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def js_scroll_into_view(self, by: str, value: str):
        el = self.find(by, value)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

    def js_get_text(self, by: str, value: str) -> str:
        el = self.find(by, value)
        return self.driver.execute_script("return arguments[0].innerText;", el).strip()

    def wait_for_dom_ready(self):
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        log.debug("DOM ready state: complete")

    # ?? Navigation ????????????????????????????????????????????????????????

    def open(self, url: str):
        self.driver.get(url)
        self.wait_for_dom_ready()
        log.info("Navigated to: %s", url)

    def refresh(self):
        self.driver.refresh()
        self.wait_for_dom_ready()
        log.info("Page refreshed")

    def get_current_url(self) -> str:
        return self.driver.current_url

    # ?? Utility ???????????????????????????????????????????????????????????

    def screenshot(self, name: str = "capture") -> str:
        return capture_screenshot(self.driver, name)
