
import _thread
import os
from datetime import datetime

import _babase
import bascenev1
import setting
import yaml

from playersdata import pdata
from serverdata import serverdata
from stats import mystats
from typing import Type

import babase
import bascenev1 as bs
from tools import servercheck, logger, notification_manager
from tools.file_handle import OpenJson

stats = {}
leaderboard = {}
top200 = {}
vapidkeys = {}
serverinfo = {}


class BsDataThread(object):
    def __init__(self):
        global stats
        stats["name"] = _babase.app.classic.server._config.party_name
        stats["discord"] = get_server_settings(
        )["ballistica_web"]["discord_link"]
        stats["vapidKey"] = notification_manager.get_vapid_keys()["public_key"]

        self.refresh_stats_cache_timer = bs.AppTimer(8, babase.CallStrict(
            self.refreshStats), repeat=True)
        self.refresh_leaderboard_cache_timer = bs.AppTimer(10, babase.CallStrict(
            self.refreshLeaderboard), repeat=True)

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

        for i in bs.get_game_roster():
            try:
                liveplayers[i['account_id']] = {
                    'name': i['players'][0]['name_full'],
                    'client_id': i['client_id'],
                    'device_id': i['display_string']}
            except:
                liveplayers[i['account_id']] = {
                    'name': "<in-lobby>", 'client_id': i['client_id'],
                    'device_id': i['display_string']}
        try:
            nextMap = bs.get_foreground_host_session(
            ).get_next_game_description().evaluate()

            current_game_spec = bs.get_foreground_host_session()._current_game_spec
            gametype: Type[bascenev1.GameActivity] = current_game_spec['resolved_type']

            currentMap = gametype.get_settings_display_string(
                current_game_spec).evaluate()
        except:
            pass
        current_games = {'current': currentMap, 'next': nextMap}
        # system={'cpu':"p.cpu_percent()",'ram':p.virtual_memory().percent}
        system = {'cpu': "null", 'ram': 'null'}
        stats['system'] = system
        stats['roster'] = liveplayers
        stats['chats'] = bs.get_chat_messages()
        stats['playlist'] = current_games
        stats['teamInfo'] = self.getTeamInfo()
        stats["sessionType"] = type(
            bs.get_foreground_host_session()).__name__

        # print(self.getTeamInfo());

    def getTeamInfo(self):
        data = {}
        session = bs.get_foreground_host_session()
        if session:
            teams = session.sessionteams
            for team in teams:
                data[str(team.id)] = {'name': team.name if isinstance(team.name,
                                                                      str) else team.name.evaluate(),
                                      'color': list(team.color),
                                      'score': team.customdata['score'],
                                      'players': []
                                      }
                for player in team.players:
                    teamplayer = {'name': player.getname(),
                                  'device_id': player.inputdevice.get_v1_account_name(
                                      True),
                                  'inGame': player.in_game,
                                  'character': player.character,
                                  'account_id': player.get_account_id()
                                  }
                    data[str(team.id)]['players'].append(teamplayer)

        return data


v = bs.AppTimer(8, babase.CallStrict(
    BsDataThread))


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
    custom = pdata.get_custom()
    from plugins.kickvote_manager import KickVoteManager
    immune_list = KickVoteManager.get().get_immune_list()
    return {
        "perks": {
            "customtag": custom.get("customtag", {}),
            "kick_vote_immune": immune_list
        }
    }


def update_perks(custom):
    logger.log('updating custom perks (tags/immunity), request from web')
    if isinstance(custom, dict):
        tags = None
        immune = None
        if "customtag" in custom:
            tags = custom["customtag"]
        elif "perks" in custom and "customtag" in custom["perks"]:
            tags = custom["perks"]["customtag"]

        if "kick_vote_immune" in custom:
            immune = custom["kick_vote_immune"]
        elif "perks" in custom and "kick_vote_immune" in custom["perks"]:
            immune = custom["perks"]["kick_vote_immune"]

        if tags is not None:
            current = pdata.get_custom()
            current["customtag"] = tags
            pdata.update_custom_perks(current)

        if immune is not None:
            from plugins.kickvote_manager import KickVoteManager
            kvm = KickVoteManager.get()
            if isinstance(immune, list):
                # Set exact list
                current_immune = set(kvm.get_immune_list())
                target_immune = set(immune)
                for to_add in (target_immune - current_immune):
                    kvm.add_immune(to_add)
                for to_remove in (current_immune - target_immune):
                    kvm.remove_immune(to_remove)
            elif isinstance(immune, dict):
                for acc_id, is_imm in immune.items():
                    if is_imm:
                        kvm.add_immune(acc_id)
                    else:
                        kvm.remove_immune(acc_id)


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
            any(search_key.lower() in s.lower() for s in
                selectedDB[key].get("display_string", [])) or
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
    if account_id in pdata.get_blacklist()[
            "muted-ids"] and current_time < datetime.strptime(
            pdata.get_blacklist()["muted-ids"][account_id]["till"],
            "%Y-%m-%d %H:%M:%S"):
        isMuted = True
        extra_info += f', Muted for > {pdata.get_blacklist()["muted-ids"][account_id]["reason"]} , till > {pdata.get_blacklist()["muted-ids"][account_id]["till"]} ,'
    if account_id in pdata.get_blacklist()[
            "kick-vote-disabled"] and current_time < datetime.strptime(
            pdata.get_blacklist()["kick-vote-disabled"][account_id]["till"],
            "%Y-%m-%d %H:%M:%S"):
        isKickVoteDisabled = True
        extra_info += f', Kick vote disabled for > {pdata.get_blacklist()["kick-vote-disabled"][account_id]["reason"]} , till > {pdata.get_blacklist()["kick-vote-disabled"][account_id]["till"]} '

    return {"extra": extra_info, "isBan": isBanned, "isMuted": isMuted,
            "isKickVoteDisabled": isKickVoteDisabled}


def unban_player(account_id):
    logger.log(f'unbanning {account_id} , request from web')
    pdata.unban_player(account_id)


def unmute_player(account_id):
    logger.log(f'unmuting {account_id} , request from web')
    pdata.unmute(account_id)


def enable_kick_vote(account_id):
    logger.log(f'enabling kick vote for {account_id} , request from web')
    from plugins.kickvote_manager import KickVoteManager
    KickVoteManager.get().remove_restriction(account_id)


# TODO take duration input


def ban_player(account_id, duration):
    logger.log(f'banning {account_id} , request from web')
    pdata.ban_player(account_id, duration, "manually from website")


def mute_player(account_id, duration):
    logger.log(f'muting {account_id} , request from web')
    pdata.mute(account_id, duration, "manually from website")


def disable_kick_vote(account_id, duration):
    logger.log(f'disable {account_id} , request from web')
    from plugins.kickvote_manager import KickVoteManager
    KickVoteManager.get().add_restriction(account_id, duration, "manually from website")


def set_kick_vote_immune(account_id, immune: bool = True):
    logger.log(f'set kick vote immune for {account_id} ({immune}) , request from web')
    from plugins.kickvote_manager import KickVoteManager
    if immune:
        KickVoteManager.get().add_immune(account_id)
    else:
        KickVoteManager.get().remove_immune(account_id)


def get_kickvote_data():
    from plugins.kickvote_manager import KickVoteManager
    kvm = KickVoteManager.get()
    return {
        "restricted": kvm.get_restricted_list(),
        "immune": kvm.get_immune_list(),
        "blacklist": pdata.get_blacklist().get("kick-vote-disabled", {})
    }


def get_server_config():
    return _babase.app.classic.server._config.__dict__


def update_server_config(config):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, '..', 'config.json')

    with OpenJson(file_path) as f:
        f.dump(config, indent=4)


def do_action(action, value):
    if action == "message":
        _babase.pushcall(babase.CallPartial(bs.chatmessage, value),
                         from_other_thread=True)
    elif action == "quit":
        _babase.pushcall(babase.CallStrict(
            _babase.quit), from_other_thread=True)


def subscribe_player(sub, account_id, name):
    notification_manager.subscribe(sub, account_id, name)


def get_whitelist():
    pdata.load_white_list()
    return pdata.CacheData.whitelist


def add_to_whitelist(account_id: str):
    pdata.add_to_whitelist(account_id)


def remove_from_whitelist(account_id: str):
    pdata.remove_from_whitelist(account_id)


def get_blacklist():
    return pdata.get_blacklist()


def get_recents():
    return serverdata.recents


def get_player_stats(account_id: str):
    return mystats.get_stats_by_id(account_id)


def get_players_paginated(page=1, per_page=50, search="", sort_by="server_profile_created_at", sort_order="desc"):
    import json
    import math
    from datetime import datetime
    from repository.db import run_query

    # Sanitize inputs
    try:
        page = max(1, int(page))
    except Exception:
        page = 1
    try:
        per_page = max(1, min(100, int(per_page)))
    except Exception:
        per_page = 50

    # White-list sortable columns
    allowed_sort_cols = {
        "id", "v2Tag", "account_id", "name",
        "registerOn", "totaltimeplayer", "warnCount", "rejoincount",
        "lastJoin", "server_profile_created_at"
    }
    db_sort_by = sort_by if sort_by in allowed_sort_cols else "server_profile_created_at"

    sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    query_where = ""
    params = []
    if search:
        query_where = "WHERE name LIKE ? OR account_id LIKE ? OR v2Tag LIKE ? OR lastIP LIKE ? OR deviceUUID LIKE ?"
        like_search = f"%{search}%"
        params = [like_search] * 5

    # Count total
    count_query = f"SELECT count(*) FROM profiles {query_where}"
    count_result = run_query(count_query, tuple(params), fetch=True)
    total_count = count_result[0][0] if count_result else 0

    # Fetch paginated rows
    offset = (page - 1) * per_page
    fetch_query = f"""
        SELECT id, v2Tag, account_id, name, display_string, registerOn, lastJoin,
               totaltimeplayer, warnCount, rejoincount, lastIP,
               deviceUUID, server_profile_created_at
        FROM profiles
        {query_where}
        ORDER BY {db_sort_by} {sort_order}
        LIMIT ? OFFSET ?
    """
    params_for_fetch = list(params)
    params_for_fetch.extend([per_page, offset])
    rows = run_query(fetch_query, tuple(params_for_fetch), fetch=True)

    players = []
    if rows:
        blacklist = pdata.get_blacklist()
        current_time = datetime.now()
        for r in rows:
            acc_id = r[2]
            ip = r[10]
            device_id = r[11]

            is_banned = False
            # Check ID
            if acc_id in blacklist.get("ban", {}).get("ids", {}):
                till_str = blacklist["ban"]["ids"][acc_id].get("till")
                try:
                    if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                        is_banned = True
                except Exception:
                    pass
            # Check IP
            if not is_banned and ip and ip in blacklist.get("ban", {}).get("ips", {}):
                till_str = blacklist["ban"]["ips"][ip].get("till")
                try:
                    if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                        is_banned = True
                except Exception:
                    pass
            # Check Device UUID
            if not is_banned and device_id and device_id in blacklist.get("ban", {}).get("deviceids", {}):
                till_str = blacklist["ban"]["deviceids"][device_id].get("till")
                try:
                    if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                        is_banned = True
                except Exception:
                    pass

            # Check if muted
            is_muted = False
            if acc_id in blacklist.get("muted-ids", {}):
                till_str = blacklist["muted-ids"][acc_id].get("till")
                try:
                    if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                        is_muted = True
                except Exception:
                    pass

            try:
                display_string = json.loads(r[4]) if r[4] else []
            except Exception:
                display_string = []
            players.append({
                "id": r[0],
                "v2Tag": r[1],
                "account_id": acc_id,
                "name": r[3],
                "display_string": display_string,
                "registerOn": r[5],
                "lastJoin": r[6],
                "totaltimeplayer": r[7],
                "isBan": is_banned,
                "isMuted": is_muted,
                "warnCount": r[8] or 0,
                "rejoincount": r[9] or 1,
                "lastIP": ip,
                "deviceUUID": device_id,
                "server_profile_created_at": r[12]
            })

        if sort_by in ("isBan", "isMuted") and players:
            players.sort(key=lambda p: bool(p.get(sort_by)), reverse=(sort_order == "desc"))

    total_pages = math.ceil(total_count / per_page)
    return {
        "players": players,
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


def get_player_by_id(account_id: str):
    from repository.profiles import get_profile_by_acc_id
    from datetime import datetime
    p = get_profile_by_acc_id(account_id)
    if p is not None:
        p_dict = dict(p)
        blacklist = pdata.get_blacklist()
        current_time = datetime.now()

        is_banned = False
        ip = p_dict.get("lastIP")
        device_id = p_dict.get("deviceUUID")

        # Check ID
        if account_id in blacklist.get("ban", {}).get("ids", {}):
            till_str = blacklist["ban"]["ids"][account_id].get("till")
            try:
                if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                    is_banned = True
            except Exception:
                pass
        # Check IP
        if not is_banned and ip and ip in blacklist.get("ban", {}).get("ips", {}):
            till_str = blacklist["ban"]["ips"][ip].get("till")
            try:
                if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                    is_banned = True
            except Exception:
                pass
        # Check Device UUID
        if not is_banned and device_id and device_id in blacklist.get("ban", {}).get("deviceids", {}):
            till_str = blacklist["ban"]["deviceids"][device_id].get("till")
            try:
                if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                    is_banned = True
            except Exception:
                pass

        # Check if muted
        is_muted = False
        if account_id in blacklist.get("muted-ids", {}):
            till_str = blacklist["muted-ids"][account_id].get("till")
            try:
                if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                    is_muted = True
            except Exception:
                pass

        # Check if kick vote disabled
        is_kick_vote_disabled = False
        if account_id in blacklist.get("kick-vote-disabled", {}):
            till_str = blacklist["kick-vote-disabled"][account_id].get("till")
            try:
                if current_time < datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S"):
                    is_kick_vote_disabled = True
            except Exception:
                pass

        p_dict["isBan"] = is_banned
        p_dict["isMuted"] = is_muted
        p_dict["canStartKickVote"] = not is_kick_vote_disabled
        try:
            from plugins.kickvote_manager import KickVoteManager
            p_dict["isKickVoteImmune"] = KickVoteManager.get().is_immune(account_id)
        except Exception:
            p_dict["isKickVoteImmune"] = False
        return p_dict
    return None


def update_player_profile(account_id: str, fields: dict):
    from repository.profiles import get_profile_by_acc_id, save_profile_single
    p = get_profile_by_acc_id(account_id)
    if p is not None:
        p_dict = dict(p)
        p_dict.update(fields)
        save_profile_single(account_id, p_dict)

        if "canStartKickVote" in fields:
            if fields["canStartKickVote"]:
                enable_kick_vote(account_id)
            else:
                disable_kick_vote(account_id, 30.0)

        if "isKickVoteImmune" in fields:
            set_kick_vote_immune(account_id, bool(fields["isKickVoteImmune"]))

        return True
    return False


# ==================== Replays Management ====================


def get_replays_dir() -> str:
    """Returns the absolute path to the replays directory."""
    try:
        import babase
        if hasattr(babase, "get_replays_dir"):
            p = babase.get_replays_dir()
            if p and os.path.exists(p):
                return os.path.abspath(p)
    except Exception:
        pass

    try:
        import _babase
        user_dir = _babase.env().get("python_directory_user")
        if user_dir:
            fallback = os.path.abspath(os.path.join(user_dir, "..", "replays"))
            if os.path.exists(fallback):
                return fallback
    except Exception:
        pass

    fallback = os.path.abspath("ba_root/replays")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def format_file_size(size_bytes: int) -> str:
    """Formats bytes into human readable format (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_replays_list(
    page: int = 1,
    per_page: int = 50,
    search: str = "",
    sort_by: str = "modified",
    sort_order: str = "desc",
) -> dict:
    """Lists all replays in the replay directory with metadata, sorting, search, and pagination."""
    replays_dir = get_replays_dir()
    if not os.path.exists(replays_dir):
        return {
            "replays": [],
            "total": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "directory": replays_dir,
        }

    search_lower = search.strip().lower()
    raw_replays = []

    for name in os.listdir(replays_dir):
        if not name.endswith(".brp"):
            continue
        if search_lower and search_lower not in name.lower():
            continue

        filepath = os.path.join(replays_dir, name)
        if not os.path.isfile(filepath):
            continue

        try:
            stat = os.stat(filepath)
            mtime = stat.st_mtime
            size = stat.st_size
            dt = datetime.fromtimestamp(mtime)
            raw_replays.append({
                "filename": name,
                "size_bytes": size,
                "size_formatted": format_file_size(size),
                "modified_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": mtime,
            })
        except Exception:
            continue

    # Sorting
    reverse = sort_order.lower() != "asc"
    if sort_by == "name":
        raw_replays.sort(key=lambda r: r["filename"].lower(), reverse=reverse)
    elif sort_by == "size":
        raw_replays.sort(key=lambda r: r["size_bytes"], reverse=reverse)
    else:  # modified / date
        raw_replays.sort(key=lambda r: r["timestamp"], reverse=reverse)

    total = len(raw_replays)
    per_page = max(1, min(per_page, 200))
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages)) if total > 0 else 1

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_replays = raw_replays[start_idx:end_idx]

    return {
        "replays": paginated_replays,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "directory": replays_dir,
    }


def get_replay_filepath(filename: str) -> str | None:
    """Validates filename and returns absolute path if it exists in the replays directory."""
    if not filename or not isinstance(filename, str):
        return None
    # Secure filename: avoid directory traversal
    clean_name = os.path.basename(filename.strip())
    if not clean_name.endswith(".brp"):
        clean_name += ".brp"

    replays_dir = get_replays_dir()
    filepath = os.path.abspath(os.path.join(replays_dir, clean_name))

    # Ensure path is strictly inside replays_dir
    if not filepath.startswith(replays_dir):
        return None

    if os.path.isfile(filepath):
        return filepath
    return None


def delete_replay(filename: str) -> bool:
    """Deletes a single replay file."""
    filepath = get_replay_filepath(filename)
    if filepath and os.path.isfile(filepath):
        try:
            os.remove(filepath)
            logger.log(f"Deleted replay file: {os.path.basename(filepath)}")
            return True
        except Exception as e:
            logger.log(f"Error deleting replay file {filename}: {e}")
            return False
    return False


def delete_replays_batch(filenames: list[str]) -> dict:
    """Deletes multiple replay files."""
    deleted = []
    failed = []
    for fn in filenames:
        if delete_replay(fn):
            deleted.append(fn)
        else:
            failed.append(fn)
    return {"deleted": deleted, "failed": failed}
