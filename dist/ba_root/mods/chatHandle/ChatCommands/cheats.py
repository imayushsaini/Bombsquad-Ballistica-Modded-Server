# Released under the MIT License. See LICENSE for details.
#
from ._handlers import (
    handlemsg,
    handlemsg_all,
    clientid_to_myself
)
import ba
import _ba

# cmds
cmds = ['kill', 'heal', 'curse', 'sleep',  'superpunch', 'gloves', 'shield', 'freeze', 'unfreeze', 'godmode']
cmdaliases = ['die', 'heath', 'cur', 'sp', 'punch', 'protect', 'ice', 'thaw', 'gm']

# main function
def Excelcmd(cmd, args, clientid, accountid):
    """Checks The cmd And Run Function
    Parameters:
        cmd : str 
        args : list
        clientid : int 
        accountid : str
    Returns:
        None 
    """
    if cmd in ['kill', 'die']:
        kill(args)
    elif cmd == 'sleep':
        sleep(args)
    elif cmd in ['freeze', 'ice']:
        freeze(args)
    elif cmd in ['unfreeze', 'thaw']:
        un_freeze(args, clientid)
    elif cmd in ['heal', 'heath']:
        heal(args, clientid)
    elif cmd in ['curse', 'cur']:
        curse(args)
    elif cmd in ['gloves', 'punch']:
        gloves(args, clientid)
    elif cmd in ['shield', 'protect']:
        shield(args, clientid)
    elif cmd in ['sp', 'superpunch']:
        super_punch(args, clientid)
    elif cmd in ['gm', 'godmode']:
        god_mode(args, clientid)

# global functions for comnands
# kill cmd
def kill(args):
    """handle kill message for player node"""
    if args == [] or args == ['']:
        _ba.chatmessage(" /kill all or /kill index of list", sender_override ="Use[server]")
    elif args[0] == 'all':
        handlemsg_all(ba.DieMessage())
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.DieMessage())
        except: _ba.chatmessage(" player not found")

# sleep cmd
def sleep(args):
    """handle sleep message of player node"""
    if args == [] or args == ['']:
        _ba.chatmessage(" /sleep all or /sleep index of list", sender_override ="Use[server]")
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for player in activity.players:
                player.actor.node.handlemessage('knockout', 8000)
    elif args[0].isdigit() and not args[0] == -1:
        try:
            activity = _ba.get_foreground_host_activity()
            with _ba.Context(activity):
                activity.players[int(args[0])].actor.node.handlemessage('knockout', 8000)
        except: _ba.chatmessage(" player not found")

# freeze cmd
def freeze(args):
    """handle freeze message for player node"""
    if args == [] or args == ['']:
        _ba.chatmessage(" /freeze all or /freeze index of list", sender_override ="Use[server]")
    elif args[0] == 'all':
        handlemsg_all(ba.FreezeMessage())
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.FreezeMessage())
        except: _ba.chatmessage(" player not found")

# unfreeze cmd
def un_freeze(args, clientid):
    """handle Thaw message for player node"""
    if args == ['']:
        _ba.chatmessage(" /thaw, /thaw all or /thaw index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        handlemsg(myself, ba.ThawMessage())
    elif args[0] == 'all':
        handlemsg_all(ba.ThawMessage())
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.ThawMessage())
        except: _ba.chatmessage(" player not found")

# heal cmd
def heal(args, clientid):
    """handle heal powerup message for player node"""
    if args == ['']:
        _ba.chatmessage(" /heal, /heal all or /heal index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        handlemsg(myself, ba.PowerupMessage(poweruptype='health'))
    elif args[0] == 'all':
        handlemsg_all(ba.PowerupMessage(poweruptype='health'))
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.PowerupMessage(poweruptype='health'))
        except: _ba.chatmessage(" player not found")

# curse cmd
def curse(args):
    """handle curse powerup message for player node"""
    if args == [] or args == ['']:
        _ba.chatmessage(" /curse all or /curse index of list", sender_override ="Use[server]")
    elif args[0] == 'all':
        handlemsg_all(ba.PowerupMessage(poweruptype='curse'))
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.PowerupMessage(poweruptype='curse'))
        except: _ba.chatmessage(" player not found")

# gloves cmd
def gloves(args, clientid):
    """handle glove powerup message for player node"""
    if args == ['']:
        _ba.chatmessage(" /gloves, /gloves all or /gloves index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        handlemsg(myself, ba.PowerupMessage(poweruptype='punch'))
    elif args[0] == 'all':
        handlemsg_all(ba.PowerupMessage(poweruptype='punch'))
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.PowerupMessage(poweruptype='punch'))
        except: _ba.chatmessage(" player not found")

# shield cmd
def shield(args, clientid):
    """handle shield powerup message for player node"""
    if args == ['']:
        _ba.chatmessage(" /shield, /shield all or /shield index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        handlemsg(myself, ba.PowerupMessage(poweruptype='shield'))
    elif args[0] == 'all':
        handlemsg_all(ba.PowerupMessage(poweruptype='shield'))
    elif args[0].isdigit() and not args[0] == -1:
        try: handlemsg(int(args[0]), ba.PowerupMessage(poweruptype='shield'))
        except: _ba.chatmessage(" player not found")

# super punch
def super_punch(args, clientid):
    """handle verious changes related to punch of player node"""
    if args == ['']:
        _ba.chatmessage(" /sp, /sp all or /sp index of list", sender_override ="Use[server]")
    elif args == []:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            myself = clientid_to_myself(clientid)
            if activity.players[myself].actor._punch_power_scale != 15:
                activity.players[myself].actor._punch_power_scale = 15
                activity.players[myself].actor._punch_cooldown = 0
            else:
                activity.players[myself].actor._punch_power_scale = 1.2
                activity.players[myself].actor._punch_cooldown = 400
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for i in activity.players:
                if i.actor._punch_power_scale != 15:
                    i.actor._punch_power_scale = 15
                    i.actor._punch_cooldown = 0
                else:
                    i.actor._punch_power_scale = 1.2
                    i.actor._punch_cooldown = 400
    elif args[0].isdigit() and not args[0] == -1:
        try:
            activity = _ba.get_foreground_host_activity()
            with _ba.Context(activity):
                if activity.players[int(args[0])].actor._punch_power_scale != 15:
                    activity.players[int(args[0])].actor._punch_power_scale = 15
                    activity.players[int(args[0])].actor._punch_cooldown = 0
                else:
                    activity.players[int(args[0])].actor._punch_power_scale = 1.2
                    activity.players[int(args[0])].actor._punch_cooldown = 400
        except: _ba.chatmessage(" player not found")

# god mode cmd
def god_mode(args, clientid):
    """god mode - increse powerup scale, hockey and invisiblity for player node"""
    if args == ['']:
        _ba.chatmessage(" /gm, /gm all or /gm index of list", sender_override ="Use[server]")
    if args == []:
        myself = clientid_to_myself(clientid)
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            player = activity.players[myself].actor
            if player._punch_power_scale != 7:
                player._punch_power_scale = 7
                player.node.hockey = True
                player.node.invincible = True
            else:
                player._punch_power_scale = 1.2
                player.node.hockey = False
                player.node.invincible = False
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for i in activity.players:
                if i.actor._punch_power_scale != 7:
                    i.actor._punch_power_scale = 7
                    i.actor.node.hockey = True
                    i.actor.node.invincible = True
                else:
                    i.actor._punch_power_scale = 1.2
                    i.actor.node.hockey = False
                    i.actor.node.invincible = False
    elif args[0].isdigit() and not args[0] == -1:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            player = activity.players[int(args[0])].actor
            if player._punch_power_scale != 7:
                player._punch_power_scale = 7
                player.node.hockey = True
                player.node.invincible = True
            else:
                player._punch_power_scale = 1.2
                player.node.hockey = False
                player.node.invincible = False