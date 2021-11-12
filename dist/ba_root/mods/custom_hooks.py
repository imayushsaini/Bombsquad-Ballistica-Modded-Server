
import ba
import _ba
from chatHandle import handlechat
import setting
def filter_chat_message(msg, client_id):

    return handlechat.filter_chat_message(msg, client_id)


def on_app_launch():
    from tools import whitelist
    whitelist.Whitelist()
    bootstraping()

	#something

def score_screen_on_begin(_stats):
    pass
	#stats

def playerspaz_init(player):
    pass
	#add tag,rank,effect





def bootstraping():
    print("starting server configuration")
    #_ba.disconnect_client=new_disconnect
    settings = setting.get_settings_data()
    _ba.set_server_device_name(settings["HostDeviceName"])
    _ba.set_server_name(settings["HostName"])
    _ba.set_transparent_kickvote(settings["ShowKickVoteStarterName"])
    _ba.set_kickvote_msg_type(settings["KickVoteMsgType"])



def new_disconnect(clid,duration=120):
    print("new new_disconnect")
    _ba.ban_client(clid,duration)

