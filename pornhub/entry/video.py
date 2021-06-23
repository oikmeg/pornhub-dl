from typing import Optional

import click

from pornhub.core import get_session, logger
from pornhub.download import download_video
from pornhub.helper import get_clip_path, link_duplicate
from pornhub.models import Clip


@click.command(name="video")
@click.argument("key")
@click.option("--folder", help="The viewkey of the video (e.g ph5c8a34423315012560.")
def get_video(key: str, folder: Optional[str] = None) -> None:
    """Download a single pornhub video."

    The viewkey of the video can be found in the URL e.g ph5c8a34423315012560.
    """
    session = get_session()

    clip = Clip.get_or_create(session, key)
    if clip.completed:
        if clip.title is not None and clip.extension is not None:
            target_path = get_clip_path(folder, clip.title, clip.extension)
            link_duplicate(clip, target_path)

        logger.warning("Clip already exists")
        return

    # Use a specific folder, if one is specified. Otherwise the default will be used.
    if folder is not None:
        info = download_video(key, name=folder)
    else:
        info = download_video(key)

    if info is None:
        return

    clip.title = info["title"]
    clip.tags = info["tags"]
    clip.cartegories = info["categories"]
    clip.completed = True
    clip.location = info["out_path"]
    clip.extension = info["ext"]

    session.commit()
