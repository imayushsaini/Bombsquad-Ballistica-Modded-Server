# Released under the MIT License. See LICENSE for details.

from _ba import chatmessage as cmsg,          screenmessage as smsg
from .handlers import activity_players, sess_players, on_command_error, handlemsg, handlemsg_all
from playersData import pdata
import ba, _ba, time

cmnds = ['kick', 'remove', 'end', 'quit', 'mute', 'unmute', 'slowmo', 'nv', 'dv', 'pause', 'cameramode', 'createrole', 'addrole', 'removerole', 'addcommand', 'addcmd', 'removecommand', 'removecmd', 'changetag']

cmnd_aliases = ['rm', 'next', 'restart', 'mutechat', 'unmutechat', 'sm', 'slow', 'night', 'day', 'pausegame', 'camera_mode', 'rotate_camera']

def exec_cmd(cmnd, arg, client_id, pbid):
	if cmnd in ['kick']:
		kick(arg[0])
		
	elif cmnd in ['end', 'next']:
		end_call(arg)
		
	elif cmnd in ['quit', 'restart']:
		quit_call(arg)
		
	elif cmnd in ['mute', 'mutechat']:
		mute_call()

	elif cmnd in ['unmute', 'unmutechat']:
		un_mute_call()
		
	elif cmnd in ['remove', 'rm']:
		remove_call(arg)
		
	elif cmnd in ['sm', 'slow', 'slowmo']:
		slow_mo_call()
		
	elif cmnd in ['nv', 'night']:
		nv_call(arg)
	
	elif cmnd in ['dv', 'day']:
		dv_call(arg)
		
	elif cmnd in ['pause', 'pausegame']:
		pause_call()
		
	elif cmnd in ['cameraMode', 'camera_mode', 'rotate_camera']:
		rotate_camera_call()
		
	elif cmnd in ['createrole']:
		create_role_call(arg)
		
	elif cmnd in ['addrole']:
		add_role_to_player(arg)
		
	elif cmnd in ['removerole']:
		remove_role_from_player(arg)
		
	elif cmnd in ['addcommand', 'addcmd']:
		add_command_to_role(arg)
	
	elif cmnd in ['removecommand', 'removecmd']:
		remove_command_to_role(arg)
		
	elif cmnd in ['changetag']:
		change_role_tag_call(arg)
		



# =============


def kick(client_id):
	_ba.disconnectclient(client_id)
	

def remove_call(arg):
	
	if on_command_error(arg):
		return 
	
	elif arg[0] == 'all':
		for i in sess_players():
			i.remove_from_game()
			
	else:
		try:
			req_player = int(arg[0])
			sess_players()[req_player].remove_from_game()
		except:
			return


def add():
	pass


def end_call(arg):
	if arg == [] or arg == ['']:
		activity = _ba.get_foreground_host_activity()
		activity.end_game()
"""
	else:
		try:
			tmr = int(arg[0])
			time.sleep(tmr)
			activity = _ba.get_foreground_host_activity()
			activity.end_game()
		except:
			return
"""


def quit_call(arg):
	
	if arg == [] or arg == ['']:
		ba.quit()
	
	"""
	else:
		try:
			tmr = int(arg[0])
			time.sleep(tmr)
			ba.quit()
		except:
			return 
	"""			


def mute_call():
	pass

def un_mute_call():
	pass
	


def slow_mo_call():
	
	activity = _ba.get_foreground_host_activity()
	
	if activity.globalsnode.slow_motion != True:
		activity.globalsnode.slow_motion = True 
	
	else:
		activity.globalsnode.slow_motion = False





def nv_call(arg):
	
	activity = _ba.get_foreground_host_activity()
	
	if arg == [] or arg == ['']:
		
		if activity.globalsnode.tint != (0.5, 0.7, 1.0):
			activity.globalsnode.tint = (0.5, 0.7, 1.0)
		else:
			#will fix this soon 
			pass
			
	elif arg[0] == 'off':
		if activity.globalsnode.tint != (0.5, 0.7, 1.0):
			return 
		else:
			pass



def dv_call(arg):
	
	activity = _ba.get_foreground_host_activity()
	
	if arg == [] or arg == ['']:
		
		if activity.globalsnode.tint != (1,1,1):
			activity.globalsnode.tint = (1,1,1)
		else:
			#will fix this soon 
			pass
			
	elif arg[0] == 'off':
		if activity.globalsnode.tint != (1,1,1):
			return 
		else:
			pass


def pause_call():
	
	activity = _ba.get_foreground_host_activity()
	
	if activity.globalsnode.paused != True:
		activity.globalsnode.paused = True 
		
	else:
		activity.globalsnode.paused = False


def rotate_camera_call():
	
	activity = _ba.get_foreground_host_activity()
	
	if activity.globalsnode.camera_mode  !=  'rotate':
		activity.globalsnode.camera_mode  =  'rotate' 
		
	else:
		activity.globalsnode.camera_mode  ==  'normal'





def create_role_call(arg):
	pdata.create_role(arg[0])


def add_role_to_player(arg):
	id = sess_players()[int(arg[1])].get_account_id()
	try:
		pdata.add_player_role(arg[0], id)
	except:
		return
	
def remove_role_from_player(arg):
	id = sess_players()[int(arg[1])].get_account_id()
	try:
		pdata.remove_player_role(arg[0], id)
	except:
		return


def change_role_tag_call(arg):
	pdata.change_role_tag(arg[0], arg[1])





all_commands = ["changetag","createrole", "addrole", "removerole", "addcommand", "addcmd","removecommand","removecmd","kick","remove","rm","end","next","quit","restart","mute","mutechat","unmute","unmutechat","sm","slow","slowmo","nv","night","dv","day","pause","pausegame","cameraMode","camera_mode","rotate_camera","kill","die","heal","heath","curse","cur","sleep","sp","superpunch","gloves","punch","shield","protect","freeze","ice","unfreeze","thaw","gm","godmode","fly","inv","invisible","hl","headless","creepy","creep","celebrate","celeb","spaz"]



def add_command_to_role(arg):
	try:
		if arg[1] in all_commands:
			pdata.add_command_role(arg[0], arg[1])
	except:
		return



def remove_command_to_role(arg):
	try:
		if arg[1] in all_commands:
			pdata.remove_command_role(arg[0], arg[1])
	except:
		return



