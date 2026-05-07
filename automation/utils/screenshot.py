"""
screenshot.py - Captures and attaches screenshots to Allure on test failure.
"""

import time
from pathlib import Path

import allure

from config.environment import config
from utils.logger import get_logger

log = get_logger(__name__)


def capture_screenshot(driver, name: str = "screenshot") -> str:
    """
    Save a PNG screenshot and attach it to the current Allure step.
    Returns the saved file path as a string.
    """
    screenshot_dir = Path(config.screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time() * 1000)
    filename = f"{name}_{timestamp}.png"
    filepath = screenshot_dir / filename

    try:
        driver.save_screenshot(str(filepath))
        log.info("Screenshot saved: %s", filepath)

        with open(filepath, "rb") as img:
            allure.attach(
                img.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
    except Exception as exc:
        log.error("Failed to capture screenshot: %s", exc)

    return str(filepath)
