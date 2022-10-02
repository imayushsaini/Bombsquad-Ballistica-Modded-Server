from .Handlers import handlemsg, handlemsg_all
import ba, _ba
from tools import corelib

Commands = ['fly', 'invisible', 'headless', 'creepy', 'celebrate', 'spaz', 'speed', 'floater']
CommandAliases = ['inv', 'hl', 'creep', 'celeb', 'flo']




def ExcelCommand(command, arguments, clientid, accountid):
	"""
	Checks The Command And Run Function

	Parameters:
		command : str
		arguments : str
		clientid : int
		accountid : int

	Returns:
		None
	"""

	if command=='speed':
		speed(arguments)

	elif command == 'fly':
		fly(arguments)

	elif command in ['inv', 'invisible']:
		invi(arguments)

	elif command in ['hl', 'headless']:
		headless(arguments)

	elif command in ['creepy', 'creep']:
		creep(arguments)

	elif command in ['celebrate', 'celeb']:
		celeb(arguments)

	elif command == 'spaz':
		spaz(arguments)

	elif command in ['floater','flo']:
		floater(arguments,clientid)


def floater(arguments,clientid):
	try:
		from .. import floater
		if arguments ==[]:
			floater.assignFloInputs(clientid)
		else:
			floater.assignFloInputs(arguments[0])
	except:
		pass

def speed(arguments):
	if arguments ==[] or arguments==['']:
		return
	else:
		corelib.set_speed(float(arguments[0]))


def fly(arguments):

	if arguments == [] or arguments == ['']:
		return


	elif arguments[0] == 'all':

		activity = _ba.get_foreground_host_activity()

		for players in activity.players:
			if players.actor.node.fly != True:
				players.actor.node.fly = True
			else:
				players.actor.node.fly = False

	else:
		try:

			activity = _ba.get_foreground_host_activity()
			player = int(arguments[0])

			if activity.players[player].actor.node.fly != True:
				activity.players[player].actor.node.fly = True
			else:
				activity.players[player].actor.node.fly = False

		except:
			return




def invi(arguments):

	if arguments == [] or arguments == ['']:
		return

	elif arguments[0] == 'all':

		activity = _ba.get_foreground_host_activity()

		for i in activity.players:
			if i.actor.exists() and i.actor.node.torso_model != None:
				body = i.actor.node
				body.head_model = None
				body.torso_model = None
				body.upper_arm_model = None
				body.forearm_model = None
				body.pelvis_model = None
				body.hand_model = None
				body.toes_model = None
				body.upper_leg_model = None
				body.lower_leg_model = None
				body.style = 'cyborg'
	else:

		player = int(arguments[0])
		activity = _ba.get_foreground_host_activity()

		body = activity.players[player].actor.node

		if body.torso_model != None:
			body.head_model = None
			body.torso_model = None
			body.upper_arm_model = None
			body.forearm_model = None
			body.pelvis_model = None
			body.hand_model = None
			body.toes_model = None
			body.upper_leg_model = None
			body.lower_leg_model = None
			body.style = 'cyborg'




def headless(arguments):

	if arguments == [] or arguments == ['']:
		return

	elif arguments[0] == 'all':

		activity = _ba.get_foreground_host_activity()

		for players in activity.players:

			node = players.actor.node
			if node.head_model != None:
				node.head_model = None
				node.style='cyborg'

	else:
		try:
			player = int(arguments[0])
			activity = _ba.get_foreground_host_activity()

			node = activity.players[player].actor.node

			if node.head_model != None:
				node.head_model = None
				node.style='cyborg'
		except:
			return



def creep(arguments):

	if arguments == [] or arguments == ['']:
		return

	elif arguments[0] == 'all':

		activity = _ba.get_foreground_host_activity()

		for players in activity.players:
			node = players.actor.node

			if node.head_model != None:
				node.head_model = None
				node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
				node.handlemessage(ba.PowerupMessage(poweruptype='shield'))

	else:
		try:
			player = int(arguments[0])
			activity = _ba.get_foreground_host_activity()

			node = activity.players[player].actor.node

			if node.head_model != None:
				node.head_model = None
				node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
				node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
		except:
			return



def celeb(arguments):

	if arguments == [] or arguments == ['']:
		return

	elif arguments[0] == 'all':
		handlemsg_all(ba.CelebrateMessage())

	else:
		try:
			player = int(arguments[0])
			handlemsg(player, ba.CelebrateMessage())
		except:
			return





def spaz(arguments):

	if arguments == [] or arguments == ['']:
		return

	return
