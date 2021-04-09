# Released under the MIT License. See LICENSE for details.
import _ba, os, json



roles = {}
data = {}
custom = {}
data_path = os.path.join(_ba.env()['python_directory_user'],"playersData" + os.sep)




def commit(data):
	global roles
	if data == {}:
		return
	with open(data_path+'roles.json','w') as f:
		json.dump(data, f, indent=4)


def get_roles():
	global roles
	if roles == {}:
		with open(data_path+'roles.json', 'r') as f:
			roles = json.load(f)
	return roles


def create_role(role):
	global roles
	_roles = get_roles()
	if role not in _roles:
		_roles[role] = {
			"tag":role,
			"tagcolor":[1,1,1],
			"commands":[],
			"ids":[]
			}
		roles = _roles
		commit(_roles)
		return
	return


def add_player_role(role, id):
	global roles
	_roles = get_roles()
	if role in _roles:
		if id not in _roles[role]["ids"]:
			_roles[role]["ids"].append(id)
			roles  =_roles
			commit(_roles)
			return "added to "+role
	return "role not exists"


def remove_player_role(role, id):
	global roles
	_roles = get_roles()
	if role in _roles:
		_roles[role]["ids"].remove(id)
		roles  =_roles
		commit(_roles)
		return "removed from "+role
	return "role not exists"




def add_command_role(role, command):
	global roles
	_roles = get_roles()
	if role in _roles:
		if command not in _roles[role]["commands"]:
			_roles[role]["commands"].append(command)
			roles  =_roles
			commit(_roles)
			return "command added to "+role
	return "command not exists"


def remove_command_role(role, command):
	global roles
	_roles = get_roles()
	if role in _roles:
		if command in _roles[role]["commands"]:
			_roles[role]["commands"].remove(command)
			roles  =_roles
			commit(_roles)
			return "command added to "+role
	return "command not exists"


def change_role_tag(role, tag):
	global roles
	_roles = get_roles()
	if role in _roles:
		_roles[role]['tag'] = tag
		roles = _roles
		commit(_roles)
		return "tag changed"
	return "role not exists"


def get_role(acc_id):
	global roles
	_roles = get_roles()
	for role in _roles:
		if acc_id in role["ids"]:
			return role


##### those ups done will clean it in future 



#=======================  CUSTOM EFFECTS/TAGS ===============


def get_custom():
	global custom
	if custom=={}:
		with open(data_path+"custom.json","r") as f:
			custom = json.loads(f.read())
		return custom


def set_effect(effect, id):
	global custom
	_custom = get_custom()
	_custom['customeffects'][id] = effect
	custom = _custom
	commit_c()


def set_tag(tag, id):
	global custom
	_custom = get_custom()
	_custom['customtag'][id] = tag
	custom = _custom
	commit_c()


def remove_effect(id):
	global custom
	_custom = get_custom()
	_custom['customeffects'].pop(id)
	custom = _custom
	commit_c()


def remove_tag(id):
	global custom
	_custom = get_custom()
	_custom['customtag'].pop(id)
	custom = _custom
	commit_c()


def commit_c():
	global custom
	with open(data_path+"custom.json",'w') as f:
		json.dump(custom,f,indent=4)
