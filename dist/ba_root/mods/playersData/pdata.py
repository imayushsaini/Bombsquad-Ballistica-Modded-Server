"""Module to manage players data."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
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

if TYPE_CHECKING:
    pass


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
    profiles=get_profiles()
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
    if CacheData.profiles=={}:
        try:
            f=open(PLAYERS_DATA_PATH + "profiles.json","r")
            profiles = json.load(f)
            CacheData.profiles=profiles
            f.close()
        except:
            f=open(PLAYERS_DATA_PATH + "profiles.json.backup","r")
            profiles = json.load(f)
            CacheData.profiles=profiles
            f.close()
            return profiles
    else:
        return CacheData.profiles


def commit_profiles(data={}) -> None:
    """Commits the given profiles in the database.

    Parameters
    ----------
        profiles of all players
    """
    # with OpenJson(PLAYERS_DATA_PATH + "profiles.json") as profiles_file:
    #     profiles_file.dump(CacheData.profiles, indent=4)


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
            "isBan": False,
            "isMuted": False,
            "accountAge": account_age,
            "registerOn": time.time(),
            "canStartKickVote": True,
            "spamCount": 0,
            "lastSpam": time.time(),
            "totaltimeplayer": 0,
        }
    CacheData.profiles=profiles
    commit_profiles()

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
    serverdata.clients[account_id]["lastIP"] = _ba.get_client_ip(cid)

    device_id = _ba.get_client_public_device_uuid(cid)
    if(device_id==None):
        device_id = _ba.get_client_device_uuid(cid)
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
        CacheData.profiles=profiles
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
    CacheData.profiles=profiles
    commit_profiles()


def ban_player(account_id: str) -> None:
    """Bans the player.

    Parameters
    ----------
    account_id : str
        account id of the player to be banned
    """
    profiles = get_profiles()
    if account_id in profiles:
        profiles[account_id]["isBan"] = True
        CacheData.profiles=profiles
        _thread.start_new_thread(commit_profiles, (profiles,))


def mute(account_id: str) -> None:
    """Mutes the player.

    Parameters
    ----------
    account_id : str
        acccount id of the player to be muted
    """
    profiles = get_profiles()
    if account_id in profiles:
        profiles[account_id]["isMuted"] = True
        CacheData.profiles=profiles
        _thread.start_new_thread(commit_profiles, (profiles,))


def unmute(account_id: str) -> None:
    """Unmutes the player.

    Parameters
    ----------
    account_id : str
        acccount id of the player to be unmuted
    """
    profiles = get_profiles()
    if account_id in profiles:
        profiles[account_id]["isMuted"] = False
        CacheData.profiles=profiles
        _thread.start_new_thread(commit_profiles, (profiles,))


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
        CacheData.profiles=profiles
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
        except:
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
            f=open(PLAYERS_DATA_PATH + "custom.json","r")
            custom = json.load(f)
            f.close()
            CacheData.custom=custom
        except:
            f=open(PLAYERS_DATA_PATH + "custom.json.backup","r")
            custom = json.load(f)
            f.close()
            CacheData.custom=custom
    return CacheData.custom


def set_effect(effect: str, accout_id: str) -> None:
    """Sets the costum effect for the player.

    Parameters
    ----------
    effect : str
        effect to be added to the player
    accout_id : str
        account id of the client
    """
    custom = get_custom()
    custom["customeffects"][accout_id] = effect
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
    commit_c()


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
    commit_c()


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

import shutil
import copy
def dump_cache():
    if CacheData.profiles!={}:
        shutil.copyfile(PLAYERS_DATA_PATH + "profiles.json",PLAYERS_DATA_PATH + "profiles.json.backup")
        profiles= copy.deepcopy(CacheData.profiles)
        with open(PLAYERS_DATA_PATH + "profiles.json","w") as f:
            json.dump(profiles,f,indent=4)
    if CacheData.roles!={}:
        shutil.copyfile(PLAYERS_DATA_PATH + "roles.json",PLAYERS_DATA_PATH + "roles.json.backup")
        roles= copy.deepcopy(CacheData.roles)
        with open(PLAYERS_DATA_PATH + "roles.json", "w") as f:
            json.dump(roles, f, indent=4)
    if CacheData.custom!={}:
        shutil.copyfile(PLAYERS_DATA_PATH + "custom.json",PLAYERS_DATA_PATH + "custom.json.backup")
        custom= copy.deepcopy(CacheData.custom)
        with open(PLAYERS_DATA_PATH + "custom.json", "w") as f:
            json.dump(custom, f, indent=4)
    time.sleep(20)
    dump_cache()
