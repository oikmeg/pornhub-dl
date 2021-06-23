import os

import click

from pornhub.core import get_session
from pornhub.download import get_user_download_dir
from pornhub.extractors import get_user_info
from pornhub.models import User


@click.command()
@click.argument("old_name")
@click.argument("new_name")
def rename(old_name: str, new_name: str) -> None:
    """Rename a user, as they can change their names.

    This function expects the same keys used in the "user" subcommand.
    """
    session = get_session()
    user = session.query(User).get(old_name)
    if user is None:
        print(f"Couldn't find user with {old_name}")
        return

    new_user = session.query(User).get(new_name)
    if new_user is not None:
        print(f"New user {new_name} already exists")
        return

    # Get new user info
    info = get_user_info(new_name)

    # Get new user info
    old_dir = get_user_download_dir(user.name)
    new_dir = get_user_download_dir(info["name"])

    if os.path.exists(old_dir):
        os.rename(old_dir, new_dir)

    user.key = new_name
    user.name = info["name"]

    session.commit()
    print(f"user {old_name} has been renamed to {new_name}")
