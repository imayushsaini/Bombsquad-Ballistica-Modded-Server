# Released under the MIT License. See LICENSE for details.
import ba, _ba
from serverData import serverdata
from tools import profanity
from tools import servercheck
import time
import setting
import _thread
settings = setting.get_settings_data()


def filter(msg,pb_id,client_id):
	new_msg=profanity.censor(msg)
	if new_msg!=msg:
		addWarn(pb_id,client_id)

	now = time.time()

	if "lastMsgTime" in serverdata.clients[pb_id]:
		count=serverdata.clients[pb_id]["cMsgCount"]
		if now - serverdata.clients[pb_id]["lastMsgTime"] < 5:
			count+=1
			if count >=2:
				addWarn(pb_id,client_id)
				count =0
		elif now - serverdata.clients[pb_id]["lastMsgTime"] < 30:
			if serverdata.clients[pb_id]["lastMsg"]==msg:
				addWarn(pb_id,client_id)
		else:
			count =0

		serverdata.clients[pb_id]['cMsgCount']=count
		serverdata.clients[pb_id]['lastMsgTime']=now
		serverdata.clients[pb_id]['lastMsg']=msg
	else:
		serverdata.clients[pb_id]['cMsgCount']=0
		serverdata.clients[pb_id]['lastMsgTime']=now
		serverdata.clients[pb_id]['lastMsg']=msg
	return new_msg



def addWarn(pb_id,client_id):
	now=time.time()
	player=serverdata.clients[pb_id]
	warn=player['warnCount']
	if now - player['lastWarned'] <= settings["WarnCooldownMinutes"]*60:
		warn+=1
		if warn > settings["maxWarnCount"]:
			_ba.screenmessage(settings["afterWarnKickMsg"],color=(1,0,0),transient=True,clients=[client_id])
			_ba.disconnect_client(client_id)
			_thread.start_new_thread(servercheck.reportSpam,(pb_id,))
			
		else:
			_ba.screenmessage(settings["warnMsg"],color=(1,0,0),transient=True,clients=[client_id])
	else:
		warn=0
	serverdata.clients[pb_id]["warnCount"]=warn
	serverdata.clients[pb_id]['lastWarned']=now



