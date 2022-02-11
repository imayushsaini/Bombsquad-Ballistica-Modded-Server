
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
from bastd.activity import drawscore
from bastd.actor.zoomtext import ZoomText
from tools import TeamBalancer
from bastd.activity.coopscore import CoopScoreScreen
from ba import _hooks
from tools import Logger


from playersData import pdata

from tools import afk_check
# from bastd.activity.multiteamvictory import 
from tools import fireflies
settings = setting.get_settings_data()

def filter_chat_message(msg, client_id):

    return handlechat.filter_chat_message(msg, client_id)


def on_app_launch():
    bootstraping()
    servercheck.checkserver().start()
    ServerUpdate.check()
    if settings["afk_remover"]['enable']:
        afk_check.checkIdle().start()



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
    if settings["elPatronPowerups"]["enable"]:
        from tools import elPatronPowerups
        elPatronPowerups.enable()
    if settings["mikirogQuickTurn"]["enable"]:
        from tools import wavedash

    if settings["whitelist"]:
        pdata.loadWhitelist()
    if settings["discordbot"]["enable"]:
        from tools import discordbot
        discordbot.token=settings["discordbot"]["token"]
        discordbot.liveStatsChannelID=settings["discordbot"]["liveStatsChannelID"]
        discordbot.logsChannelID=settings["discordbot"]["logsChannelID"]
        discordbot.liveChat=settings["discordbot"]["liveChat"]
        discordbot.BsDataThread()
        discordbot.init()
    importgames()

        




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
    act=_ba.get_foreground_host_activity()
    if isinstance(act,CoopScoreScreen):
        TeamBalancer.checkToExitCoop()
    
    org_end(self,results,delay,force)
    
ba._activity.Activity.end=new_end
org_player_join=ba._activity.Activity.on_player_join
def on_player_join(self, player) -> None:
    TeamBalancer.on_player_join()
    org_player_join(self,player)
ba._activity.Activity.on_player_join=on_player_join



def night_mode():

    if(settings['autoNightMode']['enable']):

        start=datetime.strptime(settings['autoNightMode']['startTime'],"%H:%M")
        end=datetime.strptime(settings['autoNightMode']['endTime'],"%H:%M")
        now=datetime.now()
        
        if now.time() > start.time() or now.time() < end.time():
            activity = _ba.get_foreground_host_activity()

            activity.globalsnode.tint = (0.5, 0.7, 1.0)

            if settings['autoNightMode']['fireflies']:
                fireflies.factory(settings['autoNightMode']["fireflies_random_color"])



from tools import dualteamscore as newdts

if settings["newResultBoard"]:


    dualteamscore.TeamVictoryScoreScreenActivity=  newdts.TeamVictoryScoreScreenActivity

    multiteamscore.MultiTeamScoreScreenActivity.show_player_scores = newdts.show_player_scores

    drawscore.DrawScoreScreenActivity=newdts.DrawScoreScreenActivity

def scoreScreenBegin():
    TeamBalancer.balanceTeams()


def kick_vote_started(by,to):
    Logger.log(by+" started kick vote for "+to)

_hooks.kick_vote_started=kick_vote_started

def on_kicked(id):
    Logger.log(id+" kicked by kickvotes")

_hooks.on_kicked=on_kicked

def on_kick_vote_end():
    Logger.log("Kick vote End")



import os
import importlib
def importgames():
    games=os.listdir("ba_root/mods/games")
    for game in games:
        if game.endswith(".py") or game.endswith(".so"):
            importlib.import_module("games."+game.replace(".so","").replace(".py",""))
    maps=os.listdir("ba_root/mods/maps")
    for map in maps:
        if map.endswith(".py") or map.endswith(".so"):
            importlib.import_module("maps."+map.replace(".so","").replace(".py",""))



    