# Released under the MIT License. See LICENSE for details.

from playersData import pdata
from serverData import serverdata
from chatHandle.ChatCommands import Main
from tools import Logger, servercheck
from chatHandle.chatFilter import ChatFilter
import ba, _ba
import setting

settings = setting.get_settings_data()

def filter_chat_message(msg, client_id):
	if client_id ==-1:
		return msg

	if msg.startswith("/"):
		return Main.Command(msg, client_id)
	acid=""
	for i in _ba.get_game_roster():
		if i['client_id'] == client_id:
			acid = i['account_id']
	Logger.log(acid+" | "+msg,"chat")

	if acid in serverdata.clients and serverdata.clients[acid]["verified"]:
		if serverdata.clients[acid]["isMuted"]:
			_ba.screenmessage("You are on mute", transient=True, clients=[client_id])
			return None
		elif servercheck.get_account_age(serverdata.clients[acid]["accountAge"]) < settings['minAgeToChatInHours']:
			_ba.screenmessage("New accounts not allowed to chat here", transient=True, clients=[client_id])
			return None
		else:
			return ChatFilter.filter(msg,acid,client_id)


	else:
		_ba.screenmessage("Fetching your account info , Wait a minute", transient=True, clients=[client_id])
		return None

