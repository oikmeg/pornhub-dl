from datetime import datetime

import click

from pornhub.core import get_session
from pornhub.extractors import download_user_videos, get_user_info
from pornhub.models import User


@click.command(name="user")
@click.argument("name")
def get_user(name) -> None:
    """Download a specific user.

    The required name that can be found in the link of the user's profile.
    """
    session = get_session()

    user = session.query(User).get(name)
    info = get_user_info(name)
    if user is None:
        user = User.get_or_create(session, name, info["name"], info["type"])
    else:
        user.user_type = info["type"]

    user.subscribed = True
    session.commit()

    # Only set the last scan date, if everything could be downloaded
    if download_user_videos(session, user):
        session.last_scan = datetime.now()
    session.commit()
