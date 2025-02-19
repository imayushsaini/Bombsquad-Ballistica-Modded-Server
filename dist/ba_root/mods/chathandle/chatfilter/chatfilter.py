# Released under the MIT License. See LICENSE for details.
import _thread
import time

import setting
from features import profanity
from playersdata import pdata
from serverdata import serverdata

import bascenev1 as bs
from tools import logger
from tools import servercheck

settings = setting.get_settings_data()


def check_permissions(accountid):
    roles = pdata.get_roles()
    for role in roles:
        if accountid in roles[role]["ids"] and (
            role == "bypass-warn" or role == "owner"):
            return True
    return False


def filter(msg, pb_id, client_id):
    new_msg = msg
    if new_msg != msg:
        bs.broadcastmessage("Don\'t ABUSE!", color=(1, 0, 0), transient=True,
                            clients=[client_id])
        if not check_permissions(pb_id):
            addWarn(pb_id, client_id)
        else:
            bs.broadcastmessage("Special role found, Warn BYPASSED!",
                                color=(0, 1, 0), transient=True,
                                clients=[client_id])

    now = time.time()
    if pb_id not in serverdata.clients:
        return None

    serverdata.clients[pb_id]['cMsgCount'] = 0
    serverdata.clients[pb_id]['lastMsgTime'] = now
    serverdata.clients[pb_id]['lastMsg'] = msg
    serverdata.clients[pb_id]['cSameMsg'] = 0
    return new_msg


def addWarn(pb_id, client_id):
    now = time.time()
    player = serverdata.clients[pb_id]
    warn = player['warnCount']
    if now - player['lastWarned'] <= settings["WarnCooldownMinutes"] * 60:
        warn += 1
        if warn > settings["maxWarnCount"]:
            bs.broadcastmessage(settings["afterWarnKickMsg"], color=(1, 0, 0),
                                transient=True, clients=[client_id])
            logger.log(pb_id + " | kicked for chat spam")
            bs.disconnect_client(client_id)
            _thread.start_new_thread(servercheck.reportSpam, (pb_id,))

        else:
            bs.broadcastmessage(
                settings["warnMsg"] + f"\n\nWarn Count = {warn}/3!!!",
                color=(1, 0, 0), transient=True, clients=[client_id])
    else:
        warn = 0
    serverdata.clients[pb_id]["warnCount"] = warn
    serverdata.clients[pb_id]['lastWarned'] = now
