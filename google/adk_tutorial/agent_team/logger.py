"""
Lightweight logging helper using Python's logging with Rich console output
and a rotating file handler.

Usage:
    from agent_team.logger import get_logger
    logger = get_logger("myapp")
    logger.info("Hello world")

This module avoids re-adding handlers on repeated imports.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

from rich.logging import RichHandler


def get_logger(
    name: str | None = None,
    level: int = logging.INFO,
    # log_file: str = "logs/app.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """Return a configured logger.

    - Console uses RichHandler for colorful output.
    - File uses RotatingFileHandler with UTF-8 encoding.

    Args:
        name: logger name. If None, uses the root logger.
        level: logging level (default INFO).
        log_file: path to log file (created if missing).
        max_bytes: rotation size in bytes.
        backup_count: number of rotated files to keep.

    Returns:
        logging.Logger: configured logger instance.
    """

    # Ensure parent folder exists
    log_file = Path(__file__).parent / "logs/app.log"
    log_path = Path(log_file)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If path creation fails, fallback to current working dir
        log_path = Path("app.log")

    logger = logging.getLogger(name)

    # Prevent duplicate handlers on repeated calls/imports
    if getattr(logger, "_is_configured_with_rich", False):
        return logger

    logger.setLevel(level)

    # Rich console handler (colorful)
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(level)
    # Console formatter: include filename and line number
    console_formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(filename)s:%(lineno)d — %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(filename)s:%(lineno)d — %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Mark configured to avoid double-add
    logger._is_configured_with_rich = True

    return logger


if __name__ == "__main__":
    # Quick demo when run directly
    demo_logger = get_logger("agent_team.demo")
    demo_logger.debug("Debug message (should appear only if level <= DEBUG)")
    demo_logger.info("Info message: logger is configured and writing to console+file")
    demo_logger.warning("Warning sample")
    demo_logger.error("Error sample")
    demo_logger.critical("Critical sample")
