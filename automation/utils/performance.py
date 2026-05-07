"""
performance.py - Timing utilities for API response and UI load measurements.
"""

import time
from contextlib import contextmanager
from typing import Optional

import allure

from config.environment import config
from utils.logger import get_logger

log = get_logger(__name__)


@contextmanager
def measure_time(label: str, threshold_sec: Optional[float] = None):
    """
    Context manager that measures elapsed time and logs it.
    Attaches the metric to the current Allure step.
    Raises AssertionError if threshold is breached.

    Usage:
        with measure_time("GET /notes", threshold_sec=2.0):
            response = requests.get(...)
    """
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start

    log.info("  %s completed in %.3f s", label, elapsed)
    allure.attach(
        f"{label}: {elapsed:.3f} s",
        name="Performance Metric",
        attachment_type=allure.attachment_type.TEXT,
    )

    limit = threshold_sec or config.performance_threshold
    assert elapsed <= limit, (
        f"Performance BREACH - '{label}' took {elapsed:.3f}s "
        f"(threshold: {limit}s)"
    )


def measure_ui_navigation(driver) -> dict:
    """
    Extract W3C Navigation Timing metrics from the browser via JS.
    Returns a dict with domContentLoaded and loadComplete durations in ms.
    """
    timing = driver.execute_script(
        "const t = performance.timing; "
        "return {"
        "  domContentLoaded: t.domContentLoadedEventEnd - t.navigationStart,"
        "  loadComplete:     t.loadEventEnd           - t.navigationStart"
        "};"
    )
    log.info(
        "? UI Timing - domContentLoaded: %dms | loadComplete: %dms",
        timing.get("domContentLoaded", 0),
        timing.get("loadComplete", 0),
    )
    return timing
