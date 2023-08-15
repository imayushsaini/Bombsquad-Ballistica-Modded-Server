# Released under the MIT License. See LICENSE for details.

from datetime import datetime

import setting
from chatHandle.chatFilter import ChatFilter
from chatHandle.chatcommands import executor
from features import votingmachine
from playersData import pdata
from serverData import serverdata

import bascenev1 as bs
from tools import logger, servercheck

settings = setting.get_settings_data()


def filter_chat_message(msg, client_id):
    now = datetime.now()
    if client_id == -1:
        if msg.startswith("/"):
            print("message stars with /")
            executor.execute(msg, client_id)
            return None
        logger.log(f"Host msg: | {msg}", "chat")
        return msg
    acid = ""
    displaystring = ""
    currentname = ""

    for i in bs.get_game_roster():
        if i['client_id'] == client_id:
            acid = i['account_id']
            try:
                currentname = i['players'][0]['name_full']
            except:
                currentname = "<in-lobby>"
            displaystring = i['display_string']
    if acid:
        msg = ChatFilter.filter(msg, acid, client_id)
    if msg == None:
        return
    logger.log(f'{acid}  |  {displaystring}| {currentname} | {msg}', "chat")
    if msg.startswith("/"):
        msg = executor.execute(msg, client_id)
        if msg == None:
            return

    if msg in ["end", "dv", "nv", "sm"] and settings["allowVotes"]:
        votingmachine.vote(acid, client_id, msg)

    if acid in serverdata.clients and serverdata.clients[acid]["verified"]:

        if serverdata.muted:
            bs.broadcastmessage("Server on mute",
                                transient=True, clients=[client_id])
            return

        elif acid in pdata.get_blacklist()[
            "muted-ids"] and now < datetime.strptime(
            pdata.get_blacklist()["muted-ids"][acid]["till"],
            "%Y-%m-%d %H:%M:%S"):
            bs.broadcastmessage(
                "You are on mute, maybe try after some time", transient=True,
                clients=[client_id])
            return None
        elif servercheck.get_account_age(
            serverdata.clients[acid]["accountAge"]) < settings[
            'minAgeToChatInHours']:
            bs.broadcastmessage("New accounts not allowed to chat here",
                                transient=True, clients=[client_id])
            return None
        else:
            if msg.startswith(",") and settings["allowTeamChat"]:
                return executor.QuickAccess(msg, client_id)
            if msg.startswith(".") and settings["allowInGameChat"]:
                return executor.QuickAccess(msg, client_id)
            return msg

    else:
        bs.broadcastmessage("Fetching your account info , Wait a minute",
                            transient=True, clients=[client_id])
        return None
