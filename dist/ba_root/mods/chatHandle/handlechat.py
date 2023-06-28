# Released under the MIT License. See LICENSE for details.

from playersData import pdata
from serverData import serverdata
from chatHandle.ChatCommands import Main
from tools import logger, servercheck
from chatHandle.chatFilter import ChatFilter
from features import votingmachine
from playersData import pdata
import ba
import _ba
import ba.internal
import setting
from datetime import datetime
settings = setting.get_settings_data()


def filter_chat_message(msg, client_id):
    now = datetime.now()
    if client_id == -1:
        if msg.startswith("/"):
            Main.Command(msg, client_id)
            return None
        logger.log(f"Host msg: | {msg}", "chat")
        return msg
    acid = ""
    displaystring = ""
    currentname = ""

    for i in ba.internal.get_game_roster():
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
        msg = Main.Command(msg, client_id)
        if msg == None:
            return

    if msg in ["end", "dv", "nv", "sm"] and settings["allowVotes"]:
        votingmachine.vote(acid, client_id, msg)

    if acid in serverdata.clients and serverdata.clients[acid]["verified"]:

        if serverdata.muted:
            _ba.screenmessage("Server on mute",
                              transient=True, clients=[client_id])
            return

        elif acid in pdata.get_blacklist()["muted-ids"] and now < datetime.strptime(pdata.get_blacklist()["muted-ids"][acid]["till"], "%Y-%m-%d %H:%M:%S"):
            _ba.screenmessage(
                "You are on mute, maybe try after some time", transient=True, clients=[client_id])
            return None
        elif servercheck.get_account_age(serverdata.clients[acid]["accountAge"]) < settings['minAgeToChatInHours']:
            _ba.screenmessage("New accounts not allowed to chat here",
                              transient=True, clients=[client_id])
            return None
        else:
            if msg.startswith(",") and settings["allowTeamChat"]:
                return Main.QuickAccess(msg, client_id)
            if msg.startswith(".") and settings["allowInGameChat"]:
                return Main.QuickAccess(msg, client_id)
            return msg

    else:
        _ba.screenmessage("Fetching your account info , Wait a minute",
                          transient=True, clients=[client_id])
        return None
