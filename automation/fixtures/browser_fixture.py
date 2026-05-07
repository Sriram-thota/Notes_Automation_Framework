"""
browser_fixture.py - Pytest fixture for Selenium WebDriver lifecycle.
Supports Chrome and Firefox; configures headless mode from config.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from config.environment import config
from utils.logger import get_logger

log = get_logger(__name__)


def _build_chrome_driver() -> webdriver.Chrome:
    opts = ChromeOptions()
    if config.headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-gpu")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=opts)   # selenium-manager handles driver automatically


def _build_firefox_driver() -> webdriver.Firefox:
    opts = FirefoxOptions()
    if config.headless:
        opts.add_argument("--headless")
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=opts)


@pytest.fixture(scope="function")
def driver(request):
    """
    Function-scoped WebDriver fixture.
    Browser is determined from config (overridable via BROWSER env var).
    Captures screenshot on test failure before teardown.
    """
    browser = config.browser
    log.info("Starting browser: %s  headless=%s", browser, config.headless)

    if browser == "firefox":
        drv = _build_firefox_driver()
    else:
        drv = _build_chrome_driver()

    drv.maximize_window()
    yield drv

    # ?? Teardown ??????????????????????????????????????????????????????????
    # pytest request.node.rep_call is set by the hookimpl in conftest.py
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        from utils.screenshot import capture_screenshot
        capture_screenshot(drv, name=f"FAIL_{request.node.name}")

    drv.quit()
    log.info("Browser closed")
