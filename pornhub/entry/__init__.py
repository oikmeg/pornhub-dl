import logging

import click

from pornhub.core import logger

from .channel import get_channel

from .playlist import get_playlist
from .remove import remove
from .rename import rename
from .reset import reset
from .update import update
from .user import get_user
from .video import get_video


@click.group(help="Download your favorite pornhub stuff.")
@click.option(
    "-v",
    "--verbosity",
    count=True,
    help="How verbose should it be.",
)
def cli(verbosity):
    if verbosity > 0:
        logger.sys_logger.setLevel(logging.DEBUG)
    pass


cli.add_command(get_channel)
cli.add_command(get_playlist)
cli.add_command(remove)
cli.add_command(rename)
cli.add_command(reset)
cli.add_command(update)
cli.add_command(get_user)
cli.add_command(get_video)
