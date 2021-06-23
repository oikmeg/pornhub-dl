"""The db model for a user."""
from __future__ import annotations

from sqlalchemy import Column, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.types import Boolean, DateTime, String

from pornhub.core.db import base


class User(base):
    """The model for a user."""

    __tablename__ = "user"

    USER = "users"
    MODEL = "model"
    PORNSTAR = "pornstar"

    key = Column(String, primary_key=True)
    name = Column(String, unique=True)
    user_type = Column(String)
    subscribed = Column(Boolean, default=False, nullable=False)

    last_scan = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    clips = relationship("Clip", viewonly=True)

    def __init__(self, key, name, user_type):
        """Create a new user."""
        self.key = key
        self.name = name
        self.user_type = user_type

    @staticmethod
    def get_or_create(
        session: scoped_session, key: str, name: str, user_type: str
    ) -> User:
        """Get an existing user or create a new one."""
        user = session.query(User).get(key)

        if user is None:
            user = User(key, name, user_type)
            session.add(user)
            session.commit()

        return user
