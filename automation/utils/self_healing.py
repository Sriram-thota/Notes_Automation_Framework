"""
self_healing.py - Agentic self-healing locator system.

Strategy (ordered fallback):
  1. Primary locator (as defined in POM)
  2. Attribute-based fallback  (data-testid, aria-label, name, placeholder)
  3. Text-content fallback     (visible text / partial text)
  4. XPath positional fallback (last resort)

Every healed locator is logged so developers can update the POM proactively.
"""

from __future__ import annotations

from typing import List, Tuple

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from utils.logger import get_logger

log = get_logger(__name__)

# Ordered list of (By-strategy, attribute) fallback pairs
_ATTRIBUTE_FALLBACKS: List[Tuple[str, str]] = [
    (By.CSS_SELECTOR, "[data-testid='{hint}']"),
    (By.CSS_SELECTOR, "[aria-label='{hint}']"),
    (By.CSS_SELECTOR, "[name='{hint}']"),
    (By.CSS_SELECTOR, "[placeholder*='{hint}']"),
    (By.CSS_SELECTOR, "[id*='{hint}']"),
]


def find_with_healing(
    driver: WebDriver,
    primary_by: str,
    primary_value: str,
    hint: str = "",
    tag: str = "*",
) -> WebElement:
    """
    Attempt to locate an element using the primary locator.
    On failure, iterate through fallback strategies before raising.

    Args:
        driver:         Selenium WebDriver instance.
        primary_by:     Selenium By strategy (e.g. By.CSS_SELECTOR).
        primary_value:  Locator value for the primary strategy.
        hint:           Human-readable label used in attribute fallbacks.
        tag:            HTML tag to restrict text-content fallback (default '*').

    Returns:
        WebElement if found by any strategy.

    Raises:
        NoSuchElementException if all strategies are exhausted.
    """
    # 1 - Primary
    try:
        el = driver.find_element(primary_by, primary_value)
        return el
    except NoSuchElementException:
        log.warning("Primary locator FAILED: (%s, %s)", primary_by, primary_value)

    if not hint:
        raise NoSuchElementException(
            f"Primary locator ({primary_by}, {primary_value}) failed and no hint provided."
        )

    # 2 - Attribute-based fallbacks
    for by, template in _ATTRIBUTE_FALLBACKS:
        value = template.format(hint=hint)
        try:
            el = driver.find_element(by, value)
            log.info("[OK] Healed via attribute fallback: (%s, %s)", by, value)
            _log_healing_suggestion(primary_by, primary_value, by, value)
            return el
        except NoSuchElementException:
            continue

    # 3 - Text-content fallback
    xpath_text = f"//{tag}[normalize-space(text())='{hint}']"
    try:
        el = driver.find_element(By.XPATH, xpath_text)
        log.info("[OK] Healed via text fallback: %s", xpath_text)
        _log_healing_suggestion(primary_by, primary_value, By.XPATH, xpath_text)
        return el
    except NoSuchElementException:
        pass

    xpath_partial = f"//{tag}[contains(text(),'{hint}')]"
    try:
        el = driver.find_element(By.XPATH, xpath_partial)
        log.info("[OK] Healed via partial-text fallback: %s", xpath_partial)
        _log_healing_suggestion(primary_by, primary_value, By.XPATH, xpath_partial)
        return el
    except NoSuchElementException:
        pass

    raise NoSuchElementException(
        f"Self-healing exhausted all strategies for hint='{hint}'. "
        f"Original: ({primary_by}, {primary_value})"
    )


def _log_healing_suggestion(
    old_by: str, old_val: str, new_by: str, new_val: str
) -> None:
    """Emit a structured suggestion for POM update."""
    log.warning(
        "? POM UPDATE SUGGESTED - replace (%s, '%s') -> (%s, '%s')",
        old_by, old_val, new_by, new_val,
    )
