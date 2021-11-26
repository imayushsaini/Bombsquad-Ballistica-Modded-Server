from playersData import pdata
import time
import _thread

def check():
	_thread.start_new_thread(updateProfilesJson,())


def updateProfilesJson():
	profiles=pdata.get_profiles()

	for id in profiles:
		if "spamCount" not in profiles[id]:
			profiles[id]["spamCount"]=0
			profiles[id]["lastSpam"]=time.time()

	pdata.commit_profiles(profiles)
