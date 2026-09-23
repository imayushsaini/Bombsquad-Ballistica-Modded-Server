# Released under the MIT License. See LICENSE for details.
#
"""Snippets of code for use by the c++ layer."""

# (most of these are self-explanatory)
# pylint: disable=missing-function-docstring

from typing import TYPE_CHECKING

import babase

import _bascenev1

if TYPE_CHECKING:
    from typing import Any

    import bascenev1


def launch_main_menu_session() -> None:
    assert babase.app.classic is not None

    _bascenev1.new_host_session(babase.app.classic.get_main_menu_session())


def get_player_icon(sessionplayer: bascenev1.SessionPlayer) -> dict[str, Any]:
    info = sessionplayer.get_icon_info()
    return {
        'texture': _bascenev1.aptextureget(info['texture']),
        'tint_texture': _bascenev1.aptextureget(info['tint_texture']),
        'tint_color': info['tint_color'],
        'tint2_color': info['tint2_color'],
    }


def filter_chat_message(msg: str, client_id: int) -> str | None:
    try:
        import custom_hooks as chooks
    except:
        pass
    """Intercept/filter chat messages.

    Called for all chat messages while hosting.
    Messages originating from the host will have clientID -1.
    Should filter and return the string to be displayed, or return None
    to ignore the message.
    """
    try:
        return chooks.filter_chat_message(msg, client_id)
    except:
        return msg


def bcs_verify_client_account_ip(account_id: str, ip: str, client_id: int) -> str | None:
    try:
        import custom_hooks as chooks
    except:
        pass
    """Verify a client account ID and IP address.

    This is called when a client connects while using BCS servers.
    If you return None, the connection is dropped
    If you return a string, the connection proceeds as normal.
    TODO make this actually do something. For now we have to disconnect client manually

    Here account_id is display_string of account ~ V2 account tag not pb-id (which can be spoofed easily).

    """
    try:
        return chooks.bcs_verify_client_account_ip(account_id, ip, client_id)
    except Exception as e:
        print(e)
        return


def kick_vote_started(by: str, to: str) -> bool:
    """Called from C++ when a kick vote is attempted. Return True to allow or False to reject."""
    by_id = (by or '').strip('"')
    to_id = (to or '').strip('"')
    try:
        import custom_hooks as chooks
        if hasattr(chooks, 'kick_vote_started'):
            res = chooks.kick_vote_started(by_id, to_id)
            if res is not None:
                return bool(res)
    except Exception as e:
        print(f'Error in custom_hooks.kick_vote_started: {e}')
    return True


def local_chat_message(msg: str) -> None:
    classic = babase.app.classic
    assert classic is not None
    party_window = (
        None if classic.party_window is None else classic.party_window()
    )

    if party_window is not None:
        party_window.on_chat_message(msg)


def player_entered_server(
    client_id: int,
    account_id: str,
    display_name: str,
    ip: str,
    device_id: str,
) -> bool | None:
    """Called when a client has successfully authenticated and entered the server."""
    try:
        import custom_hooks as chooks
    except Exception:
        return True

    try:
        if hasattr(chooks, 'player_entered_server'):
            return chooks.player_entered_server(
                client_id=client_id,
                account_id=account_id,
                display_name=display_name,
                ip=ip,
                device_id=device_id,
            )
        if hasattr(chooks, 'on_player_enter_server'):
            return chooks.on_player_enter_server(
                client_id=client_id,
                account_id=account_id,
                display_name=display_name,
                ip=ip,
                device_id=device_id,
            )
    except Exception as e:
        print(f"Error in player_entered_server hook: {e}")
        return True
    return True

