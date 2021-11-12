"""
Private Server whitelist by Mr.Smoothy

* don't dare to remove credits or I will bite you

GitHub : https://github.com/imayushsaini/Bombsquad-Ballistica-Modded-Server
"""
# Released under the MIT License. See LICENSE for details.


# ba_meta require api 6
from __future__ import annotations
from typing import TYPE_CHECKING
from ba._generated.enums import TimeType

import ba, _ba, time, json, datetime, setting

if TYPE_CHECKING:
    pass


whitelist={}



whitelistFile = _ba.env()["python_directory_user"]+"/tools/whitelist.json"
logs_path = _ba.env()["python_directory_user"]+"/serverData/wl_logs.txt"


def commit(data):
	with open(whitelistFile, "w") as f:
		json.dump(data, f, indent=4)


def add_commit_to_logs(commit : str):
	with open(logs_path, "a") as f:
		f.write(commit+"\n")


def get_whitelist_data():
	global whitelist
	if whitelist != {}:
		return whitelist
	try:
		with open(whitelistFile, "r") as f:
			data = json.load(f)
			whitelist=data
	except:
		print("No Whitelist Detected , Creating One")
		whitelist={}
		whitelist['pb-JiNJARBaXEFBVF9HFkNXXF1EF0ZaRlZE']=['smoothyki-id','mr.smoothy']
		commit(whitelist)

	return whitelist


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


class Whitelist:
	def __init__(self):
		global whitelist

		settings = setting.get_settings_data()["white_list"]
		whitelist_on = settings["whitelist_on"]
		spectators = settings["spectators"]
		lobbychecktime = settings["lobbychecktime"]
		# _ba.chatmessage(f"{settings} {whitelist_on} {spectators} {lobbychecktime}")


		get_whitelist_data()


		if whitelist_on and not spectators:
			self.timer = ba.Timer(lobbychecktime, self.checklobby, repeat=True, timetype=TimeType.REAL)

	def checklobby(self):
		global whitelist
		settings = setting.get_settings_data()["white_list"]
		whitelist_on = settings["whitelist_on"]
		spectators = settings["spectators"]
		lobbychecktime = settings["lobbychecktime"]

		if whitelist_on and not spectators:
			if True:

				rost = _ba.get_game_roster()
				for i in rost:
					if i['account_id'] in whitelist and i['account_id'] != '' or i['client_id'] == -1:
						pass

					else:
						try:
							add_commit_to_logs("Kicked from lobby "+i['account_id'])
						except:
							pass
						_ba.disconnect_client(i['client_id'])

			# except:
			# 	return
		else:
			self.timer =None


