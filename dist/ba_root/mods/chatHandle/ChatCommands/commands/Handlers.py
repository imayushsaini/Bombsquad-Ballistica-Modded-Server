""" Some useful handlers to reduce lot of code """
import _ba, ba
import ba.internal



def send(msg, clientid):
	"""Shortcut To Send Private Msg To Client"""
	
	_ba.chatmessage(str(msg), clients=[clientid])
	_ba.screenmessage(str(msg), transient=True, clients=[clientid])





def clientid_to_myself(clientid):
	"""Return Player Index Of Self Player"""
	
	session = ba.internal.get_foreground_host_session()
	
	for i in range(len(session.sessionplayers)):
		if session.sessionplayers[i].inputdevice.client_id == clientid:
			return int(session.sessionplayers[i].id)





def handlemsg(client, msg):
	"""Handles Spaz Msg For Single Player"""
	
	activity = _ba.get_foreground_host_activity()
	activity.players[client].actor.node.handlemessage(msg)





def handlemsg_all(msg):
	"""Handle Spaz message for all players in activity"""
	
	activity = _ba.get_foreground_host_activity()
	
	for i in activity.players:
		i.actor.node.handlemessage(msg)



