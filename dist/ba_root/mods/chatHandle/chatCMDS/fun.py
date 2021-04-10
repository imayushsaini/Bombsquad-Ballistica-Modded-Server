# Released under the MIT License. See LICENSE for details.


from _ba import chatmessage as cmsg,          screenmessage as smsg
from .handlers import activity_players, on_command_error, handlemsg, handlemsg_all
import ba, _ba


cmnds = ['fly', 'invisible', 'headless', 'creepy', 'celebrate', 'spaz']

cmnd_aliases = ['inv', 'hl', 'creep', 'celeb']


def exec_cmd(cmnd, arg, clid, pbid):
	
	if cmnd in ['fly']:
		fly_call(arg)
		
	elif cmnd in ['inv', 'invisible']:
		invi_call(arg)
		
	elif cmnd in ['hl', 'headless']:
		headless_call(arg)
		
	elif cmnd in ['creepy', 'creep']:
		creep_call(arg)
		
	elif cmnd in ['celebrate', 'celeb']:
		celeb_call(arg)
		
	elif cmnd in ['spaz']:
		spaz_call(arg)
		


def fly_call(arg):
	if on_command_error(arg):
		return
		
	elif arg[0] == 'all':
		
		for players in activity_players():
			if players.actor.node.fly != True:
				players.actor.node.fly = True 
			else:
				players.actor.node.fly = False 
				
	else:
		try:
			player = int(arg[0])
			
			if activity_players()[player].actor.node.fly != True:
				activity_players()[player].actor.node.fly = True 
			else:
				activity_players()[player].actor.node.fly = False 
				
		except:
			return




def invi_call(arg):
	if on_command_error(arg):
		return
		
	elif arg[0] == 'all':
		for i in activity_players():
			body = i.actor.node
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
	else:
		
		player = int(arg[0])
		body = activity_players()[player].actor.node
		
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




def headless_call(arg):
	if on_command_error(arg):
		return
		
	elif arg[0] == 'all':
		
		for players in activity_players():
			node = players.actor.node 
			
			if node.head_model != None:
				node.head_model = None
				node.style='cyborg'
				
	else:
		try:
			player = int(arg[0])
			node = activity_players()[player].actor.node
			
			if node.head_model != None:
				node.head_model = None
				node.style='cyborg'
		except:
			return



def creep_call(arg):
	if on_command_error(arg):
		return
		
	elif arg[0] == 'all':
		
		for players in activity_players():
			node = players.actor.node 
			
			if node.head_model != None:
				node.head_model = None 
				node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
				node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
				
	else:
		try:
			player = int(arg[0])
			node = activity_players()[player].actor.node
			
			if node.head_model != None:
				node.head_model = None
				node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
				node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
		except:
			return



def celeb_call(arg):
	if on_command_error(arg):
		return
		
	elif arg[0] == 'all':
		handlemsg_all(ba.CelebrateMessage())
		
	else:
		try:
			player = int(arg[0])
			handlemsg(player, ba.CelebrateMessage())
		except:
			return
		




def spaz_call(arg):
	if on_command_error(arg):
		return
		
	pass
