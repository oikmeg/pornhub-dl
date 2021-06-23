"""The db model for a Movie."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.types import Boolean, DateTime, String

from pornhub.core.db import base
from pornhub.models.user import User


class Clip(base):
    """The sqlite model for a Clip."""

    __tablename__ = "movie"

    viewkey = Column(String, primary_key=True)
    title = Column(String)
    extension = Column(String)
    location = Column(String)
    completed = Column(Boolean, nullable=False, default=False)
    downloaded = Column(DateTime)
    tags = Column(JSONB)
    categories = Column(JSONB)

    user_key = Column(
        String,
        ForeignKey("user.key", ondelete="cascade", onupdate="cascade"),
        index=True,
    )
    user = relationship("User")

    def __init__(self, viewkey, user=None):
        """Create a new Clip."""
        self.viewkey = viewkey
        self.user = user

    @staticmethod
    def get_or_create(
        session: scoped_session, viewkey: str, user: Optional[User] = None
    ) -> Clip:
        """Get an existing clip or create a new one."""
        clip = session.query(Clip).get(viewkey)

        if clip is None:
            clip = Clip(viewkey, user)
            session.add(clip)

        return clip
