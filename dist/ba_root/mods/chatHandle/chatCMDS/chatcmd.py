# Released under the MIT License. See LICENSE for details.

import ba
import _ba
from playersData import pdata
import fun,management
import setting
def public_id(client_id):
	rost=_ba.get_game_roster()
	for client in rost:
		if client['client_id']==client_id:
			return client['account_id']
	return None

def check_permission(pbid,cmnd):
	roles=pdata.roles()
	for role in roles:
		if pbid in role.ids and cmnd in role.commands:
			return True
	return False

def cmd_type(cmnd):
	if cmnd in fun.cmnds:
		return "fun"
	if cmnd in management.cmnds:
		return "management"

def cmd(msg,client_id):
	cmnd=msg.split(" ")[0].lower()
	arg=msg.split(" ")[1:]
	pbid=public_id(client_id)
	if check_permission(pbid,cmnd):
		if cmd_type(cmnd)=="fun":
			fun.exec_cmd(cmnd,arg,client_id,pbid)
		elif cmd_type(cmnd)=="management":
			management.exec_cmd(cmnd,arg,client_id,pbid)
	else:
		_ba.chatmessage("no access",clients=client_id)

	if setting.brdcast_chatcmd:
		return msg
	return None


