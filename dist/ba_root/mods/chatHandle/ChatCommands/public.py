# Released under the MIT License. See LICENSE for details.
#
import ba
import _ba
from ._handlers import clientid_to_myself

# cmds
cmds = ['me', 'list', 'uniqeid']
cmdaliases = ['stats', 'score', 'rank', 'myself', 'l', 'id', 'pb-id', 'pb', 'accountid']

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
    if cmd in ['me', 'stats', 'score', 'rank', 'myself']:
        stats()
    elif cmd in ['list', 'l']:
        list(clientid)
    elif cmd in ['uniqeid', 'id', 'pb-id', 'pb' , 'accountid']:
        accountid_request(args, clientid, accountid)


# global functions for comnands
# TODO: stats
def stats():
    return

# list - name, clientid , index
def list(clientid: int) -> None:
    """Returns The List Of Players Clientids and index"""
    p = u'{0:^30}{1:^15}{2:^10}'
    seprator = '\n_____________________________________\n'
    list = p.format('Name', 'Client ID' , 'Player ID') + seprator
    
    session = _ba.get_foreground_host_session()
    with _ba.Context(session):
        for i in session.sessionplayers:
            list += p.format(i.getname(icon = False).ljust(20), i.inputdevice.client_id, session.sessionplayers.index(i)) +"\n"
    ba.screenmessage(str(list), clients=[clientid], transient=True, color=(0, 2.55, 2.55))

# player accountid ->  pb-1234 
def accountid_request(args: list, clientid: int, accountid: str) -> None:
    """Returns The Account Id Of Players"""
    if args == [] or args == ['']:
        myself = clientid_to_myself(clientid)
        session = _ba.get_foreground_host_session()
        
        with _ba.Context(session):
            player = session.sessionplayers[myself]
            name = player.getname(full=True, icon=True)
            _ba.chatmessage(f" {name}'s account id is '{accountid}'")
    else:
        try:
            session = _ba.get_foreground_host_session()
            with _ba.Context(session):
                player = session.sessionplayers[int(args[0])]
                name = player.getname(full=True, icon=True)
                accountid = player.get_account_id()
                _ba.chatmessage(f" {name}'s account id is '{accountid}'")
        except:_ba.chatmessage("player not found")
