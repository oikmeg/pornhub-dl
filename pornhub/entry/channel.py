from datetime import datetime

import click

from pornhub.core import get_session
from pornhub.extractors import download_channel_videos, get_channel_info
from pornhub.models import Channel


@click.command(name="channel")
@click.argument("name")
def get_channel(name: str) -> None:
    """Download a specific channel.

    The name that can be found in the link of the channel.
    """
    session = get_session()

    channel = session.query(Channel).get(name)
    if channel is None:
        info = get_channel_info(name)
        channel = Channel.get_or_create(session, name, info["name"])

    # Only set the last scan date, if everything could be downloaded
    if download_channel_videos(session, channel):
        channel.last_scan = datetime.now()
    session.commit()
