""" Some useful handlers to reduce lot of code """
import _babase

import bascenev1 as bs


def send(msg, clientid):
    """Shortcut To Send Private Msg To Client"""
    for m in msg.split("\n"):
        bs.chatmessage(str(m), clients=[clientid])
    bs.broadcastmessage(str(msg), transient=True, clients=[clientid])


def clientid_to_myself(clientid):
    """Return Player Index Of Self Player"""

    for i, player in enumerate(_babase.get_foreground_host_activity().players):
        if player.sessionplayer.inputdevice.client_id == clientid:
            return i


def handlemsg(client, msg):
    """Handles Spaz Msg For Single Player"""
    activity = bs.get_foreground_host_activity()
    activity.players[client].actor.node.handlemessage(msg)


def handlemsg_all(msg):
    """Handle Spaz message for all players in activity"""

    activity = bs.get_foreground_host_activity()

    for i in activity.players:
        i.actor.node.handlemessage(msg)
