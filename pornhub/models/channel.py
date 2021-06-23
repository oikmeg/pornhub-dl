"""The db model for a channel."""
from __future__ import annotations

from sqlalchemy import Column, func
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.types import DateTime, String

from pornhub.core.db import base


class Channel(base):
    """The model for a channel."""

    __tablename__ = "channel"

    id = Column(String, primary_key=True)
    name = Column(String)

    last_scan = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __init__(self, channel_id, name):
        """Create a new channel."""
        self.id = channel_id
        self.name = name

    @staticmethod
    def get_or_create(session: scoped_session, channel_id: str, name: str) -> Channel:
        """Get an existing channel or create a new one."""
        channel = session.query(Channel).get(channel_id)

        if channel is None:
            channel = Channel(channel_id, name)
            session.add(channel)
            session.commit()

        return channel
