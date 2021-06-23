from datetime import datetime

import click

from pornhub.core import get_session
from pornhub.extractors import download_playlist_videos, get_playlist_info
from pornhub.models import Playlist


@click.command(name="playlist")
@click.argument("playlist_id")
def get_playlist(playlist_id: str) -> None:
    """Download a specific playlist.

    The id that can be found in the link of the playlist.
    """
    session = get_session()

    playlist = session.query(Playlist).get(playlist_id)
    if playlist is None:
        info = get_playlist_info(playlist_id)
        playlist = Playlist.get_or_create(session, playlist_id, info["name"])

    # Only set the last scan date, if everything could be downloaded
    if download_playlist_videos(session, playlist):
        playlist.last_scan = datetime.now()
    session.commit()
