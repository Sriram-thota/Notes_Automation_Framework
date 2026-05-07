"""
logger.py — Centralized colorized logger for the entire test suite.
"""

import logging
import os
from pathlib import Path

import colorlog

from config.environment import config


def get_logger(name: str) -> logging.Logger:
    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.log_level, logging.DEBUG))

    # ── Console handler (colorized) ───────────────────────────────────────
    console = colorlog.StreamHandler()
    console.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    # ── File handler ──────────────────────────────────────────────────────
    file_handler = logging.FileHandler(log_dir / "test_run.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)-8s] %(name)s - %(message)s")
    )

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
