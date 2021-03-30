# -*- coding: utf-8 -*-
# ba_meta require api 6
import _ba,ba,os,json,random,roles,bastd
from typing import List, Sequence, Optional, Dict, Any
from datetime import datetime
from administrator_setup import *

os.environ['BA_ACCESS_CHECK_VERBOSE'] = '1'

#Create Empty json Files if Doesn't Exists
emptyData = {}
default_members_data = {'special':{},'admins':{},'vips':{},'banList':{},'customTag':{},'customList':{}}
if not os.path.exists(playerLogFile):
    with open(playerLogFile, 'w') as f:
        f.write(json.dumps(emptyData))
        f.close()
if not os.path.exists(statsFile):
    with open(statsFile, 'w') as f:
        f.write(json.dumps(emptyData, indent=4))
        f.close()
if not os.path.exists(bankFile):
    with open(bankFile, 'w') as f:
        f.write(json.dumps(emptyData))
        f.close()
if not os.path.exists(membersFile):
    with open(membersFile, 'w') as f:
        f.write(json.dumps(default_members_data, indent=4))
        f.close()
if not os.path.exists(cmdLogFile):
    with open(cmdLogFile, 'w') as f:
        f.write("This is the Start of the Logs\n Logs will be in descending order (means the last used cmd will be in 1st line)")
        f.close()
if not os.path.exists(chatLogFile):
    with open(chatLogFile, 'w') as f:
        f.write("This is the Start of the Logs\n Logs will be in descending order (means the last chat will be in 1st line)")
        f.close()
if not os.path.exists(lastMsgFile):
    with open(lastMsgFile, 'w') as f:
        f.write(json.dumps(emptyData))
        f.close()

#Stats Management
enableStats = True
date = datetime.now().strftime('%d')
if int(date) < settings['statsEndDate']:
    enableStats = True
elif int(date) == settings['statsEndDate'] and ba.do_once():
    backupDate = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    os.rename(statsFile, statsFile + '.backup' + backupDate)
    enableStats = False
else: enableStats = False
enableStats = settings['stats']

#Useful Functions
def get_cmd_logs_as_list():
    cl = open(cmdLogFile, 'r')
    log = cl.read()
    return [str(row) for row in log]

def get_chat_logs_as_list():
    cmdl = open(chatLogFile, 'r')
    log = cmdl.read()
    return [str(row) for row in log]

def sendError(msg: str, ID: int = None):
    if ID is not None:
        ba.screenmessage(msg, color=(1,0,0), clients=[ID], transient=True)
    else:
        ba.screenmessage(msg, color=(1,0,0), transient=True)

def getNamesFromLog(ID: str):
    f = open(playerLogFile, 'r')
    try:
        data = json.loads(f.read())
    except:
        sendError("Logs not found", None)
        return
    if ID in data:
        return data[ID]
    else: ba.screenmessage(f"Player not found in logs")

def getStats():
    try:
        f = open(statsFile, 'r')
        return json.loads(f.read())
        f.close()
    except:
        sendError("Stats not found")
        return {}

def printStatsByID(ID: str):
    stat = getStats()
    if ID in stat:
        p_name = str(stat[ID]['name'])
        p_rank = str(stat[ID]['rank'])
        #p_dmg = str(stat[ID]['total_damage']) #wrong data, don't use
        p_score = str(stat[ID]['scores'])
        p_kills = str(stat[ID]['kills'])
        p_deaths = str(stat[ID]['deaths'])
        p_games = str(stat[ID]['games'])
        if settings['enableCoinSystem']:
            from coinSystem import getCoins
            coins = getCoins(ID)
            m = f"{p_name}||Rank:{p_rank}|{tic}{str(coins)}|Score:{p_score}|Kills:{p_kills}|Deaths:{p_deaths}|Games:{p_games}"
        else:
            m = f"{p_name}||Rank:{p_rank}|Score:{p_score}|Kills:{p_kills}|Deaths:{p_deaths}|Games:{p_games}"
        _ba.chatmessage(m)
    else:
        sendError("Player Not Found in stats", None)

#PlayerLogs Updater (runs after each 3 seconds again and again)
def CheckPlayers():
    stat = {}
    data = {}
    ros = _ba.get_game_roster()

    #Check for expired items.
    if settings['enableCoinSystem']:
        import coinSystem
        coinSystem.checkExpiredItems()
        coinSystem.checkTagExpiry()

    #Start Our Main Process
    for i in ros:
        if (i is not None) and (i != {}):
            name = i['display_string']
            cID = i['client_id']
            uID = i['account_id']

            #If Bots came, BAN Them PERMANENTLY... 
            if (cID != -1) and (name.startswith('\ue030Server')):
                _ba.disconnect_client(cID, 99999999999999999*9999999999999)

            #If master-server can't return uniqueID, ignore him/her for that time
            if (uID is None) or (uID == 'null'): continue

            #Check whether server is in whiteListMode
            if settings['whiteListMode'] and (uID not in roles.serverWhiteList): _ba.disconnect_client(cID)

            #update name in stats
            stat = getStats()
            if uID in stat:
                stat[uID]['name'] = name
                #stat[uID]['name_html'] = name
                n = open(statsFile, 'w')
                n.write(json.dumps(stat, indent=4))
                n.close()

            #Check for Banned Players,also if their name not in banned add it
            if (uID in roles.banList):
                if (name not in roles.banList[uID]):
                    roles.banList[uID].append(name)
                    with open(python_path + '/roles.py') as (file):
                        s = [ row for row in file ]
                        s[2] = 'banList = ' + str(roles.banList) + '\n'
                        f = open(python_path + '/roles.py', 'w')
                        for i in s:
                            f.write(i)
                        f.close()
                sendError(f"Hey {name}, You are Banned, Sorry :(", cID)
                _ba.disconnect_client(cID)

            #update name in all type of variables and logs...
            #playerLogFile.json
            f = open(playerLogFile, 'r')
            data = json.loads(f.read())
            if uID not in data: data[uID] = {'aid':uID, 'devices':[], 'last_played': 'Joined For the First time'}
            if name not in data[uID]['devices']: data[uID]['devices'].append(name)
            a = open(playerLogFile, 'w')
            a.write(json.dumps(data, indent=4))
            a.close()
            #Roles.serverWhiteList
            if (uID in roles.serverWhiteList):
                if (name not in roles.serverWhiteList[uID]):
                    roles.serverWhiteList[uID].append(name)
                    with open(python_path + '/roles.py') as (file):
                        s = [ row for row in file ]
                        s[3] = 'serverWhiteList = ' + str(roles.serverWhiteList) + '\n'
                        f = open(python_path + '/roles.py', 'w')
                        for i in s:
                            f.write(i)
                        f.close()
cp_timer = ba.Timer(3, ba.Call(CheckPlayers), timetype=ba.TimeType.REAL, repeat=True)

################## REJOIN COOL DOWN MANAGEMENT (Refreshed for each 0.1 seconds...) ################
class RejoinCoolDownManager(object):
    def __init__(self):
        '''The Rejoin Cool Down - RJCD Manager. Makes a cooldown for players who leave and join again'''
        self.white = roles.owners + roles.admins
        self.whiteList = []
        self.old = {}
        self.CD = {}
        self.counter = {}
        #UDDATE TIMER
        self.uTimer = ba.Timer(5, ba.Call(self.update), timetype=ba.TimeType.REAL, repeat=True)
        #CORE RUN TIMER
        self.rjcdTimer = ba.Timer(0.1, ba.Call(self.Core), timetype=ba.TimeType.REAL, repeat=True)
        #REFRESH TIMER
        self.refresh_timer = ba.Timer(60, ba.Call(self.refresh), timetype=ba.TimeType.REAL, repeat=True)

    def update(self):
        '''The Thingy Which Updates the whitelist of RJCD from PlayerLogs.json'''
        log = {}
        try:
            if os.path.exists(playerLogFile):
                with open(playerLogFile, 'r') as f:
                    log = json.loads(f.read())
            for w in self.white:
                if (w in log) and (log[w]['devices']):
                    for wn in log[w]['devices']:
                        if wn not in self.whiteList: self.whiteList.append(wn)
        except:
            pass

    def Core(self):
        '''The Core Processor Of RJCD. Runs for each 0.5 seconds'''
        time = int(ba.time(timetype=ba.TimeType.REAL, timeformat=ba.TimeFormat.MILLISECONDS))
        time_real_world = datetime.now().strftime("%S:%M:%H - %d %b %y")
        ros = _ba.get_game_roster()
        #Collect all Client's display string except our server (host)
        players = {}
        for i in ros:
            if i['client_id'] != -1: players[i['display_string']] = i['account_id']
        #Check if Players in Cool Down joins
        for i in ros:
            name = i['display_string']
            c_id = i['client_id']
            if (c_id != -1) and (name not in self.whiteList) and (name in self.CD):
                if time < self.CD[name]:
                    bal = int(self.CD[name] - time)
                    if announce_cooldown: _ba.chatmessage(f"{str(name)} has now a cooldown of {str(bal)} secs to rejoin...")
                    _ba.disconnect_client(c_id, bal)
        #Compare last players list with current
        for n, uID in self.old.items():
            #If a client's display string is missing in new roster, he/she had left
            if (n not in [k for k,v in players.items()]):

                #Fair CoolDownTime for the player who just left
                t = time + cool_down_time

                #Add him/her leaving time to playerLog, whether added to CD or not - we just want last played time
                f = open(playerLogFile, 'r')
                data = json.loads(f.read())
                if uID not in data: data[uID] = {'aid':uID, 'devices':[], 'last_played': time_real_world}
                if n not in data[uID]['devices']: data[uID]['devices'].append(n)
                data[uID]['last_played'] = time_real_world
                a = open(playerLogFile, 'w')
                a.write(json.dumps(data, indent=4))
                a.close()

                #Make Sure We Don't touch Whitelist members
                if (n in self.whiteList):
                    continue

                #Add him/her to counter if he left for the first time
                if n not in self.counter: self.counter[n] = [1, int(time + player_rjcd_reset_time)]
                if n in self.counter:
                    t = int(time + cool_down_time)
                    self.CD[n] = t
                    #the below counter system need to be fixed
                    '''#replace his last counters if he left after playing 'player_rjcd_reset_time' seconds
                    if self.counter[n][1] <= time:
                        self.counter[n][0] = 1
                        self.counter[n][1] = int(time + player_rjcd_reset_time)
                        continue
                    #Add him/her to RJCD if Limit Reeached
                    if self.counter[n][0] >= rejoin_limit:
                        t = int(time + cool_down_time)
                        self.CD[n] = t
                        print(f"'{n}' has been added to RJCD: CD time = {t}")
                    #Add counter if he/she has not touched the Limit
                    else:
                        self.counter[n][0] += 1
                        self.counter[n][1] = int(time + player_rjcd_reset_time)
                print(self.counter)'''
        #make this players list as old players for using it next time
        self.old = players

    def refresh(self):
        '''Refresh all RJCD Things for each 60 seconds'''
        #Check UPDATE Timer
        if not os.path.exists(playerLogFile):
            self.uTimer = None
            print("mysettings.py : RejoinCoolDownManager.Core -> playerLogFile Path dosen't exits!")
        if os.path.exists(playerLogFile) and enableRJCD and self.uTimer == None: self.uTimer = ba.Timer(5, ba.Call(self.update), timetype=ba.TimeType.REAL, repeat=True)
        #Check Core Timer
        if enableRJCD and not self.rjcdTimer: self.rjcdTimer = ba.Timer(0.1, ba.Call(self.Core), timetype=ba.TimeType.REAL, repeat=True)
        if not enableRJCD and self.rjcdTimer: self.rjcdTimer = None

RejoinCoolDownManager()
#####################################################################################################

#Ultimate Function which imports all mod files
imported = []
black = ['mysettings.py', 'administrator_setup.py']
def run_nk2_script():
    global imported
    for i, d in enumerate(directories):
        if os.path.isdir(d):
            try: dirlist = os.listdir(d)
            except Exception as e:
                import errno
                if (type(e) == OSError
                        and e.errno in (errno.EACCES, errno.ENOENT)):
                    pass # we expect these sometimes..
                else:
                    ba.print_exception('Error while collecting various files/modules during : '
                                      'mysettings.run_nk2_script(): in the path \''+d+'\'')
                dirlist = []
        else: dirlist = []
        for name in dirlist:
            if (name.endswith('.py')) and (name not in black):
                moduleName = name.replace('.py', '')
                if (name not in imported):
                    module = __import__(moduleName)
                    imported.append(name)
    print("All Custom Modules Checked!")