# Released under the MIT License. See LICENSE for details.
#
"""Common bits of functionality shared between all efro projects.

Things in here should be hardened, highly type-safe, and well-covered by unit
tests since they are widely used in live client and server code.
"""
from . import (
    cheats,
    fun,
    management,
    public
)
import ba
import _ba
import json
import setting

# get to roles file and return all roles
def get_roles():
    """helper function returns roles dir"""
    p = _ba.env()['python_directory_user']+'/playersData/roles.json'
    with open(p, "r") as f:
        roles = json.load(f)
    return roles

# clientid to accountid, very useful in some cases
def clientid_to_accountid(clientid):
    """clientid to accoutid using roster"""
    for client in _ba.get_game_roster():
        if int(client['client_id']) == int(clientid):
            return str(client['account_id'])
    return None

# cheacks if client has role or cmd in that role
def check_permissions(accountid, command):
    """cheacks if accoutid in roles.ids and cmd in roles.cmds"""
    roles = get_roles()
    for role in roles:
        if accountid in roles[role]["ids"]  and "ALL" in roles[role]["commands"]:
            return True
        elif accountid in roles[role]["ids"] and command in roles[role]["commands"]:
            return True
    return False

# check cmd type from different files if cmd is there
def command_type(cmd):
    """cmd to cmdtype scpecified in 4 files"""
    if cmd in public.cmds or cmd in public.cmdaliases:return "public"
    if cmd in management.cmds or cmd in management.cmdaliases:return "manage"
    if cmd in fun.cmds or cmd in fun.cmdaliases:return "fun"
    if cmd in cheats.cmds or cmd in cheats.cmdaliases:return "cheats"

# main function, spliting cmd and arguments  from msg
def Command(msg, clientid):
    """cheack msg, extract and execture command"""
    command = msg.lower().split(" ")[0].split("/")[1]
    arguments = msg.lower().split(" ")[1:]
    accountid = clientid_to_accountid(clientid)
    
    try:
        if command_type(command) == "public":
            public.Excelcmd(command, arguments, clientid, accountid)
        if command_type(command) == "manage":
            if check_permissions(accountid, command):
                management.Excelcmd(command, arguments, clientid, accountid)
            else:_ba.chatmessage("permision decline")
        if command_type(command) == "fun":
            if check_permissions(accountid, command):
                fun.Excelcmd(command, arguments, clientid, accountid)
            else:_ba.chatmessage("permision decline")
        if command_type(command) == "cheats":
            if check_permissions(accountid, command):
                cheats.Excelcmd(command, arguments, clientid, accountid)
            else:_ba.chatmessage("permision decline")
    except Exception as e:print(e)
    
    settings = setting.get_settings_data()
    if settings["ChatCommands"]["BrodcastCommand"]:
        return msg
    return None

