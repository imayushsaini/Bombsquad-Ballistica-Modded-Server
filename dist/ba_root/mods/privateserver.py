"""Define a simple example plugin."""

# ba_meta require api 6

# Private Server whitelist by Mr.Smoothy
from __future__ import annotations

from typing import TYPE_CHECKING

import ba,json,_ba,time

if TYPE_CHECKING:
    pass
import datetime
from ba._enums import TimeType


whitelist_on=True   # change it by chat commands  for by editing here 
spectators=False   #    ,,           ,,                  ,,        ,,   False means spectating not allowed
whitelist={}   # dont change 
lobbychecktime=3   # time in seconds, to check lobby players ...  increase time ,for more time unwanted players can watch match  
                 #   decrease time , kick them fast ,    but can also give some lagg to the server , adjust yourself acrd. to cpu power

admins=['pb-JiNJARBaXEFBVF9HFkNXXF1EF0ZaRlZE']     # dirty admin system , for now , until we get good working chat commands


def inWhiteList(id):
    global whitelist
    if id in whitelist:
        return True
    else:
        return False
def addToWhitelist(id,displaystr):
    global whitelist
    if id not in whitelist:
        whitelist[id]=[displaystr]
    else:
        whitelist[id].append(displaystr)
    f=open("whitelist.json","w")
    json.dump(whitelist,f,indent=4)
    f.close()

def handlechat(msg,clientid):
    gg=_ba.get_game_roster()
    acc_id="LOL"
    if msg.startswith("/"):
        for clt in gg:
            if clt['client_id'] ==clientid:
                acc_id=clt['account_id']
        global admins
        if acc_id in admins:
            commands(acc_id ,msg)
def handlerequest(player):
    if whitelist_on:
        if inWhiteList(player.get_account_id()):
            pass
        else:
            for clt in _ba.get_game_roster():
                if clt['account_id']==player.get_account_id():
                    
                    f=open("loggs.txt",'a+')
                    f.write("kicked for joining"+clt['account_id']+"\n")
                    f.close()
                    _ba.disconnect_client(clt['client_id'])




def commands(acc_id,msg):
    global whitelist
    global whitelist_on
    global spectators
    cmnd=msg.split(" ")[0]
    
    args=msg.split(" ")[1:]
    if cmnd=='/add' and args!=[]:
        
        gg=_ba.get_game_roster()
        for clt in gg:
            if clt['client_id']==int(args[0]):
                
                addToWhitelist(clt['account_id'],clt['display_string'])
                f=open("loggs.txt",'a+')
                f.write(acc_id+" added "+clt['account_id']+"\n")
                f.close()
                ba.screenmessage(clt['display_string']+" whitelisted")
    if cmnd=='/whitelist':
        whitelist_on=whitelist_on==False
        if whitelist_on:
            ba.screenmessage("WhiteList turned on")
        else:
            ba.screenmessage("whitelist turned off")
    if cmnd=='/spectators':
        spectators=spectators==False
        if spectators:
            ba.screenmessage("Spectators can watch now")
        else:
            ba.screenmessage("Spectators will be kicked")
            


def dstrinWhiteList(dstr):
    global whitelist
    return any(dstr in chici for chici in whitelist.values())


# ba_meta export plugin
class private(ba.Plugin):
    """My first ballistica plugin!"""

    def __init__(self):
        global whitelist
        global whitelist_on
        global spectators
        global lobbychecktime
        
        try:
            f=open("whitelist.json")
            dat=json.loads(f.read())
            whitelist=dat
            f.close()
        except:
            print("no whitelist detected , creating one")
            self.li={}
            self.li['pb-JiNJARBaXEFBVF9HFkNXXF1EF0ZaRlZE']=['smoothyki-id','mr.smoothy']
            f=open("whitelist.json",'w')
            json.dump(self.li,f,indent=4)
            f.close()
        if whitelist_on and not spectators:
            self.timerr=ba.Timer(lobbychecktime,self.checklobby,repeat=True,timetype=TimeType.REAL)
    def checklobby(self):
        global whitelist_on
        global whitelist
        global spectators
        
        try:
            gg=_ba.get_game_roster()
            for clt in gg:
                if clt['account_id'] in whitelist and clt['account_id']!='':
                    pass
                else:
                    f=open("loggs.txt","a+")
                    f.write("Kicked from lobby"+clt['account_id']+" "+clt['spec_string']+"\n")
                    _ba.disconnect_client(clt['client_id'])
        except:
            pass
               
            

    


