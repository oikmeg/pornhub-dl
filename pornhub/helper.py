import os

from pornhub.core import logger


def get_clip_path(folder, title, extension):
    """Get a path for a clip by folder and title."""
    return f"~/pornhub/{folder}/{title}.{extension}"


def link_duplicate(clip, new_path):
    """Handle multiple references to a clip.

    If a clip has already been downloaded, but is used in another source as well,
    symlink the existing file to the new location.
    """
    # Handle legacy clips (pre "location" migration)
    if clip.location is None:
        return

    # Same location, nothing to do here
    if clip.location == new_path:
        return

    if os.path.exists(clip.location):
        os.link(clip.location, new_path)
    else:
        clip.location = new_path


def check_logged_out(soup):
    """Check if we got logged out."""
    enterPremium = soup.find("div", {"class": "enterPremium"})
    if enterPremium:
        logger.error("Looks like we got logged out.")
