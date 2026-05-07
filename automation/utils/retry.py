"""
retry.py - Decorator-based and explicit retry utilities for flaky UI/API actions.
Uses tenacity for fine-grained retry control.
"""

import functools
import time
from typing import Callable, Tuple, Type

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from utils.logger import get_logger

log = get_logger(__name__)

# Exceptions considered "transient" in Selenium interactions
_FLAKY_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException,
)


def retry_on_flaky(max_attempts: int = 3, wait_sec: float = 1.0):
    """
    Decorator: re-runs a UI action on known flaky Selenium exceptions.

    Usage:
        @retry_on_flaky(max_attempts=3)
        def click_save(self): ...
    """
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except _FLAKY_EXCEPTIONS as exc:
                    last_exc = exc
                    log.warning(
                        "Flaky action '%s' - attempt %d/%d - %s",
                        fn.__name__, attempt, max_attempts, exc,
                    )
                    time.sleep(wait_sec)
            raise last_exc
        return wrapper
    return decorator


# Tenacity-based retry for API calls
api_retry = retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
