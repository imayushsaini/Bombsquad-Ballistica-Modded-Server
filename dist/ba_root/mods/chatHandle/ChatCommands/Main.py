# Released under the MIT License. See LICENSE for details.


from .commands import NormalCommands
from .commands import Management
from .commands import Fun
from .commands import Cheats

from .Handlers import clientid_to_accountid
from .Handlers import check_permissions
from chatHandle.chatFilter import ChatFilter
import ba, _ba
import setting

from serverData import serverdata
settings = setting.get_settings_data()

def command_type(command):
	"""
	Checks The Command Type
	
	Parameters:
		command : str
	
	Returns:
		any 
	"""
	if command in NormalCommands.Commands or command in NormalCommands.CommandAliases:
		return "Normal"
	
	if command in Management.Commands or command in Management.CommandAliases:
		return "Manage"
	
	if command in Fun.Commands or command in Fun.CommandAliases:
		return "Fun"
	
	if command in Cheats.Commands or command in Cheats.CommandAliases:
		return "Cheats"







def Command(msg, clientid):
	"""
	Command Execution
	
	Parameters:
		msg : str 
		clientid : int
	
	Returns:
		any
	"""
	command = msg.lower().split(" ")[0].split("/")[1]
	arguments = msg.lower().split(" ")[1:]
	accountid = clientid_to_accountid(clientid)
	
	
	if command_type(command) == "Normal":
		NormalCommands.ExcelCommand(command, arguments, clientid, accountid)
	
	
	elif command_type(command) == "Manage":
		if check_permissions(accountid, command):
			Management.ExcelCommand(command, arguments, clientid, accountid)
			_ba.screenmessage("Executed", transient=True, clients=[clientid])
		else:
			_ba.screenmessage("access denied", transient=True, clients=[clientid])
	
	
	elif command_type(command) == "Fun":
		if check_permissions(accountid, command):
			Fun.ExcelCommand(command, arguments, clientid, accountid)
			_ba.screenmessage("Executed", transient=True, clients=[clientid])
		else:
			_ba.screenmessage("access denied", transient=True, clients=[clientid])
	
	
	elif command_type(command) == "Cheats":
		if check_permissions(accountid, command):
			Cheats.ExcelCommand(command, arguments, clientid, accountid)
			_ba.screenmessage("Executed", transient=True, clients=[clientid])
		else:
			_ba.screenmessage("access denied", transient=True, clients=[clientid])
	
	
	
	
	if accountid in serverdata.clients:
		if serverdata.clients[accountid]["isMuted"]:
			_ba.screenmessage("You are on mute", transient=True, clients=[clientid])
			return None
	if serverdata.muted:
		return None
	if settings["ChatCommands"]["BrodcastCommand"]:
		return msg
	return None


def QuickAccess(msg,client_id):
	if msg.startswith(","):
		acid=""
		teamid=0
		for i in _ba.get_foreground_host_session().sessionplayers:
			if i.inputdevice.client_id==client_id:
				teamid=i.sessionteam.id

		for i in _ba.get_foreground_host_session().sessionplayers:
			if teamid==i.sessionteam.id and i.inputdevice.client_id!=client_id:
				_ba.screenmessage(i.getname(True)+":"+msg[1:],clients=[i.inputdevice.client_id],color=(0.3,0.6,0.3))
	
	return None;



