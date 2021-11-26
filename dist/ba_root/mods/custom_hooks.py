
import ba
import _ba
from chatHandle import handlechat
import setting
from tools import servercheck
from tools import ServerUpdate
import _thread
from stats import mystats
from datetime import datetime
from ba import _activity

from typing import Optional, Any
from spazmod import modifyspaz
from bastd.activity import dualteamscore
from bastd.activity import multiteamscore
from bastd.actor.zoomtext import ZoomText
# from tools import fireflies
settings = setting.get_settings_data()

def filter_chat_message(msg, client_id):

    return handlechat.filter_chat_message(msg, client_id)


def on_app_launch():
    from tools import whitelist
    whitelist.Whitelist()
    bootstraping()
    servercheck.checkserver().start()
    ServerUpdate.check()



	#something

def score_screen_on_begin(_stats):
    pass
	#stats

def playerspaz_init(player):
    pass
	#add tag,rank,effect





def bootstraping():
    
    #_ba.disconnect_client=new_disconnect
    
    _ba.set_server_device_name(settings["HostDeviceName"])
    _ba.set_server_name(settings["HostName"])
    _ba.set_transparent_kickvote(settings["ShowKickVoteStarterName"])
    _ba.set_kickvote_msg_type(settings["KickVoteMsgType"])
    _thread.start_new_thread(mystats.refreshStats,())




def new_disconnect(clid,duration=120):
    print("new new_disconnect")
    _ba.ban_client(clid,duration)

org_begin=ba._activity.Activity.on_begin 
def new_begin(self):
    org_begin(self)
    night_mode()
    
ba._activity.Activity.on_begin=new_begin

org_end=ba._activity.Activity.end
def new_end(self,results:Any=None,delay:float=0.0,force:bool=False):
    
    org_end(self,results,delay,force)
ba._activity.Activity.end=new_end


def night_mode():

    if(settings['autoNightMode']['enable']):

        start=datetime.strptime(settings['autoNightMode']['startTime'],"%H:%M")
        end=datetime.strptime(settings['autoNightMode']['endTime'],"%H:%M")
        now=datetime.now()
        
        if now.time() > start.time() or now.time() < end.time():
            activity = _ba.get_foreground_host_activity()

            activity.globalsnode.tint = (0.5, 0.7, 1.0)

            # if settings['autoNightMode']['fireflies']:
            #     fireflies.factory()



