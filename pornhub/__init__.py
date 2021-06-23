"""Entry point for pornhub downloader."""
import sys

from pornhub.core.db import create_db
from pornhub.entry import cli


def main() -> None:
    """Parse args, check if everything is ok and start pornhub."""

    create_db()

    try:
        cli()
    except KeyboardInterrupt:
        print("Keyboard interrupt. Shutting down")
        sys.exit(1)
