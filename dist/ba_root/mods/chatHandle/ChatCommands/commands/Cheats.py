from .Handlers import handlemsg, handlemsg_all, clientid_to_myself
import ba, _ba


Commands = ['kill', 'heal', 'curse', 'sleep',  'superpunch', 'gloves', 'shield', 'freeze', 'unfreeze', 'godmode']
CommandAliases = ['die', 'heath', 'cur', 'sp', 'punch', 'protect', 'ice', 'thaw', 'gm']





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
	
	if command in ['kill', 'die']:
		kill(arguments, clientid)
		
	elif command in ['heal', 'heath']:
		heal(arguments, clientid)
		
	elif command in ['curse', 'cur']:
		curse(arguments, clientid)
		
	elif command == 'sleep':
		sleep(arguments, clientid)
		
	elif command in ['sp', 'superpunch']:
		super_punch(arguments, clientid)
		
	elif command in ['gloves', 'punch']:
		gloves(arguments, clientid)
		
	elif command in ['shield', 'protect']:
		shield(arguments, clientid)
		
	elif command in ['freeze', 'ice']:
		freeze(arguments, clientid)
		
	elif command in ['unfreeze', 'thaw']:
		un_freeze(arguments, clientid)
		
	elif command in ['gm', 'godmode']:
		god_mode(arguments, clientid)




def kill(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.DieMessage())
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.DieMessage())
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.DieMessage())
		except:
			return





def heal(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.PowerupMessage(poweruptype='health')) 
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='health'))
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='health'))
		except:
			return





def curse(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.PowerupMessage(poweruptype='curse')) 
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='curse'))
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='curse'))
		except:
			return





def sleep(arguments, clientid):
	
	activity = _ba.get_foreground_host_activity()
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		activity.players[myself].actor.node.handlemessage('knockout', 8000) 
		
	elif arguments[0] == 'all':
		for i in activity.players:
			i.actor.node.handlemessage('knockout', 8000)
	else:
		try:
			req_player = int(arguments[0])
			activity.players[req_player].actor.node.handlemessage('knockout', 8000)
		except:
			return





def super_punch(arguments, clientid):
	
	activity = _ba.get_foreground_host_activity()
	
	if arguments == [] or arguments == ['']:
		
		myself = clientid_to_myself(clientid)
		
		if activity.players[myself].actor._punch_power_scale != 15:
			activity.players[myself].actor._punch_power_scale = 15
			activity.players[myself].actor._punch_cooldown = 0
		else:
			activity.players[myself].actor._punch_power_scale = 1.2
			activity.players[myself].actor._punch_cooldown = 400
	
	elif arguments[0] == 'all':
		
		activity = _ba.get_foreground_host_activity()
		
		for i in activity.players:
			if i.actor._punch_power_scale != 15:
				i.actor._punch_power_scale = 15
				i.actor._punch_cooldown = 0
			else:
				i.actor._punch_power_scale = 1.2
				i.actor._punch_cooldown = 400
			
	else:
		try:
			activity = _ba.get_foreground_host_activity()
			req_player = int(arguments[0])
			
			if activity.players[req_player].actor._punch_power_scale != 15:
				activity.players[req_player].actor._punch_power_scale = 15
				activity.players[req_player].actor._punch_cooldown = 0
			else:
				activity.players[req_player].actor._punch_power_scale = 1.2
				activity.players[req_player].actor._punch_cooldown = 400
		except:
			return





def gloves(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.PowerupMessage(poweruptype='punch')) 
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='punch'))
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='punch'))
		except:
			return





def shield(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.PowerupMessage(poweruptype='shield')) 
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.PowerupMessage(poweruptype='shield'))
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.PowerupMessage(poweruptype='shield'))
		except:
			return





def freeze(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.FreezeMessage()) 
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.FreezeMessage())
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.FreezeMessage())
		except:
			return





def un_freeze(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		handlemsg(myself, ba.ThawMessage()) 
	
	elif arguments[0] == 'all':
		handlemsg_all(ba.ThawMessage())
			
	else:
		try:
			req_player = int(arguments[0])
			handlemsg(req_player, ba.ThawMessage())
		except:
			return





def god_mode(arguments, clientid):
	
	if arguments == [] or arguments == ['']:
		myself = clientid_to_myself(clientid)
		activity = _ba.get_foreground_host_activity()
		player = activity.players[myself].actor
		
		if player._punch_power_scale != 7:
			player._punch_power_scale = 7
			player.node.hockey = True 
			player.node.invincible = True 
			
		else:
			player._punch_power_scale = 1.2
			player.node.hockey = False 
			player.node.invincible = False 
	
	elif arguments[0] == 'all':
		
		activity = _ba.get_foreground_host_activity()
		
		for i in activity.players:
			if i.actor._punch_power_scale != 7:
				i.actor._punch_power_scale = 7
				i.actor.node.hockey = True 
				i.actor.node.invincible = True 
			else:
				i.actor._punch_power_scale = 1.2
				i.actor.node.hockey = False 
				i.actor.node.invincible = False 
				
	else:
		activity = _ba.get_foreground_host_activity()
		req_player = int(arguments[0])
		player = activity.players[req_player].actor
		
		if player._punch_power_scale != 7:
			player._punch_power_scale = 7
			player.node.hockey = True 
			player.node.invincible = True 
			
		else:
			player._punch_power_scale = 1.2
			player.node.hockey = False 
			player.node.invincible = False 
