"""A scraper for pornhub."""
import os
from datetime import datetime, timedelta

import click

from pornhub.core import get_session, logger
from pornhub.download import download_video
from pornhub.extractors import (
    download_channel_videos,
    download_playlist_videos,
    download_user_videos,
    get_user_info,
)
from pornhub.models import Channel, Clip, Playlist, User


@click.command()
def update():
    """Update everything and check for new vids.."""
    session = get_session()

    threshold = datetime.now() - timedelta(hours=8)

    # Go through all users
    users = (
        session.query(User).filter(User.last_scan <= threshold).order_by(User.key).all()
    )
    for user in users:
        try:
            # Re query the user type, since this can change over time
            logger.info(f"\nStart downloading: {user.name} ({user.user_type})")
            info = get_user_info(user.key)
            user.user_type = info["type"]

            if download_user_videos(session, user):
                user.last_scan = datetime.now()
            session.commit()
        except Exception as e:
            logger.error(f"Failed download of user with exception {e}")

    # Go through all playlists
    playlists = (
        session.query(Playlist)
        .filter(Playlist.last_scan <= threshold)
        .order_by(Playlist.name)
        .all()
    )
    for playlist in playlists:
        try:
            logger.info(f"\nStart downloading playlist: {playlist.name}")
            if download_playlist_videos(session, playlist):
                playlist.last_scan = datetime.now()
            session.commit()
        except Exception as e:
            logger.error(f"Failed download of user with exception {e}")

    # Go through all channels
    channels = (
        session.query(Channel)
        .filter(Channel.last_scan <= threshold)
        .order_by(Channel.name)
        .all()
    )
    for channel in channels:
        try:
            logger.info(f"\nStart downloading channel: {channel.name}")
            if download_channel_videos(session, channel):
                channel.last_scan = datetime.now()
            session.commit()
        except Exception as e:
            logger.error(f"Failed download of user with exception {e}")

    # Retry any failed clips from previous runs
    clips = (
        session.query(Clip)
        .filter(Clip.completed.is_(False))
        .filter(Clip.location.isnot(None))
        .all()
    )
    for clip in clips:
        download_video(clip.viewkey, name=os.path.dirname(clip.location))
        clip.completed = True
        session.commit()
