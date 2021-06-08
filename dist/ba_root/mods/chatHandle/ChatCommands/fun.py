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
cmds = ['fly', 'invisible', 'headless', 'creepy', 'celebrate', 'spaz']
cmdaliases = ['inv', 'hl', 'creep', 'celeb']

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
    if cmd == 'fly':
        fly(args, clientid)
    elif cmd in ['inv', 'invisible']:
        invi(args, clientid)
    elif cmd in ['hl', 'headless']:
        headless(args, clientid)
    elif cmd in ['creepy', 'creep']:
        creep(args, clientid)
    elif cmd in ['celebrate', 'celeb']:
        celeb(args, clientid)
    elif cmd == 'spaz':
        spaz(args, clientid)

# global functions for comnands
# fly cmd
def fly(args, clientid):
    """handles fly activity of player node"""
    if args == ['']:
        _ba.chatmessage(" /fly, /fly all or /kill index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            if activity.players[myself].actor.node.fly != True:
                activity.players[myself].actor.node.fly = True
            else:
                activity.players[myself].actor.node.fly = False
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for players in activity.players:
                if players.actor.node.fly != True:
                    players.actor.node.fly = True 
                else:
                    players.actor.node.fly = False 
    elif args[0].isdigit() and not args[0] == -1:
        try:
            activity = _ba.get_foreground_host_activity()
            with _ba.Context(activity):
                if activity.players[int(args[0])].actor.node.fly != True:
                    activity.players[int(args[0])].actor.node.fly = True 
                else:
                    activity.players[int(args[0])].actor.node.fly = False 
        except: _ba.chatmessage("player not found")

# invisible cmd
def invi(args, clientid):
    """handles player node invisiblity"""
    if args == ['']:
        _ba.chatmessage(" /inv, /inv all or /inv index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            body = activity.players[myself].actor.node
            if body.torso_model != None:
                body.head_model = None
                body.torso_model = None
                body.upper_arm_model = None
                body.forearm_model = None
                body.pelvis_model = None
                body.hand_model = None
                body.toes_model = None
                body.upper_leg_model = None
                body.lower_leg_model = None
                body.style = 'cyborg'
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for i in activity.players:
                body = i.actor.node
                if body.torso_model != None:
                    body.head_model = None
                    body.torso_model = None
                    body.upper_arm_model = None
                    body.forearm_model = None
                    body.pelvis_model = None
                    body.hand_model = None
                    body.toes_model = None
                    body.upper_leg_model = None
                    body.lower_leg_model = None
                    body.style = 'cyborg'
    elif args[0].isdigit() and not args[0] == -1:
        player = int(args[0])
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            body = activity.players[player].actor.node
            if body.torso_model != None:
                body.head_model = None
                body.torso_model = None
                body.upper_arm_model = None
                body.forearm_model = None
                body.pelvis_model = None
                body.hand_model = None
                body.toes_model = None
                body.upper_leg_model = None
                body.lower_leg_model = None
                body.style = 'cyborg'

# headless cmd
def headless(args, clientid):
    """headless player node"""
    if args == ['']:
        _ba.chatmessage(" /hl, /hl all or /hl index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            node = activity.players[myself].actor.node
            if node.head_model != None:
                node.head_model = None
                node.style='cyborg'
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for players in activity.players:
                node = players.actor.node 
                if node.head_model != None:
                    node.head_model = None
                    node.style='cyborg'
    elif args[0].isdigit() and not args[0] == -1:
        try:
            activity = _ba.get_foreground_host_activity()
            with _ba.Context(activity):
                node = activity.players[int(args[0])].actor.node
                if node.head_model != None:
                    node.head_model = None
                    node.style='cyborg'
        except: _ba.chatmessage("player not found")

# creep cmd
def creep(args, clientid):
    """makes player creepy"""
    if args == ['']:
        _ba.chatmessage(" /creep, /creep all or /creep index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            node = activity.players[myself].actor.node
            if node.head_model != None:
                node.head_model = None
                node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
                node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
    elif args[0] == 'all':
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for players in activity.players:
                node = players.actor.node
                if node.head_model != None:
                    node.head_model = None 
                    node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
                    node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
    elif args[0].isdigit() and not args[0] == -1:
        try:
            activity = _ba.get_foreground_host_activity()
            with _ba.Context(activity):
                node = activity.players[int(args[0])].actor.node
                if node.head_model != None:
                    node.head_model = None
                    node.handlemessage(ba.PowerupMessage(poweruptype='punch'))
                    node.handlemessage(ba.PowerupMessage(poweruptype='shield'))
        except: _ba.chatmessage("player not found")

# celebrate cmd
def celeb(args, clientid):
    """handles celebrate msg"""
    if args == ['']:
        _ba.chatmessage(" /celeb, /celeb all or /celeb index of list", sender_override ="Use[server]")
    elif args == []:
        myself = clientid_to_myself(clientid)
        handlemsg(myself, ba.CelebrateMessage())
    elif args[0] == 'all':
        handlemsg_all(ba.CelebrateMessage())
    else:
        try: handlemsg(int(args[0]), ba.CelebrateMessage())
        except: _ba.chatmessage("player not found")

# spaz cmd
_spaz = ["ali", "spaz", "kronk", "zoe", "jack", "ninja", "bear", "bones", "agent", "frosty", "penguin","pixie", "wizard", "cyborg"]

def spaz(args, clientid):
    """avatar cmd for player"""
    if args[0] == 'help' or args == []:
        _ba.chatmessage(' /spaz ["ali", "spaz", "kronk", "zoe", "jack", "ninja", "bear", "bones", "agent", "frosty", "penguin","pixie", "wizard", "cyborg"]')
        
    if args[0] in _spaz:
        myself = clientid_to_myself(clientid)
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            t = activity.players[myself].actor.node
            t.color_texture = ba.gettexture(args[0]+"Color")
            t.color_mask_texture = ba.gettexture(args[0]+"ColorMask")
            t.head_model = ba.getmodel(args[0]+"Head")
            t.torso_model = ba.getmodel(args[0]+"Torso")
            t.pelvis_model = ba.getmodel(args[0]+"Pelvis")
            t.upper_arm_model = ba.getmodel(args[0]+"UpperArm")
            t.forearm_model = ba.getmodel(args[0]+"ForeArm")
            t.hand_model = ba.getmodel(args[0]+"Hand")
            t.upper_leg_model = ba.getmodel(args[0]+"UpperLeg")
            t.lower_leg_model = ba.getmodel(args[0]+"LowerLeg")
            t.toes_model = ba.getmodel(args[0]+"Toes")
            t.style = args[0]
    elif args[0] == 'all' and args[1] in _spaz:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            for i in activity.players:
                t = i.actor.node
                t.color_texture = ba.gettexture(args[1]+"Color")
                t.color_mask_texture = ba.gettexture(args[1]+"ColorMask")
                t.head_model = ba.getmodel(args[1]+"Head")
                t.torso_model = ba.getmodel(args[1]+"Torso")
                t.pelvis_model = ba.getmodel(args[1]+"Pelvis")
                t.upper_arm_model = ba.getmodel(args[1]+"UpperArm")
                t.forearm_model = ba.getmodel(args[1]+"ForeArm")
                t.hand_model = ba.getmodel(args[1]+"Hand")
                t.upper_leg_model = ba.getmodel(args[1]+"UpperLeg")
                t.lower_leg_model = ba.getmodel(args[1]+"LowerLeg")
                t.toes_model = ba.getmodel(args[1]+"Toes")
                t.style = args[0]
    elif args[0].isdigit() and args[1] in _spaz:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            try:
                t = activity.players[int(args[0])].actor.node
                t.color_texture = ba.gettexture(args[1]+"Color")
                t.color_mask_texture = ba.gettexture(args[1]+"ColorMask")
                t.head_model = ba.getmodel(args[1]+"Head")
                t.torso_model = ba.getmodel(args[1]+"Torso")
                t.pelvis_model = ba.getmodel(args[1]+"Pelvis")
                t.upper_arm_model = ba.getmodel(args[1]+"UpperArm")
                t.forearm_model = ba.getmodel(args[1]+"ForeArm")
                t.hand_model = ba.getmodel(args[1]+"Hand")
                t.upper_leg_model = ba.getmodel(args[1]+"UpperLeg")
                t.lower_leg_model = ba.getmodel(args[1]+"LowerLeg")
                t.toes_model = ba.getmodel(args[1]+"Toes")
                t.style = args[0]
            except: _ba.chatmessage("player not found")
    else:
        _ba.chatmessage(" /spaz help for help", sender_override ="Use[server]")

