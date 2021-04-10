# Released under the MIT License. See LICENSE for details.

from _ba import chatmessage as cmsg,          screenmessage as smsg
from .handlers import activity_players, on_command_error, handlemsg, handlemsg_all
import ba, _ba, time

cmnds = ['kill', 'heal', 'curse', 'sleep',  'superpunch', 'gloves', 'shield', 'freeze', 'unfreeze', 'godmode']

cmnd_aliases = ['die', 'heath', 'cur', 'sp', 'punch', 'protect', 'ice', 'thaw', 'gm']



def exec_cmd(cmnd, arg, client_id, pbid):
	
	if cmnd in ['kill', 'die']:
		kill_call(arg)
		
	elif cmnd in ['heal', 'heath']:
		heal_call(arg)
		
	elif cmnd in ['curse', 'cur']:
		curse_call(arg)
		
	elif cmnd in ['sleep']:
		sleep_call(arg)
		
	elif cmnd in ['sp', 'superpunch']:
		super_punch_call(arg)
		
	elif cmnd in ['gloves', 'punch']:
		gloves_call(arg)
		
	elif cmnd in ['shield', 'protect']:
		shield_call(arg)
		
	elif cmnd in ['freeze', 'ice']:
		freeze_call(arg)
		
	elif cmnd in ['unfreeze', 'thaw']:
		un_freeze_call(arg)
		
	elif cmnd in ['gm', 'godmode']:
		god_mode_call(arg)




def kill_call(arg):
	if on_command_error(arg):
		return
	
	elif arg[0] == 'all':
		handlemsg_all(ba.DieMessage())
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.DieMessage())
		except:
			return





def heal_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='health'))
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='health'))
		except:
			return


def curse_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='curse'))
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='curse'))
		except:
			return



def sleep_call(arg):
	if on_command_error(arg):
		return 
	# ahh ! harsh here maybe fix in future 
	elif arg[0] == 'all':
		for i in activity_players():
			i.actor.node.handlemessage('knockout', 8000)
	else:
		try:
			req_player = int(arg[0])
			activity_players()[req_player].actor.node.handlemessage('knockout', 8000)
		except:
			return



def super_punch_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		for i in activity_players():
			if i.actor._punch_power_scale != 15:
				i.actor._punch_power_scale = 15
				i.actor._punch_cooldown = 0
			else:
				i.actor._punch_power_scale = 1.2
				i.actor._punch_cooldown = 400
			
	else:
		try:
			req_player = int(arg[0])
			
			if activity_players()[req_player].actor._punch_power_scale != 15:
				activity_players()[req_player].actor._punch_power_scale = 15
				activity_players()[req_player].actor._punch_cooldown = 0
			else:
				activity_players()[req_player].actor._punch_power_scale = 1.2
				activity_players()[req_player].actor._punch_cooldown = 400
		except:
			return



def gloves_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='punch'))
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='punch'))
		except:
			return



def shield_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='shield'))
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='shield'))
		except:
			return



def freeze_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		handlemsg_all(ba.FreezeMessage())
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.FreezeMessage())
		except:
			return



def un_freeze_call(arg):
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		handlemsg_all(ba.ThawMessage())
			
	else:
		try:
			req_player = int(arg[0])
			handlemsg(req_player, ba.ThawMessage())
		except:
			return



def god_mode_call(arg):
	if on_command_error(arg):
		return
	
	elif arg[0] == 'all':
		
		for i in activity_players():
			if i.actor._punch_power_scale != 7:
				i.actor._punch_power_scale = 7
				i.actor.node.hockey = True 
				i.actor.node.invincible = True 
			else:
				i.actor._punch_power_scale = 1.2
				i.actor.node.hockey = False 
				i.actor.node.invincible = False 
				
	else:
		req_player = int(arg[0])
		player = activity_players()[req_player].actor
		
		if player._punch_power_scale != 7:
			player._punch_power_scale = 7
			player.node.hockey = True 
			player.node.invincible = True 
			
		else:
			player._punch_power_scale = 1.2
			player.node.hockey = False 
			player.node.invincible = False 
			
			

