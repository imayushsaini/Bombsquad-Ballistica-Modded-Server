# Released under the MIT License. See LICENSE for details.
"""Permission and helper utilities for chat commands."""

from playersdata import pdata
import bascenev1 as bs


def clientid_to_accountid(clientid: int) -> str | None:
    """Transform Client ID to Account ID."""
    for i in bs.get_game_roster():
        if i.get('client_id') == clientid:
            return i.get('account_id')
    return None


def is_server(accid: str) -> bool:
    """Check if the given account ID belongs to the host server (-1 client ID)."""
    for i in bs.get_game_roster():
        if i.get('account_id') == accid and i.get('client_id') == -1:
            return True
    return False


def check_permissions(accountid: str | None, command: str) -> bool:
    """Checks the permission of a player to execute a command."""
    if not accountid:
        return False

    if is_server(accountid):
        return True

    roles = pdata.get_roles()
    for role_name, role_info in roles.items():
        role_ids = role_info.get("ids", [])
        role_commands = role_info.get("commands", [])
        if accountid in role_ids:
            if "ALL" in role_commands or command in role_commands:
                return True
    return False
