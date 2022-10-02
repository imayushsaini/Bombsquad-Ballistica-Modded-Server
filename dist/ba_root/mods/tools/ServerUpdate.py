from playersData import pdata
import time
import _thread
import urllib.request
from efro.terminal import Clr
import json
VERSION=71

def check():
	_thread.start_new_thread(updateProfilesJson,())
	_thread.start_new_thread(checkChangelog,())


def updateProfilesJson():
	profiles=pdata.get_profiles()

	for id in profiles:
		if "spamCount" not in profiles[id]:
			profiles[id]["spamCount"]=0
			profiles[id]["lastSpam"]=time.time()

	pdata.commit_profiles(profiles)



def fetchChangelogs():
	url="https://raw.githubusercontent.com/imayushsaini/Bombsquad-Ballistica-Modded-Server/public-server/dist/ba_root/mods/changelogs.json"

	if 2*2==4:
		try:
			data=urllib.request.urlopen(url)
			changelog=json.loads(data.read())
		except:
			return None
		else:
			return changelog

def checkChangelog():
	changelog=fetchChangelogs()
	if changelog==None:
		print(f'{Clr.BRED} UNABLE TO CHECK UPDATES , CHECK MANUALLY FROM URL {Clr.RST}',flush=True)
	else:
		msg=""
		avail=False
		for log in changelog:
			if int(log)>VERSION:
				avail=True

		if not avail:
			print(f'{Clr.BGRN}{Clr.WHT} YOU ARE ON LATEST VERSION {Clr.RST}',flush=True)
		else:
			print(f'{Clr.BYLW}{Clr.BLU} UPDATES AVAILABLE {Clr.RST}',flush=True)
			for log in changelog:
				if int(log)>VERSION:
					msg=changelog[log]["time"]
					print(f'{Clr.CYN} {msg} {Clr.RST}',flush=True)

					msg=changelog[log]["log"]
					print(f'{Clr.MAG} {msg} {Clr.RST}',flush=True)





