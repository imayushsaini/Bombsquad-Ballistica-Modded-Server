# Released under the MIT License. See LICENSE for details.
"""Management chat commands for administrators."""

import random
import babase
import _babase
import _bascenev1
import setting
from playersdata import pdata
from serverdata import serverdata
from tools import logger, playlist
import bascenev1 as bs
from .handlers import send
from .registry import registry


@registry.register(['unban'], category='Manage')
def unban(arguments: list[str], clientid: int, accountid: str) -> None:
    """Unban a player by client ID."""
    if not arguments or arguments == ['']:
        return
    try:
        target_cl_id = int(arguments[0])
        for account in serverdata.recents:
            if account['client_id'] == target_cl_id:
                pdata.unban_player(account["pbid"])
                logger.log(
                    f'unbanned {account["pbid"]} by chat command, recents')
    except (ValueError, TypeError):
        pass


@registry.register(['recents'], category='Manage')
def recents(arguments: list[str], clientid: int, accountid: str) -> None:
    """List recent players."""
    for players in serverdata.recents:
        send(
            f"{players['client_id']} {players['deviceId']} {players['pbid']}", clientid)


@registry.register(['info'], category='Manage')
def info(arguments: list[str], clientid: int, accountid: str) -> None:
    """Get info about a player by client ID."""
    if not arguments or arguments == ['']:
        send("invalid client id", clientid)
        return
    try:
        target_cl_id = int(arguments[0])
        for account in serverdata.recents:
            if account['client_id'] == target_cl_id:
                send(pdata.get_detailed_info(account["pbid"]), clientid)
    except (ValueError, TypeError):
        pass


@registry.register(['maxplayers', 'max'], category='Manage')
def maxplayers(arguments: list[str], clientid: int, accountid: str) -> None:
    """Change the public party max size."""
    if not arguments or arguments == ['']:
        bs.chatmessage("enter number")
    else:
        try:
            bs.set_public_party_max_size(int(arguments[0]))
        except (ValueError, TypeError):
            pass


@registry.register(['createteam'], category='Manage')
def createteam(arguments: list[str], clientid: int, accountid: str) -> None:
    """Create a new team in the session."""
    if not arguments or arguments == ['']:
        bs.chatmessage("enter team name")
    else:
        from bascenev1._team import SessionTeam
        session = bs.get_foreground_host_session()
        if session:
            session.sessionteams.append(SessionTeam(
                team_id=len(session.sessionteams) + 1,
                name=str(arguments[0]),
                color=(random.uniform(0, 1.2), random.uniform(
                    0, 1.2), random.uniform(0, 1.2))
            ))
            from bascenev1._lobby import Lobby
            session.lobby = Lobby()


@registry.register(['playlist'], category='Manage')
def playlist_cmd(arguments: list[str], clientid: int, accountid: str) -> None:
    """Change the current playlist."""
    if not arguments or arguments == ['']:
        bs.chatmessage("enter list code or name")
    else:
        if arguments[0] == 'coop':
            serverdata.coopmode = True
        else:
            serverdata.coopmode = False
        playlist.setPlaylist(arguments[0])


def kick_player(cl_id: int) -> None:
    """Internal helper to kick a player."""
    for ros in bs.get_game_roster():
        if ros["client_id"] == cl_id:
            logger.log("kicked " + ros["display_string"])
    bs.disconnect_client(cl_id)


@registry.register(['kick'], category='Manage')
def kick(arguments: list[str], clientid: int, accountid: str) -> None:
    """Kick a player by client ID."""
    if not arguments or arguments == ['']:
        return
    try:
        kick_player(int(arguments[0]))
    except (ValueError, TypeError):
        pass


@registry.register(['ban'], category='Manage')
def ban(arguments: list[str], clientid: int, accountid: str) -> None:
    """Ban a player by client ID and duration."""
    if not arguments or arguments == ['']:
        return
    try:
        cl_id = int(arguments[0])
        duration = float(arguments[1]) if len(arguments) >= 2 else 0.5

        for ros in bs.get_game_roster():
            if ros["client_id"] == cl_id:
                pdata.ban_player(ros['account_id'],
                                 duration, "by chat command")
                logger.log(f'banned {ros["display_string"]} by chat command')

        for account in serverdata.recents:
            if account['client_id'] == cl_id:
                pdata.ban_player(account["pbid"], duration, "by chat command")
                logger.log(
                    f'banned {account["pbid"]} by chat command, recents')

        kick_player(cl_id)
    except (ValueError, TypeError):
        pass


@registry.register(['end', 'next'], category='Manage')
def end(arguments: list[str], clientid: int, accountid: str) -> None:
    """End the current game/activity."""
    if not arguments or arguments == ['']:
        try:
            game = bs.get_foreground_host_activity()
            if game:
                with game.context:
                    game.end_game()
        except Exception:
            pass


def _resolve_target_account(target: str) -> tuple[str | None, str]:
    """Resolves a client ID or account ID into (account_id, display_name)."""
    target = target.strip()
    if target.startswith("pb-"):
        return target, target
    try:
        cl_id = int(target)
        for ros in bs.get_game_roster():
            if ros.get("client_id") == cl_id:
                return ros.get("account_id"), ros.get("display_string", str(cl_id))
        for account in serverdata.recents:
            if account.get("client_id") == cl_id:
                return account.get("pbid"), account.get("pbid")
    except (ValueError, TypeError):
        pass
    return None, target


@registry.register(['kickvote'], category='Manage')
def kickvote(arguments: list[str], clientid: int, accountid: str) -> None:
    """Manage kick voting: enable, disable, immune, unimmune, list."""
    if not arguments:
        send("Usage: /kickvote <enable|disable|immune|unimmune|list> [target] [duration]", clientid)
        return

    action = arguments[0].lower()
    from plugins.kickvote_manager import KickVoteManager
    kvm = KickVoteManager.get()

    if action == 'list':
        restricted = kvm.get_restricted_list()
        immune = kvm.get_immune_list()
        send(f"KickVote Restricted: {len(restricted)} players: {', '.join(restricted[:5])}", clientid)
        send(f"KickVote Immune: {len(immune)} players: {', '.join(immune[:5])}", clientid)
        return

    if len(arguments) < 2:
        send("Target required for this action", clientid)
        return

    target = arguments[1]

    if action == 'enable':
        if target == 'all':
            _bascenev1.set_enable_default_kick_voting(True)
            send("Kick voting enabled globally", clientid)
        else:
            acc_id, display_name = _resolve_target_account(target)
            if acc_id:
                kvm.remove_restriction(acc_id)
                logger.log(f'kick vote restriction removed for {acc_id} ({display_name})')
                send(f"Kick-vote enabled for {display_name}", clientid)
            else:
                send(f"Player not found: {target}", clientid)

    elif action == 'disable':
        if target == 'all':
            _bascenev1.set_enable_default_kick_voting(False)
            send("Kick voting disabled globally", clientid)
        else:
            duration = 2.0
            if len(arguments) >= 3:
                try:
                    duration = float(arguments[2])
                except ValueError:
                    duration = 2.0
            acc_id, display_name = _resolve_target_account(target)
            if acc_id:
                kvm.add_restriction(acc_id, duration_days=duration, reason="by chat command")
                logger.log(f'kick vote restricted for {acc_id} ({display_name})')
                send(f"Kick-vote disabled for {display_name} for {duration} days", clientid)
            else:
                send(f"Player not found: {target}", clientid)

    elif action in ('immune', 'addimmune'):
        acc_id, display_name = _resolve_target_account(target)
        if acc_id:
            kvm.add_immune(acc_id)
            logger.log(f'kick vote immunity granted to {acc_id} ({display_name})')
            send(f"Kick-vote immunity granted to {display_name}", clientid)
        else:
            send(f"Player not found: {target}", clientid)

    elif action in ('unimmune', 'removeimmune'):
        acc_id, display_name = _resolve_target_account(target)
        if acc_id:
            kvm.remove_immune(acc_id)
            logger.log(f'kick vote immunity removed from {acc_id} ({display_name})')
            send(f"Kick-vote immunity removed from {display_name}", clientid)
        else:
            send(f"Player not found: {target}", clientid)


@registry.register(['kickimmune', 'immune'], category='Manage')
def kickimmune(arguments: list[str], clientid: int, accountid: str) -> None:
    """Grant kick vote immunity (VIP perk) to a player."""
    if not arguments or arguments == ['']:
        send("Usage: /kickimmune <client_id or pb-id>", clientid)
        return
    from plugins.kickvote_manager import KickVoteManager
    acc_id, display_name = _resolve_target_account(arguments[0])
    if acc_id:
        KickVoteManager.get().add_immune(acc_id)
        logger.log(f'kick vote immunity granted to {acc_id} ({display_name}) by chat command')
        send(f"Kick-vote immunity granted to {display_name}", clientid)
    else:
        send(f"Player not found: {arguments[0]}", clientid)


@registry.register(['kickunimmune', 'unimmune'], category='Manage')
def kickunimmune(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove kick vote immunity from a player."""
    if not arguments or arguments == ['']:
        send("Usage: /kickunimmune <client_id or pb-id>", clientid)
        return
    from plugins.kickvote_manager import KickVoteManager
    acc_id, display_name = _resolve_target_account(arguments[0])
    if acc_id:
        KickVoteManager.get().remove_immune(acc_id)
        logger.log(f'kick vote immunity removed from {acc_id} ({display_name}) by chat command')
        send(f"Kick-vote immunity removed from {display_name}", clientid)
    else:
        send(f"Player not found: {arguments[0]}", clientid)


@registry.register(['disablekickvote', 'dkv'], category='Manage')
def disablekickvote(arguments: list[str], clientid: int, accountid: str) -> None:
    """Restrict a player from starting kick votes."""
    if not arguments or arguments == ['']:
        send("Usage: /disablekickvote <client_id or pb-id> [duration_days]", clientid)
        return
    from plugins.kickvote_manager import KickVoteManager
    duration = 2.0
    if len(arguments) >= 2:
        try:
            duration = float(arguments[1])
        except ValueError:
            duration = 2.0
    acc_id, display_name = _resolve_target_account(arguments[0])
    if acc_id:
        KickVoteManager.get().add_restriction(acc_id, duration_days=duration, reason="by chat command")
        logger.log(f'kick vote restricted for {acc_id} ({display_name}) by chat command')
        send(f"Kick-vote disabled for {display_name} for {duration} days", clientid)
    else:
        send(f"Player not found: {arguments[0]}", clientid)


@registry.register(['enablekickvote', 'ekv'], category='Manage')
def enablekickvote(arguments: list[str], clientid: int, accountid: str) -> None:
    """Allow a player to start kick votes again."""
    if not arguments or arguments == ['']:
        send("Usage: /enablekickvote <client_id or pb-id>", clientid)
        return
    from plugins.kickvote_manager import KickVoteManager
    acc_id, display_name = _resolve_target_account(arguments[0])
    if acc_id:
        KickVoteManager.get().remove_restriction(acc_id)
        logger.log(f'kick vote enabled for {acc_id} ({display_name}) by chat command')
        send(f"Kick-vote enabled for {display_name}", clientid)
    else:
        send(f"Player not found: {arguments[0]}", clientid)


@registry.register(['hideid'], category='Manage')
def hideid(arguments: list[str], clientid: int, accountid: str) -> None:
    """Hide player device ID."""
    _bascenev1.hide_player_device_id(True)


@registry.register(['showid'], category='Manage')
def showid(arguments: list[str], clientid: int, accountid: str) -> None:
    """Show player device ID."""
    _bascenev1.hide_player_device_id(False)


@registry.register(['lm'], category='Manage')
def lm(arguments: list[str], clientid: int, accountid: str) -> None:
    """Send last chat messages to client."""
    for msg in bs.get_chat_messages():
        send(msg, clientid)


@registry.register(['gp'], category='Manage')
def gp(arguments: list[str], clientid: int, accountid: str) -> None:
    """Get player profiles by player ID."""
    try:
        player_id = int(arguments[0])
        session = bs.get_foreground_host_session()
        if session and 0 <= player_id < len(session.sessionplayers):
            profiles = session.sessionplayers[player_id].inputdevice.get_player_profiles(
            )
            for num, profile in enumerate(profiles, 1):
                send(f"{num})-  {profile}", clientid)
    except (ValueError, TypeError, IndexError):
        pass


@registry.register(['party'], category='Manage')
def party(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle party public/private status."""
    if not arguments or arguments == ['']:
        return
    if arguments[0] == 'public':
        bs.set_public_party_enabled(True)
        bs.chatmessage("party is public now")
    elif arguments[0] == 'private':
        bs.set_public_party_enabled(False)
        bs.chatmessage("party is private now")


@registry.register(['quit', 'restart'], category='Manage')
def quit_cmd(arguments: list[str], clientid: int, accountid: str) -> None:
    """Quit the game/server."""
    if not arguments or arguments == ['']:
        babase.quit()


@registry.register(['mute', 'mutechat'], category='Manage')
def mute(arguments: list[str], clientid: int, accountid: str) -> None:
    """Mute a client or global chat."""
    if not arguments or arguments == ['']:
        serverdata.muted = True
        return
    try:
        cl_id = int(arguments[0])
        duration = float(arguments[1]) if len(arguments) >= 2 else 0.5
        for ros in bs.get_game_roster():
            if ros["client_id"] == cl_id:
                logger.log(f'muted {ros["display_string"]}')
                pdata.mute(ros['account_id'], duration,
                           "muted by chat command")
                return
        for account in serverdata.recents:
            if account['client_id'] == cl_id:
                pdata.mute(account["pbid"], duration,
                           "muted by chat command, from recents")
    except (ValueError, TypeError):
        pass


@registry.register(['unmute', 'unmutechat'], category='Manage')
def unmute(arguments: list[str], clientid: int, accountid: str) -> None:
    """Unmute a client or global chat."""
    if not arguments or arguments == ['']:
        serverdata.muted = False
        return
    try:
        cl_id = int(arguments[0])
        for ros in bs.get_game_roster():
            if ros["client_id"] == cl_id:
                pdata.unmute(ros['account_id'])
                logger.log(f'unmuted {ros["display_string"]} by chat command')
                return
        for account in serverdata.recents:
            if account['client_id'] == cl_id:
                pdata.unmute(account["pbid"])
                logger.log(
                    f'unmuted {account["pbid"]} by chat command, recents')
    except (ValueError, TypeError):
        pass


@registry.register(['remove', 'rm'], category='Manage')
def remove(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove a player from the game."""
    if not arguments or arguments == ['']:
        return
    session = bs.get_foreground_host_session()
    if not session:
        return
    if arguments[0] == 'all':
        for player in list(session.sessionplayers):
            player.remove_from_game()
    else:
        try:
            target_cl_id = int(arguments[0])
            for player in session.sessionplayers:
                if player.inputdevice.client_id == target_cl_id:
                    player.remove_from_game()
        except (ValueError, TypeError):
            pass


@registry.register(['sm', 'slow', 'slowmo'], category='Manage')
def slow_motion(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle slow motion."""
    activity = bs.get_foreground_host_activity()
    if activity and activity.globalsnode:
        activity.globalsnode.slow_motion = not activity.globalsnode.slow_motion


@registry.register(['nv'], category='Manage')
def nv(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle night vision mode tint."""
    def is_close(a, b, tol=1e-5):
        return all(abs(x - y) < tol for x, y in zip(a, b))
    try:
        activity = bs.get_foreground_host_activity()
        if activity and activity.globalsnode:
            nv_tint = (0.5, 0.5, 1.0)
            nv_ambient = (1.5, 1.5, 1.5)

            if is_close(activity.globalsnode.tint, nv_tint):
                activity.globalsnode.tint = (1.0, 1.0, 1.0)
                activity.globalsnode.ambient_color = (1.0, 1.0, 1.0)
            else:
                activity.globalsnode.tint = nv_tint
                activity.globalsnode.ambient_color = nv_ambient
    except Exception:
        pass


@registry.register(['dv'], category='Manage')
def dv(arguments: list[str], clientid: int, accountid: str) -> None:
    """Set daylight mode tint."""
    try:
        activity = bs.get_foreground_host_activity()
        if activity and activity.globalsnode:
            activity.globalsnode.tint = (1.0, 1.0, 1.0)
            activity.globalsnode.ambient_color = (1.0, 1.0, 1.0)
    except Exception:
        pass


@registry.register(['tint'], category='Manage')
def tint(arguments: list[str], clientid: int, accountid: str) -> None:
    """Set custom tint color."""
    if len(arguments) == 3:
        try:
            r = float(arguments[0])
            g = float(arguments[1])
            b = float(arguments[2])
            activity = bs.get_foreground_host_activity()
            if activity and activity.globalsnode:
                activity.globalsnode.tint = (r, g, b)
        except (ValueError, TypeError):
            pass


@registry.register(['pause', 'pausegame'], category='Manage')
def pause(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle pause state."""
    activity = bs.get_foreground_host_activity()
    if activity and activity.globalsnode:
        activity.globalsnode.paused = not activity.globalsnode.paused


@registry.register(['cameraMode', 'camera_mode', 'rotate_camera'], category='Manage')
def camera_mode(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle camera mode."""
    activity = bs.get_foreground_host_activity()
    if activity and activity.globalsnode:
        if activity.globalsnode.camera_mode != 'rotate':
            activity.globalsnode.camera_mode = 'rotate'
        else:
            activity.globalsnode.camera_mode = 'normal'


@registry.register(['createrole'], category='Manage')
def createrole(arguments: list[str], clientid: int, accountid: str) -> None:
    """Create a new role."""
    if arguments and arguments[0] != '':
        try:
            pdata.create_role(arguments[0])
        except Exception:
            pass


@registry.register(['addrole'], category='Manage')
def addrole(arguments: list[str], clientid: int, accountid: str) -> None:
    """Add a role to a player."""
    if len(arguments) >= 2:
        try:
            role = arguments[0]
            target_cl_id = int(arguments[1])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        pdata.add_player_role(role, player.get_v1_account_id())
        except (ValueError, TypeError):
            pass


@registry.register(['removerole'], category='Manage')
def removerole(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove a role from a player."""
    if len(arguments) >= 2:
        try:
            role = arguments[0]
            target_cl_id = int(arguments[1])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        pdata.remove_player_role(
                            role, player.get_v1_account_id())
        except (ValueError, TypeError):
            pass


@registry.register(['getroles'], category='Manage')
def getroles(arguments: list[str], clientid: int, accountid: str) -> None:
    """Get roles of a player."""
    if arguments:
        try:
            target_cl_id = int(arguments[0])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        roles = pdata.get_player_roles(
                            player.get_v1_account_id())
                        reply = ",".join(roles)
                        send(reply, clientid)
                        break
        except (ValueError, TypeError):
            pass


@registry.register(['changetag'], category='Manage')
def changetag(arguments: list[str], clientid: int, accountid: str) -> None:
    """Change role tag."""
    if len(arguments) >= 2:
        try:
            pdata.change_role_tag(arguments[0], arguments[1])
        except Exception:
            pass


@registry.register(['customtag'], category='Manage')
def customtag(arguments: list[str], clientid: int, accountid: str) -> None:
    """Set custom tag for a player."""
    if len(arguments) >= 2:
        try:
            tag = arguments[0]
            target_cl_id = int(arguments[1])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        pdata.set_tag(tag, player.get_v1_account_id())
        except (ValueError, TypeError):
            pass


@registry.register(['customeffect', 'addeffect', 'gifteffect'], category='Manage')
def customeffect(arguments: list[str], clientid: int, accountid: str) -> None:
    """Gift a custom effect permanently to a player."""
    if len(arguments) >= 2:
        try:
            effect = arguments[0].lower()
            target_cl_id = int(arguments[1])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        target_aid = player.get_v1_account_id()
                        if target_aid:
                            from spazmod.effects_inventory import add_admin_effect
                            add_admin_effect(target_aid, effect)
                            pdata.set_effect(effect, target_aid)
                            bs.chatmessage(f"Gifted permanent effect '{effect}' to {player.getname(False)}")
        except (ValueError, TypeError):
            pass


@registry.register(['removetag'], category='Manage')
def removetag(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove custom tag from a player."""
    if arguments:
        try:
            target_cl_id = int(arguments[0])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        pdata.remove_tag(player.get_v1_account_id())
        except (ValueError, TypeError):
            pass


@registry.register(['removeeffect'], category='Manage')
def removeeffect(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove custom effect from a player."""
    if arguments:
        try:
            target_cl_id = int(arguments[0])
            effect = arguments[1].lower() if len(arguments) > 1 else None
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_cl_id:
                        target_aid = player.get_v1_account_id()
                        if target_aid:
                            from spazmod.effects_inventory import remove_effect
                            remove_effect(target_aid, effect)
                            pdata.remove_effect(target_aid)
                            bs.chatmessage(f"Removed effect(s) from {player.getname(False)}")
        except (ValueError, TypeError):
            pass


@registry.register(['addcommand', 'addcmd'], category='Manage')
def addcommand(arguments: list[str], clientid: int, accountid: str) -> None:
    """Add a command to a role."""
    if len(arguments) == 2:
        try:
            pdata.add_command_role(arguments[0], arguments[1])
        except Exception:
            pass
    else:
        bs.chatmessage("invalid command arguments")


@registry.register(['removecommand', 'removecmd'], category='Manage')
def removecommand(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove a command from a role."""
    if len(arguments) == 2:
        try:
            pdata.remove_command_role(arguments[0], arguments[1])
        except Exception:
            pass


@registry.register(['spectators'], category='Manage')
def spectators(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle spectators option."""
    if arguments and arguments[0] in ['on', 'off']:
        settings_data = setting.get_settings_data()
        settings_data["white_list"]["spectators"] = (arguments[0] == 'on')
        setting.commit(settings_data)
        bs.chatmessage(f"spectators {arguments[0]}")


@registry.register(['lobbytime'], category='Manage')
def lobbytime(arguments: list[str], clientid: int, accountid: str) -> None:
    """Change lobby check time."""
    if not arguments:
        return
    try:
        argument = int(arguments[0])
        settings_data = setting.get_settings_data()
        settings_data["white_list"]["lobbychecktime"] = argument
        setting.commit(settings_data)
        bs.chatmessage(f"lobby check time is {argument} now")
    except (ValueError, TypeError):
        bs.chatmessage("must type number to change lobby check time")
