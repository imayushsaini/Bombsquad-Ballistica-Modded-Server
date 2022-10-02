import _ba,ba
import ba.internal
import setting
from serverData import serverdata

from ba._dualteamsession import DualTeamSession
from ba._coopsession import CoopSession
settings = setting.get_settings_data()
from tools import playlist

def balanceTeams():
	
	session = ba.internal.get_foreground_host_session()
	if settings["coopModeWithLessPlayers"]["enable"] and len(session.sessionplayers) < settings["coopModeWithLessPlayers"]["minPlayerToExitCoop"]:
		playlist.setPlaylist('coop')
		return
	
	if not isinstance(session,DualTeamSession) or len(session.sessionplayers)<4 or len(session.sessionteams)!=2:
		return
	teamASize=0
	teamBSize=0
	try:

		for player in session.sessionplayers:
			if player.sessionteam.id==0:
				teamASize+=1
			else:
				teamBSize+=1
	except:
		pass
	if abs(teamBSize-teamASize)>=0:
		if teamBSize> teamASize and teamBSize!=0:
			movePlayers(1,0,abs(teamBSize-teamASize)-1)
		elif teamASize>teamBSize and teamASize!=0:
			movePlayers(0,1,abs(teamBSize-teamASize)-1)

def movePlayers(fromTeam,toTeam,count):
	return  
	# disabling team balance for now , until we found solution 
	#  Error : on score screen when shifted player left the game on_player_leave unable to found player in activity team
	session=ba.internal.get_foreground_host_session()
	fromTeam=session.sessionteams[fromTeam]
	toTeam=session.sessionteams[toTeam]
	for i in range(0,count):
		player=fromTeam.players.pop()
		print("moved"+player.get_v1_account_id())
		broadCastShiftMsg(player.get_v1_account_id())
		player.setdata(team=toTeam,character=player.character,color=toTeam.color,highlight=player.highlight)
		iconinfo=player.get_icon_info()
		player.set_icon_info(iconinfo['texture'],iconinfo['tint_texture'],toTeam.color,player.highlight)
		toTeam.players.append(player)

def broadCastShiftMsg(pb_id):
	for ros in ba.internal.get_game_roster():
		if ros['account_id']==pb_id:
			_ba.screenmessage("Shifted "+ros["display_string"]+" to balance team")

def on_player_join():
	session = ba.internal.get_foreground_host_session()
	if len(session.sessionplayers)>1:
		return
	if isinstance(session,DualTeamSession):
		if settings["coopModeWithLessPlayers"]["enable"] and len(session.sessionplayers) < settings["coopModeWithLessPlayers"]["minPlayerToExitCoop"]:
			playlist.setPlaylist('coop')

	# this not usefull now ., leave it here for now
	elif isinstance(session,CoopSession):
		if len(session.sessionplayers) >= settings["coopModeWithLessPlayers"]["minPlayerToExitCoop"]:
			playlist.setPlaylist('default')


def checkToExitCoop():
	session = ba.internal.get_foreground_host_session()
	if len(session.sessionplayers) >= settings["coopModeWithLessPlayers"]["minPlayerToExitCoop"] and not serverdata.coopmode:
		playlist.setPlaylist('default')



