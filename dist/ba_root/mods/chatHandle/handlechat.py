# Released under the MIT License. See LICENSE for details.
from playersData import pdata
from chatHandle.chatCMDS import chatcmd 
#from chatFilter import chatfilter
import ba,_ba

def public_id(client_id):
	rost=_ba.get_game_roster()
	for client in rost:
		if client['client_id']==client_id:
			return client['account_id']
	return None

def filter_chat_message(msg,client_id):
	if msg.startswith("/"):
		return chatcmd.cmd(msg,client_id)
	return msg

"""
	if chatfilter.isAbuse(msg):
		pdata.warn(public_id(client_id))
		return None
	return msg
"""


