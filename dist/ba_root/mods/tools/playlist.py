# ba_meta require api 8

# Thanks to Rikko  for playlist fetch by code

import _thread
import time

import _babase
import setting
from bascenev1 import filter_playlist
import babase
import bascenev1 as bs
import bauiv1 as bui
from babase._general import Call
from bascenev1._coopsession import CoopSession
from bascenev1._dualteamsession import DualTeamSession
# session change by smoothy
from bascenev1._freeforallsession import FreeForAllSession

settings = setting.get_settings_data()

_babase.app.classic.coop_session_args['max_players'] = 14
_babase.app.classic.coop_session_args['campaign'] = "Default"
_babase.app.classic.coop_session_args['level'] = "Onslaught Training"


def set_playlist(content):
    if content is None:
        return
    _playlists_var = "{} Playlists".format(content["playlistType"])
    playlists = _babase.app.config[_playlists_var]
    playlist = playlists[content["playlistName"]]
    bs.chatmessage("Fetched playlist:" + content["playlistName"])
    typename = (
        'teams' if content['playlistType'] == 'Team Tournament' else
        'ffa' if content['playlistType'] == 'Free-for-All' else '??')
    return set_playlist_inline(playlist, typename)


def set_playlist_inline(playlist, newPLaylistType):
    session = bs.get_foreground_host_session()

    if (isinstance(session, DualTeamSession) or isinstance(session,
                                                           CoopSession)) and newPLaylistType == 'ffa':
        bs.get_foreground_host_session().end()
        _thread.start_new_thread(withDelay, (FreeForAllSession, playlist,))
    elif (isinstance(session, FreeForAllSession) or isinstance(session,
                                                               CoopSession)) and newPLaylistType == "teams":
        bs.get_foreground_host_session().end()
        _thread.start_new_thread(withDelay, (DualTeamSession, playlist,))
    else:
        updatePlaylist(playlist)


def withDelay(session, playlist):
    time.sleep(1)

    _babase.pushcall(Call(updateSession, session, playlist),
                     from_other_thread=True)


def updateSession(session, playlist):
    bs.new_host_session(session)
    if playlist:
        updatePlaylist(playlist)


def updatePlaylist(playlist):
    session = bs.get_foreground_host_session()
    content = filter_playlist(
        playlist,
        sessiontype=type(session),
        add_resolved_type=True,
    )
    playlist = bs._multiteamsession.ShuffleList(content, shuffle=False)
    session._playlist = playlist
    set_next_map(session, playlist.pull_next())


def set_next_map(session, game_map):
    session._next_game_spec = game_map
    with session.context():
        session._instantiate_next_game()


def playlist(code):
    bui.app.plus.add_v1_account_transaction(
        {
            'type': 'IMPORT_PLAYLIST',
            'code': str(code),
            'overwrite': True
        },
        callback=set_playlist)
    bui.app.plus.run_v1_account_transactions()


def setPlaylist(para):
    if para.isdigit():
        playlist(para)
    elif para == "coop":
        _thread.start_new_thread(withDelay, (CoopSession, None,))

    elif para in settings["playlists"]:
        playlist(settings["playlists"][para])
    else:
        bs.chatmessage("Available Playlist")
        for play in settings["playlists"]:
            bs.chatmessage(play)


def flush_playlists():
    print("Clearing old playlists..")
    for playlist in _babase.app.config["Team Tournament Playlists"]:
        bui.app.plus.add_v1_account_transaction(
            {
                "type": "REMOVE_PLAYLIST",
                "playlistType": "Team Tournament",
                "playlistName": playlist
            })
    bui.app.plus.run_v1_account_transactions()
    for playlist in _babase.app.config["Free-for-All Playlists"]:
        bui.app.plus.add_v1_account_transaction(
            {
                "type": "REMOVE_PLAYLIST",
                "playlistType": "Free-for-All",
                "playlistName": playlist
            })
    bui.app.plus.run_v1_account_transactions()
