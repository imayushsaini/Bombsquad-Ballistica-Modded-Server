# Released under the MIT License. See LICENSE for details.


from serverData import serverdata
from playersData import pdata
import _ba
import ba.internal
import urllib.request
import json
from datetime import datetime, timedelta
import time
import ba
from ba._general import Call
import threading
import setting
import _thread
from tools import logger
from features import profanity
from playersData import pdata
from . import notification_manager
blacklist = pdata.get_blacklist()

settings = setting.get_settings_data()
ipjoin = {}


class checkserver(object):
    def start(self):
        self.players = []

        self.t1 = ba.Timer(1, ba.Call(self.check),
                           repeat=True,  timetype=ba.TimeType.REAL)

    def check(self):
        newPlayers = []
        ipClientMap = {}
        deviceClientMap = {}
        for ros in ba.internal.get_game_roster():
            ip = _ba.get_client_ip(ros["client_id"])
            device_id = _ba.get_client_public_device_uuid(ros["client_id"])
            if (device_id == None):
                device_id = _ba.get_client_device_uuid(ros["client_id"])
            if device_id not in deviceClientMap:
                deviceClientMap[device_id] = [ros["client_id"]]
            else:
                deviceClientMap[device_id].append(ros["client_id"])
                if len(deviceClientMap[device_id]) >= settings['maxAccountPerIP']:
                    _ba.chatmessage(f"Only {settings['maxAccountPerIP']} player per IP allowed, disconnecting this device.", clients=[
                                    ros["client_id"]])
                    ba.internal.disconnect_client(ros["client_id"])
                    logger.log(f'Player disconnected, reached max players per device || {ros["account_id"]}',
                               "playerjoin")
                    continue
            if ip not in ipClientMap:
                ipClientMap[ip] = [ros["client_id"]]
            else:
                ipClientMap[ip].append(ros["client_id"])
                if len(ipClientMap[ip]) >= settings['maxAccountPerIP']:
                    _ba.chatmessage(f"Only {settings['maxAccountPerIP']} player per IP allowed, disconnecting this device.", clients=[
                                    ros["client_id"]])
                    ba.internal.disconnect_client(ros["client_id"])
                    logger.log(f'Player disconnected, reached max players per IP address || {ros["account_id"]}',
                               "playerjoin")
                    continue
            newPlayers.append(ros['account_id'])
            if ros['account_id'] not in self.players and ros[
                    'client_id'] != -1:
                # new player joined lobby

                d_str = ros['display_string']
                d_str2 = profanity.censor(d_str)
                try:
                    logger.log(
                        f'{d_str}  || {ros["account_id"]} || joined server',
                        "playerjoin")
                    logger.log(f'{ros["account_id"]} {ip} {device_id}')
                except:
                    pass
                if d_str2 != d_str:
                    _ba.screenmessage(
                        "Profanity in Id , change your ID and join back",
                        color=(1, 0, 0), transient=True,
                        clients=[ros['client_id']])
                    try:
                        logger.log(f'{d_str} || { ros["account_id"] } || kicked by profanity check',
                                   "sys")
                    except:
                        pass
                    ba.internal.disconnect_client(ros['client_id'], 1)
                    return

                if settings["whitelist"] and ros["account_id"] != None:
                    if ros["account_id"] not in pdata.CacheData.whitelist:
                        _ba.screenmessage("Not in whitelist,contact admin",
                                          color=(1, 0, 0), transient=True,
                                          clients=[ros['client_id']])
                        logger.log(
                            f'{d_str}  || { ros["account_id"]} | kicked > not in whitelist')
                        ba.internal.disconnect_client(ros['client_id'])

                        return

                if ros['account_id'] != None:
                    if ros['account_id'] in serverdata.clients:
                        on_player_join_server(ros['account_id'],
                                              serverdata.clients[
                                                  ros['account_id']], ip, device_id)
                    else:
                        # from local cache, then call on_player_join_server
                        LoadProfile(ros['account_id'], ip, device_id).start()

        self.players = newPlayers


def on_player_join_server(pbid, player_data, ip, device_id):
    global ipjoin
    now = time.time()
    # player_data=pdata.get_info(pbid)
    clid = 113
    device_string = ""
    for ros in ba.internal.get_game_roster():
        if ros["account_id"] == pbid:
            clid = ros["client_id"]
            device_string = ros['display_string']
    if ip in ipjoin:
        lastjoin = ipjoin[ip]["lastJoin"]
        joincount = ipjoin[ip]["count"]
        if now - lastjoin < 15:
            joincount += 1
            if joincount > 2:
                _ba.screenmessage("Joining too fast , slow down dude",  # its not possible now tho, network layer will catch it before reaching here
                                  color=(1, 0, 1), transient=True,
                                  clients=[clid])
                logger.log(f'{pbid} || kicked for joining too fast')
                ba.internal.disconnect_client(clid)
                _thread.start_new_thread(reportSpam, (pbid,))
                return
        else:
            joincount = 0

        ipjoin[ip]["count"] = joincount
        ipjoin[ip]["lastJoin"] = now
    else:
        ipjoin[ip] = {"lastJoin": now, "count": 0}
    if pbid in serverdata.clients:
        serverdata.clients[pbid]["lastJoin"] = now

    if player_data != None:  # player data is in serevrdata or in local.json cache
        serverdata.recents.append(
            {"client_id": clid, "deviceId": device_string, "pbid": pbid})
        serverdata.recents = serverdata.recents[-20:]
        if check_ban(ip, device_id, pbid):
            _ba.chatmessage(
                'sad ,your account is flagged contact server owner for unban', clients=[clid])
            ba.internal.disconnect_client(clid)
            return
        if get_account_age(player_data["accountAge"]) < \
                settings["minAgeToJoinInHours"]:
            for ros in ba.internal.get_game_roster():
                if ros['account_id'] == pbid:
                    _ba.screenmessage(
                        "New Accounts not allowed here , come back later",
                        color=(1, 0, 0), transient=True,
                        clients=[ros['client_id']])
                    logger.log(pbid + " | kicked > reason:Banned account")
                    ba.internal.disconnect_client(ros['client_id'])

            return
        else:
            current_time = datetime.now()
            if pbid not in serverdata.clients:
                # ahh , lets reset if plyer joining after some long time
                serverdata.clients[pbid] = player_data
                serverdata.clients[pbid]["warnCount"] = 0
                serverdata.clients[pbid]["lastWarned"] = time.time()
                serverdata.clients[pbid]["verified"] = False
                serverdata.clients[pbid]["rejoincount"] = 1
                serverdata.clients[pbid]["lastJoin"] = time.time()
                if pbid in blacklist["kick-vote-disabled"] and current_time < datetime.strptime(blacklist["kick-vote-disabled"][pbid]["till"], "%Y-%m-%d %H:%M:%S"):
                    _ba.disable_kickvote(pbid)

            serverdata.clients[pbid]["lastIP"] = ip

            device_id = _ba.get_client_public_device_uuid(clid)
            if (device_id == None):
                device_id = _ba.get_client_device_uuid(clid)
            serverdata.clients[pbid]["deviceUUID"] = device_id
            verify_account(pbid, player_data)  # checked for spoofed ids
            logger.log(
                f'{pbid} ip: {serverdata.clients[pbid]["lastIP"]} , Device id: {device_id}')
            _ba.screenmessage(settings["regularWelcomeMsg"] + " " + device_string,
                              color=(0.60, 0.8, 0.6), transient=True,
                              clients=[clid])
            notification_manager.player_joined(pbid)
    else:
        # fetch id for first time.
        thread = FetchThread(
            target=my_acc_age,
            callback=save_age,
            pb_id=pbid,
            display_string=device_string
        )

        thread.start()
        _ba.screenmessage(settings["firstTimeJoinMsg"], color=(0.6, 0.8, 0.6),
                          transient=True, clients=[clid])
        notification_manager.player_joined(pbid)

    # pdata.add_profile(pbid,d_string,d_string)


def check_ban(ip, device_id, pbid, log=True):
    current_time = datetime.now()

    if ip in blacklist["ban"]['ips'] and current_time < datetime.strptime(blacklist["ban"]["ips"][ip]["till"], "%Y-%m-%d %H:%M:%S"):
        msg = f' reason: matched IP | {blacklist["ban"]["ips"][ip]["reason"]} , Till : {blacklist["ban"]["ips"][ip]["till"]}'
        if log:
            logger.log(f'{pbid} | kicked > {msg}')
            return True
        return msg
    elif device_id in blacklist["ban"]["deviceids"] and current_time < datetime.strptime(blacklist["ban"]["deviceids"][device_id]["till"], "%Y-%m-%d %H:%M:%S"):
        msg = f'reason: matched deviceId | {blacklist["ban"]["deviceids"][device_id]["reason"]}, Till : {blacklist["ban"]["deviceids"][device_id]["till"]}'
        if log:
            logger.log(
                f'{pbid} | kicked > {msg}')
            return True
        return msg
    elif pbid in blacklist["ban"]["ids"] and current_time < datetime.strptime(blacklist["ban"]["ids"][pbid]["till"], "%Y-%m-%d %H:%M:%S"):
        msg = f'reason: matched ID | {blacklist["ban"]["ids"][pbid]["reason"]} , Till : {blacklist["ban"]["ids"][pbid]["till"]}'
        if log:
            logger.log(
                f'{pbid} | kicked > {msg}')
            return True
        return msg
    return False


def verify_account(pb_id, p_data):
    d_string = ""
    for ros in ba.internal.get_game_roster():
        if ros['account_id'] == pb_id:
            d_string = ros['display_string']

    if d_string not in p_data['display_string']:

        thread2 = FetchThread(
            target=get_device_accounts,
            callback=save_ids,
            pb_id=pb_id,
            display_string=d_string
        )
        thread2.start()
    else:
        serverdata.clients[pb_id]["verified"] = True


# ============== IGNORE BELOW CODE  =======================

def _make_request_safe(request, retries=2, raise_err=True):
    try:
        return request()
    except:
        if retries > 0:
            time.sleep(1)
            return _make_request_safe(request, retries=retries - 1,
                                      raise_err=raise_err)
        if raise_err:
            raise


def get_account_creation_date(pb_id):
    # thanks rikko
    account_creation_url = "http://bombsquadgame.com/accountquery?id=" + pb_id
    account_creation = _make_request_safe(
        lambda: urllib.request.urlopen(account_creation_url))
    if account_creation is not None:
        try:
            account_creation = json.loads(account_creation.read())
        except ValueError:
            pass
        else:
            creation_time = account_creation["created"]
            creation_time = map(str, creation_time)
            creation_time = datetime.strptime("/".join(creation_time),
                                              "%Y/%m/%d/%H/%M/%S")
            # Convert to IST
            creation_time += timedelta(hours=5, minutes=30)
            return str(creation_time)


def get_device_accounts(pb_id):
    url = "http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID=" + pb_id
    data = _make_request_safe(lambda: urllib.request.urlopen(url))
    if data is not None:
        try:
            accounts = json.loads(data.read())["accountDisplayStrings"]
        except ValueError:
            return ['???']
        else:
            return accounts


# =======  yes fucking threading code , dont touch ==============


# ============ file I/O =============

class LoadProfile(threading.Thread):
    def __init__(self, pb_id, ip, device_id):
        threading.Thread.__init__(self)
        self.pbid = pb_id
        self.ip = ip
        self.device_id = device_id

    def run(self):
        player_data = pdata.get_info(self.pbid)
        _ba.pushcall(Call(on_player_join_server, self.pbid, player_data, self.ip, self.device_id),
                     from_other_thread=True)


# ================ http ================
class FetchThread(threading.Thread):
    def __init__(self, target, callback=None, pb_id="ji",
                 display_string="XXX"):
        super(FetchThread, self).__init__(target=self.target_with_callback,
                                          args=(pb_id, display_string,))
        self.callback = callback
        self.method = target

    def target_with_callback(self, pb_id, display_string):
        data = self.method(pb_id)
        if self.callback is not None:
            self.callback(data, pb_id, display_string)


def my_acc_age(pb_id):
    return get_account_creation_date(pb_id)


def save_age(age, pb_id, display_string):
    _ba.pushcall(Call(pdata.add_profile, pb_id, display_string,
                 display_string, age), from_other_thread=True)
    time.sleep(2)
    thread2 = FetchThread(
        target=get_device_accounts,
        callback=save_ids,
        pb_id=pb_id,
        display_string=display_string
    )
    thread2.start()
    if get_account_age(age) < settings["minAgeToJoinInHours"]:
        msg = "New Accounts not allowed to play here , come back tmrw."
        logger.log(pb_id + "|| kicked > new account")
        _ba.pushcall(Call(kick_by_pb_id, pb_id, msg), from_other_thread=True)


def save_ids(ids, pb_id, display_string):
    pdata.update_display_string(pb_id, ids)

    if display_string not in ids:
        msg = "Spoofed Id detected , Goodbye"
        _ba.pushcall(Call(kick_by_pb_id, pb_id, msg), from_other_thread=True)
        serverdata.clients[pb_id]["verified"] = False
        logger.log(
            pb_id + "|| kicked , for using spoofed id " + display_string)
    else:
        serverdata.clients[pb_id]["verified"] = True


def kick_by_pb_id(pb_id, msg):
    for ros in ba.internal.get_game_roster():
        if ros['account_id'] == pb_id:
            _ba.screenmessage(msg, transient=True, clients=[ros['client_id']])
            ba.internal.disconnect_client(ros['client_id'])


def get_account_age(ct):
    creation_time = datetime.strptime(ct, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    delta = now - creation_time
    delta_hours = delta.total_seconds() / (60 * 60)
    return delta_hours


def reportSpam(id):
    now = time.time()
    profiles = pdata.get_profiles()
    if id in profiles:
        count = profiles[id]["spamCount"]
        if now - profiles[id]["lastSpam"] < 2 * 24 * 60 * 60:
            count += 1
            if count > 3:
                logger.log(id+" auto banned for spamming")
                # by default ban for 1 day , change here if you want
                pdata.ban_player(id, 1, "auto ban exceed warn count")
        else:
            count = 0

        profiles[id]["spamCount"] = count
        profiles[id]["lastSpam"] = now


def on_join_request(ip):
    now = time.time()
    if ip in serverdata.ips:
        lastRequest = serverdata.ips[ip]["lastRequest"]
        count = serverdata.ips[ip]["count"]
        if now - lastRequest < 5:
            count += 1
            if count > 40:
                _ba.ban_ip(ip)
        else:
            count = 0
        serverdata.ips[ip] = {"lastRequest": time.time(), "count": count}
    else:
        serverdata.ips[ip] = {"lastRequest": time.time(), "count": 0}
