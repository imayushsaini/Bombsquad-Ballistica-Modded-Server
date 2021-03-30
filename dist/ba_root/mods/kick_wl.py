import ba,_ba,roles,mysettings
from _ba import disconnect_client
white = []
def filter_disconnectClient(client_id: int, ban_time: int= 300, request_from = None):
    ros = _ba.get_game_roster()
    whiteList = roles.unKickable + white
    request_by = None
    ID = None
    for i in ros:
        if (request_from is not None) and (i['client_id'] == request_from):
            request_by = i['account_id']
    for i in ros:
        if (client_id == -1):
            ba.screenmessage(f"Can't Kick Host !", color=(1,0,0))
            return
        if (request_from is not None) and (client_id == request_from):
            ba.screenmessage(f"Can't Kick Yourself !", color=(1,0,0))
            return
        if (i['client_id'] == client_id):
            ID = i['account_id']
            name = i['display_string']
            if ID in whiteList:
                if (request_by is not None) and (request_by in roles.owners) and (ID not in roles.owners):
                    disconnect_client(client_id, ban_time)
                    return
                if mysettings.announce_unkickable: ba.screenmessage(f"'{name}' is immune from being kicked, xD!", color=(1,0,0))
                return
            else: disconnect_client(client_id, ban_time)
_ba.disconnect_client = filter_disconnectClient