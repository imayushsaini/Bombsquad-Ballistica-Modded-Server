import ecdsa
import base64
import json
import ba
import _ba
import ba.internal
from stats import mystats
from typing import Optional, Any, Dict, List, Type, Sequence
from ba._gameactivity import GameActivity
from playersData import pdata
from serverData import serverdata
from tools import servercheck, logger, notification_manager
import setting
from datetime import datetime
import _thread
import os
import yaml
stats = {}
leaderboard = {}
top200 = {}
vapidkeys = {}
serverinfo = {}


class BsDataThread(object):
    def __init__(self):
        global stats
        stats["name"] = _ba.app.server._config.party_name
        stats["discord"] = "https://discord.gg/ucyaesh"
        stats["vapidKey"] = notification_manager.get_vapid_keys()["public_key"]

        self.refresh_stats_cache_timer = ba.Timer(8, ba.Call(self.refreshStats),
                                                  timetype=ba.TimeType.REAL, repeat=True)
        self.refresh_leaderboard_cache_timer = ba.Timer(10, ba.Call(
            self.refreshLeaderboard), timetype=ba.TimeType.REAL, repeat=True)

    def startThread(self):
        _thread.start_new_thread(self.refreshLeaderboard, ())

    def refreshLeaderboard(self):
        global leaderboard
        global top200

        lboard = mystats.get_cached_stats()
        leaderboard = lboard
        sorted_data = sorted(lboard.values(), key=lambda x: x["rank"])
        top_200_players = sorted_data[:200]

        top200 = {player["aid"]: player for player in top_200_players}

    def refreshStats(self):
        global stats
        global serverinfo
        liveplayers = {}
        nextMap = ''
        currentMap = ''

        for i in ba.internal.get_game_roster():
            try:
                liveplayers[i['account_id']] = {
                    'name': i['players'][0]['name_full'], 'client_id': i['client_id'], 'device_id': i['display_string']}
            except:
                liveplayers[i['account_id']] = {
                    'name': "<in-lobby>", 'client_id': i['client_id'], 'device_id': i['display_string']}
        try:
            nextMap = ba.internal.get_foreground_host_session(
            ).get_next_game_description().evaluate()

            current_game_spec = ba.internal.get_foreground_host_session()._current_game_spec
            gametype: Type[GameActivity] = current_game_spec['resolved_type']

            currentMap = gametype.get_settings_display_string(
                current_game_spec).evaluate()
        except:
            pass
        current_games = {'current': currentMap, 'next': nextMap}
        # system={'cpu':"p.cpu_percent()",'ram':p.virtual_memory().percent}
        system = {'cpu': "null", 'ram': 'null'}
        stats['system'] = system
        stats['roster'] = liveplayers
        stats['chats'] = ba.internal.get_chat_messages()
        stats['playlist'] = current_games
        stats['teamInfo'] = self.getTeamInfo()
        stats["sessionType"] = type(
            ba.internal.get_foreground_host_session()).__name__

        # print(self.getTeamInfo());

    def getTeamInfo(self):
        data = {}
        session = ba.internal.get_foreground_host_session()
        if session:
            teams = session.sessionteams
            for team in teams:
                data[str(team.id)] = {'name': team.name if isinstance(team.name, str) else team.name.evaluate(),
                                      'color': list(team.color),
                                      'score': team.customdata['score'],
                                      'players': []
                                      }
                for player in team.players:
                    teamplayer = {'name': player.getname(),
                                  'device_id': player.inputdevice.get_v1_account_name(True),
                                  'inGame': player.in_game,
                                  'character': player.character,
                                  'account_id': player.get_v1_account_id()
                                  }
                    data[str(team.id)]['players'].append(teamplayer)

        return data


BsDataThread()


def get_stats():
    return stats


def get_complete_leaderboard():
    return leaderboard


def get_top_200():
    return top200


def get_server_settings():
    return setting.get_settings_data()


def update_server_settings(settings):
    logger.log(f'updating server settings, request from web')
    setting.commit(settings)


def get_roles():
    return pdata.get_roles()


def get_perks():
    # TODO wire with spaz_effects to fetch list of effects.
    return {"perks": pdata.get_custom_perks(), "availableEffects": ["spark", "glow", "fairydust", "sparkground", "sweat", "sweatground", "distortion", "shine", "highlightshine", "scorch", "ice", "iceground",
                                                                    "slime", "metal",  "splinter",  "rainbow"]}


def update_perks(custom):
    logger.log(f'updating custom perks, request from web')
    pdata.update_custom_perks(custom)


def update_roles(roles):
    logger.log("updated roles from web")
    return pdata.update_roles(roles)


def get_profiles_db_list():
    return pdata.get_profiles_archive_index()


def get_logs_db_list():
    return serverdata.get_stats_index()


def get_matching_logs(key: str, filename: str):
    logs = serverdata.read_logs(filename)
    matching_lines = [line.strip() for line in logs.split('\n') if key in line]
    return matching_lines


def search_player_profile(search_key: str, db: str):
    selectedDB = {}
    if db == "profiles.json":
        selectedDB = pdata.get_profiles()

    elif db in pdata.get_profiles_archive_index():
        selectedDB = pdata.get_old_profiles(db)

    matching_objects = {}
    count = 0
    for key in selectedDB.keys():
        if (search_key == key or
           any(search_key.lower() in s.lower() for s in selectedDB[key].get("display_string", [])) or
                search_key.lower() in selectedDB[key].get("name", "").lower()):
            matching_objects[key] = selectedDB[key]
            count += 1
            if count > 50:
                break
    return matching_objects


def get_player_details(account_id: str):
    current_time = datetime.now()
    current_profiles = pdata.get_profiles()
    ip = ""
    device_id = ""
    if account_id in current_profiles:
        ip = current_profiles[account_id]["lastIP"]
        device_id = current_profiles[account_id]["deviceUUID"]
    extra_info = pdata.get_detailed_info(account_id)
    isBanned = False
    isMuted = False
    isKickVoteDisabled = False
    haveBanReason = servercheck.check_ban(ip, device_id, account_id, False)
    if haveBanReason:
        isBanned = True
        extra_info += " , Banned for > " + haveBanReason
    if account_id in pdata.get_blacklist()["muted-ids"] and current_time < datetime.strptime(pdata.get_blacklist()["muted-ids"][account_id]["till"], "%Y-%m-%d %H:%M:%S"):
        isMuted = True
        extra_info += f', Muted for > { pdata.get_blacklist()["muted-ids"][account_id]["reason"] } , till > {pdata.get_blacklist()["muted-ids"][account_id]["till"]} ,'
    if account_id in pdata.get_blacklist()["kick-vote-disabled"] and current_time < datetime.strptime(pdata.get_blacklist()["kick-vote-disabled"][account_id]["till"], "%Y-%m-%d %H:%M:%S"):
        isKickVoteDisabled = True
        extra_info += f', Kick vote disabled for > { pdata.get_blacklist()["kick-vote-disabled"][account_id]["reason"] } , till > {pdata.get_blacklist()["kick-vote-disabled"][account_id]["till"]} '

    return {"extra": extra_info, "isBan": isBanned, "isMuted": isMuted, "isKickVoteDisabled": isKickVoteDisabled}


def unban_player(account_id):
    logger.log(f'unbanning {account_id} , request from web')
    pdata.unban_player(account_id)


def unmute_player(account_id):
    logger.log(f'unmuting {account_id} , request from web')
    pdata.unmute(account_id)


def enable_kick_vote(account_id):
    logger.log(f'enabling kick vote for {account_id} , request from web')
    pdata.enable_kick_vote(account_id)

# TODO take duration input


def ban_player(account_id, duration):
    logger.log(f'banning {account_id} , request from web')
    pdata.ban_player(account_id, duration, "manually from website")


def mute_player(account_id, duration):
    logger.log(f'muting {account_id} , request from web')
    pdata.mute(account_id, duration, "manually from website")


def disable_kick_vote(account_id, duration):
    logger.log(f'disable {account_id} , request from web')
    pdata.disable_kick_vote(account_id, duration, "manually from website")


def get_server_config():
    return _ba.app.server._config.__dict__


def update_server_config(config):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, '..', 'config.yaml')

    with open(file_path, "w") as f:
        f.write(yaml.dump(config))


def do_action(action, value):
    if action == "message":
        _ba.pushcall(ba.Call(_ba.chatmessage, value), from_other_thread=True)
    elif action == "quit":
        _ba.pushcall(ba.Call(_ba.quit), from_other_thread=True)


def subscribe_player(sub, account_id, name):
    notification_manager.subscribe(sub, account_id, name)
