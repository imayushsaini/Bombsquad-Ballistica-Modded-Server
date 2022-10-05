# Released under the MIT License. See LICENSE for details.

from playersData import pdata
from serverData import serverdata
from chatHandle.ChatCommands import Main
from tools import logger, servercheck
from chatHandle.chatFilter import ChatFilter
from features import EndVote
import ba, _ba
import ba.internal
import setting

settings = setting.get_settings_data()


def filter_chat_message(msg, client_id):
    if client_id == -1:
        if msg.startswith("/"):
            Main.Command(msg, client_id)
            return None
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
    if msg.startswith("/"):
        return Main.Command(msg, client_id)

    if msg.startswith(",") and settings["allowTeamChat"]:
        return Main.QuickAccess(msg, client_id)
    if msg.startswith(".") and settings["allowInGameChat"]:
        return Main.QuickAccess(msg, client_id)

    if msg == "end" and settings["allowEndVote"]:
        EndVote.vote_end(acid, client_id)

    logger.log(acid + " | " + displaystring + "|" + currentname + "| " + msg, "chat")

    if acid in serverdata.clients and serverdata.clients[acid]["verified"]:

        if serverdata.muted:
            _ba.screenmessage("Server on mute", transient=True, clients=[client_id])
            return

        elif serverdata.clients[acid]["isMuted"]:
            _ba.screenmessage("You are on mute", transient=True, clients=[client_id])
            return None
        elif servercheck.get_account_age(serverdata.clients[acid]["accountAge"]) < settings['minAgeToChatInHours']:
            _ba.screenmessage("New accounts not allowed to chat here", transient=True, clients=[client_id])
            return None
        else:
            return msg


    else:
        _ba.screenmessage("Fetching your account info , Wait a minute", transient=True, clients=[client_id])
        return None
