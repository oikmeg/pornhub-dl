"""The db model for a playlist."""
from __future__ import annotations

from sqlalchemy import Column, func
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.types import DateTime, String

from pornhub.core.db import base


class Playlist(base):
    """The model for a playlist."""

    __tablename__ = "playlist"

    id = Column(String, primary_key=True)
    name = Column(String)

    last_scan = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __init__(self, playlist_id, name):
        """Create a new playlist."""
        self.id = playlist_id
        self.name = name

    @staticmethod
    def get_or_create(session: scoped_session, playlist_id, name):
        """Get an existing playlist or create a new one."""
        playlist = session.query(Playlist).get(playlist_id)

        if playlist is None:
            playlist = Playlist(playlist_id, name)
            session.add(playlist)
            session.commit()

        return playlist
