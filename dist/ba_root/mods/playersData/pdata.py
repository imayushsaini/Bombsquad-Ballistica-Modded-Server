# Released under the MIT License. See LICENSE for details.
import _ba, os, json



roles = {}
data = {}
custom = {}
data_path = os.path.join(_ba.env()['python_directory_user'],"playersData" + os.sep)


def get_info(id):
	with open(data_path+'profiles.json', 'r') as f:

		profile = json.load(f)
		return profile[id]

def add_profile(id,display_string,allprofiles,currentname):
	f=open(data_path+"profiles.json","r")
	profiles=json.load(f.read())
	f.close()

	profiles[id]['display_string']=[display_string]
	profiles[id]['profiles']=allprofiles
	profiles[id]['name']=currentname

	f=open(data_path+"profiles.json","w")
	json.dump(profiles,f,indent=4)
	f.close()


		
def update_profile(id,display_string=None,allprofiles=[],name=None):
	f=open(data_path+"profiles.json","r")
	profiles=json.load(f.read())
	f.close()
	if id in profiles:
		if display_string != None and display_string not in profiles[id]['display_string']:
			profiles[id]['display_string'].append(display_string)
		if profiles!=[]:
			for profile in allprofiles:
				if profile not in profiles[id]['profiles']:
					profiles[id]['profiles'].append(profile)
		if name != None:
			profiles[id]['name']=name


	f=open(data_path+"profiles.json","w")
	json.dump(profiles,f,indent=4)
	f.close()
	



def commit_roles(data):
	global roles
	if data == {}:
		return
	output=json.dumps(data,indent=4)
	import re
	output2 = re.sub(r'": \[\s+', '": [', output)
	output3 = re.sub(r'",\s+', '", ', output2)
	output4 = re.sub(r'"\s+\]', '"]', output3)
	with open(data_path+'roles.json','w') as f:
		f.write(output4)


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
		commit_roles(_roles)
		return
	return


def add_player_role(role, id):
	global roles
	_roles = get_roles()
	if role in _roles:
		
		if id not in _roles[role]["ids"]:
			_roles[role]["ids"].append(id)
			roles  =_roles
			commit_roles(_roles)
			
	else:
		print("no role such")
	


def remove_player_role(role, id):
	global roles
	_roles = get_roles()
	if role in _roles:
		_roles[role]["ids"].remove(id)
		roles  =_roles
		commit_roles(_roles)
		return "removed from "+role
	return "role not exists"




def add_command_role(role, command):
	global roles
	_roles = get_roles()
	if role in _roles:
		if command not in _roles[role]["commands"]:
			_roles[role]["commands"].append(command)
			roles  =_roles
			commit_roles(_roles)
			return "command added to "+role
	return "command not exists"


def remove_command_role(role, command):
	global roles
	_roles = get_roles()
	if role in _roles:
		if command in _roles[role]["commands"]:
			_roles[role]["commands"].remove(command)
			roles  =_roles
			commit_roles(_roles)
			return "command added to "+role
	return "command not exists"


def change_role_tag(role, tag):
	global roles
	_roles = get_roles()
	if role in _roles:
		_roles[role]['tag'] = tag
		roles = _roles
		commit_roles(_roles)
		return "tag changed"
	return "role not exists"


def get_player_roles(acc_id):
	
	_roles = get_roles()
	roles=[]
	for role in _roles:
		if acc_id in _roles[role]["ids"]:
			roles.append(role)
	return roles


##### those ups done will clean it in future 



#=======================  CUSTOM EFFECTS/TAGS ===============


def get_custom():
	global custom
	if custom=={}:
		with open(data_path+"custom.json","r") as f:
			custom = json.loads(f.read())
		return custom
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

def update_toppers(topperlist):
	global roles
	_roles = get_roles()
	if "top5" not in _roles:
		create_role("top5")
	roles["top5"]["ids"]=topperlist
	commit_roles(roles)


