# Released under the MIT License. See LICENSE for details.


from .Objects import NormalCommands
from .Objects import Management
from .Objects import Fun
from .Objects import Cheats

from .Handlers import clientid_to_accountid
from .Handlers import cheak_permissions

import ba, _ba
import setting




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
		if cheak_permissions(accountid, command):
			Management.ExcelCommand(command, arguments, clientid, accountid)
	
	
	elif command_type(command) == "Fun":
		if cheak_permissions(accountid, command):
			Fun.ExcelCommand(command, arguments, clientid, accountid)
	
	
	elif command_type(command) == "Cheats":
		if cheak_permissions(accountid, command):
			Cheats.ExcelCommand(command, arguments, clientid, accountid)
	
	
	settings = setting.get_settings_data()
	
	if settings["ChatCommands"]["BrodcastCommand"]:
		return msg
	return None

