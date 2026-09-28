# Released under the MIT License. See LICENSE for details.
"""Useful handlers and helpers for chat commands."""

from typing import List, Any
import _babase
import bascenev1 as bs


def send(msg: str, clientid: int) -> None:
    """Shortcut to send private message to client."""
    for m in msg.split("\n"):
        bs.chatmessage(str(m), clients=[clientid])
    bs.broadcastmessage(str(msg), transient=True, clients=[clientid])


def clientid_to_myself(clientid: int) -> int | None:
    """Return player index of self player."""
    activity = bs.get_foreground_host_activity()
    if not activity or not hasattr(activity, 'players'):
        return None
    for i, player in enumerate(activity.players):
        if player.sessionplayer.inputdevice.client_id == clientid:
            return i
    return None


def handlemsg(client: int, msg: Any) -> None:
    """Handles spaz message for a single player."""
    activity = bs.get_foreground_host_activity()
    if activity and hasattr(activity, 'players') and 0 <= client < len(activity.players):
        player = activity.players[client]
        if player.actor and player.actor.exists() and player.actor.node:
            player.actor.node.handlemessage(msg)


def handlemsg_all(msg: Any) -> None:
    """Handles spaz message for all players in the activity."""
    activity = bs.get_foreground_host_activity()
    if activity and hasattr(activity, 'players'):
        for player in activity.players:
            if player.actor and player.actor.exists() and player.actor.node:
                player.actor.node.handlemessage(msg)


def get_target_actors(arguments: List[str], clientid: int) -> List[bs.Actor]:
    """Resolves target player actors from chat command arguments.
    
    If arguments is empty, targets the executing player.
    If arguments[0] is 'all', targets all players.
    Otherwise, parses arguments[0] as a player index in the activity's player roster.
    """
    activity = bs.get_foreground_host_activity()
    if not activity or not hasattr(activity, 'players') or not activity.players:
        return []

    targets = []
    # If no arguments, target self
    if not arguments or arguments == [] or arguments == ['']:
        for player in activity.players:
            if player.sessionplayer.inputdevice.client_id == clientid:
                if player.actor and player.actor.exists():
                    targets.append(player.actor)
                break
    # If 'all', target everyone
    elif arguments[0] == 'all':
        for player in activity.players:
            if player.actor and player.actor.exists():
                targets.append(player.actor)
    # Otherwise try to parse player index
    else:
        try:
            idx = int(arguments[0])
            if 0 <= idx < len(activity.players):
                player = activity.players[idx]
                if player.actor and player.actor.exists():
                    targets.append(player.actor)
        except (ValueError, TypeError, IndexError):
            pass

    return targets
