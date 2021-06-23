import click

from pornhub.core import get_session
from pornhub.models import Clip


@click.command()
def reset() -> None:
    """Schedules all videos to be downloaded again.

    Useful if you get your hands on a premium account."""
    session = get_session()
    session.query(Clip).update({"completed": False})
    session.commit()

    print(
        "All videos have been scheduled for new download. Please run `update` to start downloading."
    )
