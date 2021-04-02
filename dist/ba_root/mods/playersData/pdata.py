# Released under the MIT License. See LICENSE for details.
roles={}
data={}
custom={}

def roles():
	global roles
	if roles=={}:
		f=open("roles.json","r")
		dat=json.loads(f.read())
		roles=dat
		f.close()
	return roles

def create_role(role):
	global roles
	_roles=roles()
	if role not in _roles:
		_roles[role]={
			"tag":role,
			"tagcolor":(1,1,1),
			"commands":[],
			"ids":[]
		}
		roles=_roles
		comit()
		return 'created successfully'
	
	
	return 'already exists'

def add_player_role(role,id):
	global roles
	_roles=roles()
	if role in _roles:
		_roles[role].ids.append(id)
		roles=_roles
		commit()
		return 'added to '+role
	return "role not exists"

def add_command_role(role,command):
	global roles
	_roles=roles()
	if role in _roles:
		_roles[role].commands.append(command)
		roles=_roles
		commit()
		return 'added '+command+"to "+role
	return role+"not exists"


def remove_player_role(role,id):
	global roles
	_roles=roles()
	if role in _roles:
		_roles[role].ids.remove(id)
		roles=_roles
		commit()
		return "removed"
	return "role not exists"

def remove_command_role():
	global roles
	_roles=roles()
	if role in _roles:
		_roles[role].commands.remove(command)
		roles=_roles
		commit()
		return 'removed '+command+"from "+role
	return role+"not exists"

def change_role_tag(role,tag):
	global roles
	_roles=roles()
	if role in _roles:
		_roles[role].tag=tag
		roles=_roles
		commit()
		return "tag changed"
	return "role not exists"


def commit():
	global roles
	f=open("roles.json",'w')
	json.dump(roles,f,indent=4)
	f.close()
#=======================  CUSTOM EFFECTS/TAGS ===============


def custom():
	global custom
	if custom=={}:
		f=open("custom.json","r")
		dat=json.loads(f.read())
		custom=dat
		f.close()
	return custom



def set_effect(effect,id):
	global custom
	_custom=custom()
	_custom['customeffects'][id]=effect
	custom=_custom
	commit_c()


def set_tag(tag,id):
	global custom
	_custom=custom()
	_custom['customtag'][id]=tag
	custom=_custom
	commit_c()

def remove_effect(id):
	global custom
	_custom=custom()
	_custom['customeffects'].pop(id)
	custom=_custom
	commit_c()


def remove_tag(id):
	global custom
	_custom=custom()
	_custom['customtag'].pop(id)
	custom=_custom
	commit_c()


def commit_c():
	global custom
	f=open("custom.json",'w')
	json.dump(custom,f,indent=4)
	f.close()
