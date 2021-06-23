"""Logging for encarne."""
from __future__ import annotations

import logging
import sys


class Logger:
    """Custom logger to always get instant flushes."""

    def __init__(self):
        # Logger init and logger format
        self.sys_logger = logging.getLogger("")
        self.sys_logger.setLevel(logging.INFO)
        format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Stream handler
        self.channel_handler = logging.StreamHandler(sys.stdout)
        self.channel_handler.setFormatter(format_str)
        self.sys_logger.addHandler(self.channel_handler)

    def debug(self, message):
        self.sys_logger.debug(message)
        self.channel_handler.flush()

    def info(self, message: str) -> None:
        self.sys_logger.info(message)
        self.channel_handler.flush()

    def warning(self, message):
        self.sys_logger.warning(message)
        self.channel_handler.flush()

    def error(self, message):
        self.sys_logger.error(message)
        self.channel_handler.flush()


logger = Logger()
