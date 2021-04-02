# Released under the MIT License. See LICENSE for details.


settings={}

def get_setting():
	global settings
	if settings=={}:
		f=open("setting.json","r")
		dat=json.loads(f.read())
		settings=dat
		f.close()
	return settings

def commit():
	global settings
	f=open("setting.json",'w')
	json.dump(setting,f,indent=4)
	f.close()