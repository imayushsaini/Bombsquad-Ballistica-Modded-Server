# Released under the MIT License. See LICENSE for details.
from __future__ import annotations

import _thread
import json
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from efro.dataclassio import dataclass_from_json
from bacommon.restapi.v1.accounts import AccountResponse

import _babase
import _bascenev1
import babase
import bascenev1 as bs

from features import profanity
from playersdata import pdata
from repository import profiles
from serverdata import serverdata
from tools import logger
import setting

# Get the blacklist from pdata
blacklist = pdata.get_blacklist()

# Get settings
settings = setting.get_settings_data()

# Track IP join statistics for rate limiting/spam protection
ipjoin: Dict[str, IPJoin] = {}


@dataclass
class PlayerData:
    """A dataclass to hold player-related data."""
    pbid: str
    player_data: Dict[str, Any]
    ip: str
    device_id: str
    last_join: float = field(default_factory=time.time)
    join_count: int = 0
    client_id: int = -1
    display_string: str = ""


@dataclass
class IPJoin:
    """A dataclass to hold IP join information."""
    last_join: float = field(default_factory=time.time)
    count: int = 0


class ServerCheck:
    """A class to check for new players and handle their joining process."""

    def __init__(self) -> None:
        self.players: List[str] = []
        self.ip_client_map: Dict[str, List[int]] = {}
        self.device_client_map: Dict[str, List[int]] = {}
        self.ip_join: Dict[str, IPJoin] = {}
        self.timer = bs.AppTimer(1, babase.CallStrict(self.check), repeat=True)

    def check(self) -> None:
        """
        Checks for new players, handles their joining process, and performs various checks.
        """
        new_players: List[str] = []
        self.ip_client_map.clear()
        self.device_client_map.clear()

        for ros in bs.get_game_roster():
            client_id = ros["client_id"]
            if client_id == -1:
                continue

            ip = _bascenev1.get_client_ip(client_id)
            device_id = self._get_device_id(client_id)
            account_id = ros["account_id"]

            if not self._handle_connection_limits(ip, device_id, client_id, account_id):
                continue

            new_players.append(account_id)

            if account_id not in self.players:
                self._handle_new_player(ros, ip, device_id)

        self.players = new_players

    def _get_device_id(self, client_id: int) -> str:
        """
        Returns the public or private device UUID for a given client_id.
        """
        device_id = _bascenev1.get_client_public_device_uuid(client_id)
        if device_id is None:
            device_id = _bascenev1.get_client_device_uuid(client_id)
        return device_id

    def _handle_connection_limits(self, ip: str, device_id: str, client_id: int, account_id: str) -> bool:
        """
        Handles connection limits per IP and device.
        """
        if not self._check_limit(self.device_client_map, device_id, client_id, "device", account_id):
            return False
        if not self._check_limit(self.ip_client_map, ip, client_id, "IP", account_id):
            return False
        return True

    def _check_limit(self, client_map: Dict[str, List[int]], key: str, client_id: int, limit_type: str, account_id: str) -> bool:
        """
        Checks if the connection limit for a given type (IP or device) has been reached.
        """
        if key not in client_map:
            client_map[key] = [client_id]
        else:
            client_map[key].append(client_id)
            if len(client_map[key]) >= settings['maxAccountPerIP']:
                self._disconnect_player(
                    client_id,
                    f"Only {settings['maxAccountPerIP']} players per {limit_type} allowed, disconnecting this device.",
                    f'Player disconnected, reached max players per {limit_type} || {account_id}',
                )
                return False
        return True

    def _disconnect_player(self, client_id: int, message: str, log_message: str) -> None:
        """
        Disconnects a player with a given message and logs the disconnection.
        """
        kick_client(client_id, message, log_message, use_chat=True, chat_func=bs.chatmessage)

    def _handle_new_player(self, ros: Dict[str, Any], ip: str, device_id: str) -> None:
        """
        Handles the joining process for a new player.
        """
        account_id = ros["account_id"]
        display_string = ros["display_string"]
        client_id = ros["client_id"]

        censored_name = profanity.censor(display_string)
        if censored_name != display_string:
            self._disconnect_player(
                client_id,
                "Profanity in ID, change your ID and join back",
                f'{display_string} || {account_id} || kicked by profanity check',
            )
            return

        if settings["whitelist"] and account_id not in pdata.CacheData.whitelist:
            self._disconnect_player(
                client_id,
                "Not in whitelist, contact admin",
                f'{display_string} || {account_id} | kicked > not in whitelist',
            )
            return

        logger.log(f'{display_string}  || {account_id} || joined server', "playerjoin")
        logger.log(f'{account_id} {ip} {device_id}')

        on_player_join_server(account_id, ip, device_id)


def get_roster_by_pb_id(pb_id: str) -> Optional[Dict[str, Any]]:
    """Returns the game roster entry for the given player ID if currently connected."""
    for ros in bs.get_game_roster():
        if ros.get("account_id") == pb_id:
            return ros
    return None


def kick_client(
    client_id: int,
    message: str,
    log_message: Optional[str] = None,
    log_category: Optional[str] = None,
    use_chat: bool = False,
    chat_func: Optional[Callable] = None,
    color: Optional[tuple] = None,
) -> None:
    """Disconnects a client with a message, log, and optional display parameters."""
    if use_chat:
        fn = chat_func or bs.chatmessage
        fn(message, clients=[client_id])
    else:
        if color is not None:
            bs.broadcastmessage(message, color=color, transient=True, clients=[client_id])
        else:
            bs.broadcastmessage(message, transient=True, clients=[client_id])

    bs.disconnect_client(client_id)

    if log_message:
        if log_category:
            logger.log(log_message, log_category)
        else:
            logger.log(log_message)


def kick_by_pb_id(pb_id: str, msg: str) -> None:
    """Kicks a player by their account/PB ID."""
    ros = get_roster_by_pb_id(pb_id)
    if ros is not None and ros.get("client_id", -1) != -1:
        kick_client(ros["client_id"], msg)


def notify_web_player_joined(pb_id: str) -> None:
    """Helper to notify the web service about a player joining if enabled."""
    if settings.get("ballistica_web", {}).get("enable"):
        from . import notification_manager
        notification_manager.player_joined(pb_id)


def _fetch_and_verify_device_accounts(pb_id: str, display_string: str) -> None:
    """Helper to fetch device accounts and start verification callback."""
    thread = FetchThread(
        target=get_device_accounts,
        callback=save_ids,
        pb_id=pb_id,
        display_string=display_string,
    )
    thread.start()


def _add_to_recents(client_id: int, display_string: str, pbid: str, ip: str, device_id: str) -> None:
    """Helper to record the recently joined player."""
    serverdata.recents.append(
        {
            "client_id": client_id,
            "deviceId": display_string,
            "pbid": pbid,
            "ip": ip,
            "device_uuid": device_id,
        }
    )
    serverdata.recents = serverdata.recents[-20:]


def _setup_client_data_structures(pbid: str, player_data: Dict[str, Any], ip: str, device_id: str) -> None:
    """Helper to initialize server cache metadata for the player."""
    current_time = datetime.now()
    if pbid not in serverdata.clients:
        serverdata.clients[pbid] = player_data
        serverdata.clients[pbid]["warnCount"] = 0
        serverdata.clients[pbid]["lastWarned"] = time.time()
        serverdata.clients[pbid]["verified"] = False
        serverdata.clients[pbid]["rejoincount"] = 1
        serverdata.clients[pbid]["lastJoin"] = time.time()
        
        # Check kick-vote disabled from blacklist
        kv_blacklist = blacklist.get("kick-vote-disabled", {})
        if pbid in kv_blacklist:
            try:
                till_time = datetime.strptime(kv_blacklist[pbid]["till"], "%Y-%m-%d %H:%M:%S")
                if current_time < till_time:
                    _bascenev1.disable_kickvote(pbid)
            except (ValueError, TypeError):
                pass

    serverdata.clients[pbid]["lastIP"] = ip
    serverdata.clients[pbid]["deviceUUID"] = device_id


def _check_ip_join_rate_limit(ip: str, pbid: str, client_id: int) -> bool:
    """Checks and updates IP join rate limits. Returns True if allowed, False if kicked."""
    global ipjoin
    now = time.time()

    if ip in ipjoin:
        ip_info = ipjoin[ip]
        if now - ip_info.last_join < 15:
            ip_info.count += 1
            if ip_info.count > 2:
                kick_client(
                    client_id,
                    "Joining too fast, slow down dude",
                    log_message=f"{pbid} || kicked for joining too fast",
                    color=(1, 0, 1),
                )
                _thread.start_new_thread(report_spam, (pbid,))
                return False
        else:
            ip_info.count = 0
        ip_info.last_join = now
    else:
        ipjoin[ip] = IPJoin(last_join=now, count=0)

    return True


def on_player_join_server(pbid: str, ip: str, device_id: str) -> None:
    """
    Stage 1: Ingress / Initial Checks.
    This is called when a player connects.
    """
    ros = get_roster_by_pb_id(pbid)
    if ros is None or ros.get("client_id", -1) == -1:
        return

    client_id = ros["client_id"]
    display_string = ros["display_string"]

    # 1. IP rate limiting check
    if not _check_ip_join_rate_limit(ip, pbid, client_id):
        return

    # 2. Ban checking (applies to all players, new and existing)
    if check_ban(ip, device_id, pbid):
        kick_client(
            client_id,
            "sad, your account is flagged contact server owner for unban",
            use_chat=True,
            chat_func=_bascenev1.chatmessage,
        )
        return

    # 3. Transition to database loading or verification
    if pbid in serverdata.clients:
        # Fast path: Already cached in memory, proceed directly to Stage 3
        _setup_and_verify_player(pbid, serverdata.clients[pbid], ip, device_id, client_id, display_string, is_new=False)
    else:
        # Slow path: Not cached, load profile from database in background
        LoadProfile(pbid, ip, device_id, client_id, display_string).start()


def _on_profile_loaded(pbid: str, player_data: Optional[Dict[str, Any]], ip: str, device_id: str, client_id: int, display_string: str) -> None:
    """
    Stage 2: Database Load Result.
    Processes the loaded profile, routing to creation/API fetch if missing.
    """
    ros = get_roster_by_pb_id(pbid)
    if ros is None or ros.get("client_id", -1) == -1:
        return

    if player_data is not None:
        # Profile exists in database, proceed directly to Stage 3
        _setup_and_verify_player(pbid, player_data, ip, device_id, client_id, display_string, is_new=False)
    else:
        # Profile doesn't exist, proceed to Stage 2b (Account creation date fetch)
        _fetch_and_register_new_player(pbid, ip, device_id, client_id, display_string)


def _fetch_and_register_new_player(pbid: str, ip: str, device_id: str, client_id: int, display_string: str) -> None:
    """
    Stage 2b: API creation date fetch & database registration.
    """
    # Print first time welcome message
    bs.broadcastmessage(
        settings["firstTimeJoinMsg"],
        color=(0.6, 0.8, 0.6),
        transient=True,
        clients=[client_id],
    )
    notify_web_player_joined(pbid)

    # Start API call to fetch registration date
    def api_callback(account_creation_date: Optional[str], pb_id: str, display_name: str) -> None:
        if not account_creation_date:
            return
        
        # Register new profile in database
        register_new_profile(pb_id, display_name, account_creation_date)
        
        # Load the newly created profile data
        new_player_data = pdata.get_info(pb_id)
        if new_player_data is not None:
            # Profile successfully registered, proceed to Stage 3
            _setup_and_verify_player(pb_id, new_player_data, ip, device_id, client_id, display_name, is_new=True)

    thread = FetchThread(
        target=get_account_creation_date,
        callback=api_callback,
        pb_id=pbid,
        display_string=display_string,
    )
    thread.start()


def _setup_and_verify_player(pbid: str, player_data: Dict[str, Any], ip: str, device_id: str, client_id: int, display_string: str, is_new: bool = False) -> None:
    """
    Stage 3: Verification, Age Checks, Caching & Welcoming.
    Runs for all players (cached, uncached existing, and brand-new after creation).
    """
    # 1. Update recents & server client caching
    _add_to_recents(client_id, display_string, pbid, ip, device_id)
    _setup_client_data_structures(pbid, player_data, ip, device_id)

    # 2. Enforce the minimum account age requirement
    if get_account_age(player_data.get("creationDate", "")) < settings["minAgeToJoinInHours"]:
        kick_client(
            client_id,
            "New Accounts not allowed here, come back later",
            log_message=f"{pbid} | kicked > reason:Banned account",
            color=(1, 0, 0),
        )
        return

    # 3. Verify display name authenticity
    verify_account(pbid, player_data)

    logger.log(f'{pbid} ip: {ip}, Device id: {device_id}')

    # 4. Display welcome message for returning/existing players
    if not is_new:
        bs.broadcastmessage(
            settings["regularWelcomeMsg"] + " " + display_string,
            color=(0.6, 0.8, 0.6),
            transient=True,
            clients=[client_id],
        )
        notify_web_player_joined(pbid)


# Keep compatibility aliases for legacy external calls (if any exist)
def handle_existing_player(pbid: str, player_data: Dict[str, Any], ip: str, device_id: str, client_id: int, display_string: str) -> None:
    _setup_and_verify_player(pbid, player_data, ip, device_id, client_id, display_string, is_new=False)


def handle_new_player_data(pbid: str, display_string: str, client_id: int) -> None:
    # Retrieve connection info to pass along
    ros = get_roster_by_pb_id(pbid)
    if ros is not None:
        ip = _bascenev1.get_client_ip(client_id)
        device_id = _bascenev1.get_client_public_device_uuid(client_id) or _bascenev1.get_client_device_uuid(client_id)
        _fetch_and_register_new_player(pbid, ip, device_id, client_id, display_string)


def check_ban(ip: str, device_id: str, pbid: str, log: bool = True) -> bool | str:
    """
    Checks if a player is banned based on their IP, device ID, or player ID.
    """
    current_time = datetime.now()

    def check_ban_list(ban_list: Dict[str, Any], key: str, ban_type: str) -> Optional[str]:
        if key in ban_list:
            try:
                till_time = datetime.strptime(ban_list[key]["till"], "%Y-%m-%d %H:%M:%S")
                if current_time < till_time:
                    return f'reason: matched {ban_type} | {ban_list[key]["reason"]}, Till: {ban_list[key]["till"]}'
            except (ValueError, TypeError):
                pass
        return None

    ban_msg = check_ban_list(blacklist["ban"]["ips"], ip, "IP")
    if ban_msg is None:
        ban_msg = check_ban_list(
            blacklist["ban"]["deviceids"], device_id, "deviceId")
    if ban_msg is None:
        ban_msg = check_ban_list(blacklist["ban"]["ids"], pbid, "ID")

    if ban_msg:
        if log:
            logger.log(f'{pbid} | kicked > {ban_msg}')
            return True
        return ban_msg
    return False


def verify_account(pb_id: str, p_data: Dict[str, Any]) -> None:
    """
    Verifies a player's account by checking their display string against their device accounts.
    """
    if _bascenev1.protocol_version() > 35:
        if pb_id in serverdata.clients:
            serverdata.clients[pb_id]["verified"] = True
        return

    ros = get_roster_by_pb_id(pb_id)
    if ros is None:
        return
    display_string = ros["display_string"]

    if display_string not in p_data.get('display_string', []):
        _fetch_and_verify_device_accounts(pb_id, display_string)
    else:
        if pb_id in serverdata.clients:
            serverdata.clients[pb_id]["verified"] = True


def _make_request_safe(request: Callable, retries: int = 2, raise_err: bool = True) -> Any:
    """
    A wrapper to make a request safely with retries.
    """
    try:
        return request()
    except Exception:
        if retries > 0:
            time.sleep(1)
            return _make_request_safe(request, retries=retries - 1, raise_err=raise_err)
        if raise_err:
            raise


def get_account_creation_date(pb_id: str) -> Optional[str]:
    """
    Gets the account creation date for a given player ID.
    """
    if _bascenev1.protocol_version() > 35:
        try:
            req = urllib.request.Request(
                f"https://www.ballistica.net/api/v1/accounts/{pb_id}",
                headers={
                    "Authorization": f"Bearer {settings['accountApiToken']}"
                },
            )
            with urllib.request.urlopen(req) as response:
                response_json_str = response.read().decode('utf-8')
                account = json.loads(response_json_str)

                if account:
                    account = dataclass_from_json(
                        AccountResponse, response_json_str)
                    return str(account.create_time)
        except (urllib.error.URLError, ValueError) as e:
            logger.log(
                f"Error getting account creation date for {pb_id}: {e}", "error")
            return None
    else:
        account_creation_url = f"http://bombsquadgame.com/accountquery?id={pb_id}"
        try:
            with urllib.request.urlopen(account_creation_url) as response:
                account_creation = json.loads(response.read())
                creation_time = datetime.strptime(
                    "/".join(map(str, account_creation["created"])), "%Y/%m/%d/%H/%M/%S")
                # Convert to IST
                creation_time += timedelta(hours=5, minutes=30)
                return str(creation_time)
        except (urllib.error.URLError, ValueError) as e:
            logger.log(
                f"Error getting account creation date for {pb_id}: {e}", "error")
            return None
    return None


def get_device_accounts(pb_id: str) -> List[str]:
    """
    Gets the device accounts associated with a given player ID.
    """
    url = f"http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID={pb_id}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())["accountDisplayStrings"]
    except (urllib.error.URLError, ValueError) as e:
        logger.log(f"Error getting device accounts for {pb_id}: {e}", "error")
        return ['???']


class LoadProfile(threading.Thread):
    """
    A thread to load a player's profile from pdata.
    """

    def __init__(self, pb_id: str, ip: str, device_id: str, client_id: int, display_string: str) -> None:
        super().__init__()
        self.pbid = pb_id
        self.ip = ip
        self.device_id = device_id
        self.client_id = client_id
        self.display_string = display_string

    def run(self) -> None:
        player_data = pdata.get_info(self.pbid)
        _babase.pushcall(
            babase.CallPartial(_on_profile_loaded, self.pbid, player_data, self.ip, self.device_id, self.client_id, self.display_string),
            from_other_thread=True,
        )


class FetchThread(threading.Thread):
    """
    A thread to fetch data from a URL and execute a callback with the result.
    """

    def __init__(self, target: Callable, callback: Optional[Callable] = None, pb_id: str = "ji", display_string: str = "XXX") -> None:
        super().__init__(target=self.target_with_callback, args=(pb_id, display_string))
        self.callback = callback
        self.method = target

    def target_with_callback(self, pb_id: str, display_string: str) -> None:
        data = self.method(pb_id)
        if self.callback is not None:
            _babase.pushcall(
                babase.CallPartial(self.callback, data, pb_id, display_string),
                from_other_thread=True,
            )


def my_acc_age(pb_id: str) -> Optional[str]:
    return get_account_creation_date(pb_id)


def register_new_profile(pb_id: str, display_string: str, creation_date: str) -> None:
    """Registers a new profile in the database/player data cache."""
    pdata.add_profile(pb_id, display_string, display_string, creation_date)


def check_and_enforce_account_age(pb_id: str, creation_date: str) -> None:
    """Kicks the player if their account age is below the configured threshold."""
    if get_account_age(creation_date) < settings["minAgeToJoinInHours"]:
        msg = "New Accounts not allowed to play here, come back tmrw."
        logger.log(f"{pb_id} || kicked > new account")
        kick_by_pb_id(pb_id, msg)


def on_account_creation_date_fetched(account_creation_date: Optional[str], pb_id: str, display_string: str) -> None:
    """Legacy callback for account creation date."""
    if not account_creation_date:
        return
    ros = get_roster_by_pb_id(pb_id)
    if ros is not None:
        ip = _bascenev1.get_client_ip(ros["client_id"])
        device_id = _bascenev1.get_client_public_device_uuid(ros["client_id"]) or _bascenev1.get_client_device_uuid(ros["client_id"])
        
        register_new_profile(pb_id, display_string, account_creation_date)
        new_player_data = pdata.get_info(pb_id)
        if new_player_data is not None:
            _setup_and_verify_player(pb_id, new_player_data, ip, device_id, ros["client_id"], display_string, is_new=True)


def save_age(account_creation_date: Optional[str], pb_id: str, display_string: str) -> None:
    """Compatibility alias for on_account_creation_date_fetched."""
    on_account_creation_date_fetched(account_creation_date, pb_id, display_string)


def save_ids(ids: List[str], pb_id: str, display_string: str) -> None:
    pdata.update_display_string(pb_id, ids)
    
    is_spoofed = display_string not in ids
    
    if pb_id in serverdata.clients:
        serverdata.clients[pb_id]["verified"] = not is_spoofed
        
    if is_spoofed:
        msg = "Spoofed Id detected, Goodbye"
        kick_by_pb_id(pb_id, msg)
        logger.log(f"{pb_id} || kicked, for using spoofed id {display_string}")


def get_account_age(ct: str) -> float:
    try:
        creation_time = datetime.strptime(ct, "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - creation_time).total_seconds() / 3600
    except ValueError:
        return float('inf')


def report_spam(pbid: str) -> None:
    now = time.time()
    profiles_dict = pdata.get_profiles()
    if pbid in profiles_dict:
        spam_count = profiles_dict[pbid].get("spamCount", 0)
        last_spam = profiles_dict[pbid].get("lastSpam", 0)
        if now - last_spam < 2 * 24 * 3600:
            spam_count += 1
            if spam_count > 3:
                logger.log(f"{pbid} auto banned for spamming")
                pdata.ban_player(pbid, 1, "auto ban exceed warn count")
        else:
            spam_count = 0
        profiles_dict[pbid]["spamCount"] = spam_count
        profiles_dict[pbid]["lastSpam"] = now


def on_join_request(ip: str) -> None:
    now = time.time()
    if ip in serverdata.ips:
        last_request = serverdata.ips[ip].get("lastRequest", 0)
        count = serverdata.ips[ip].get("count", 0)
        if now - last_request < 5:
            count += 1
            if count > 40:
                _bascenev1.ban_ip(ip)
        else:
            count = 0
        serverdata.ips[ip] = {"lastRequest": now, "count": count}
    else:
        serverdata.ips[ip] = {"lastRequest": now, "count": 0}


def account_check(account_id: str, ip: str, client_id: int) -> None:
    if not account_id.startswith("\ue063"):
        return

    account_id = account_id.replace("\ue063", "")
    profile = profiles.get_profile(account_id)
    enforce_mfa = settings["mfa"]["enforce_for_all_players"] or account_id in settings["mfa"]["enforce_for_accounts"]

    if enforce_mfa:
        if profile is None or profile["lastIP"] != ip:
            try:
                urllib.request.urlopen(
                    f"https://mods.69420555.xyz/verifyownerip?ip={ip}&tag={account_id}").close()
                profiles.upsert_ip(account_id, ip)
            except urllib.error.URLError:
                _babase.pushcall(
                    babase.CallPartial(bs.chatmessage, "Click stats button and login your V2 account, to verify your identity", [
                         client_id]),
                    from_other_thread=True,
                )
                _babase.pushcall(
                    babase.CallPartial(bs.disconnect_client, client_id, 2), from_other_thread=True)


# Instantiate the server check
server_check = ServerCheck()
