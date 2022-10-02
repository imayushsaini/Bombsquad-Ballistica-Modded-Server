from .Handlers import handlemsg, handlemsg_all,send
from playersData import pdata
# from tools.whitelist import add_to_white_list, add_commit_to_logs
from serverData import serverdata
import ba, _ba, time, setting
import ba.internal
import _thread
from tools import playlist
Commands = ['lm', 'gp', 'party', 'quit', 'kickvote','maxplayers','playlist','ban','kick', 'remove', 'end', 'quit', 'mute', 'unmute', 'slowmo', 'nv', 'dv', 'pause', 'cameramode', 'createrole', 'addrole', 'removerole', 'addcommand', 'addcmd', 'removecommand','getroles', 'removecmd', 'changetag','customtag','customeffect','add', 'spectators', 'lobbytime']
CommandAliases = ['max','rm', 'next', 'restart', 'mutechat', 'unmutechat', 'sm', 'slow', 'night', 'day', 'pausegame', 'camera_mode', 'rotate_camera','effect']



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
	if command in ['maxplayers','max']:
		changepartysize(arguments)
	elif command =='playlist':
		changeplaylist(arguments)
	elif command == 'kick':
		kick(arguments)
	elif command == 'ban':
		ban(arguments)
	elif command in ['end', 'next']:
		end(arguments)
	elif command == 'kickvote':
		kikvote(arguments, clientid)
	
	elif command == 'lm':
		last_msgs(clientid)

	elif command == 'gp':
		get_profiles(arguments, clientid)

	elif command == 'party':
		party_toggle(arguments)
	
	elif command in ['quit', 'restart']:
		quit(arguments)
		
	elif command in ['mute', 'mutechat']:
		mute(arguments)

	elif command in ['unmute', 'unmutechat']:
		un_mute(arguments)
		
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
		create_role(arguments)
		
	elif command == 'addrole':
		add_role_to_player(arguments)
		
	elif command == 'removerole':
		remove_role_from_player(arguments)

	elif command=='getroles':
		get_roles_of_player(arguments,clientid)
		
	elif command in ['addcommand', 'addcmd']:
		add_command_to_role(arguments)
	
	elif command in ['removecommand', 'removecmd']:
		remove_command_to_role(arguments)
		
	elif command == 'changetag':
		change_role_tag(arguments)
	
	elif command=='customtag':
		set_custom_tag(arguments)

	elif command in ['customeffect','effect']:
		set_custom_effect(arguments)

	# elif command in ['add', 'whitelist']:
	# 	whitelst_it(accountid, arguments)
	
	elif command == 'spectators':
		spectators(arguments)
	
	elif command == 'lobbytime':
		change_lobby_check_time(arguments)

def changepartysize(arguments):
	if len(arguments)==0:
		ba.internal.chatmessage("enter number")
	else:
		ba.internal.set_public_party_max_size(int(arguments[0]))

def changeplaylist(arguments):
	if len(arguments)==0:
		ba.internal.chatmessage("enter list code or name")
	else:
		if arguments[0]=='coop':
			serverdata.coopmode=True
		else:
			serverdata.coopmode=False
		playlist.setPlaylist(arguments[0])
	return


def kick(arguments):
	ba.internal.disconnect_client(int(arguments[0]))
	return
def kikvote(arguments, clientid):
	if arguments == [] or arguments == [''] or len(arguments) < 2:
		return 

	elif arguments[0] == 'enable':
		if arguments[1] == 'all':
			_ba.set_enable_default_kick_voting(True)
		else:
			try:
				cl_id=int(arguments[1])
				for ros in ba.internal.get_game_roster():
					if ros["client_id"]==cl_id:
						if ros["account_id"] in serverdata.clients:
							serverdata.clients[ros["account_id"]]["canStartKickVote"]=True
							send("Upon server restart, Kick-vote will be enabled for this person", clientid)
				return
			except:
				return

	elif arguments[0] == 'disable':
		if arguments[1] == 'all':
			_ba.set_enable_default_kick_voting(False)
		else:
			try:
				cl_id=int(arguments[1])
				for ros in ba.internal.get_game_roster():
					if ros["client_id"]==cl_id:
						_ba.disable_kickvote(ros["account_id"])
						send("Kick-vote disabled for this person", clientid)
						if ros["account_id"] in serverdata.clients:
							serverdata.clients[ros["account_id"]]["canStartKickVote"]=False
				return
			except:
				return
	else:
		return					

def last_msgs(clientid):
	for i in ba.internal.get_chat_messages():
		send(i,clientid)

def get_profiles(arguments,clientid):
	try:
		playerID = int(arguments[0])
		num = 1
		for i in ba.internal.get_foreground_host_session().sessionplayers[playerID].inputdevice.get_player_profiles():
			try:
				send(f"{num})-  {i}",clientid)
				num += 1
			except:
				pass
	except:
		pass

def party_toggle(arguments):
	if arguments == ['public']:
		ba.internal.set_public_party_enabled(True)
		ba.internal.chatmessage("party is public now")
	elif arguments == ['private']:
		ba.internal.set_public_party_enabled(False)
		ba.internal.chatmessage("party is private now")
	else:
		pass


def end(arguments):
	if arguments == [] or arguments == ['']:
		try:
			with _ba.Context(_ba.get_foreground_host_activity()):
				_ba.get_foreground_host_activity().end_game()
		except:
			pass

def ban(arguments):
	try:
		cl_id=int(arguments[0])
		ac_id=""
		for ros in ba.internal.get_game_roster():
			if ros["client_id"]==cl_id:
				_thread.start_new_thread(pdata.ban_player,(ros['account_id'],))
				
				ac_id=ros['account_id']
		if ac_id in serverdata.clients:
			serverdata.clients[ac_id]["isBan"]=True
		kick(arguments)
	except:
		pass
	


def quit(arguments):
	
	if arguments == [] or arguments == ['']:
		ba.quit()		



def mute(arguments):
	if len(arguments)==0:
		serverdata.muted=True
	try:
		cl_id=int(arguments[0])
		ac_id=""
		for ros in ba.internal.get_game_roster():
			if ros["client_id"]==cl_id:
				_thread.start_new_thread(pdata.mute,(ros['account_id'],))
				
				ac_id=ros['account_id']
		if ac_id in serverdata.clients:
			serverdata.clients[ac_id]["isMuted"]=True
	except:
		pass
	return



def un_mute(arguments):
	if len(arguments)==0:
		serverdata.muted=False
	try:
		cl_id=int(arguments[0])
		ac_id=""
		for ros in ba.internal.get_game_roster():
			if ros["client_id"]==cl_id:
				pdata.unmute(ros['account_id'])
				ac_id=ros['account_id']
		if ac_id in serverdata.clients:
			serverdata.clients[ac_id]["isMuted"]=False
		return
	except:
		pass



def remove(arguments):
	
	if arguments == [] or arguments == ['']:
		return 
	
	elif arguments[0] == 'all':
		session = ba.internal.get_foreground_host_session()
		for i in session.sessionplayers:
			i.remove_from_game()
	
	else:
		try:
			session = ba.internal.get_foreground_host_session()
			for i in session.sessionplayers:
				if i.inputdevice.client_id== int(arguments[0]):
					i.remove_from_game()
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
		
		session = ba.internal.get_foreground_host_session()
		for i in session.sessionplayers:
			if i.inputdevice.client_id== int(arguments[1]):
				roles=pdata.add_player_role(arguments[0],i.get_v1_account_id())
	except:
		return



def remove_role_from_player(arguments):
	try:
		session = ba.internal.get_foreground_host_session()
		for i in session.sessionplayers:
			if i.inputdevice.client_id== int(arguments[1]):
				roles=pdata.remove_player_role(arguments[0],i.get_v1_account_id())

	except:
		return
def get_roles_of_player(arguments,clientid):
	try:
		session = ba.internal.get_foreground_host_session()
		roles=[]
		reply=""
		for i in session.sessionplayers:
			if i.inputdevice.client_id== int(arguments[0]):
				roles=pdata.get_player_roles(i.get_v1_account_id())
				print(roles)
		for role in roles:
			reply=reply+role+","
		send(reply,clientid)
	except:
	    return
def change_role_tag(arguments):
	try:
		pdata.change_role_tag(arguments[0], arguments[1])
	except:
		return

def set_custom_tag(arguments):
	try:
		session = ba.internal.get_foreground_host_session()
		for i in session.sessionplayers:
			if i.inputdevice.client_id== int(arguments[1]):
				roles=pdata.set_tag(arguments[0],i.get_v1_account_id())
	except:
	    return
def set_custom_effect(arguments):
	try:
		session = ba.internal.get_foreground_host_session()
		for i in session.sessionplayers:
			if i.inputdevice.client_id== int(arguments[1]):
				roles=pdata.set_effect(arguments[0],i.get_v1_account_id())
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



# def whitelst_it(accountid : str, arguments):
# 	settings = setting.get_settings_data()
	
# 	if arguments[0] == 'on':
# 		if settings["white_list"]["whitelist_on"]:
# 			ba.internal.chatmessage("Already on")
# 		else:
# 			settings["white_list"]["whitelist_on"] = True
# 			setting.commit(settings)
# 			ba.internal.chatmessage("whitelist on")
# 			from tools import whitelist
# 			whitelist.Whitelist() 
# 		return
		
# 	elif arguments[0] == 'off':
# 		settings["white_list"]["whitelist_on"] = False
# 		setting.commit(settings)
# 		ba.internal.chatmessage("whitelist off")
# 		return
	
	# else:
	# 	rost = ba.internal.get_game_roster()
		
	# 	for i in rost:
	# 		if i['client_id'] == int(arguments[0]):
	# 			add_to_white_list(i['account_id'], i['display_string'])
	# 			ba.internal.chatmessage(str(i['display_string'])+" whitelisted")
	# 			add_commit_to_logs(accountid+" added "+i['account_id'])




def spectators(arguments):
	
	if arguments[0] in ['on', 'off']:
		settings = setting.get_settings_data()
		
		if arguments[0] == 'on':
			settings["white_list"]["spectators"] = True
			setting.commit(settings)
			ba.internal.chatmessage("spectators on")
		
		elif arguments[0] == 'off':
			settings["white_list"]["spectators"] = False
			setting.commit(settings)
			ba.internal.chatmessage("spectators off")




def change_lobby_check_time(arguments):
    try:
        argument = int(arguments[0])
    except:
        ba.internal.chatmessage("must type number to change lobby check time")
        return
    settings = setting.get_settings_data()
    settings["white_list"]["lobbychecktime"] = argument
    setting.commit(settings)
    ba.internal.chatmessage(f"lobby check time is {argument} now")
