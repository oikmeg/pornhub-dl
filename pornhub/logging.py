"""Logging for encarne."""
import logging
import sys

# Logger init and logger format
sys_logger = logging.getLogger("")
sys_logger.setLevel(logging.INFO)
format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Stream handler
channel_handler = logging.StreamHandler(sys.stdout)
channel_handler.setFormatter(format_str)
sys_logger.addHandler(channel_handler)


class Logger:
    """Custom logger to always get instant flushes."""

    def debug(self, message):
        sys_logger.debug(message)
        channel_handler.flush()

    def info(self, message: str) -> None:
        sys_logger.info(message)
        channel_handler.flush()

    def warning(self, message):
        sys_logger.warning(message)
        channel_handler.flush()

    def error(self, message):
        sys_logger.error(message)
        channel_handler.flush()


logger = Logger()
