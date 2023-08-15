import setting
from serverdata import serverdata

import bascenev1 as bs
from bascenev1._coopsession import CoopSession
from bascenev1._dualteamsession import DualTeamSession
from tools import playlist

settings = setting.get_settings_data()


def balanceTeams():
    session = bs.get_foreground_host_session()
    if settings["coopModeWithLessPlayers"]["enable"] and len(
        session.sessionplayers) < settings["coopModeWithLessPlayers"][
        "minPlayerToExitCoop"]:
        playlist.setPlaylist('coop')
        return
    if not isinstance(session, DualTeamSession) or len(
        session.sessionplayers) < 4 or len(session.sessionteams) != 2:
        return
    teamASize = 0
    teamBSize = 0
    try:
        for player in session.sessionplayers:
            if player.sessionteam.id == 0:
                teamASize += 1
            else:
                teamBSize += 1
    except:
        pass
    if settings["autoTeamBalance"]:
        if abs(teamBSize - teamASize) >= 0:
            if teamBSize > teamASize and teamBSize != 0:
                movePlayers(1, 0, abs(teamBSize - teamASize) - 1)
            elif teamASize > teamBSize and teamASize != 0:
                movePlayers(0, 1, abs(teamBSize - teamASize) - 1)


def movePlayers(fromTeam, toTeam, count):
    session = bs.get_foreground_host_session()
    fromTeam = session.sessionteams[fromTeam]
    toTeam = session.sessionteams[toTeam]
    for i in range(0, count):
        player = fromTeam.players.pop()
        broadCastShiftMsg(player.get_v1_account_id())
        player.setdata(team=toTeam, character=player.character,
                       color=toTeam.color, highlight=player.highlight)
        iconinfo = player.get_icon_info()
        player.set_icon_info(
            iconinfo['texture'], iconinfo['tint_texture'], toTeam.color,
            player.highlight)
        toTeam.players.append(player)
        player.sessionteam.activityteam.players.append(player.activityplayer)


def broadCastShiftMsg(pb_id):
    for ros in bs.get_game_roster():
        if ros['account_id'] == pb_id:
            bs.broadcastmessage(
                "Shifted " + ros["display_string"] + " to balance team")


def on_player_join():
    session = bs.get_foreground_host_session()
    if len(session.sessionplayers) > 1:
        return
    if isinstance(session, DualTeamSession):
        if settings["coopModeWithLessPlayers"]["enable"] and len(
            session.sessionplayers) < settings["coopModeWithLessPlayers"][
            "minPlayerToExitCoop"]:
            playlist.setPlaylist('coop')

    # this not usefull now ., leave it here for now
    elif isinstance(session, CoopSession):
        if len(session.sessionplayers) >= settings["coopModeWithLessPlayers"][
            "minPlayerToExitCoop"]:
            playlist.setPlaylist('default')


def checkToExitCoop():
    session = bs.get_foreground_host_session()
    if len(session.sessionplayers) >= settings["coopModeWithLessPlayers"][
        "minPlayerToExitCoop"] and not serverdata.coopmode:
        playlist.setPlaylist('default')
