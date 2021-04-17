# Released under the MIT License. See LICENSE for details.
import _ba, json

settings_path = _ba.env()["python_directory_user"]+"/setting.json"




def get_settings_data():
	with open(settings_path, "r") as f:
		data = json.load(f)
	return data



def commit(data):
	with open(settings_path, "w") as f:
		json.dump(data, f, indent=4)



def sendError(msg : str, client_id : int = None):
	if client_id == None:
		_ba.screenmessage(msg, color=(1,0,0))
	else:
		_ba.screenmessage(msg, color=(1,0,0), transient=True, clients=[client_id])

