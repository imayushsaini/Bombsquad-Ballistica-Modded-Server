# Released under the MIT License. See LICENSE for details.


# NOT COMPLETED YET

from serverData import serverdata
from playersData import pdata
import _ba
import urllib.request
import json
import datetime
import time
import ba
from ba._general import Call
import threading
import setting
import _thread
from tools import logger
from features import profanity

# class ServerChecker:

# 	def __init__():
# 		run()

# 	def run(self):
# 		clients=roset.players
# 		# check if some one joined the party
# 		for client in clients:
# 			if cleint.account_id not in serverdata.currentclients:
# 				self.playerjoined(client)
# 		# check if some one left the party
# 		clients_id=[client.account_id for client in clients]
# 		for player in serverdata.currentclients:
# 			if player not in clients_id:
# 				self.playerleft(player)


# 	def playerjoined(self,client):
# 		if client.account_id in serverdata.cachedclients:
# 			serevrdata.currentclients[client_account_id]=serverdata.cachedclients[id]

# 		playerData=pdata.get_info(client.account_id)
# 		playerData["lastjoin"]=time.time()
# 		if playerData ==None:
# 			self.registernewplayer(cleint)
# 		else if playerData['isBan']:
# 			_ba.disconnect_client(client.client_id,9999)
# 		else:
# 			serverData.currentclients[client_account_id]=playerData


# 	def playerleft(self,player):
# 		serverdata.cachedclients[player]=serverdata.currentclients[player]

# 		serverdata.currentclients.remove(player)

# 		timeplayed=time.time()-serverdata.currentclients[player]['lastjoin']
# 		serverdata.cachedclients[player]["totaltimeplayed"]+=timeplayed

# 		pdata.update_profile(serverdata.cachedclients[player])

settings = setting.get_settings_data()

class checkserver(object):
	def start(self):
		self.players=[]
		
		self.t1=ba.timer(1,  ba.Call(self.check),repeat=True)

	def check(self):
		newPlayers=[]
		for ros in _ba.get_game_roster():
			
			newPlayers.append(ros['account_id'])
			if ros['account_id'] not in self.players and ros['client_id'] !=-1:
				d_str=ros['display_string']
				d_str2=profanity.censor(d_str)
				try:
					logger.log("Login Id :"+d_str+"\nUnique Id :"+ros["account_id"]+"\nAction : Joined the server","playerjoin")
				except:
					pass
				if d_str2!=d_str:
					_ba.screenmessage("Profanity in Id , change your ID and join back",color=(1,0,0),transient=True,clients=[ros['client_id']])
					try:
						logger.log("Login Id :"+d_str+"\nUnique Id :"+ros["account_id"]+"\nAction : Kicked > Profanity check","sys")
					except:
						pass
					_ba.disconnect_client(ros['client_id'],1)
					
					return
				if settings["whitelist"] and ros["account_id"]!=None:
					if ros["account_id"] not in pdata.whitelist:
						_ba.screenmessage("Not in whitelist,contact admin",color=(1,0,0),transient=True,clients=[ros['client_id']])
						logger.log("Login Id :"+d_str+"\nUnique Id :"+ros["account_id"]+"\nAction : Kicked > Not in whitelist")
						_ba.disconnect_client(ros['client_id'])
					
							
						return

				if ros['account_id'] != None:
					if ros['account_id'] in serverdata.clients:
						on_player_join_server(ros['account_id'],serverdata.clients[ros['account_id']])
					else:
						LoadProfile(ros['account_id']).start()
		
		self.players=newPlayers





def on_player_join_server(pbid,player_data):
	now=time.time()
	#player_data=pdata.get_info(pbid)
	clid=113
	for ros in _ba.get_game_roster():
		if ros["account_id"]==pbid:
			clid=ros["client_id"]
	if pbid in serverdata.clients:
		rejoinCount=serverdata.clients[pbid]["rejoincount"]
		spamCount=serverdata.clients[pbid]["spamCount"]
		if now-serverdata.clients[pbid]["lastJoin"] < 15:
			rejoinCount+=1
			if rejoinCount >2:
				_ba.screenmessage("Joining too fast , slow down dude",color=(1,0,1),transient=True,clients=[clid])
				logger.log("Unique Id :"+pbid+"\nAction : Kicked > Joining too fast")
				_ba.disconnect_client(clid)
				
				_thread.start_new_thread(reportSpam,(pbid,))
				
				return
		else:
			rejoinCount=0

		serverdata.clients[pbid]["rejoincount"]=rejoinCount
		serverdata.clients[pbid]["lastJoin"]=now






	
	if player_data!=None:
		device_strin=""
		if player_data["isBan"] or get_account_age(player_data["accountAge"]) < settings["minAgeToJoinInHours"]:
			for ros in _ba.get_game_roster():
				if ros['account_id']==pbid:
					if not player_data["isBan"]:
						_ba.screenmessage("New Accounts not allowed here , come back later",color=(1,0,0), transient=True,clients=[ros['client_id']])
					logger.log("Unique Id :"+pbid+"\nAction : Kicked > Banned account")
					_ba.disconnect_client(ros['client_id'])
					
			return
		else:
			if pbid not in serverdata.clients:
				serverdata.clients[pbid]=player_data
				serverdata.clients[pbid]["warnCount"]=0
				serverdata.clients[pbid]["lastWarned"]=time.time()
				serverdata.clients[pbid]["verified"]=False
				serverdata.clients[pbid]["rejoincount"]=1
				serverdata.clients[pbid]["lastJoin"]=time.time()
				if not player_data["canStartKickVote"]:
					_ba.disable_kickvote(pbid)

			verify_account(pbid,player_data)
			cid=113
			d_st="xx"
			for ros in _ba.get_game_roster():
				if ros['account_id']==pbid:
					cid=ros['client_id']
					d_st=ros['display_string']
			_ba.screenmessage(settings["regularWelcomeMsg"]+" "+d_st,color=(0.60,0.8,0.6),transient=True,clients=[cid])
		
	else:
		
		d_string=""
		cid=113
		for ros in _ba.get_game_roster():
			if ros['account_id']==pbid:
				d_string=ros['display_string']
				cid=ros['client_id']

		thread = FetchThread(
		    target=my_acc_age,
		    callback=save_age,
		    pb_id=pbid,
		    display_string=d_string
		)

		thread.start()
		_ba.screenmessage(settings["firstTimeJoinMsg"],color=(0.6,0.8,0.6),transient=True,clients=[cid])

		

		#pdata.add_profile(pbid,d_string,d_string)

def verify_account(pb_id,p_data):
	d_string=""
	for ros in _ba.get_game_roster():
		if ros['account_id']==pb_id:
			d_string=ros['display_string']

	if d_string not in p_data['display_string']:

		thread2 = FetchThread(
			    target=get_device_accounts,
			    callback=save_ids,
			    pb_id=pb_id,
			    display_string=d_string
			)
		thread2.start()
	else:
		serverdata.clients[pb_id]["verified"]=True


#============== IGNORE BLOW CODE , ELSE DIE =======================

def _make_request_safe(request, retries=2, raise_err=True):
    try:
        return request()
    except:
        if retries > 0:
            time.sleep(1)
            return _make_request_safe(request, retries=retries-1, raise_err=raise_err)
        if raise_err:
            raise

def get_account_creation_date(pb_id):
	# thanks rikko 
    account_creation_url = "http://bombsquadgame.com/accountquery?id=" + pb_id
    account_creation = _make_request_safe(lambda: urllib.request.urlopen(account_creation_url))
    if account_creation is not None:
        try:
            account_creation = json.loads(account_creation.read())
        except ValueError:
            pass
        else:
            creation_time = account_creation["created"]
            creation_time = map(str, creation_time)
            creation_time = datetime.datetime.strptime("/".join(creation_time), "%Y/%m/%d/%H/%M/%S")
            # Convert to IST
            creation_time += datetime.timedelta(hours=5, minutes=30)
            return str(creation_time)
            # now = datetime.datetime.now()
            # delta = now - creation_time
            # delta_hours = delta.total_seconds() / (60 * 60)
            # return delta_hours

def get_device_accounts(pb_id):
	url="http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID="+pb_id
	data=_make_request_safe(lambda:urllib.request.urlopen(url))
	if data is not None:
		try:
			accounts=json.loads(data.read())["accountDisplayStrings"]
		except ValueError:
			return ['???']
		else:
			return accounts

# =======  yes fucking threading code , dont touch ==============


# ============ file I/O =============

class LoadProfile(threading.Thread):
	def __init__(self,pb_id):
		threading.Thread.__init__(self)
		self.pbid=pb_id
		

	def run(self):
		player_data=pdata.get_info(self.pbid)
		_ba.pushcall(Call(on_player_join_server,self.pbid,player_data),from_other_thread=True)







# ================ http ================
class FetchThread(threading.Thread):
    def __init__(self,target, callback=None,pb_id="ji",display_string="XXX"):
        
        super(FetchThread, self).__init__(target=self.target_with_callback, args=(pb_id,display_string,))
        self.callback = callback
        self.method = target
        
        
    def target_with_callback(self,pb_id,display_string):
        
        data=self.method(pb_id)
        if self.callback is not None:
            self.callback(data,pb_id,display_string)


def my_acc_age(pb_id):
    
    return get_account_creation_date(pb_id)


def save_age(age, pb_id,display_string):
    
    
    pdata.add_profile(pb_id,display_string,display_string,age)
    time.sleep(2)
    thread2 = FetchThread(
		    target=get_device_accounts,
		    callback=save_ids,
		    pb_id=pb_id,
		    display_string=display_string
		)
    thread2.start()
    if get_account_age(age) < settings["minAgeToJoinInHours"]:
    	msg="New Accounts not allowed to play here , come back tmrw."
    	logger.log("Unique Id :"+pbid+"\nAction : Kicked > New account")
    	_ba.pushcall(Call(kick_by_pb_id,pb_id,msg),from_other_thread=True)

def save_ids(ids,pb_id,display_string):

	
	pdata.update_displayString(pb_id,ids)


	if display_string not in ids:
		msg="Spoofed Id detected , Goodbye"
		_ba.pushcall(Call(kick_by_pb_id,pb_id,msg),from_other_thread=True)
		serverdata.clients[pb_id]["verified"]=False
		logger.log("Unique Id :"+pbid+"\nAction : Kicked > Using spoofed id "+display_string)
	else:
		serverdata.clients[pb_id]["verified"]=True
	


def kick_by_pb_id(pb_id,msg):
	for ros in _ba.get_game_roster():
		if ros['account_id']==pb_id:
			_ba.screenmessage(msg, transient=True, clients=[ros['client_id']])
			_ba.disconnect_client(ros['client_id'])

	

def get_account_age(ct):
    creation_time=datetime.datetime.strptime(ct,"%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    delta = now - creation_time
    delta_hours = delta.total_seconds() / (60 * 60)
    return delta_hours


def reportSpam(id):
	now=time.time()
	profiles=pdata.get_profiles()
	if id in profiles:
		count=profiles[id]["spamCount"]
		
		if now-profiles[id]["lastSpam"] < 2*24*60*60:
			count+=1
			if count > 3:
				profiles[id]["isBan"]=True
		else:
			count =0

		profiles[id]["spamCount"]=count
		profiles[id]["lastSpam"]=now
		pdata.commit_profiles(profiles)