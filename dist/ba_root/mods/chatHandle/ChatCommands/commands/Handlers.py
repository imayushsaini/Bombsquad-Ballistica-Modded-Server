""" Some useful handlers to reduce lot of code """
import _ba, ba
import ba.internal



def send(msg, clientid):
	"""Shortcut To Send Private Msg To Client"""

	ba.internal.chatmessage(str(msg), clients=[clientid])
	_ba.screenmessage(str(msg), transient=True, clients=[clientid])





def clientid_to_myself(clientid):
	"""Return Player Index Of Self Player"""

	for i in  _ba.get_foreground_host_activity().players:
		if i.sessionplayer.inputdevice.client_id == clientid:
			return i





def handlemsg(client, msg):
	"""Handles Spaz Msg For Single Player"""

	activity = _ba.get_foreground_host_activity()
	activity.players[client].actor.node.handlemessage(msg)





def handlemsg_all(msg):
	"""Handle Spaz message for all players in activity"""

	activity = _ba.get_foreground_host_activity()

	for i in activity.players:
		i.actor.node.handlemessage(msg)



