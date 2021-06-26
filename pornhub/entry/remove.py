import click

from pornhub.core import get_session
from pornhub.models import Channel, Playlist, User


@click.command(help="Remove stuff from the database")
@click.argument(
    "entity_type",
    type=click.Choice(["user", "playlist", "channel"], case_sensitive=False),
)
@click.argument("entity_id")
def remove(entity_type, entity_id) -> None:
    """Remove all information about a user/channel/playlist.

    typ: What kind of thing you want to delete.
    entity_id: The id of whatever you want to delete. (name for user, id for playlist, etc.)
    """
    session = get_session()
    if entity_type.lower() == "user":
        entity = session.query(User).get(entity_id)
    elif entity_type.lower() == "playlist":
        entity = session.query(Playlist).get(entity_id)
    elif entity_type.lower() == "channel":
        entity = session.query(Channel).get(entity_id)
    else:
        print(f"Unkown type {entity_type}. Use either `user`, `playlist` or `channel`")
        return

    if entity is None:
        print(f"Couldn't finde {entity_type} {entity_id}")
        return

    session.delete(entity)
    session.commit()
    print(f"{entity_type} {entity_id} has been removed")
