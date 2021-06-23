#!/bin/env python3
"""A scraper for pornhub."""
import os
from datetime import datetime, timedelta

from pornhub.db import get_session
from pornhub.download import download_video, get_user_download_dir
from pornhub.extractors import (
    download_channel_videos,
    download_playlist_videos,
    download_user_videos,
    get_channel_info,
    get_playlist_info,
    get_user_info,
)
from pornhub.helper import get_clip_path, link_duplicate
from pornhub.logging import logger
from pornhub.models import Channel, Clip, Playlist, User


def get_user(args: dict):
    """Get all information about a user and download their videos."""
    key = args["key"]
    session = get_session()

    user = session.query(User).get(key)
    info = get_user_info(key)
    if user is None:
        user = User.get_or_create(session, key, info["name"], info["type"])
    else:
        user.user_type = info["type"]

    user.subscribed = True
    session.commit()

    # Only set the last scan date, if everything could be downloaded
    if download_user_videos(session, user):
        session.last_scan = datetime.now()
    session.commit()


def get_playlist(args: dict):
    """Get all information about the playlist and download it's videos."""
    playlist_id = args["id"]
    session = get_session()

    playlist = session.query(Playlist).get(playlist_id)
    if playlist is None:
        info = get_playlist_info(playlist_id)
        playlist = Playlist.get_or_create(session, playlist_id, info["name"])

    # Only set the last scan date, if everything could be downloaded
    if download_playlist_videos(session, playlist):
        playlist.last_scan = datetime.now()
    session.commit()


def get_channel(args: dict):
    """Get all information about the channel and download it's videos."""
    channel_id = args["id"]
    session = get_session()

    channel = session.query(Channel).get(channel_id)
    if channel is None:
        info = get_channel_info(channel_id)
        channel = Channel.get_or_create(session, channel_id, info["name"])

    # Only set the last scan date, if everything could be downloaded
    if download_channel_videos(session, channel):
        channel.last_scan = datetime.now()
    session.commit()


def get_video(args: dict):
    """Get a single videos."""
    session = get_session()

    folder = args.get("folder")

    clip = Clip.get_or_create(session, args["viewkey"])
    if clip.completed:
        if clip.title is not None and clip.extension is not None:
            target_path = get_clip_path(folder, clip.title, clip.extension)
            link_duplicate(clip, target_path)

        logger.warning("Clip already exists")
        return

    _, info = download_video(args["viewkey"], name=str(folder))

    clip.title = info["title"]
    clip.tags = info["tags"]
    clip.cartegories = info["categories"]
    clip.completed = True
    clip.location = info["out_path"]
    clip.extension = info["ext"]

    session.commit()


def update(args: dict):
    """Get all information about a user and download their videos."""
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


def rename(args: dict):
    """Rename a user."""
    old_key = args["old_key"]
    new_key = args["new_key"]

    session = get_session()
    user = session.query(User).get(old_key)
    if user is None:
        print(f"Couldn't find user with {old_key}")
        return

    new_user = session.query(User).get(new_key)
    if new_user is not None:
        print(f"New user {new_key} already exists")
        return

    # Get new user info
    info = get_user_info(new_key)

    # Get new user info
    old_dir = get_user_download_dir(user.name)
    new_dir = get_user_download_dir(info["name"])

    if os.path.exists(old_dir):
        os.rename(old_dir, new_dir)

    user.key = new_key
    user.name = info["name"]

    session.commit()
    print(f"user {old_key} has been renamed to {new_key}")


def reset(args: dict):
    """Reset all videos and schedule for download."""
    session = get_session()
    session.query(Clip).update({"completed": False})
    session.commit()

    print(
        "All videos have been scheduled for new download. Please run `update` to start downloading."
    )


def remove(args: dict):
    """Remove all information about a user/channel/playlist."""
    entity_type = args["type"]
    key = args["key"]

    session = get_session()
    if entity_type.lower() == "user":
        entity = session.query(User).get(key)
    elif entity_type.lower() == "playlist":
        entity = session.query(Playlist).get(key)
    elif entity_type.lower() == "channel":
        entity = session.query(Channel).get(key)
    else:
        print(f"Unkown type {entity_type}. Use either `user`, `playlist` or `channel`")
        return

    if entity is None:
        print(f"Couldn't finde {entity_type} {key}")
        return

    session.delete(entity)
    session.commit()
    print(f"{entity_type} {key} has been removed")
