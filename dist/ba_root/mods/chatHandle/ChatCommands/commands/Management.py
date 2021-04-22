from .Handlers import handlemsg, handlemsg_all
from playersData import pdata
from tools.whitelist import add_to_white_list, add_commit_to_logs

import ba, _ba, time, setting


Commands = ['kick', 'remove', 'end', 'quit', 'mute', 'unmute', 'slowmo', 'nv', 'dv', 'pause', 'cameramode', 'createrole', 'addrole', 'removerole', 'addcommand', 'addcmd', 'removecommand', 'removecmd', 'changetag', 'add', 'spectators', 'lobbytime']
CommandAliases = ['rm', 'next', 'restart', 'mutechat', 'unmutechat', 'sm', 'slow', 'night', 'day', 'pausegame', 'camera_mode', 'rotate_camera', 'whitelist']



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
	if command == 'kick':
		kick(arguments)
		
	elif command in ['end', 'next']:
		end(arguments)
	
	elif command in ['quit', 'restart']:
		quit(arguments)
		
	elif command in ['mute', 'mutechat']:
		mute()

	elif command in ['unmute', 'unmutechat']:
		un_mute()
		
	elif command in ['remove', 'rm']:
		remove(arguments)
		
	elif command in ['sm', 'slow', 'slowmo']:
		slow_motion()
		
	elif command in ['nv', 'night']:
		nv(arguments)
	
	elif command in ['dv', 'day']:
		dv(arguments)
		
	elif command in ['pause', 'pausegame']:
		pause()
		
	elif command in ['cameraMode', 'camera_mode', 'rotate_camera']:
		rotate_camera()
		
	elif command == 'createrole':
		create_role_call(arguments)
		
	elif command == 'addrole':
		add_role_to_player(arguments)
		
	elif command == 'removerole':
		remove_role_from_player(arguments)
		
	elif command in ['addcommand', 'addcmd']:
		add_command_to_role(arguments)
	
	elif command in ['removecommand', 'removecmd']:
		remove_command_to_role(arguments)
		
	elif command == 'changetag':
		change_role_tag_call(arguments)
	
	elif command in ['add', 'whitelist']:
		whitelst_it(accountid, arguments)
	
	elif command == 'spectators':
		spectators(arguments)
	
	elif command == 'lobbytime':
		change_lobby_check_time(arguments)








def kick(arguments):
	return



def end(arguments):
	
	if arguments == [] or arguments == ['']:
		
		activity = _ba.get_foreground_host_activity()
		activity.end_game()



def quit(arguments):
	
	if arguments == [] or arguments == ['']:
		ba.quit()		



def mute():
	return



def un_mute():
	return



def remove(arguments):
	
	if arguments == [] or arguments == ['']:
		return 
	
	elif arguments[0] == 'all':
		session = _ba.get_foreground_host_session()
		for i in session.sessionplayers:
			i.remove_from_game()
	
	else:
		try:
			session = _ba.get_foreground_host_session()
			session.sessionplayers[int(arguments[0])].remove_from_game()
		except:
			return



def slow_motion():
	
	activity = _ba.get_foreground_host_activity()
	
	if activity.globalsnode.slow_motion != True:
		activity.globalsnode.slow_motion = True 
	
	else:
		activity.globalsnode.slow_motion = False



def nv(arguments):
	
	activity = _ba.get_foreground_host_activity()
	
	if arguments == [] or arguments == ['']:
		
		if activity.globalsnode.tint != (0.5, 0.7, 1.0):
			activity.globalsnode.tint = (0.5, 0.7, 1.0)
		else:
			#will fix this soon 
			pass
			
	elif arguments[0] == 'off':
		if activity.globalsnode.tint != (0.5, 0.7, 1.0):
			return 
		else:
			pass



def dv(arguments):
	
	activity = _ba.get_foreground_host_activity()
	
	if arguments == [] or arguments == ['']:
		
		if activity.globalsnode.tint != (1,1,1):
			activity.globalsnode.tint = (1,1,1)
		else:
			#will fix this soon 
			pass
			
	elif arguments[0] == 'off':
		if activity.globalsnode.tint != (1,1,1):
			return 
		else:
			pass



def pause():
	
	activity = _ba.get_foreground_host_activity()
	
	if activity.globalsnode.paused != True:
		activity.globalsnode.paused = True 
		
	else:
		activity.globalsnode.paused = False


def rotate_camera():
	
	activity = _ba.get_foreground_host_activity()
	
	if activity.globalsnode.camera_mode  !=  'rotate':
		activity.globalsnode.camera_mode  =  'rotate' 
		
	else:
		activity.globalsnode.camera_mode  ==  'normal'



def create_role(arguments):
	try:
		pdata.create_role(arguments[0])
	except:
		return


def add_role_to_player(arguments):
	try:
		
		session = _ba.get_foreground_host_session()
		
		id = session.sessionplayers[int(arguments[1])].get_account_id()

		pdata.add_player_role(arguments[0], id)
	except:
		return



def remove_role_from_player(arguments):
	try:
		session = _ba.get_foreground_host_session()
		
		id = session.sessionplayers[int(arguments[1])].get_account_id()
		
		pdata.remove_player_role(arguments[0], id)
	except:
		return


def change_role_tag(arguments):
	try:
		pdata.change_role_tag(arguments[0], arguments[1])
	except:
		return



all_commands = ["changetag","createrole", "addrole", "removerole", "addcommand", "addcmd","removecommand","removecmd","kick","remove","rm","end","next","quit","restart","mute","mutechat","unmute","unmutechat","sm","slow","slowmo","nv","night","dv","day","pause","pausegame","cameraMode","camera_mode","rotate_camera","kill","die","heal","heath","curse","cur","sleep","sp","superpunch","gloves","punch","shield","protect","freeze","ice","unfreeze","thaw","gm","godmode","fly","inv","invisible","hl","headless","creepy","creep","celebrate","celeb","spaz"]



def add_command_to_role(arguments):
	try:
		if arguments[1] in all_commands:
			pdata.add_command_role(arguments[0], arguments[1])
	except:
		return



def remove_command_to_role(arguments):
	try:
		if arguments[1] in all_commands:
			pdata.remove_command_role(arguments[0], arguments[1])
	except:
		return



def whitelst_it(accountid : str, arguments):
	settings = setting.get_settings_data()
	
	if arguments[0] == 'on':
		settings["white_list"]["whitelist_on"] = True
		setting.commit(settings)
		cmsg("whitelist on")
		return
		
	elif arguments[0] == 'off':
		settings["white_list"]["whitelist_on"] = False
		setting.commit(settings)
		cmsg("whitelist off")
		return
	
	else:
		rost = _ba.get_game_roster()
		
		for i in rost:
			if i['client_id'] == int(arguments[0]):
				add_to_white_list(i['account_id'], i['display_string'])
				cmsg(str(i['display_string'])+" whitelisted")
				add_commit_to_logs(accountid+" added "+i['account_id'])




def spectators(arguments):
	
	if arguments[0] in ['on', 'off']:
		settings = setting.get_settings_data()
		
		if arguments[0] == 'on':
			settings["white_list"]["spectators"] = True
			setting.commit(settings)
			cmsg("spectators on")
		
		elif arguments[0] == 'off':
			settings["white_list"]["spectators"] = False
			setting.commit(settings)
			cmsg("spectators off")




def change_lobby_check_time(arguments):
	try:
		argument = int(arguments[0])
	except:
		cmsg("must type numbe to change lobby check time")
	settings = setting.get_settings_data()
	settings["white_list"]["lobbychecktime"] = argument
	setting.commit(settings)
	cmsg(f"lobby check time is {arg} now")
