"""Module to manage players data."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
import shutil
import copy
from typing import TYPE_CHECKING

import time
import os
import _thread

from serverData import serverdata
from tools.file_handle import OpenJson
# pylint: disable=import-error
import _ba
import ba.internal
import json

from tools.ServerUpdate import checkSpammer
import setting
from datetime import datetime, timedelta
if TYPE_CHECKING:
    pass

settings = setting.get_settings_data()

PLAYERS_DATA_PATH = os.path.join(
    _ba.env()["python_directory_user"], "playersData" + os.sep
)


class CacheData:  # pylint: disable=too-few-public-methods
    """Stores the cache data."""

    roles: dict = {}
    data: dict = {}
    custom: dict = {}
    profiles: dict = {}
    whitelist: list[str] = []
    blacklist: dict = {}


def get_info(account_id: str) -> dict | None:
    """Returns the information about player.

    Parameters
    ----------
    account_id : str
        account_id of the client

    Returns
    -------
    dict | None
        information of client
    """
    profiles = get_profiles()
    if account_id in profiles:
        return profiles[account_id]
    return None


def get_profiles() -> dict:
    """Returns the profiles of all players.

    Returns
    -------
    dict
        profiles of the players
    """
    if CacheData.profiles == {}:
        try:
            if os.stat(PLAYERS_DATA_PATH+"profiles.json").st_size > 1000000:
                newpath = f'{PLAYERS_DATA_PATH}profiles-{str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}.json'
                shutil.copyfile(PLAYERS_DATA_PATH + "profiles.json", newpath)
                profiles = {"pb-sdf": {}}
                print("resetting profiles")
            else:
                f = open(PLAYERS_DATA_PATH + "profiles.json", "r")
                profiles = json.load(f)
                f.close()
                print("loading old proiles.json")
            CacheData.profiles = profiles

        except Exception as e:
            f = open(PLAYERS_DATA_PATH + "profiles.json.backup", "r")
            profiles = json.load(f)
            print(e)
            print("exception happened , falling back to profiles.json.backup")
            CacheData.profiles = profiles
            f.close()
            return profiles
    else:
        return CacheData.profiles


def get_profiles_archive_index():
    return [x for x in os.listdir(PLAYERS_DATA_PATH) if x.startswith("profiles")]


def get_old_profiles(filename):
    try:
        f = open(PLAYERS_DATA_PATH + filename, "r")
        profiles = json.load(f)
        return profiles
    except:
        return {}


def get_blacklist() -> dict:
    if CacheData.blacklist == {}:
        try:
            f = open(PLAYERS_DATA_PATH + "blacklist.json", "r")
            CacheData.blacklist = json.load(f)
        except:
            print('error opening blacklist json')
            return {
                "ban": {
                    "ids": {},
                    "ips": {},
                    "deviceids": {}
                },
                "muted-ids": {},
                "kick-vote-disabled": {}
            }

    return CacheData.blacklist


def update_blacklist():
    with open(PLAYERS_DATA_PATH + "blacklist.json", "w") as f:
        json.dump(CacheData.blacklist, f, indent=4)


def commit_profiles(data={}) -> None:
    """Commits the given profiles in the database.

    Parameters
    ----------
        profiles of all players
    """
    # with OpenJson(PLAYERS_DATA_PATH + "profiles.json") as profiles_file:
    #     profiles_file.dump(CacheData.profiles, indent=4)


def get_detailed_info(pbid):
    main_account = get_info(pbid)
    if main_account == None:
        return "No info"
    linked_accounts = ' '.join(main_account["display_string"])
    ip = main_account["lastIP"]
    deviceid = main_account["deviceUUID"]
    otheraccounts = ""
    dob = main_account["accountAge"]
    profiles = get_profiles()
    for key, value in profiles.items():
        if ("lastIP" in value and value["lastIP"] == ip) or ("deviceUUID" in value and value["deviceUUID"] == deviceid):
            otheraccounts += ' '.join(value["display_string"])
    return f"Accounts:{linked_accounts} \n other accounts {otheraccounts} \n created on {dob}"


def add_profile(
    account_id: str,
    display_string: str,
    current_name: str,
    account_age: int,
) -> None:
    """Adds the profile in database.

    Parameters
    ----------
    account_id : str
        account id of the client
    display_string : str
        display string of the client
    current_name : str
        name of the client
    account_age : int
        account_age of the account
    """
    profiles = get_profiles()
    profiles[account_id] = {
        "display_string": display_string,
        "profiles": [],
        "name": current_name,
        "accountAge": account_age,
        "registerOn": time.time(),
        "spamCount": 0,
        "lastSpam": time.time(),
        "totaltimeplayer": 0,
    }
    CacheData.profiles = profiles

    serverdata.clients[account_id] = profiles[account_id]
    serverdata.clients[account_id]["warnCount"] = 0
    serverdata.clients[account_id]["lastWarned"] = time.time()
    serverdata.clients[account_id]["verified"] = False
    serverdata.clients[account_id]["rejoincount"] = 1
    serverdata.clients[account_id]["lastJoin"] = time.time()
    cid = 113
    for ros in ba.internal.get_game_roster():
        if ros['account_id'] == account_id:
            cid = ros['client_id']
    ip = _ba.get_client_ip(cid)
    serverdata.clients[account_id]["lastIP"] = ip
    serverdata.recents.append(
        {"client_id": cid, "deviceId": display_string, "pbid": account_id})
    serverdata.recents = serverdata.recents[-20:]
    device_id = _ba.get_client_public_device_uuid(cid)
    if (device_id == None):
        device_id = _ba.get_client_device_uuid(cid)
    checkSpammer({'id': account_id, 'display': display_string,
                 'ip': ip, 'device': device_id})
    if device_id in get_blacklist()["ban"]["deviceids"] or account_id in get_blacklist()["ban"]["ids"]:
        ba.internal.disconnect_client(cid)
    serverdata.clients[account_id]["deviceUUID"] = device_id


def update_display_string(account_id: str, display_string: str) -> None:
    """Updates the display string of the account.

    Parameters
    ----------
    account_id : str
        account id of the client
    display_string : str
        new display string to be updated
    """
    profiles = get_profiles()
    if account_id in profiles:
        profiles[account_id]["display_string"] = display_string
        CacheData.profiles = profiles
        commit_profiles()


def update_profile(
    account_id: str,
    display_string: str = None,
    allprofiles: list[str] = None,
    name: str = None,
) -> None:
    """Updates the profile of client.

    Parameters
    ----------
    account_id : str
        account id of the client
    display_string : str, optional
        display string of the account, by default None
    allprofiles : list[str], optional
        all profiles of the client, by default None
    name : str, optional
        name to be updated, by default None
    """

    profiles = get_profiles()

    if profiles is None:
        return

    if account_id in profiles and display_string is not None:
        if display_string not in profiles[account_id]["display_string"]:
            profiles[account_id]["display_string"].append(display_string)

    if allprofiles is not None:
        for profile in allprofiles:
            if profile not in profiles[account_id]["profiles"]:
                profiles[account_id]["profiles"].append(profile)

    if name is not None:
        profiles[account_id]["name"] = name
    CacheData.profiles = profiles
    commit_profiles()


def ban_player(account_id: str,  duration_in_days: float, reason: str) -> None:
    """Bans the player.

    Parameters
    ----------
    account_id : str
        account id of the player to be banned
    """
    current_profiles = get_profiles()
    ip = ""
    device_id = ""
    if account_id in current_profiles:
        ip = current_profiles[account_id]["lastIP"]
        device_id = current_profiles[account_id]["deviceUUID"]

    ban_time = datetime.now() + timedelta(days=duration_in_days)

    CacheData.blacklist["ban"]["ips"][ip] = {"till": ban_time.strftime(
        "%Y-%m-%d %H:%M:%S"), "reason": f'linked with account {account_id}'}
    CacheData.blacklist["ban"]["ids"][account_id] = {
        "till": ban_time.strftime("%Y-%m-%d %H:%M:%S"), "reason": reason}
    CacheData.blacklist["ban"]["deviceids"][device_id] = {"till": ban_time.strftime(
        "%Y-%m-%d %H:%M:%S"), "reason": f'linked with account {account_id}'}
    _thread.start_new_thread(update_blacklist, ())


def unban_player(account_id):
    current_profiles = get_profiles()
    ip = ""
    device_id = ""
    if account_id in current_profiles:
        ip = current_profiles[account_id]["lastIP"]
        device_id = current_profiles[account_id]["deviceUUID"]

    CacheData.blacklist["ban"]["ips"].pop(ip, None)
    CacheData.blacklist["ban"]["deviceids"].pop(device_id, None)
    CacheData.blacklist["ban"]["ids"].pop(account_id, None)
    _thread.start_new_thread(update_blacklist, ())


def disable_kick_vote(account_id, duration, reason):
    ban_time = datetime.now() + timedelta(days=duration)
    CacheData.blacklist["kick-vote-disabled"][account_id] = {"till": ban_time.strftime(
        "%Y-%m-%d %H:%M:%S"), "reason": reason}
    _thread.start_new_thread(update_blacklist, ())


def enable_kick_vote(account_id):
    CacheData.blacklist["kick-vote-disabled"].pop(account_id, None)
    _thread.start_new_thread(update_blacklist, ())


def mute(account_id: str, duration_in_days: float, reason: str) -> None:
    """Mutes the player.

    Parameters
    ----------
    account_id : str
        acccount id of the player to be muted
    """
    ban_time = datetime.now() + timedelta(days=duration_in_days)

    CacheData.blacklist["muted-ids"][account_id] = {"till": ban_time.strftime(
        "%Y-%m-%d %H:%M:%S"), "reason": reason}
    _thread.start_new_thread(update_blacklist, ())


def unmute(account_id: str) -> None:
    """Unmutes the player.

    Parameters
    ----------
    account_id : str
        acccount id of the player to be unmuted
    """
    CacheData.blacklist["muted-ids"].pop(account_id, None)
    _thread.start_new_thread(update_blacklist, ())


def update_spam(account_id: str, spam_count: int, last_spam: float) -> None:
    """Updates the spam time and count.

    Parameters
    ----------
    account_id : str
        account id of the client
    spam_count : int
        spam count to be added
    last_spam : float
        last spam time
    """
    profiles = get_profiles()
    if account_id in profiles:
        profiles[account_id]["spamCount"] = spam_count
        profiles[account_id]["lastSpam"] = last_spam
        CacheData.profiles = profiles
        commit_profiles(profiles)


def commit_roles(data: dict) -> None:
    """Commits the roles in database.

    Parameters
    ----------
    data : dict
        data to be commited
    """
    if not data:
        return

    # with OpenJson(PLAYERS_DATA_PATH + "roles.json") as roles_file:
    #     roles_file.format(data)


def get_roles() -> dict:
    """Returns the roles.

    Returns
    -------
    dict
        roles
    """
    if CacheData.roles == {}:
        try:
            f = open(PLAYERS_DATA_PATH + "roles.json", "r")
            roles = json.load(f)
            f.close()
            CacheData.roles = roles
        except Exception as e:
            print(e)
            f = open(PLAYERS_DATA_PATH + "roles.json.backup", "r")
            roles = json.load(f)
            f.close()
            CacheData.roles = roles
    return CacheData.roles


def create_role(role: str) -> None:
    """Ceates the role.

    Parameters
    ----------
    role : str
        role to be created
    """
    roles = get_roles()

    if role in roles:
        return

    roles[role] = {
        "tag": role,
        "tagcolor": [1, 1, 1],
        "commands": [],
        "ids": [],
    }
    CacheData.roles = roles
    commit_roles(roles)


def add_player_role(role: str, account_id: str) -> None:
    """Adds the player to the role.

    Parameters
    ----------
    role : str
        role to be added
    account_id : str
        account id of the client
    """
    roles = get_roles()

    if role in roles:
        if account_id not in roles[role]["ids"]:
            roles[role]["ids"].append(account_id)
            CacheData.roles = roles
            commit_roles(roles)

    else:
        print("no role such")


def remove_player_role(role: str, account_id: str) -> str:
    """Removes the role from player.

    Parameters
    ----------
    role : str
        role to br removed
    account_id : str
        account id of the client

    Returns
    -------
    str
        status of the removing role
    """
    roles = get_roles()
    if role in roles:
        roles[role]["ids"].remove(account_id)
        CacheData.roles = roles
        commit_roles(roles)
        return "removed from " + role
    return "role not exists"


def add_command_role(role: str, command: str) -> str:
    """Adds the command to the role.

    Parameters
    ----------
    role : str
        role to add the command
    command : str
        command to be added

    Returns
    -------
    str
        status of the adding command
    """
    roles = get_roles()
    if role in roles:
        if command not in roles[role]["commands"]:
            roles[role]["commands"].append(command)
            CacheData.roles = roles
            commit_roles(roles)
            return "command added to " + role
    return "command not exists"


def remove_command_role(role: str, command: str) -> str:
    """Removes the command from the role.

    Parameters
    ----------
    role : str
        role to remove command from
    command : str
        command to be removed

    Returns
    -------
    str
        status of the removing command
    """
    roles = get_roles()
    if role in roles:
        if command in roles[role]["commands"]:
            roles[role]["commands"].remove(command)
            CacheData.roles = roles
            commit_roles(roles)
            return "command added to " + role
    return "command not exists"


def change_role_tag(role: str, tag: str) -> str:
    """Changes the tag of the role.

    Parameters
    ----------
    role : str
        role to chnage the tag
    tag : str
        tag to be added

    Returns
    -------
    str
        status of the adding tag
    """
    roles = get_roles()
    if role in roles:
        roles[role]["tag"] = tag
        CacheData.roles = roles
        commit_roles(roles)
        return "tag changed"
    return "role not exists"


def get_player_roles(account_id: str) -> list[str]:
    """Returns the avalibe roles of the account.

    Parameters
    ----------
    account_id : str
        account id of the client

    Returns
    -------
    list[str]
        list of the roles
    """

    roles = get_roles()
    have_roles = []
    for role in roles:
        if account_id in roles[role]["ids"]:
            have_roles.append(role)
    return have_roles


def get_custom() -> dict:
    """Returns the custom effects.

    Returns
    -------
    dict
        custom effects
    """
    if CacheData.custom == {}:
        try:
            f = open(PLAYERS_DATA_PATH + "custom.json", "r")
            custom = json.load(f)
            f.close()
            CacheData.custom = custom
        except:
            f = open(PLAYERS_DATA_PATH + "custom.json.backup", "r")
            custom = json.load(f)
            f.close()
            CacheData.custom = custom
        for account_id in custom["customeffects"]:
            custom["customeffects"][account_id] = [custom["customeffects"][account_id]] if type(
                custom["customeffects"][account_id]) is str else custom["customeffects"][account_id]

    return CacheData.custom


def set_effect(effect: str, account_id: str) -> None:
    """Sets the costum effect for the player.

    Parameters
    ----------
    effect : str
        effect to be added to the player
    accout_id : str
        account id of the client
    """
    custom = get_custom()
    if account_id in custom["customeffects"]:
        effects = [custom["customeffects"][account_id]] if type(
            custom["customeffects"][account_id]) is str else custom["customeffects"][account_id]
        effects.append(effect)
        custom["customeffects"][account_id] = effects
    else:
        custom["customeffects"][account_id] = [effect]
    CacheData.custom = custom
    commit_c()


def set_tag(tag: str, account_id: str) -> None:
    """Sets the custom tag to the player.

    Parameters
    ----------
    tag : str
        tag to be added to the player
    account_id : str
        account id of the client
    """
    custom = get_custom()
    custom["customtag"][account_id] = tag
    CacheData.custom = custom
    commit_c()


def update_roles(roles):
    CacheData.roles = roles


def get_custom_perks():
    return CacheData.custom


def update_custom_perks(custom):
    CacheData.custom = custom


def remove_effect(account_id: str) -> None:
    """Removes the effect from player.

    Parameters
    ----------
    account_id : str
        account id of the client
    """
    custom = get_custom()
    custom["customeffects"].pop(account_id)
    CacheData.custom = custom


def remove_tag(account_id: str) -> None:
    """Removes the tag from the player

    Parameters
    ----------
    account_id : str
        account id of the client
    """
    custom = get_custom()
    custom["customtag"].pop(account_id)
    CacheData.custom = custom


def commit_c():
    """Commits the custom data into the custom.json."""
    # with OpenJson(PLAYERS_DATA_PATH + "custom.json") as custom_file:
    #     custom_file.dump(CacheData.custom, indent=4)


def update_toppers(topper_list: list[str]) -> None:
    """Updates the topper list into top5 role.

    Parameters
    ----------
    topper_list : list[str]
        list of the topper players
    """
    roles = get_roles()
    if "top5" not in roles:
        create_role("top5")
    CacheData.roles["top5"]["ids"] = topper_list
    commit_roles(roles)


def load_white_list() -> None:
    """Loads the whitelist."""
    with OpenJson(PLAYERS_DATA_PATH + "whitelist.json") as whitelist_file:
        data = whitelist_file.load()
        for account_id in data:
            CacheData.whitelist.append(account_id)


def load_cache():
    """ to be called on server boot"""
    get_profiles()
    get_custom()
    get_roles()


def dump_cache():
    if CacheData.profiles != {}:
        shutil.copyfile(PLAYERS_DATA_PATH + "profiles.json",
                        PLAYERS_DATA_PATH + "profiles.json.backup")
        profiles = copy.deepcopy(CacheData.profiles)
        with open(PLAYERS_DATA_PATH + "profiles.json", "w") as f:
            json.dump(profiles, f, indent=4)
    if CacheData.roles != {}:
        shutil.copyfile(PLAYERS_DATA_PATH + "roles.json",
                        PLAYERS_DATA_PATH + "roles.json.backup")
        roles = copy.deepcopy(CacheData.roles)
        with open(PLAYERS_DATA_PATH + "roles.json", "w") as f:
            json.dump(roles, f, indent=4)
    if CacheData.custom != {}:
        shutil.copyfile(PLAYERS_DATA_PATH + "custom.json",
                        PLAYERS_DATA_PATH + "custom.json.backup")
        custom = copy.deepcopy(CacheData.custom)
        with open(PLAYERS_DATA_PATH + "custom.json", "w") as f:
            json.dump(custom, f, indent=4)
    time.sleep(60)
    dump_cache()
