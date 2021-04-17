""" 
Private Server whitelist by Mr.Smoothy

* don't dare to remove credits or I will bite you

GitHub : https://github.com/imayushsaini/Bombsquad-Ballistica-Modded-Server
"""
# Released under the MIT License. See LICENSE for details.


# ba_meta require api 6
from __future__ import annotations
from typing import TYPE_CHECKING
from ba._enums import TimeType

import ba, _ba, time, json, datetime, setting

if TYPE_CHECKING:
    pass





white_logs_path = _ba.env()["python_directory_user"]+"/tools/whitelist.json"
logs_paths = _ba.env()["python_directory_user"]+"/tools/logs.txt"


def commit(data):
	with open(white_logs_path, "w") as f:
		json.dump(data, f, indent=4)


def add_commit_to_logs(commit : str):
	with open(logs_path, "a") as f:
		f.write(commit+"\n")


def get_whitelist_data():
	with open(white_logs_path, "r") as f:
		data = json.load(f)
	return data


def in_white_list(accountid : str):
	data = get_whitelist_data()
	
	if str(accountid) in data:
		return True
	else:
		return False


def add_to_white_list(accountid : str, display_string : str):
	data = get_whitelist_data()
	
	if accountid not in data:
		data[str(accountid)] = [str(display_string)]
	
	else:
		data[str(accountid)].append(str(display_string))
	
	commit(data)


def handle_player_request(player):
	data = get_whitelist_data()
	settings = setting.get_settings_data()["white_list"]
	accountid = player.get_account_id()
	
	if settings["whitelist_on"]:
		if in_white_list(accountid):
			return
		else:
			rost = _ba.get_game_roster()
			
			for i in rost:
				if i["account_id"] == accountid:
					_ba.disconnect_client(int(i['client_id']))


def display_string_in_white_list(display_string : str):
	return any(display_string in i for i in data.values())


class _whitelist_:
	def __init__(self):
		
		settings = setting.get_settings_data()["white_list"]
		whitelist_on = settings["whitelist_on"]
		spectators = settings["spectators"]
		lobbychecktime = settings["lobbychecktime"]
		_ba.chatmessage(f"{settings} {whitelist_on} {spectators} {lobbychecktime}")
		
		try:
			data = get_whitelist_data()
			
		except:
			print("No Whitelist Detected , Creating One")
			self.whitelst = {}
			self.whitelst['pb-JiNJARBaXEFBVF9HFkNXXF1EF0ZaRlZE']=['smoothyki-id','mr.smoothy']
			commit(whitelst)
		
		if whitelist_on and not spectators:
			self.timer = ba.timer(lobbychecktime, self.checklobby, repeat=True, timetype=TimeType.REAL)
	
	def checklobby(self):
		
		settings = setting.get_settings_data()["white_list"]
		whitelist_on = settings["whitelist_on"]
		spectators = settings["spectators"]
		lobbychecktime = settings["lobbychecktime"]
		
		if whitelist_on and not spectators:
			try:
				
				rost = _ba.get_game_roster()
				for i in rost:
					if i['account_id'] in whitelist and i['account_id'] != '' or i['client_id'] == -1:
						return 
						
					else:
						add_commit_to_logs("Kicked from lobby "+i['account_id']+" "+i['spec_string'])
						_ba.disconnect_client(i['client_id'])
			
			except:
				return
	

