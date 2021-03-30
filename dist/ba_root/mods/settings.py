settings = {'enableChatFilter': True, 'enableTop5effects': True, 'enableTop5commands': False, 'enableCoinSystem': True, 'pUpLight': True, 'pUpTag': True, 'pUpShield': True, 'screenTexts': True, 'statsEndDate': 25, 'whiteListMode': False, 'chatWhitelistMode': False, 'showHP': True, 'hitTexts': True, 'hideCmds': False}
powerups = {'shield': False, 'punch': False, 'sticky': True, 'curse': False, 'triple': True, 'speed': True, 'impact': True, 'cc': True, 'land': True, 'ice': False, 'health': True}
chatCoolDownTime = 3 #In Seconds

#Provide the account_id (pb-ID) of owners (add other players details in roles.py)
#Also provide the same/exact/accurate name u provided for ur server
#This name will be defaulty added to Website's html document, so u don't need to change from time to time
owners = ['pb-IF40V1hYXQ=='] #This is my ID which i had put when i was testing...
server_name = "Test Server" #Copy paste from bombsquad_server.py or config.yaml
#This server name will change temproraly if u change name through chatCmd, results to change in html too (temproraly)

#anounce when a player was tried to kicked but was in whitelist
announce_unkickable = True

# -*- coding: utf-8 -*-
# ba_meta require api 6
###################### Don't touch the below things... ##########################
import _ba,ba,os,json,random,roles
from typing import List, Sequence, Optional, Dict, Any
from datetime import datetime


############### DO NOT CHANGE ANY STRUCTURE / ORDER / LINES / NAME OF THE VARIABLES, ETC..  ELSE RIP SCRIPT... ###############
##################################### SETTINGUP IS STARTING FROM THE BELOW THINGS #####################################


##### FILE PATH SETUP - START ####

#The below lines till line number 34, no need to edit...
#Note: Use the 'python' if my scripts are placed in dist/ba_data/python
#Use the 'mods' if my scripts are placed in dist/ba_root/mods
path = 'mods' #'python'
#Don't change the below 4 lines
directories = [_ba.env()['python_directory_user'], _ba.env()['python_directory_app']]
python_path = None
if path == 'mods': python_path = directories[0]
if path == 'python': python_path = directories[1]

#Edit the File Paths according to ur need...
#
htmlFile = python_path + '/mydata/stats.html' #'/var/www/mydomainname.ml/stats.html'
#Log file of players contains their device ids
playerLogFile = python_path + '/logs/PlayerLogs.json' #'/home/ubuntu/folderName/logs/PlayerLogs.json'
#stats file contains their rank, score, kills, deaths, kd (killDeathRatio), avg_score (averageScore), games (gamesPlayed) and account_id
statsFile = python_path + '/mydata/stats.json' #'/home/ubuntu/folderName/stats.json'
#bankFile contains their server currency data
bankFile = python_path + '/mydata/bank.json' #'/home/ubuntu/folderName/bank.json'
#this contains of the various people in roles.py (owners,admins,banned players,etc)
membersFile = python_path + '/mydata/members.json' #'/home/ubuntu/folderName/members.json'
#this contains only the successful commands executed by people in the server
cmdLogFile = python_path + '/logs/cmd_logs.txt' #'/home/ubuntu/folderName/logs/cmd_logs.json'
#this contains all chats sent in server including cmds
chatLogFile = python_path + '/logs/chatLogs.txt' #'/home/ubuntu/folderName/logs/chatLogs.txt'
#this will have only last msg sent in server (Useable for live status data)
lastMsgFile = python_path + '/logs/last_message.json' #'/home/ubuntu/folderName/logs/last_message.json'

##### FILE PATH SETUP - END ####

##### REJOIN COOL DOWN - START ####

"""Rejoin CoolDown Manager Setup for 1.5.29 by CocaCola aka FireFighter1027#3441"""
#Whether to enable Rejoin Cool Down or Not
enableRJCD = True

#Add extra white list here (PC_id, Android_id, Google_id)
#Should not add pb_id (Note: Owners and admins are defaultly added through logPlayers.json)
#PC/Android icon = '\ue030'
#Google icon = '\ue020'
whiteList = ['\ue020FireFighter1027', '\ue030PC276734'] #Both my IDs xD

#Whether to send msg when client added to cooldown
announce_cooldown = True #False

#Number of times that a client can rejoin as for accidential leaving..
#if a client rejoined 1 times greater than the following,
#he/she will be kicked
rejoin_limit = 2

#Manage the cool down time
cool_down_time = 20 #seconds
cool_down_time *= 1000 #Don't touch this line (converts into millisec)

#Removes a player from RJCD if he/she has been playing for the following
#time period without leaving inbetween
player_rjcd_reset_time = 60 #seconds
player_rjcd_reset_time *= 1000 #Don't touch this line (converts into millisec)

##### REJOIN COOL DOWN - END ####

##################### OTHER VARIABLES - Edit values if Necessary #####################

questionsList = {'Who is the owner of this server?': ['eoni', 'ankit', 'aleena'],
                 'Who is the editor of this server?': ['eoni', 'ankit', 'aleena', 'nk2'], 
                 'What is the smallest planet in the solar system?': ['mercury'],
                 'Which type of currency used in this game?': ['tickets'],
                 'Who created this game?': ['eric', 'eric froemling'],
                 'What is the main theme of this server, (fun or competition)?': ['fun'],
                 'This game is made up of which Programming lang..?': ['python'],
                 'In which planet do we live?': ['earth'],
                 'add': [None], 
                 'multiply': [None]}
questionDelay = 30 #seconds
screenTextColor = None #format = (red, green, blue)
tic = ba.charstr(ba.SpecialChar.TICKET) #not working in 1.5
uni = {'\\c': '\\ue043','\\sh': '\\ue049','\\v':'\\ue04c', '\\h': '\\ue047', '\\z':'\\ue044', '\\n': '\\ue04b', '\\b': '\\ue04b', '\\d': '\\ue048', '\\s': '\\ue046', '\\f': '\\ue04f', '\\l': '\\ue00c', '\\g': '\\ue02c', '\\t': '\\ue02f', '\\i': '\\ue03a'}
multicolor = {0:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),250:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),500:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),750:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),1000:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),1250:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),1500:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),1750:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),2000:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),2250:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),2500:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0))}
tournament_texts = []
texts = [f'\\ue043Welcome to {tic}Eoni\\ue043',
         f"Use '/shop commands' to see commands available to use.",
         f"Use '/shop effects' to see effects available and their price.",
         f"Use '/me' or '/stats' to see your {tic} and your stats in this server",
         f"Use '/buy' to buy effects that you like",
         f"Use '/donate' to give some of your tickets to other players",
         f"Use '/scoretocash' to convert some of your score into {tic}\nCurrent Rate: 5scores = {tic}1"]
all_cmds = [
   #PUBLIC or STATS CMDS
   '/help',
   '/list',
   '/id',
   ('/me','/stats','/rank','/myself'),
   '/donate',
   '/buy',
   '/shop',
   '/cashtoscore',
   '/scoretocash',
   #PUBLIC or COIN SYSTEM CMDS
   '/nv',
   '/ooh',
   '/playSound',
   '/box',
   '/boxall',
   '/spaz',
   '/spazall',
   '/inv',
   '/invall',
   '/tex',
   '/texall',
   '/freeze',
   '/freezeall',
   '/sleep',
   '/sleepall',
   '/thaw',
   '/thawall',
   '/kill',
   '/killall',
   '/end',
   '/hug',
   '/hugall',
   '/sm',
   '/fly',
   '/flyall',
   '/curse',
   '/curseall',
   '/heal',
   '/healall',
   '/custom',
   #ADMIN CMDS
   '/bunny', #'/bunnyNotYetModded',
   '/lm',
   '/gp',
   '/whois',
   '/mute',
   '/unmute',
   '/kick',
   '/kickall',
   '/remove',
   '/removeall',
   '/shatter',
   '/shatterall',
   ('/quit','/restartserver','/restart'),
   '/ac',
   '/tint',
   '/reflections',
   '/floorreflection',
   ('/icy','/exchange'),
   ('/iceoff','/hockey'),
   '/vip',
   '/maxPlayers',
   '/say',
   #OWNER CMDS
   '/kickvote',
   '/top',
   ('/setScore','/reset'),
   '/warn',
   '/clearwarns',
   '/whoinqueue',
   '/text',
   '/admin',
   '/ban',
   '/special',
   '/partyname',
   '/party',
   '/pause',
   ('/setscreentextcolor', '/settextcolor', '/setscreencolor'),
   ('/setchatcooldowntime', '/setchatcdtime', '/setchattime'),
   '/settings']
availableCommands = {'/nv': 50, 
   '/ooh': 5, 
   '/playSound': 10, 
   '/box': 30, 
   '/boxall': 60, 
   '/spaz': 50, 
   '/spazall': 100, 
   '/inv': 40, 
   '/invall': 80, 
   '/tex': 20, 
   '/texall': 40, 
   '/freeze': 60, 
   '/freezeall': 100, 
   '/sleep': 40, 
   '/sleepall': 80, 
   '/thaw': 50, 
   '/thawall': 70, 
   '/kill': 80, 
   '/killall': 150, 
   '/end': 100, 
   '/hug': 60, 
   '/hugall': 100, 
   '/tint': 90, 
   '/sm': 50, 
   '/fly': 50, 
   '/flyall': 100, 
   '/curse': 50, 
   '/curseall': 100, 
   '/heal': 50, 
   '/healall': 70, 
   '/gm': 200, 
   '/custom': 250}
availableEffects = {'ice': 500, 
   'sweat': 750, 
   'scorch': 500, 
   'glow': 400, 
   'distortion': 750, 
   'slime': 500, 
   'metal': 500, 
   'surrounder': 1000}

##################################### END OF SETTING UP #####################################