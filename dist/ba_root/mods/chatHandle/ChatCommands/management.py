# Released under the MIT License. See LICENSE for details.
#
from ._handlers import (
    handlemsg,
    handlemsg_all,
    clientid_to_myself,
    get_roles,
    commit,
    clientid_to_accountid
)
import ba
import _ba
import time
import json
import setting

from playersData import pdata
from tools.whitelist import *

# cmds
cmds = ['kick', 'remove', 'end', 'quit', 'slowmo', 'nv', 'dv', 'pause', 'cameramode', 'createrole', 'deleterole', 'addrole', 'removerole', 'addcommand', 'addcmd', 'removecommand', 'removecmd', 'changetag', 'add', 'spectators', 'lobbytime']
cmdaliases = ['rm', 'next', 'restart', 'sm', 'slow', 'night', 'day', 'pausegame', 'camera_mode', 'rotate_camera', 'rmrole', 'rmcmd', 'whitelist']

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
    if cmd == 'kick':
        kick(args)
    elif cmd == 'unmute':
        unmute(args)
    elif cmd in ['end', 'next']:
        end(args)
    elif cmd in ['quit', 'restart']:
        quit(args)
    elif cmd in ['remove', 'rm']:
        remove(args)
    elif cmd in ['sm', 'slow', 'slowmo']:
        slow_motion()
    elif cmd in ['nv', 'night']:
        nv(args)
    elif cmd in ['dv', 'day']:
        dv(args)
    elif cmd in ['pause', 'pausegame']:
        pause()
    elif cmd in ['cameraMode', 'camera_mode', 'rotate_camera']:
        rotate_camera()
    elif cmd == 'createrole':
        create_role(args)
    elif cmd == 'deleterole':
        delete_role(args)
    elif cmd == 'addrole':
        add_role_to_player(args, clientid)
    elif cmd in ['removerole', 'rmrole']:
        remove_role_from_player(args, clientid)
    elif cmd in ['addcommand', 'addcmd']:
        add_command_to_role(args, clientid)
    elif cmd in ['removecommand', 'removecmd', 'rmcmd']:
        remove_command_to_role(args, clientid)
    elif cmd in ['add', 'whitelist']:
        whitelst_it(accountid, args)
    elif cmd == 'spectators':
        spectators(args)
    elif cmd == 'lobbytime':
        change_lobby_check_time(args)

# global functions for comnands
# kick cmd
def kick(args):
    """kicks the player from server"""
    if args == [] or args == [""]:
        _ba.chatmessage(" /kick client_id", sender_override ="Use[server]")
    elif args[0].isdigit() and not args[0] == -1:
        clientids = [player['client_id'] for player in _ba.get_game_roster()]
        if int(args[0]) in clientids:
            accountid = clientid_to_accountid(args[0])
            roles = get_roles()
            if accountid in roles["owner"]["ids"]:
                _ba.chatmessage("cant kick host")
            else:
                ban_time = 300
                _ba.disconnect_client(int(args[0]), ban_time=ban_time)

# remove cmd
def remove(args):
    """remove player from activity"""
    if args == [] or args == ['']:
        _ba.chatmessage(" /rm all or /rm index of list", sender_override ="Use[server]")
    elif args[0] == 'all':
        session = _ba.get_foreground_host_session()
        with _ba.Context(session):
            for i in session.sessionplayers:
                i.remove_from_game()
    elif args[0].isdigit():
        try:
            session = _ba.get_foreground_host_session()
            with _ba.Context(session): session.sessionplayers[int(args[0])].remove_from_game()
        except: _ba.chatmessage("player not found")

# nv cmd
tint = None

def nv(args):
    """converts night tint map"""
    global tint
    if tint is None:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            tint = activity.globalsnode.tint
    if args == [] or args == ['']:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            if activity.globalsnode.tint == (0.5, 0.5, 1.0):activity.globalsnode.tint = tint
            else:activity.globalsnode.tint = (0.5, 0.5, 1.0)

# dv cmd
def dv(args):
    """coverts day tint map"""
    global tint
    if tint is None:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            tint = activity.globalsnode.tint
    if args == [] or args == ['']:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            if activity.globalsnode.tint == (1.0,1.0,1.0):activity.globalsnode.tint = tint
            else:activity.globalsnode.tint = (1.0,1.0,1.0)

# end cmd
def end(args):
    """finish the game and begin next round"""
    if args == [] or args == ['']:
        activity = _ba.get_foreground_host_activity()
        with _ba.Context(activity):
            activity.end_game()

# quit cmd
def quit(args):
    """quit the game and restart it"""
    if args == [] or args == ['']:
        ba.quit()

# slow mo cmd
def slow_motion():
    """enables epic mode"""
    activity = _ba.get_foreground_host_activity()
    with _ba.Context(activity):
        if activity.globalsnode.slow_motion != True:
            activity.globalsnode.slow_motion = True 
        else:
            activity.globalsnode.slow_motion = False

# pause cmd
def pause():
    """pause's game"""
    activity = _ba.get_foreground_host_activity()
    with _ba.Context(activity):
        if activity.globalsnode.paused != True:
            activity.globalsnode.paused = True
        else:
            activity.globalsnode.paused = False

# rorate cmd
def rotate_camera():
    """changes game camera mode"""
    activity = _ba.get_foreground_host_activity()
    with _ba.Context(activity):
        if activity.globalsnode.camera_mode  !=  'rotate':
            activity.globalsnode.camera_mode  =  'rotate' 
        else:
            activity.globalsnode.camera_mode  =  'normal'

# create role cmd
def create_role(args):
    """creates role"""
    roles = get_roles()
    if not args[0] in roles and not args == [""]:
        pdata.create_role(args[0])
        _ba.chatmessage("created role {}".format(str(args[0])))
    else:
        _ba.chatmessage("role alwardy created")

# delete role cmd
def delete_role(args):
    """creates role"""
    roles = get_roles()
    if args[0] in roles and not args == [""]:
        pdata.delete_role(args[0])
        _ba.chatmessage("deleted role {}".format(str(args[0])))
    else:
        _ba.chatmessage("role not found")

# addrole cmd
def add_role_to_player(args, clientid):
    """ add role to given player"""
    session = _ba.get_foreground_host_session()
    try:
        with _ba.Context(session):
            id = session.sessionplayers[int(args[1])].get_account_id()
            name = session.sessionplayers[int(args[1])].getname(full=True, icon=True)
            try:
                pdata.add_player_role(args[0], id)
                _ba.chatmessage("added {} to {}".format(name, str(args[0])))
            except: _ba.chatmessage("role not found")
    except: _ba.screenmessage("/addrole {role} {number of list}", clients=[clientid], transient=True)

# removerole cmd
def remove_role_from_player(args, clientid):
    """remove role from given player"""
    session = _ba.get_foreground_host_session()
    try:
        with _ba.Context(session):
            id = session.sessionplayers[int(args[1])].get_account_id()
            name = session.sessionplayers[int(args[1])].getname(full=True, icon=True)
            try:
                pdata.remove_player_role(args[0], id)
                _ba.chatmessage("removed {} from {}".format(name, str(args[0])))
            except:
                _ba.chatmessage("role not found")
    except: _ba.screenmessage("/removerole {role} {number of list}", clients=[clientid], transient=True)


all_commands = ["changetag","createrole", "addrole", "removerole", "addcommand", "addcmd","removecommand","removecmd","kick","remove","rm","end","next","quit","restart","mute","mutechat","unmute","unmutechat","sm","slow","slowmo","nv","night","dv","day","pause","pausegame","cameraMode","camera_mode","rotate_camera","kill","die","heal","heath","curse","cur","sleep","sp","superpunch","gloves","punch","shield","protect","freeze","ice","unfreeze","thaw","gm","godmode","fly","inv","invisible","hl","headless","creepy","creep","celebrate","celeb","spaz"]

# addcmd cmd
def add_command_to_role(args, clientid):
    """add's command to role"""
    roles = get_roles()
    if args[0] in roles:
        if not args[1] in roles[str(args[0])]["commands"]:
            if args[1] in all_commands:
                pdata.add_command_role(args[0], args[1])
                _ba.chatmessage("added {} cmd to {}".format(str(args[1]), str(args[0])))
            else:
                _ba.chatmessage("unkown command")
        else: _ba.screenmessage("command alwardy in role", clients=[clientid], transient=True)
    else: _ba.chatmessage("role not found")

# removecmd cmd
def remove_command_to_role(args, clientid):
    """add's command to role"""
    roles = get_roles()
    help = "/addcmd {role} {cmd}"
    if args[0] in roles:
        if args[0] in roles and args[1] in roles[str(args[0])]["commands"] and args[1] in all_commands:
            if args[1] in all_commands:
                pdata.remove_command_role(args[0], args[1])
                _ba.chatmessage("removed {} cmd from {}".format(str(args[1]), str(args[0])))
            else:
                _ba.chatmessage("unkown command")
        else: _ba.screenmessage("command alwardy in role", clients=[clientid], transient=True)
    else: _ba.chatmessage("role not found")

# whitelist cmds
def whitelst_it(accountid : str, args):
    """enable disable whitelist and add player to white list"""
    settings = setting.get_settings_data()
    if args[0] == 'on':
        settings["white_list"]["whitelist_on"] = True
        setting.commit(settings)
        _ba.chatmessage("whitelist on")
        
    elif args[0] == 'off':
        settings["white_list"]["whitelist_on"] = False
        setting.commit(settings)
        _ba.chatmessage("whitelist off")
    else:
        rost = _ba.get_game_roster()
        for i in rost:
            if int(i['client_id']) == int(args[0]):
                add_to_white_list(i['account_id'], i['display_string'])
                _ba.chatmessage("whitelisted "+str(i['display_string']))
                add_commit_to_logs(accountid+" added "+i['account_id'])

def spectators(args):
    """spectators mode for tornament purpose"""
    if args[0] in ['on', 'off']:
        settings = setting.get_settings_data()
        
        if args[0] == 'on':
            settings["white_list"]["spectators"] = True
            setting.commit(settings)
            _ba.chatmessage("spectators on")
            
        elif args[0] == 'off':
            settings["white_list"]["spectators"] = False
            setting.commit(settings)
            _ba.chatmessage("spectators off")

def change_lobby_check_time(args):
    """looby check time"""
    if args[0].isdigit():
        arg = int(args[0])
        settings = setting.get_settings_data()
        settings["white_list"]["lobbychecktime"] = arg
        setting.commit(settings)
        _ba.chatmessage(f"lobby check time is {arg} now")
    else:
        _ba.chatmessage("must type numbe to change lobby check time")
