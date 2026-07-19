# Released under the MIT License. See LICENSE for details.
"""Module to manage players data."""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import _thread
import copy
import json
import os
import shutil
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Dict, Any, Optional

import _bascenev1
import babase
import bascenev1 as bs
import setting
from serverdata import serverdata
from tools.server_update import checkSpammer
from repository import profiles as db_profiles

if TYPE_CHECKING:
    pass

settings = setting.get_settings_data()

PLAYERS_DATA_PATH = os.path.join(
    babase.env()["python_directory_user"], "playersdata" + os.sep
)
PROFILES_PATH = os.path.join(PLAYERS_DATA_PATH, "profiles.json")
PROFILES_BACKUP_PATH = os.path.join(PLAYERS_DATA_PATH, "profiles.json.backup")
BLACKLIST_PATH = os.path.join(PLAYERS_DATA_PATH, "blacklist.json")
ROLES_PATH = os.path.join(PLAYERS_DATA_PATH, "roles.json")
ROLES_BACKUP_PATH = os.path.join(PLAYERS_DATA_PATH, "roles.json.backup")
CUSTOM_PATH = os.path.join(PLAYERS_DATA_PATH, "custom.json")
CUSTOM_BACKUP_PATH = os.path.join(PLAYERS_DATA_PATH, "custom.json.backup")
WHITELIST_PATH = os.path.join(PLAYERS_DATA_PATH, "whitelist.json")


class CacheData:
    """Stores the cache data."""
    roles: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    custom: Dict[str, Any] = {}
    profiles: Any = None
    whitelist: List[str] = []
    blacklist: Dict[str, Any] = {}


def use_sqlite() -> bool:
    """Check if the SQLite database should be used instead of JSON files."""
    try:
        return setting.get_settings_data().get("useSqlite", False)
    except Exception:
        return False


def _load_json_file(path: str, backup_path: Optional[str] = None) -> Dict | List:
    """A utility function to load a json file with an optional backup."""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as f:
                return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading {path}: {e}")
        if backup_path and os.path.exists(backup_path):
            print(f"Falling back to {backup_path}")
            try:
                with open(backup_path, "r", encoding='utf-8') as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as backup_e:
                print(f"Error reading backup {backup_path}: {backup_e}")
    return {}


def _save_json_file(path: str, data: Any, backup_path: Optional[str] = None) -> None:
    """A utility function to save data to a json file with an optional backup."""
    if backup_path and os.path.exists(path):
        shutil.copyfile(path, backup_path)
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def get_info(account_id: str) -> Optional[Dict[str, Any]]:
    """Returns the information about a player."""
    return get_profiles().get(account_id)


def get_profiles() -> Dict[str, Any]:
    """Returns the profiles of all players."""
    if CacheData.profiles is None:
        if use_sqlite():
            CacheData.profiles = db_profiles.SQLiteLazyProfiles()
        else:
            try:
                if os.path.exists(PROFILES_PATH) and os.stat(PROFILES_PATH).st_size > 1000000:
                    newpath = os.path.join(
                        PLAYERS_DATA_PATH, f'profiles-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.json')
                    shutil.copyfile(PROFILES_PATH, newpath)
                    CacheData.profiles = {"pb-sdf": {}}
                    print("Resetting Profiles.")
                else:
                    CacheData.profiles = _load_json_file(
                        PROFILES_PATH, PROFILES_BACKUP_PATH) or {"pb-sdf": {}}
            except Exception as e:
                print(f"Exception in get_profiles: {e}")
                CacheData.profiles = _load_json_file(
                    PROFILES_BACKUP_PATH) or {"pb-sdf": {}}
    return CacheData.profiles


def get_profiles_archive_index() -> List[str]:
    """Returns a list of archived profile filenames."""
    return [x for x in os.listdir(PLAYERS_DATA_PATH) if x.startswith("profiles")]


def get_old_profiles(filename: str) -> Dict[str, Any]:
    """Loads profiles from an archived file."""
    return _load_json_file(os.path.join(PLAYERS_DATA_PATH, filename))


def get_blacklist() -> Dict[str, Any]:
    """Returns the blacklist."""
    if not CacheData.blacklist:
        if use_sqlite():
            try:
                CacheData.blacklist = db_profiles.load_blacklist()
            except Exception as e:
                print(f"Exception loading blacklist from DB: {e}")
                CacheData.blacklist = {
                    "ban": {"ids": {}, "ips": {}, "deviceids": {}},
                    "muted-ids": {},
                    "kick-vote-disabled": {}
                }
        else:
            default_blacklist = {
                "ban": {"ids": {}, "ips": {}, "deviceids": {}},
                "muted-ids": {},
                "kick-vote-disabled": {}
            }
            CacheData.blacklist = _load_json_file(
                BLACKLIST_PATH) or default_blacklist
    return CacheData.blacklist


def update_blacklist() -> None:
    """Saves the blacklist."""
    if use_sqlite():
        try:
            db_profiles.save_blacklist(CacheData.blacklist)
        except Exception as e:
            print(f"Exception updating blacklist in DB: {e}")
    else:
        _save_json_file(BLACKLIST_PATH, CacheData.blacklist)


def commit_profiles(data: Dict = {}) -> None:
    """Commits the given profiles in the database."""
    # This function is now a no-op as saving is handled by dump_cache/on-the-fly
    pass


def get_detailed_info(pbid: str) -> str:
    """Gets detailed information for a given player build id."""
    main_account = get_info(pbid)
    if not main_account:
        return "No info"

    linked_accounts = ' '.join(main_account.get("display_string", []))
    ip = main_account.get("lastIP", "N/A")
    deviceid = main_account.get("deviceUUID", "N/A")
    dob = main_account.get("accountAge", "N/A")

    other_accounts = set()
    profiles = get_profiles()
    for key, value in profiles.items():
        if ("lastIP" in value and value["lastIP"] == ip) or (
                "deviceUUID" in value and value["deviceUUID"] == deviceid):
            other_accounts.add(' '.join(value.get("display_string", [])))
    other_accounts_str = ' '.join(other_accounts)
    return f"Accounts:{linked_accounts} \n other accounts {other_accounts_str} \n created on {dob}"


def add_profile(
    account_id: str,
    display_string: str,
    current_name: str,
    account_creation_date: str,
) -> None:
    """Adds a new player profile."""
    profiles = get_profiles()
    profiles[account_id] = {
        "display_string": [display_string],
        "profiles": [],
        "name": current_name,
        "creationDate": account_creation_date,
        "registerOn": time.time(),
        "spamCount": 0,
        "lastSpam": time.time(),
        "totaltimeplayer": 0,
    }
    CacheData.profiles = profiles


def update_display_string(account_id: str, display_string: List[str]) -> None:
    """Updates the display string of the account."""
    profiles = get_profiles()
    if account_id in profiles:
        p = profiles[account_id]
        p["display_string"] = display_string
        profiles[account_id] = p


def update_profile(
    account_id: str,
    display_string: Optional[str] = None,
    allprofiles: Optional[List[str]] = None,
    name: Optional[str] = None,
) -> None:
    """Updates the profile of a client."""
    profiles = get_profiles()
    if not profiles or account_id not in profiles:
        return

    p = profiles[account_id]
    if display_string and display_string not in p.get("display_string", []):
        p["display_string"].append(display_string)

    if allprofiles:
        for profile in allprofiles:
            if profile not in p.get("profiles", []):
                p["profiles"].append(profile)

    if name:
        p["name"] = name

    profiles[account_id] = p


def _ban_unban_helper(account_id: str, ban: bool, duration_in_days: float = 0, reason: str = ""):
    """Helper function to ban or unban a player."""
    profiles = get_profiles()
    ip = profiles.get(account_id, {}).get("lastIP")
    device_id = profiles.get(account_id, {}).get("deviceUUID")

    if not (ip and device_id):
        for account in reversed(serverdata.recents):
            if account.get("pbid") == account_id:
                ip = account.get("ip")
                device_id = account.get("device_uuid")
                break

    if ban:
        ban_time = (datetime.now() + timedelta(days=duration_in_days)
                    ).strftime("%Y-%m-%d %H:%M:%S")
        ban_entry = {"till": ban_time, "reason": reason}
        linked_reason = f'linked with account {account_id}'
        if ip:
            CacheData.blacklist["ban"]["ips"][ip] = {
                "till": ban_time, "reason": linked_reason}
        if device_id:
            CacheData.blacklist["ban"]["deviceids"][device_id] = {
                "till": ban_time, "reason": linked_reason}
        CacheData.blacklist["ban"]["ids"][account_id] = ban_entry
    else:
        if ip:
            CacheData.blacklist["ban"]["ips"].pop(ip, None)
        if device_id:
            CacheData.blacklist["ban"]["deviceids"].pop(device_id, None)
        CacheData.blacklist["ban"]["ids"].pop(account_id, None)

    _thread.start_new_thread(update_blacklist, ())


def ban_player(account_id: str, duration_in_days: float, reason: str) -> None:
    """Bans a player."""
    _ban_unban_helper(account_id, True, duration_in_days, reason)


def unban_player(account_id: str):
    """Unbans a player."""
    _ban_unban_helper(account_id, False)


def disable_kick_vote(account_id: str, duration: float, reason: str):
    """Disables kick voting for a player."""
    ban_time = (datetime.now() + timedelta(days=duration)
                ).strftime("%Y-%m-%d %H:%M:%S")
    CacheData.blacklist["kick-vote-disabled"][account_id] = {
        "till": ban_time, "reason": reason}
    _thread.start_new_thread(update_blacklist, ())


def enable_kick_vote(account_id: str):
    """Enables kick voting for a player."""
    CacheData.blacklist["kick-vote-disabled"].pop(account_id, None)
    _thread.start_new_thread(update_blacklist, ())


def mute(account_id: str, duration_in_days: float, reason: str) -> None:
    """Mutes a player."""
    ban_time = (datetime.now() + timedelta(days=duration_in_days)
                ).strftime("%Y-%m-%d %H:%M:%S")
    CacheData.blacklist["muted-ids"][account_id] = {
        "till": ban_time, "reason": reason}
    _thread.start_new_thread(update_blacklist, ())


def unmute(account_id: str) -> None:
    """Unmutes a player."""
    CacheData.blacklist["muted-ids"].pop(account_id, None)
    _thread.start_new_thread(update_blacklist, ())


def update_spam(account_id: str, spam_count: int, last_spam: float) -> None:
    """Updates the spam time and count for a player."""
    profiles = get_profiles()
    if account_id in profiles:
        p = profiles[account_id]
        p["spamCount"] = spam_count
        p["lastSpam"] = last_spam
        profiles[account_id] = p


def commit_roles(data: Dict) -> None:
    """Commits the roles in the database."""
    # This function is now a no-op as saving is handled by dump_cache
    pass


def get_roles() -> Dict[str, Any]:
    """Returns all roles."""
    if not CacheData.roles:
        if use_sqlite():
            try:
                CacheData.roles = db_profiles.load_roles()
            except Exception as e:
                print(f"Exception loading roles from DB: {e}")
                CacheData.roles = {}
        else:
            CacheData.roles = _load_json_file(ROLES_PATH, ROLES_BACKUP_PATH)
    return CacheData.roles


def create_role(role: str) -> None:
    """Creates a new role."""
    roles = get_roles()
    if role not in roles:
        roles[role] = {"tag": role, "tagcolor": [
            1, 1, 1], "commands": [], "ids": []}
        CacheData.roles = roles


def add_player_role(role: str, account_id: str) -> None:
    """Adds a player to a role."""
    roles = get_roles()
    if role in roles and account_id not in roles[role]["ids"]:
        roles[role]["ids"].append(account_id)
        CacheData.roles = roles
    else:
        print(f'Role named {role} does not exist or player already in role.')


def remove_player_role(role: str, account_id: str) -> str:
    """Removes a role from a player."""
    roles = get_roles()
    if role in roles and account_id in roles[role]["ids"]:
        roles[role]["ids"].remove(account_id)
        CacheData.roles = roles
        return f"Removed from {role}"
    return "Role not found or player not in role."


def add_command_role(role: str, command: str) -> str:
    """Adds a command to a role."""
    roles = get_roles()
    if role in roles and command not in roles[role]["commands"]:
        roles[role]["commands"].append(command)
        CacheData.roles = roles
        return f"Command added to {role}"
    return "Role not found or command already in role."


def remove_command_role(role: str, command: str) -> str:
    """Removes a command from a role."""
    roles = get_roles()
    if role in roles and command in roles[role]["commands"]:
        roles[role]["commands"].remove(command)
        CacheData.roles = roles
        return f"Command removed from {role}"
    return "Role not found or command not in role."


def change_role_tag(role: str, tag: str) -> str:
    """Changes the tag of a role."""
    roles = get_roles()
    if role in roles:
        roles[role]["tag"] = tag
        CacheData.roles = roles
        return "Tag changed"
    return "Role not found"


def get_player_roles(account_id: str) -> List[str]:
    """Returns the roles of a player."""
    return [role for role, data in get_roles().items() if account_id in data.get("ids", [])]


def get_custom() -> Dict[str, Any]:
    """Returns custom effects and tags."""
    if not CacheData.custom:
        if use_sqlite():
            try:
                CacheData.custom = db_profiles.load_custom()
            except Exception as e:
                print(f"Exception loading custom perks from DB: {e}")
                CacheData.custom = {"customtag": {}, "customeffects": {}}
        else:
            custom_data = _load_json_file(CUSTOM_PATH, CUSTOM_BACKUP_PATH)
            if "customeffects" in custom_data:
                for acc_id, effects in custom_data["customeffects"].items():
                    if isinstance(effects, str):
                        custom_data["customeffects"][acc_id] = [effects]
            CacheData.custom = custom_data
    return CacheData.custom


def set_effect(effect: str, account_id: str) -> None:
    """Sets a custom effect for a player."""
    custom = get_custom()
    if "customeffects" not in custom:
        custom["customeffects"] = {}

    effects = custom["customeffects"].get(account_id, [])
    if isinstance(effects, str):
        effects = [effects]

    effects.append(effect)
    custom["customeffects"][account_id] = effects
    CacheData.custom = custom


def set_tag(tag: str, account_id: str) -> None:
    """Sets a custom tag for a player."""
    custom = get_custom()
    if "customtag" not in custom:
        custom["customtag"] = {}
    custom["customtag"][account_id] = tag
    CacheData.custom = custom


def update_roles(roles: Dict):
    """Updates the cached roles."""
    CacheData.roles = roles


def get_custom_perks() -> Dict:
    """Returns all custom perks."""
    return CacheData.custom


def update_custom_perks(custom: Dict):
    """Updates the cached custom perks."""
    CacheData.custom = custom


def remove_effect(account_id: str) -> None:
    """Removes effects from a player."""
    custom = get_custom()
    if "customeffects" in custom:
        custom["customeffects"].pop(account_id, None)
        CacheData.custom = custom


def remove_tag(account_id: str) -> None:
    """Removes a tag from a player."""
    custom = get_custom()
    if "customtag" in custom:
        custom["customtag"].pop(account_id, None)
        CacheData.custom = custom


def commit_c():
    """Commits the custom data into the custom.json."""
    # This function is now a no-op as saving is handled by dump_cache
    pass


def update_toppers(topper_list: List[str]) -> None:
    """Updates the topper list into the top5 role."""
    roles = get_roles()
    if "top5" not in roles:
        create_role("top5")
    CacheData.roles["top5"]["ids"] = topper_list


def load_white_list() -> None:
    """Loads the whitelist."""
    if use_sqlite():
        try:
            CacheData.whitelist = db_profiles.load_whitelist()
        except Exception as e:
            print(f"Exception loading whitelist from DB: {e}")
            CacheData.whitelist = []
    else:
        data = _load_json_file(WHITELIST_PATH)
        if isinstance(data, list):
            CacheData.whitelist = data
        elif isinstance(data, dict):
            CacheData.whitelist = list(data.keys())


def load_cache():
    """To be called on server boot to load all data into cache."""
    if use_sqlite():
        # Check if database is empty, if so perform one-time migration from JSON files
        try:
            from repository.db import run_query
            rows = run_query("SELECT count(*) FROM profiles", fetch=True)
            db_empty = (rows[0][0] == 0) if rows else True
            if db_empty:
                print("SQLite database is empty. Migrating existing JSON data to SQLite...")

                # Migrate profiles
                json_profiles = _load_json_file(PROFILES_PATH, PROFILES_BACKUP_PATH)
                if json_profiles:
                    db_profiles.save_all_profiles(json_profiles)
                    print(f"Migrated {len(json_profiles)} profiles to SQLite")

                # Migrate roles
                json_roles = _load_json_file(ROLES_PATH, ROLES_BACKUP_PATH)
                if json_roles:
                    db_profiles.save_roles(json_roles)
                    print("Migrated roles to SQLite")

                # Migrate custom perks
                json_custom = _load_json_file(CUSTOM_PATH, CUSTOM_BACKUP_PATH)
                if json_custom:
                    if "customeffects" in json_custom:
                        for acc_id, effects in json_custom["customeffects"].items():
                            if isinstance(effects, str):
                                json_custom["customeffects"][acc_id] = [effects]
                    db_profiles.save_custom(json_custom)
                    print("Migrated custom tags/effects to SQLite")

                # Migrate blacklist
                json_blacklist = _load_json_file(BLACKLIST_PATH)
                if json_blacklist:
                    db_profiles.save_blacklist(json_blacklist)
                    print("Migrated blacklist to SQLite")

                # Migrate whitelist
                json_whitelist = _load_json_file(WHITELIST_PATH)
                if json_whitelist:
                    w_list = []
                    if isinstance(json_whitelist, list):
                        w_list = json_whitelist
                    elif isinstance(json_whitelist, dict):
                        w_list = list(json_whitelist.keys())
                    db_profiles.save_whitelist(w_list)
                    print("Migrated whitelist to SQLite")

                print("JSON to SQLite migration completed successfully!")
        except Exception as e:
            print(f"Failed to migrate JSON to SQLite: {e}")

        CacheData.profiles = db_profiles.SQLiteLazyProfiles()
    else:
        get_profiles()

    get_custom()
    get_roles()
    load_white_list()
    get_blacklist()


def dump_cache():
    """Periodically saves all cached data to disk or database."""
    if use_sqlite():
        try:
            # We avoid taking the whole profiles database to in-memory CacheData,
            # and do not do periodic dump of profiles in SQLite since it's already updated on the fly.
            if CacheData.roles:
                db_profiles.save_roles(copy.deepcopy(CacheData.roles))
            if CacheData.custom:
                db_profiles.save_custom(copy.deepcopy(CacheData.custom))
            if CacheData.whitelist:
                db_profiles.save_whitelist(copy.deepcopy(CacheData.whitelist))
        except Exception as e:
            print(f"Exception dumping cache to DB: {e}")
    else:
        if CacheData.profiles:
            _save_json_file(PROFILES_PATH, copy.deepcopy(
                CacheData.profiles), PROFILES_BACKUP_PATH)
        if CacheData.roles:
            _save_json_file(ROLES_PATH, copy.deepcopy(
                CacheData.roles), ROLES_BACKUP_PATH)
        if CacheData.custom:
            _save_json_file(CUSTOM_PATH, copy.deepcopy(
                CacheData.custom), CUSTOM_BACKUP_PATH)

    # Schedule the next dump
    time.sleep(60)
    dump_cache()
