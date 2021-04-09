# Released under the MIT License. See LICENSE for details.

import ba, _ba
import setting
from playersData import pdata
from . import fun
from . import management, cheats, normal_commands as normal_cmds


def client_to_account(client_id):
	rost = _ba.get_game_roster()
	for i in rost:
		if i['client_id'] == client_id:
			return i['account_id']
	return None


def check_permission(account_id, command):
	roles = pdata.get_roles()
	for role in roles:
		if account_id in roles[role]["ids"] and command in roles[role]["commands"]:
			return True
	return False


def cmd_type(cmnd):
	
	if cmnd in normal_cmds.cmnds or cmnd in normal_cmds.cmnd_aliases:
		return "normal_cmd"
		
	if cmnd in management.cmnds or cmnd in management.cmnd_aliases:
		return "management"
	
	if cmnd in fun.cmnds or cmnd in fun.cmnd_aliases:
		return "fun"
		
	if cmnd in cheats.cmnds or cmnd in cheats.cmnd_aliases:
		return "cheats"


def cmd(msg, client_id):
	cmnd = msg.split(" ")[0].lower().split("/")[1]
	arg = msg.split(" ")[1:]
	acid = "pb-IF48VgWkBFQ"
#client_to_account(client_id)
	
	if cmd_type(cmnd) == "fun":
		if check_permission(acid, cmnd):
			fun.exec_cmd(cmnd, arg, client_id, acid)
		
	elif cmd_type(cmnd) == "management":
		if check_permission(acid, cmnd):
			management.exec_cmd(cmnd, arg, client_id, acid)
		
	elif cmd_type(cmnd) == "cheats":
		if check_permission(acid, cmnd):
			cheats.exec_cmd(cmnd, arg, client_id, acid)
		
	elif cmd_type(cmnd) == "normal_cmd":
		normal_cmds.exec_cmd(cmnd, arg, client_id, acid) 
			
	else:
		_ba.chatmessage("no access")


	if setting.brdcast_chatcmd:
		return msg
	return None


