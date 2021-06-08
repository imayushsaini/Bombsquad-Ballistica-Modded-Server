# Released under the MIT License. See LICENSE for details.

from playersData import pdata
from chatHandle.ChatCommands import _main

import ba, _ba



def filter_chat_message(msg, client_id):
	if msg.startswith("/"):
		return _main.Command(msg, client_id)
	return msg

"""
	if chatfilter.isAbuse(msg):
		pdata.warn(public_id(client_id))
		return None
	return msg
"""