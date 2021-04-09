""" helper functions to reduce lot code """
import _ba, ba


def activity_players():
	return _ba.get_foreground_host_activity().players

def sess_players():
	return _ba.get_foreground_host_session().sessionplayers

def on_command_error(arg):
	if arg == [] or arg == ['']:
		return True 
	return False



def handlemsg(client, msg):
	activity_players()[client].actor.node.handlemessage(msg)

def handlemsg_all(msg):
	for i in activity_players():
		i.actor.node.handlemessage(msg)



