# Released under the MIT License. See LICENSE for details.


# NOT COMPLETED YET

from serverData import serverdata
from playersData import pdata
import _ba
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



def on_player_join(pbid):
	
	player_data=pdata.get_info(pbid)
	
	


	if player_data!=None:
		if player_data["isBan"]:
			for ros in _ba.get_game_roster():
				if ros['account_id']==pbid:
					_ba.disconnect_client(ros['client_id'])
			return
		serverdata.clients[pbid]=player_data
		
	else:
		d_string=""
		for ros in _ba.get_game_roster():
			if ros['account_id']==pbid:
				d_string=ros['display_string']
		pdata.add_profile(pbid,d_string,d_string)
















