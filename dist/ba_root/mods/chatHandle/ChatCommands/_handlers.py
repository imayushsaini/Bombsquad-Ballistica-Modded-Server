# Released under the MIT License. See LICENSE for details.
import ba
import _ba
import json

# helper functions, useful reduces lot's of lines of code
# handles actor node message for single given node
def handlemsg(player, msg):
    """Handles Msg For Single Player"""
    activity = _ba.get_foreground_host_activity()
    with _ba.Context(activity):
        activity.players[int(player)].actor.node.handlemessage(msg)

# handles actot node message for all players in activity
def handlemsg_all(msg):
    """Handle message for all players in activity"""
    activity = _ba.get_foreground_host_activity()
    with _ba.Context(activity):
        for player in activity.players:
            player.actor.node.handlemessage(msg)

# clientid to index of player, useful to some cmds to use for self like /heal
def clientid_to_myself(clientid):
    """Return Player Index Of Self Player"""
    session = _ba.get_foreground_host_session()
    with _ba.Context(session):
        for i in range(len(session.sessionplayers)):
            if session.sessionplayers[i].inputdevice.client_id == clientid:
                return int(session.sessionplayers.index(session.sessionplayers[i]))

# make's changes in roles file
def commit(changes):
    """'commit changes in roles"""
    p = _ba.env()['python_directory_user']+'/playersData/roles.json'
    with open(p, "w") as f:
        json.dump(changes, f, indent=4)

# get to roles file and return all roles
def get_roles():
    """helper function returns roles dir"""
    p = _ba.env()['python_directory_user']+'/playersData/roles.json'
    with open(p, "r") as f:
        roles = json.load(f)
    return roles

# clientid to accountid, very useful in some cases
def clientid_to_accountid(clientid):
    """clientid to accoutid using roster"""
    for i in _ba.get_game_roster():
        if i['client_id'] == clientid:
            return i['account_id']
    return None