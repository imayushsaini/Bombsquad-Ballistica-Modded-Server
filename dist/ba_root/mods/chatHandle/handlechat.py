# Released under the MIT License. See LICENSE for details.

from playersData import pdata
from serverData import serverdata
from chatHandle.ChatCommands import Main
from tools import Logger
import ba, _ba
import setting

settings = setting.get_settings_data()

def filter_chat_message(msg, client_id):

	if msg.startswith("/"):
		return Main.Command(msg, client_id)
	acid=""
	for i in _ba.get_game_roster():
		if i['client_id'] == client_id:
			acid = i['account_id']
	Logger.log(acid+" | "+msg,"chat")

	if acid in serverdata.clients:
		if serverdata.clients[acid]["isMuted"]:
			_ba.screenmessage("You are on mute", transient=True, clients=[client_id])
			return None
		elif serverdata.clients[acid]["accountAge"] < settings['minAgeToChatInHours']:
			_ba.screenmessage("New accounts not allowed to chat here", transient=True, clients=[client_id])
			return None
		else:
			return msg


	else:
		_ba.screenmessage("Fetching your account info , Wait a minute", transient=True, clients=[client_id])
		return None


"""
	if chatfilter.isAbuse(msg):
		pdata.warn(public_id(client_id))
		return None
	return msg
"""