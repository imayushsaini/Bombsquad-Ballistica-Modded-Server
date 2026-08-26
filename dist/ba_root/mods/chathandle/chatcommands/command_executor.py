# Released under the MIT License. See LICENSE for details.
"""Command execution logic for chat commands."""

from datetime import datetime
import _babase
import setting
import bascenev1 as bs
from playersdata import pdata
from serverdata import serverdata
from .handlers import check_permissions, clientid_to_accountid
from .commands import registry

settings = setting.get_settings_data()


def command_type(command: str) -> str | None:
    """Checks the command type.

    Returns the category name (e.g. 'Normal', 'Manage', 'Fun', 'Cheats')
    or None if the command is not found.
    """
    cmd = registry.get_command(command)
    return cmd.category if cmd else None


def execute(msg: str, clientid: int) -> str | None:
    """Parses and executes a chat command if valid."""
    try:
        command = msg.lower().split(" ")[0].split("/")[1]
    except IndexError:
        return msg

    arguments = msg.lower().split(" ")[1:]
    accountid = clientid_to_accountid(clientid)

    cmd = registry.get_command(command)
    if cmd:
        if cmd.category == "Normal":
            cmd.handler(arguments, clientid, accountid)
        else:
            from shop import has_purchased_command, consume_command_usage
            is_permitted = check_permissions(accountid, command)
            if is_permitted or has_purchased_command(accountid, command):
                cmd.handler(arguments, clientid, accountid)
                bs.broadcastmessage(
                    "Executed", transient=True, clients=[clientid])
                if not is_permitted:
                    consume_command_usage(accountid, command)
            else:
                bs.broadcastmessage(
                    "access denied", transient=True, clients=[clientid])

    now = datetime.now()
    if accountid in pdata.get_blacklist()["muted-ids"]:
        till_str = pdata.get_blacklist()["muted-ids"][accountid]["till"]
        try:
            till_dt = datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S")
            if now < till_dt:
                bs.broadcastmessage("You are on mute",
                                    transient=True, clients=[clientid])
                return None
        except ValueError:
            pass

    if serverdata.muted:
        return None

    if settings.get("ChatCommands", {}).get("BrodcastCommand", False):
        return msg
    return None


def QuickAccess(msg: str, client_id: int) -> str | None:
    """Quick access commands like team chat or popup text."""
    from bascenev1lib.actor import popuptext
    if msg.startswith(","):
        name = ""
        teamid = 0
        session = bs.get_foreground_host_session()
        if session:
            for player in session.sessionplayers:
                if player.inputdevice.client_id == client_id:
                    teamid = getattr(player.sessionteam, 'id', 0)
                    name = player.getname(True)
                    break

            for player in session.sessionplayers:
                if (hasattr(player, 'sessionteam') and
                        player.sessionteam and
                        teamid == player.sessionteam.id and
                        player.inputdevice.client_id != client_id):
                    bs.broadcastmessage(
                        name + ":" + msg[1:],
                        clients=[player.inputdevice.client_id],
                        color=(0.3, 0.6, 0.3),
                        transient=True
                    )
        return None

    elif msg.startswith("."):
        msg_text = msg[1:]
        msg_ar = msg_text.split(" ")
        if len(msg_text) > 25 or int(len(msg_text) / 5) > len(msg_ar):
            bs.broadcastmessage("msg/word length too long",
                                clients=[client_id], transient=True)
            return None

        msg_ar.insert(int(len(msg_ar) / 2), "\n")
        activity = bs.get_foreground_host_activity()
        if activity:
            for player in activity.players:
                if (player.sessionplayer.inputdevice.client_id == client_id and
                        player.actor and player.actor.exists() and
                        player.actor.node and hasattr(player.actor.node, "position")):
                    pos = player.actor.node.position
                    with activity.context:
                        popuptext.PopupText(
                            " ".join(msg_ar),
                            position=(pos[0], pos[1] + 1, pos[2])
                        ).autoretain()
                    return None
        return None
