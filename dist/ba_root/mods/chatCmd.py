# -*- coding: utf-8 -*-
# coding: utf-8
# ba_meta require api 6

import ba,_ba,random,os,json,roles,mysettings
from mysettings import *
from typing import List, Sequence, Optional, Dict, Any

reply = None
client_str = None
uniqueID = None
commandByCoin = False
commandSuccess = False
costOfCommand = None


def clientIdFromNick(nick):
    client_id = None
    for i in _ba.get_game_roster():
        if len(i['players']) > 0:
            name = i['players'][0]['name_full']
        else:						    
            name = i['display_string']
        if name.lower().find(nick.lower()) != -1:
            #player found go ahead
            client_id = i['client_id']
            break
    if client_id == None: _ba.chatmessage('player not found')
    return client_id

def playerIdFromNick(nick):
    p = _ba.get_foreground_host_activity().players
    for i in p:
        name = i.getname()
        if name.lower().find(nick.lower()) != -1:
            return p.index(i)
    _ba.chatmessage('player not found')
    return None

class chatOptions(object):
    def __init__(self):
        self.all = True
        self.tint = None
    def checkDevice(self, client_id: int, msg: str):
        global reply
        global clientID
        global client_str
        global uniqueID
        global commandByCoin
        global commandSuccess
        global costOfCommand
        clientID = client_id

        #Check Commands.txt to check all types of cmds.
        #Update The Below Lists for perfect Restrictions
        publicCmd = ['/me', '/stats', '/rank', '/myself', '/id', '/list', '/', '/help']
        adminDeny = ['/kickvote','/top','/setScore','/reset','/warn','/clearwarns','/whoinqueue','/text','/admin','/ban','/special','/partyname','/party','/pause','/setscreentextcolor', '/settextcolor', '/setscreencolor','/setchatcooldowntime', '/setchatcdtime', '/setchattime','/settings']
        topperDeny = adminDeny + ['/mute','/unmute','/kick','/kickall','/remove','/shatter','/quit','/restartserver','/restart','/reflections','/floorreflection','/icy','/exchange','/vip','/maxPlayers','/say']

        if settings['enableCoinSystem']:
            import coinSystem
            publicCmd = publicCmd + ['/donate','/buy','/shop','/scoretocash','/cashtoscore']

        ros = _ba.get_game_roster()
        for i in ros:
            if (i is not None) and (i != {}):
                if i['client_id'] == clientID:
                    client_str = i['players'][0]['name']
                    uniqueID = i['account_id']
                    cmd = msg.split(' ')[0]
                    with ba.Context(_ba.get_foreground_host_activity()):
                        if cmd in publicCmd: return True
                        if (uniqueID in roles.owners):
                            if settings['enableCoinSystem']: reply = u"\ue043O.W.N.E.R, Command Accepted\ue043"
                            else: reply = ":)"
                            return True
                        if (uniqueID in roles.admins) and (cmd not in adminDeny):
                            if settings['enableCoinSystem']: reply = u"\ue043A.D.M.I.N, Command Accepted\ue043"
                            else: reply = ":)"
                            return True
                        if (uniqueID in roles.vips) and (cmd not in topperDeny):
                            if settings['enableCoinSystem']: reply = u"\ue043V.I.P, Command Accepted\ue043"
                            else: reply = ":)"
                            return True
                        if (uniqueID in roles.toppersList) and (cmd not in topperDeny):
                            if settings['enableCoinSystem']: reply = u"\ue043TOP 5 PLAYER, Command Accepted\ue043"
                            else: reply = ":)"
                            return True
                        if  (uniqueID in roles.special) and (cmd in roles.special[uniqueID]):
                            reply = ":)"
                            return True
                        if settings['enableCoinSystem']:
                            if cmd in availableCommands:
                                user_bal = coinSystem.getCoins(uniqueID)
                                costOfCommand = availableCommands[cmd]
                                if (user_bal >= cost_of_cmd):
                                    commandByCoin = True
                                    return True
                                else:
                                    ba.screenmessage(f"You need {tic}{str(costOfCommand)} for that, You have {tic}{str(user_bal)} only.",color=(1,0,0),clients=[clientID],transient=True)
                                    return False
                        else: return False
    def kickByNick(self, nick: str):
        roster = _ba.get_game_roster()
        for i in roster:
            try:
                if i['players'][0]['name_full'].lower().find(nick.encode('utf-8').lower()) != -1:
                    _ba.disconnect_client(int(i['client_id']))
            except:
                pass
    def opt(self, msg: str, clientID: int):
        if settings['enableCoinSystem']:
            import coinSystem
            from datetime import datetime, timedelta
        commandSuccess = False
        ros = _ba.get_game_roster()
        allUser = [int(u['client_id']) for u in ros]
        for i in ros:
            if (i is not None) and (i != {}):
                if i['client_id'] == clientID:
                    client_str = i['players'][0]['name']
                    uniqueID = i['account_id']

                    #Main Base Variables
                    activity = _ba.get_foreground_host_activity()
                    session = _ba.get_foreground_host_session()
                    players = activity.players
                    splayers = session.sessionplayers
                    pID = playerIdFromNick(client_str)
        if self.checkDevice(clientID,msg):
            m = msg.split(' ')[0].lower()
            a = msg.split(' ')[1:]
            with ba.Context(activity):

                ###################### PUBLIC COMMANDS #########################
                #HELP
                if m == '/help':
                    if uniqueID in roles.owners:
                        thing = {}
                        for k,v in settings.items():
                            thing[k] = v
                        for k,v in powerups.items():
                            thing[k] = v
                        string = ''
                        separator = '          '
                        for x in thing:
                            string += f"{x}----{str(thing[x])}{separator}"
                            if separator == '          ': separator = '\n'
                            else: separator = '          '
                        ba.screenmessage(string, clients=[clientID], transient=True)
                    else:
                        ba.screenmessage(f"Use '/shop' to check what you can buy.",color=(1,0,0),clients=[clientID],transient=True)
                #LIST
                elif m == '/list':
                    #string = u'==Name========ClientID====PlayerID==\n'
                    string = u"{0:^16}{1:^15}{2:^10}\n------------------------------------------------------------------------------\n".format('Name','ClientID','PlayerID')
                    lname = None
                    lcid = None
                    lpid = None
                    for i in _ba.get_game_roster():
                        if i['players'] == []:
                            lname = str(i['display_string'])
                            lcid = str(i['client_id'])
                            lpid = str('In Lobby')
                            string += u"{0:^16}{1:^15}{2:^10}\n".format(lname, lcid, lpid)
                        else:
                            for lp in i['players']:
                                lname = lp['name_full']
                                lcid = i['client_id']
                                lpid = lp['id']
                                string += u"{0:^16}{1:^15}{2:^10}\n".format(lname, lcid, lpid)
                    '''for s in _ba.get_foreground_host_session().sessionplayers:
                        #string += s.getname() '========' + str(s.getinputdevice().client_id) + '====' + str(_ba.get_foreground_host_session().sessionplayers.index(s)) + '\n'
                        string += u"{0:^16}{1:^15}{2:^10}\n".format(str(s.getname()), str(s.getinputdevice().client_id), str(_ba.get_foreground_host_session().sessionplayers.index(s)))'''
                    ba.screenmessage(string, transient=True, color=(1, 1, 1), clients=[clientID])
                #ID
                elif m == '/id':
                    if a == []:
                        ba.screenmessage(f"Unique_ID of {client_str} => '{uniqueID}'", clients=[clientID], transient=True)
                    else:
                        #try:
                        if True:
                            for i in _ba.get_game_roster():
                                if str(i['client_id']) == a[0]:
                                    admins = roles.owners + roles.admins
                                    if True: # (uniqueID in admins):
                                        _ba.chatmessage(f"Unique_ID of {str(i['display_string'])} => '{str(i['account_id'])}'")
                        '''except:
                            pass'''
                #STATS
                elif m in ('/me', '/stats', '/rank', '/myself'):
                    if enableStats: printStatsByID(uniqueID)
                    else: sendError(f"Stats Disabled !",clientID)
                #DONATE
                elif m == '/donate' and settings['enableCoinSystem']:
                    try:
                        if len(a) < 2: ba.screenmessage(f"Usage: /donate [amount] [clientID]", transient=True, clients=[clientID])
                        else:
                            transfer = int(a[0])
                            if transfer < 100:
                                sendError(f"You can only transfer more than {tic}100.",clientID)
                                return
                            sendersID = uniqueID
                            receiversID = None
                            for player in aplayers:
                                clID = player.inputdevice.get_client_id()
                                aid = player.get_account_id()
                                if clID == int(a[1]):
                                    receiversID = aid
                                    name = player.getname()
                            if None not in [sendersID, receiversID]:
                                if sendersID == receiversID: sendError('You can\'t transfer to your own account',clientID)
                                elif coinSystem.getCoins(sendersID) < transfer: _ba.chatmessage(f"Not enough {tic}s to perform transaction")
                                else:
                                    coinSystem.addCoins(sendersID, int(transfer * -1))
                                    coinSystem.addCoins(receiversID, int(transfer))
                                    _ba.chatmessage(f"Successfully transfered {tic}{str(a[0])} to {name}'s account.")
                            else:
                                sendError('Player not Found in current game !',clientID)
                    except:
                        ba.screenmessage('Usage: /donate amount clientID', transient=True, clients=[clientID])
                #BUY
                elif m == '/buy' and settings['enableCoinSystem']:
                    if a == []:
                        _ba.chatmessage('Usage: /buy item_name')
                    elif a[0] in availableEffects:
                        effect = a[0]
                        costOfEffect = availableEffects[effect]
                        haveCoins = coinSystem.getCoins(uniqueID)
                        if haveCoins >= costOfEffect:
                            customers = roles.effectCustomers
                            if uniqueID not in customers:
                                expiry = datetime.now() + timedelta(days=1)
                                customers[uniqueID] = {'effect': effect, 'expiry': expiry.strftime('%d-%m-%Y %H:%M:%S')}
                                with open(python_path + '/roles.py') as (file):
                                    s = [ row for row in file ]
                                    s[0] = 'effectCustomers = ' + str(customers) + '\n'
                                    f = open(python_path + '/roles.py', 'w')
                                    for i in s:
                                        f.write(i)
                                    f.close()
                                coinSystem.addCoins(uniqueID, costOfEffect * -1)
                                _ba.chatmessage(f"Success! That cost you {tic}{str(costOfEffect)}")
                            else:
                                activeEffect = customers[uniqueID]['effect']
                                sendError(f"You already have {activeEffect} effect active",clientID)
                        else:
                            sendError(f"You need {tic}{str(costOfEffect)} for that, You have {tic}{str(haveCoins)} only.",clientID)
                    else: sendError(f"invalid item, try using '/shop effects'.",clientID)
                #SHOP
                elif m == '/shop' and settings['enableCoinSystem']:
                    string = '==You can buy following items==\n'
                    if a == []: ba.screenmessage('Usage: /shop commands or /shop effects', transient=True, clients=[clientID])
                    elif a[0].startswith('effects'):
                        for x in availableEffects:
                            string += f"{x}----{tic}{str(availableEffects[x])}----for 1 day\n"
                        ba.screenmessage(string, transient=True, color=(0, 1, 0), clients=[clientID])
                    elif a[0].startswith('commands'):
                        separator = '          '
                        for x in availableCommands:
                            string += f"{x}----{tic}{str(availableCommands[x])}{separator}"
                            if separator == '          ': separator = '\n'
                            else: separator = '          '
                        ba.screenmessage(string, transient=True, color=(0, 1, 0), clients=[clientID])
                    else: ba.screenmessage('Usage: /shop commands or /shop effects', transient=True, clients=[clientID])
                #CASH TO SCORE
                elif m == '/cashtoscore' and settings['enableCoinSystem']:
                    try:
                        coins = int(a[0])
                        for player in players:
                            haveCoins = coinSystem.getCoins(uniqueID)
                            if haveCoins < coins:
                                sendError(f"Not enough {tic}s to perform the transaction",clientID)
                            elif coins < 100:
                                sendError(f"You can only convert more than {tic}100",clientID)
                            else:
                                coinSystem.addCoins(uniqueID, coins * -1)
                                stats = getStats()
                                equivalentScore = int(coins * 5 * 0.9)
                                stats[uniqueID]['score'] += equivalentScore
                                f = open(statsFile, 'w')
                                f.write(json.dumps(stats))
                                ba.screenmessage(f'Transaction Successful', color=(0,1,0))
                                f.close()
                                _ba.chatmessage(f"{str(equivalentScore)} score added to your account stats. [10% transaction fee deducted]")
                                import mystats
                                mystats.refreshStats()
                            break
                    except:
                        ba.screenmessage('Usage: /cashtoscore amount_of_cash', transient=True, clients=[clientID])
                #SCORE TO CASH
                elif m == '/scoretocash' and settings['enableCoinSystem']:
                    try:
                        score = int(a[0])
                        for player in activity.players:
                            stats = getStats()
                            haveScore = stats[uniqueID]['score']
                            f.close()
                            if haveScore < score:
                                sendError('Not enough scores to perform the transaction',clientID)
                            elif score < 500:
                                sendError('You can only convert more than 500 scores',clientID)
                            else:
                                f = open(statsFile, 'w')
                                stats[uniqueID]['score'] -= score
                                f.write(json.dumps(stats))
                                equivalentCoins = int(score / 5 * 0.9)
                                coinSystem.addCoins(uniqueID, equivalentCoins)
                                ba.screenmessage('Transaction Successful', color=(0, 1, 0))
                                f.close()
                                _ba.chatmessage(f"{tic}{str(equivalentCoins)} added to your account. [10% transaction fee deducted]")
                                import mystats
                                mystats.refreshStats()
                            break
                    except:
                        bs.screenMessage('Usage: /scoretocash amount_of_score', transient=True, clients=[clientID])

                ################## COIN SYSTEM COMMANDS #####################
                #NV
                elif m == '/nv':
                    if self.tint is None:
                        self.tint = activity.globalsnode.tint
                    activity.globalsnode.tint = (0.5,0.7,1) if a == [] or not a[0] == u'off' else self.tint
                    commandSuccess=True
                #OOH
                elif m == '/ooh':
                    if a is not None and len(a) > 0:
                        s = int(a[0])
                        def oohRecurce(c):
                            ba.playsound(ba.getsound('ooh'), volume =2)
                            c -= 1
                            if c > 0:
                                ba.Timer(int(a[1]) if len(a) > 1 and a[1] is not None else 1000, ba.Call(oohRecurce, c=c))
                            return
                        oohRecurce(c=s)
                    else:
                        ba.playsound(ba.getsound('ooh'), volume =2)
                    commandSuccess = True
                #PLAYSOUND
                elif m == '/playsound':
                    try:
                        if a is not None and len(a) > 1:
                            s = int(a[1])
                            def oohRecurce(c):
                                ba.playsound(ba.getsound(str(a[0])), volume =2)
                                c -= 1
                                if c > 0:
                                    ba.Timer(int(a[2]) if len(a) > 2 and a[2] is not None else 1000, ba.Call(oohRecurce, c=c))
                                return
                            oohRecurce(c=s)
                        else:
                            ba.playsound(ba.getsound(str(a[0])), volume =2)
                        commandSuccess = True
                    except:
                        bs.screenMessage('Usage: /playsound music times', transient=True, clients=[clientID])
                #BOX
                elif m == '/box':
                    try:
                        try:
                            if a != []:
                                n = int(a[0])
                            else:
                                n = pID
                            players[n].actor.node.torso_model = ba.getmodel("tnt"); 
                            players[n].actor.node.color_mask_texture = ba.gettexture("tnt"); 
                            players[n].actor.node.color_texture = ba.gettexture("tnt") 
                            players[n].actor.node.highlight = (1,1,1); 
                            players[n].actor.node.color = (1,1,1); 
                            players[n].actor.node.head_model = None; 
                            players[n].actor.node.style = "cyborg";
                            commandSuccess = True
                        except:
                            pass
                    except:
                        ba.screenmessage(f"Using: /boxall [or] /box [PlayerID]", transient=True, clients=[clientID])
                #BOXALL
                elif m == '/boxall':
                    try:
                        for i in players:
                            try:
                                i.actor.node.torso_model = ba.getmodel("tnt")
                                i.actor.node.color_mask_texture = ba.gettexture("tnt")
                                i.actor.node.color_texture = ba.gettexture("tnt")
                                i.actor.node.highlight = (1,1,1)
                                i.actor.node.color = (1,1,1)
                                i.actor.node.style = "cyborg"
                                commandSuccess = True
                            except:
                                pass
                    except:
                        pass
                #SPAZ
                elif m == '/spaz':
                    try:
                        try:
                            if a != []:
                                n = int(a[0])
                            else:
                                n = pID
                            t = players[n].actor.node
                            t.color_texture = ba.gettexture(a[1]+"Color")
                            t.color_mask_texture = ba.gettexture(a[1]+"ColorMask")
                            t.head_model = ba.getmodel(a[1]+"Head")
                            t.torso_model = ba.getmodel(a[1]+"Torso")
                            t.pelvis_model = ba.getmodel(a[1]+"Pelvis")
                            t.upper_arm_model = ba.getmodel(a[1]+"UpperArm")
                            t.forearm_model = ba.getmodel(a[1]+"ForeArm")
                            t.hand_model = ba.getmodel(a[1]+"Hand")
                            t.upper_leg_model = ba.getmodel(a[1]+"UpperLeg")
                            t.lower_leg_model = ba.getmodel(a[1]+"LowerLeg")
                            t.toes_model = ba.getmodel(a[1]+"Toes")
                            t.style = a[1]
                            commandSuccess=True
                        except:
                            pass
                    except:
                        ba.screenmessage(f"Using: /spazall [AppearanceName] [or] /spaz [PlayerID] [AppearanceName]", transient=True, clients=[clientID])
                #SPAZALL
                elif m == '/spazall':
                    for i in players:
                        t = i.actor.node
                        try:
                            t.color_texture = ba.gettexture(a[1]+"Color")
                            t.color_mask_texture = ba.gettexture(a[1]+"ColorMask")
                            t.head_model = ba.getmodel(a[1]+"Head")
                            t.torso_model = ba.getmodel(a[1]+"Torso")
                            t.pelvis_model = ba.getmodel(a[1]+"Pelvis")
                            t.upper_arm_model = ba.getmodel(a[1]+"UpperArm")
                            t.forearm_model = ba.getmodel(a[1]+"ForeArm")
                            t.hand_model = ba.getmodel(a[1]+"Hand")
                            t.upper_leg_model = ba.getmodel(a[1]+"UpperLeg")
                            t.lower_leg_model = ba.getmodel(a[1]+"LowerLeg")
                            t.toes_model = ba.getmodel(a[1]+"Toes")
                            t.style = a[1]
                            commandSuccess=True
                        except:
                            ba.screenmessage(f"Using: /spazall [AppearanceName] [or] /spaz [PlayerID] [AppearanceName]", transient=True, clients=[clientID])
                #INV
                elif m == '/inv':
                    try:
                        if True:
                            if a != []:
                                n = int(a[0])
                            else:
                                n = pID
                            t = players[n].actor.node
                            t.head_model = None
                            t.torso_model = None
                            t.pelvis_model = None
                            t.upper_arm_model = None
                            t.forearm_model = None
                            t.hand_model = None
                            t.upper_leg_model = None
                            t.lower_leg_model = None
                            t.toes_model = None
                            t.style = "cyborg"
                            commandSuccess=True
                        '''except:
                            pass'''
                    except:
                        ba.screenmessage(f"Using: /invall [or] /inv [PlayerID]", transient=True, clients=[clientID])
                #INVALL
                elif m == '/invall':
                    try:
                        for i in players:
                            t = i.actor.node
                            try:
                                t.head_model = None
                                t.torso_model = None
                                t.pelvis_model = None
                                t.upper_arm_model = None
                                t.forearm_model = None
                                t.hand_model = None
                                t.upper_leg_model = None
                                t.lower_leg_model = None
                                t.toes_model = None
                                t.style = "cyborg"
                                commandSuccess=True
                            except:
                                pass
                    except:
                        pass
                #TEX
                elif m == '/tex':
                    try:
                        if len(a) > 1: n = int(a[0])
                        else: n = pID
                        color = None
                        if (len(a) > 1) and (str(a[1]) == 'kronk'): color = str(a[1])
                        else:color = str(a[0]) + 'Color'
                        try:
                            players[n].actor.node.color_mask_texture= ba.gettexture(str(a[1])); 
                            players[n].actor.node.color_texture= ba.gettexture(str(a[1])) 
                            commandSuccess=True
                        except:
                            ba.screenmessage(f"Using: /texall [texture] [or] /tex [PlayerID] [texture]", transient=True, clients=[clientID])
                    except:
                        ba.screenmessage(f"Using: /texall [texture] [or] /tex [PlayerID] [texture]", transient=True, clients=[clientID])
                #TEXALL
                elif m == '/texall':
                    try:
                        color = None
                        if str(a[0]) == 'kronk':
                            color = str(a[0])
                        else:color = str(a[0]) + 'Color'
                        for i in players:
                            try:
                                i.actor.node.color_mask_texture= ba.gettexture(str(a[0]) + 'ColorMask')
                                i.actor.node.color_texture= ba.gettexture(color)
                                commandSuccess=True
                            except:
                                pass
                    except:
                        ba.screenmessage(f"Using: /texall [texture] [or] /tex [PlayerID] [texture]", transient=True, clients=[clientID])
                    
                #FREEZE
                elif m == '/freeze':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /freezeall [or] /freeze [PlayerID]", transient=True, clients=[clientID])
                    else:
                        players[int(a[0])].actor.node.handlemessage(ba.FreezeMessage())
                        commandSuccess=True
                #FREEZEALL
                elif m == '/freezeall':
                    for i in players:
                        try:
                            i.actor.node.handlemessage(ba.FreezeMessage())
                            commandSuccess=True
                        except:
                            pass
                #SLEEP
                elif m == '/sleep':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /sleepall [or] /sleep [PlayerID] [secToSleep]", transient=True, clients=[clientID])
                    else:
                        players[int(a[0])].actor.node.handlemessage("knockout",int(a[1])*1000+1)
                        commandSuccess=True
                #SLEEPALL
                elif m == '/sleepall':
                    for i in players:
                        try:
                            i.actor.node.handlemessage("knockout",int(a[1])*1000+1)
                            commandSuccess=True
                        except:
                            pass
                #THAW
                elif m == '/thaw':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /thawall [or] /thaw[PlayerID]", transient=True, clients=[clientID])
                    else:
                        players[int(a[0])].actor.node.handlemessage(ba.ThawMessage())
                        commandSuccess=True
                #THAWALL
                elif m == '/thawall':
                    for i in players:
                        try:
                            i.actor.node.handlemessage(ba.ThawMessage())
                            commandSuccess=True
                        except:
                            pass
                #KILL
                elif m == '/kill':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /killall [or] /kill [PlayerID]", transient=True, clients=[clientID])
                    else:
                        players[int(a[0])].actor.node.handlemessage(ba.DieMessage())
                        commandSuccess=True
                #KILLALL
                elif m == '/killall':
                    for i in players:
                        try:
                            i.actor.node.handlemessage(ba.DieMessage())
                            commandSuccess=True
                        except:
                            pass
                #END
                elif m == '/end':
                    try:
                        _ba.get_foreground_host_activity().end_game()
                        commandSuccess=True
                    except:
                        pass
                #HUG
                elif m == '/hug':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /hugall [or] /hug [player1Index] [player2Index]", transient=True, clients=[clientID])
                    else:
                        try:
                            players[int(a[0])].actor.node.hold_node = players[int(a[1])].actor.node
                            commandSuccess=True
                        except:
                            pass
                #HUGALL
                elif m == '/hugall':
                    try:
                        players[0].actor.node.hold_node = players[1].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[1].actor.node.hold_node = players[0].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[2].actor.node.hold_node = players[3].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[3].actor.node.hold_node = players[2].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[4].actor.node.hold_node = players[5].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[5].actor.node.hold_node = players[4].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[6].actor.node.hold_node = players[7].actor.node
                        commandSuccess=True
                    except:
                        pass
                    try:
                        players[7].actor.node.hold_node = players[6].actor.node
                        commandSuccess=True
                    except:
                        pass
                #SM
                elif m == '/sm':
                    activity.globalsnode.slow_motion = activity.globalsnode.slow_motion == False
                    commandSuccess=True
                #FLY
                elif m == '/fly':
                    try:
                        try:
                            playerID = int(a[0])
                        except:
                            playerID = pID
                        players[playerID].actor.node.fly = players[playerID].actor.node.fly == False
                        commandSuccess = True
                    except:
                        bsInternal._chatMessage('Failed!!! Usage: /flyall or /fly number of list', transient=True, clients=[clientID])
                #FLYALL
                elif m == '/flyall':
                    for i in players:
                        i.actor.node.fly = i.actor.node.fly == False
                    commandSuccess = True
                #CURSE
                elif m == '/curse':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /curseall [or] /curse [PlayerID]", transient=True, clients=[clientID])
                    else:
                        players[int(a[0])].actor.curse()
                        commandSuccess=True
                #CURSEALL
                elif m == '/curseall':
                    for i in players:
                        try:
                            i.actor.curse()
                        except:
                            pass
                    commandSuccess=True
                #HEAL
                elif m == '/heal':
                    try:
                        if len(a) > 0: n = int(a[0])
                        else: n = pID
                        players[n].actor.node.handlemessage(ba.PowerupMessage('health'))
                    except:
                        ba.screenmessage(f"Using: /healall [or] /heal [PlayerID]", transient=True, clients=[clientID])
                        commandSuccess=True
                #HEALALL
                elif m == '/healall':
                    for i in players:
                        try:
                            i.actor.node.handlemessage(ba.PowerupMessage('health'))
                        except:
                            pass
                    commandSuccess=True
                #CUSTOM
                elif m == '/custom':
                    if True: #try:
                        clID = int(a[0])
                        ros = _ba.get_game_roster()
                        for i in ros:
                            if (i is not None) and (i != {}) and (i['client_id'] == clID):
                                name = i['players'][0]['name']
                                newID = i['account_id']
                                a[2] = a[2].replace('_',' ')
                                commandSuccess = False
                                if a[1] == 'add':
                                    if (len(a) > 3) and (not str(a[2]).startswith('perm')) and (new not in roles.customTag):
                                        roles.customTag[new] = str(a[2])
                                        n = 1
                                        string = 'customTag'
                                        updated = roles.customTag
                                        commandSuccess=True
                                    if (len(a) < 3) and (new not in roles.customList):
                                        roles.customList.append(new)
                                        n = 4
                                        string = 'customList'
                                        updated = roles.customList
                                        commandSuccess=True
                                if a[1] == 'remove':
                                    if (new in roles.customTag):
                                        roles.customTag.pop(new)
                                        n = 1
                                        string = 'customTag'
                                        updated = roles.customTag
                                        commandSuccess=True
                                    if (new in roles.customList):
                                        roles.customList.remove(new)
                                        n = 4
                                        string = 'customList'
                                        updated = roles.customList
                                        commandSuccess=True
                                def save_data():
                                    m = open(membersFile, 'r')
                                    d = json.loads(m)
                                    if string == 'customTag': d['customTag'] = roles.customTag
                                    if string == 'customList': d['customList'] = roles.customList
                                    m2 = open(membersFile, 'w')
                                    m2.write(json.dumps(d, indent=4))
                                    m2.close()
                                    with open(python_path + '/roles.py') as (file):
                                        s = [ row for row in file ]
                                        s[n] = str(string) + ' = ' + str(updated) + '\n'
                                        f = open(python_path + '/roles.py', 'w')
                                        for i in s:
                                            f.write(i)
                                        f.close()
                                if commandByCoin and commandSuccess:
                                    save_data()
                                    exp = datetime.now() + timedelta(days=1)
                                    cms = coinSystem.tag_customers
                                    cms[newID] = {'expiry':exp, 'type':string, 'line':n}
                                    with open(python_path + '/coinSystem.py') as (FILE):
                                        line = [row for row in FILE]
                                        line[0] = 'tag_customers = ' + str(cms) + '\n'
                                        f = open(python_path + '/coinSystem.py', 'w')
                                        for i in line:
                                            f.write(i)
                                        f.close()
                                if (uniqueID in roles.owners) and (commandSuccess == True):
                                    if (str(a[2]).startswith('perm')) or (str(a[3]).startswith('perm')): save_data()
                    '''except:
                        ba.screenmessage(f"Using: /custom [ClientID] add/remove (Optional: TAG) (Optional: permanent)", clients=[clientID], transient=True)'''

                #################### ADMIN COMMANDS ########################
                #BUNNY
                elif m == '/bunnyNotYetModded':
                    try:
                        """
                        import BuddyBunny
                        for i in range(int(a[0])):
                            p=ba.getactivity().players[int(a[1])]
                            if not 'bunnies' in p.gameData:
                                p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(p)
                            p.gameData['bunnies'].doBunny()
                        commandSuccess=True
                        """
                        _ba.chatmessage("'/bunny' command removed !")
                    except:
                        _ba.chatmessage("'/bunny' command removed !")
                        #ba.screenmessage(f"Using: /bunny [count] [owner's_PlayerID]", transient=True, clients=[clientID])
                #LOAD MESSAGES
                elif m == '/lm':
                    arr = []
                    for i in range(len(_ba.get_chat_messages())):
                        if True: #try:
                            arr.append(_ba.get_chat_messages()[(-1 - i)])
                        '''except:
                            pass'''
                    arr.reverse()
                    for i in arr:
                        _ba.chatmessage(i)
                    commandSuccess = True
                #GET PROFILES
                elif m == '/gp':
                    try:
                        try:
                            playerID = int(a[0])
                        except:
                            playerID = playerIdFromNick(a[0])
                        num = 1
                        for i in splayers[playerID].inputdevice.get_player_profiles():
                            try:
                                _ba.chatmessage(f"{num}) - {i}")
                                num += 1
                            except:
                                pass
                        commandSuccess = True
                    except:
                        ba.screenmessage(f"Using: /gp number of list", transient=True, clients=[clientID])
                #WHO IS
                elif m == '/whois':
                    try:
                        #clID = int(a[0])
                        try:
                            clID = int(a[0])
                        except:
                            clID = clientIdFromNick(str(a[0]))
                        ID = ''
                        for i in splayers:
                            if i.inputdevice.client_id == clID:
                                ID = i.get_account_id()
                                name = i.getname()
                        if (ID != '') and (ID is not None) and (ID != 'null'):
                            with open(playerLogFile,'r') as f:
                                allPlayers = json.loads(f.read())
                                allID = allPlayers[ID]
                                string = f'Login ID of {name} is:'
                                for i in allID:
                                    #_ba.chatmessage(i)
                                    if (i != ID): string += '\n' + i
                                ba.screenmessage(string, transient=True, color=(1, 1, 1))
                                commandSuccess = True
                    except:
                        ba.screenmessage(f"Using: /whois [ClientID or Name]", clients=[clientID], transient=True)
                #MUTE
                elif m == '/mute':
                    import chatFilter
                    try:
                        try:
                            clID = int(a[0])
                        except:
                            clID = clientIdFromNick(str(a[0]))
                        ID = None
                        for i in _ba.get_game_roster():
                            if i['clientID'] == clID:
                                ID = i['account_id']
                                name = i['display_string']						
                        if (ID not in [None, 'null']):
                            try:
                                chatFilter.chatCoolDown[ID] = a[1] * 60
                                sendError(f'{name} muted for {str(a[1])} minutes.')
                                commandSuccess = True
                            except:
                                chatFilter.chatCoolDown[ID] = 99999 * 60
                                sendError(f'{name} muted until server restarts.')
                                commandSuccess = True
                        else:
                            sendError(f"{name} is already muted", clientID)
                    except:
                        ba.screenmessage(f"Usage: /mute <ClientId/Name> <Minutes>", clients=[clientID], transient=True)
                #UN MUTE
                elif m == '/unmute':
                    import chatFilter
                    try:
                        try:
                            clID = int(a[0])
                        except:
                            clID = clientIdFromNick(str(a[0]))
                        ID = None
                        for i in _ba.get_game_roster():
                            if i['clientID'] == clID:
                                ID = i['account_id']
                                name = i['display_string']
                        if (ID not in [None, 'null']) and (ID in chatFilter.chatCoolDown) and (chatFilter.chatCoolDown[ID] > 3):
                            chatFilter.chatCoolDown.pop(ID)
                            _ba.chatmessage(f'Unmuted {name}')
                            commandSuccess = True
                        else:
                            sendError(f"{name} is not muted yet", clientID)
                    except:
                        ba.screenmessage(f"Usage: /unmute <ClientId/Name>", clients=[clientID], transient=True)
                #KICK
                elif m == '/kick':
                    if a == []:
                        ba.screenmessage(f"Using: /kick [name/ClientID]", clients=[clientID], transient=True)
                    else:
                        if len(a[0]) > 3:
                            self.kickByNick(a[0])
                        else:
                            try:
                                s = int(a[0])
                                _ba.disconnect_client(int(a[0]))
                            except:
                                self.kickByNick(a[0])
                        commandSuccess=True
                #KICK
                elif m == '/kickall':
                    try:
                        for i in ros:
                            if i['client_id'] != clientID:
                                _ba.disconnect_client(i['client_id'])
                        commandSuccess=True
                    except:
                        pass
                #REMOVE
                elif m == '/remove':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /removeall [or] /remove [PlayerID]", transient=True, clients=[clientID])
                    else:
                        activity.remove_player(players[int(a[0])])
                        commandSuccess=True
                #REMOVEALL
                elif m == '/removeall':
                    for i in players:
                        try:
                            activity.remove_player(i)
                        except:
                            pass
                    commandSuccess=True
                #SHATTER
                elif m == '/shatter':
                    if a == [] or a[0] == 'all':
                        ba.screenmessage(f"Using: /shatterall [or] /shatter [PlayerID]", transient=True, clients=[clientID])
                    else:
                        players[int(a[0])].actor.node.shattered = int(a[1])
                        commandSuccess=True
                #SHATTERALL
                elif m == '/shatterall':
                    for i in players:
                        i.actor.node.shattered = int(a[1])
                    commandSuccess=True
                #QUIT
                elif m in ('/quit', '/restart', '/restartserver'):
                    _ba.chatmessage("Server Restarting, Please Join in a moment !")
                    commandSuccess=True
                    _ba.quit()
                #AC
                elif m == '/ac':
                    try:
                        if a[0] == 'r':
                            m = 1.3 if a[1] is None else float(a[1])
                            s = 1000 if a[2] is None else float(a[2])
                            ba.animate_array(activity.globalsnode, 'ambient_color',3, {0: (1*m,0,0), s: (0,1*m,0),s*2:(0,0,1*m),s*3:(1*m,0,0)},True)
                            commandSuccess=True
                        else:
                            try:
                                if a[1] is not None:
                                    activity.globalsnode.ambient_color = (float(a[0]),float(a[1]),float(a[2]))
                                    commandSuccess=True
                            except:
                                pass
                    except:
                        ba.screenmessage(f"Using: '/ac [Red] [Green] [Blue]' or '/ac r [brightness] [speed]'", transient=True, clients=[clientID])
                #TINT
                elif m == '/tint':
                    try:
                        if a[0] == 'r':
                            m = 1.3 if a[1] is None else float(a[1])
                            s = 1000 if a[2] is None else float(a[2])
                            ba.animate_array(activity.globalsnode, 'tint',3, {0: (1*m,0,0), s: (0,1*m,0),s*2:(0,0,1*m),s*3:(1*m,0,0)},True)
                            commandSuccess=True
                        else:
                            if a[1] is not None:
                                activity.globalsnode.tint = (float(a[0]),float(a[1]),float(a[2]))
                                commandSuccess=True
                            else:
                                pass
                    except:
                        ba.screenmessage(f"Using: '/tint [Red] [Green] [Blue]' or '/tint r [brightness] [speed]'", transient=True, clients=[clientID])
                #REFLECTIONS
                elif m.startswith('/reflectionNotAvail'):
                    if a == [] or len(a) < 2:
                        ba.screenmessage(f"Using: /reflections [type(1/0)] [scale]", transient=True, clients=[clientID])
                    rs = [int(a[1])]
                    type = 'soft' if int(a[0]) == 0 else 'powerup'
                    try:
                        _ba.get_foreground_host_activity().getMap().node.reflection = type
                        _ba.get_foreground_host_activity().getMap().node.reflectionScale = rs
                    except:
                        pass
                    try:
                        _ba.get_foreground_host_activity().getMap().bg.reflection = type
                        _ba.get_foreground_host_activity().getMap().bg.reflectionScale = rs
                    except:
                        pass
                    try:
                        _ba.get_foreground_host_activity().getMap().floor.reflection = type
                        _ba.get_foreground_host_activity().getMap().floor.reflectionScale = rs
                    except:
                        pass
                    try:
                        _ba.get_foreground_host_activity().getMap().center.reflection = type
                        _ba.get_foreground_host_activity().getMap().center.reflectionScale = rs
                    except:
                        pass
                    commandSuccess=True
                #FLOOR REFLECTION
                elif m.startswith('/floorreflectionNotAvail'):
                    bs.getSharedObject('globals').floorReflection = bs.getSharedObject('globals').floorReflection == False
                    commandSuccess=True
                #ICY or EXCHANGE
                elif m in ('/exchange','/icy'):
                    try:
                        if True:
                            try:
                                player1 = int(a[0])
                            except:
                                player1 = playerIdFromNick(a[0])
                            try:
                                player2 = int(a[1])
                            except:
                                player2 = playerIdFromNick(a[1])
                        node1 = players[player1].actor.node
                        node2 = players[player2].actor.node
                        players[player1].actor.node = node2
                        players[player2].actor.node = node1
                        commandSuccess = True
                    except:
                        ba.screenmessage(f"Using: /exchange [PlayerID1] [PlayerID2]", transient=True, clients=[clientID])
                #ICEOFF or HOCKEY
                elif m in ('/hockey','/iceoff'):
                    try:
                        activity.getMap().isHockey = activity.getMap().isHockey == False
                    except:
                        pass
                    for i in players:
                        i.actor.node.hockey = i.actor.node.hockey == False
                    commandSuccess = True
                #VIP
                elif m == '/vip':
                    try:
                        clID = int(a[0])
                        updated = roles.vips
                        ros = _ba.get_game_roster()
                        for i in ros:
                            if (i is not None) and (i != {}) and (i['client_id'] == clID):
                                name = i['players'][0]['name']
                                newID = i['account_id']
                                if a[1] == 'add':
                                    if newID not in updated:
                                        roles.vips.append(newID)
                                        commandSuccess=True
                                    else: sendError(f"{str(name)}, is already a vip !",clientID)
                                elif a[1] == 'remove':
                                    if newID in updated:
                                        roles.vips.remove(newID)
                                        commandSuccess=True
                                    else: sendError(f"{str(name)}, is already not a vip !",clientID)
                                updated = roles.vips
                                if (len(a) > 2) and (uniqueID in roles.owners) and commandSuccess:
                                    if str(a[2]).startswith('perm'):
                                        #Add them to members.json (log)
                                        m = open(membersFile, 'r')
                                        d = json.loads(m)
                                        if (newID not in d['vips']): d['vips'][newID] = []
                                        if (name not in d['vips'][newID]): d['vips'][newID].append(name)
                                        m2 = open(membersFile, 'w')
                                        m2.write(json.dumps(d, indent=4))
                                        m2.close()
                                        #Add them to roles.py
                                        with open(python_path + '/roles.py') as (file):
                                            s = [ row for row in file ]
                                            s[8] = 'vips = ' + str(updated) + '\n'
                                            f = open(python_path + '/roles.py', 'w')
                                            for i in s:
                                                f.write(i)
                                            f.close()
                    except:
                        ba.screenmessage(f"Using: /vip [ClientID] add/remove perm/None", clients=[clientID], transient=True)
                #MAXPLAYERS
                elif m.startswith('/maxplayer'):
                    if a == []:
                        ba.screenmessage(f"Using: /maxplayers [count]", clients=[clientID], transient=True)
                    else:
                        try:
                            _ba.get_foreground_host_().max_players = int(a[0])
                            _ba.set_public_party_max_size(int(a[0]))
                            _ba.chatmessage(f"MaxPlayers limit set to {str(int(a[0]))}")
                            commandSuccess=True
                        except:
                            pass
                #SAY (Send Chat Message in Server's name)
                elif m == "/say":
                    if a == []:
                        ba.screenmessage('Usage: /say <text to send>', transient=True, clients=[clientID])
                    else:
                        message = " ".join(a)
                        _ba.chatmessage(message)

                #################### OWNER COMMANDS ########################
                #KICK VOTE
                elif m == '/kickvote':
                    try:
                        if a[0] in ('enable','yes','true'): _ba.set_enable_default_kick_voting(True)
                        if a[0] in ('disable','no','false'): _ba.set_enable_default_kick_voting(False)
                        commandSuccess = True
                    except:
                        ba.screenmessage(f"Using: /kickvote [enable/yes/true or disable/no/false]", clients=[clientID], transient=True)
                #TOP
                elif m == '/top':
                    try:
                        temp_limit = int(a[0])
                        temp_toppers = []
                        f = open(statsFile, 'r')
                        temp_stats = json.loads(f.read())
                        for i in range(1,limit+1):
                            for id in temp_stats:
                                if int(temp_stats[id]['rank'])==i: temp_toppers.append(id)
                        if temp_toppers != []:
                            for account_id in temp_toppers:
                                temp_name = temp_stats[account_id]['name_html']
                                #print(temp_toppers.index(account_id)+1,temp_name[temp_name.find('>')+1:].encode('utf8'),temp_stats[account_id]['scores'])
                                _ba.chatmessage("{0}. {1}  ----->  {2}".format(temp_toppers.index(account_id)+1,temp_name[temp_name.find('>')+1:].encode('utf8'),temp_stats[account_id]['scores']))
                            commandSuccess=True
                        f.close()
                    except:
                        sendError('Usage: /top <range>',clientID)
                #SETSCORE
                elif m in ['/setscore','/reset']:
                    try:
                        temp_rank = int(a[0])
                        temp_stats = getStats()
                        for id in temp_stats:
                            if int(temp_stats[id]['rank']) == temp_rank: ID = id
                        f.close()
                        temp_name = temp_stats[ID]['name_html']
                        temp_name = temp_name[temp_name.find('>')+1:].encode('utf-8')
                        try:
                            temp_score = int(a[1])
                        except:
                            temp_score = 0
                        stats[ID]['score'] = temp_score
                        _ba.chatmessage("{}'s score set to {}".format(temp_name,temp_score))
                        #backup
                        from shutil import copyfile
                        src = statsFile
                        from datetime import datetime
                        now = datetime.now().strftime('%d-%m %H:%M:%S')
                        dst = 'stats.bak---' + now
                        copyfile(src,dst)
                        #write new stats
                        f = open(statsFile, 'w')
                        f.write(json.dumps(temp_stats))
                        f.close()
                        '''
                        import mystats
                        mystats.refreshStats()
                        '''
                        commandSuccess=True
                    except:
                        sendError('Usage: /reset <rank of player> (optional:newScore)',clientID)
                #WARN
                elif m == "/warn":
                    try:
                        try:
                            clID = int(a[0])
                        except:
                            clID = clientIdFromNick(str(a[0]))
                        for i in _ba.get_game_roster():
                            if i['clientID'] == clID:
                                ID = i['displayString']
                                name = ID
                                try:
                                    name = i['players'][0]['name']
                                except:
                                    pass
                        import chatFilter
                        warnCount = chatFilter.warn(ID)
                        if warnCount < 3:
                            bsInternal._chatMessage("Warning {str(name)}.")
                            for i in range(3):
                                sendError('Warning!!!!',clID)
                            sendError("Warn count: % 1d/3"%(warnCount),clID)	
                        else:
                            chatFilter.abusers.pop(ID)		
                            _ba.chatmessage(f"Warn limit exceeded. Kicking {str(name)}.")
                            _ba.chatmessage("Warn system Made By Aleena")
                            _ba.chatmessage(clID)
                        commandSuccess = True
                    except:
                        ba.screenmessage('Usage: /warn <client_id or name>', transient=True, clients=[clientID])
                #CLEAR WARN
                elif m.startswith("/clearwarn"):
                    import chatFilter
                    try:
                        try:
                            clID = int(a[0])
                        except:
                            clID = clientIdFromNick(str(a[0]))
                        ID = None
                        for i in _ba.get_game_roster():
                            if i['clientID'] == clID:
                                ID = i['account_id']
                                name = i['display_string']
                                chatFilter.abusers.pop(ID)
                                _ba.chatmessage(f"{name} has been removed from Abuse/Warn List")
                                commandSuccess = True			    
                    except:
                        ba.screenmessage('Usage: /clearwarn <client_id or name>', transient=True, clients=[clientID])
                #WHOINQUEUE
                elif m == '/whoinqueue':
                    def _onQueueQueryResult(result):
                        from queueChecker import queueID
                        #print result, ' is result'
                        inQueue = result['e']
                        #print inQueue, ' is inQueue'
                        string = 'No one '
                        if inQueue != []:
                            string = ''
                            for queue in inQueue:
                                #print queue[3]
                                string += queue[3] + ' '
                        _ba.chatmessage(f"{string} is in the queue")
							
                    _ba.add_transaction(
                            {'type': 'PARTY_QUEUE_QUERY', 'q': queueID},callback=ba.Call(_onQueueQueryResult))
                    _ba.run_transactions()
                    commandSuccess=True
                #TEXT
                elif m in ('/text', '/texts'):
                    from BsTextOnMap import texts
                    if a == []:
                        ba.screenmessage(f"Usage: /text showall or /text add [text] or /text del [textnumber]", clients=[clientID], transient=True)
                    elif a[0] == 'add' and len(a)>1:
                        #get whole sentence from argument list
                        newText = u''
                        for i in range(1,len(a)):
                            newText += a[i] + ' '
                        #print newText
                        texts.append(newText)
                        #write to file
                        with open(python_path + '/BsTextOnMap.py') as (file):
                            s = [ row for row in file ]
                            s[0] = 'texts = ' + str(texts) + '\n'
                            f = open(python_path + '/BsTextOnMap.py', 'w')
                            for i in s:
                                f.write(i)
                            f.close()
                            commandSuccess=True
                    elif a[0] == 'showall':
                        for i in range(len(texts)):
                            #print texts(i)
                            _ba.chatmessage(str(i) + '. ' + texts[i])
                        commandSuccess=True
                    elif a[0] == 'del' and len(a)>1:
                        try:
                            if len(texts) > 1:
                                texts.pop(int(a[1]))
                                #write to file
                                with open(python_path + '/BsTextOnMap.py') as (file):
                                    s = [ row for row in file ]
                                    s[0] = 'texts = ' + str(texts) + '\n'
                                    f = open(python_path + '/BsTextOnMap.py', 'w')
                                    for i in s:
                                        f.write(i)
                                    f.close()
                                    commandSuccess=True
                            else:
                                sendError(f"At least one text should be present",clientID)
                        except:
                            pass
                    else:
                        ba.screenmessage(f"Usage: /text showall or /text add [text] or /text del [textnumber]", clients=[clientID], transient=True)
                #ADMIN
                elif m == '/admin':
                    if True: #try:
                        clID = int(a[0])
                        updated = roles.admins
                        ros = _ba.get_game_roster()
                        for i in ros:
                            if (i is not None) and (i != {}) and (i['client_id'] == clID):
                                name = i['players'][0]['name']
                                newID = i['account_id']
                                if a[1] == 'add':
                                    if newID not in updated:
                                        roles.admins.append(newID)
                                        commandSuccess=True
                                    else: sendError(f"{str(name)}, is already an admin !",clientID)
                                elif a[1] == 'remove':
                                    if newID in updated:
                                        roles.admins.remove(newID)
                                        commandSuccess=True
                                    else: sendError(f"{str(name)}, is already not an admin !",clientID)
                                updated = roles.admins
                                if (len(a) > 2) and (uniqueID in roles.owners) and commandSuccess:
                                    if str(a[2]).startswith('perm'):
                                        #Add them to members.json (log)
                                        m = open(membersFile, 'r')
                                        d = json.loads(m)
                                        if (newID not in d['admins']): d['admins'][newID] = []
                                        if (name not in d['admins'][newID]): d['admins'][newID].append(name)
                                        m2 = open(membersFile, 'w')
                                        m2.write(json.dumps(d, indent=4))
                                        m2.close()
                                        #Add them to roles.py
                                        with open(python_path + '/roles.py') as (file):
                                            s = [ row for row in file ]
                                            s[9] = 'admins = ' + str(updated) + '\n'
                                            f = open(python_path + '/roles.py', 'w')
                                            for i in s:
                                                f.write(i)
                                            f.close()
                    '''except:
                        ba.screenmessage(f"Using: /admin [ClientID] add/remove perm/None", clients=[clientID], transient=True)'''
                #BAN
                elif m == '/ban':
                    try:
                        clID = int(a[0])
                        updated = roles.banList
                        ros = _ba.get_game_roster()
                        for i in ros:
                            if (i is not None) and (i != {}) and (i['client_id'] == clID):
                                name = i['players'][0]['name']
                                new = i['account_id']
                                if new not in roles.banList:
                                    if len(a) > 1: roles.banList[new] = [i['display_string'], str(a[1])] #Add Name If Provided
                                    else: roles.banList[new] = [i['display_string']]
                                    updated = roles.banList
                                    commandSuccess=True
                                    _ba.chatmessage(f"{str(name)}, has been BANNED !")
                                    _ba.disconnect_client(clID)
                                else: sendError(f"{str(name)}, is already BANNED !",clientID)
                                if not commandSuccess: return
                                m = open(membersFile, 'r')
                                d = json.loads(m)
                                if (newID not in d['banList']): d['banList'][newID] = []
                                if (name not in d['banList'][newID]): d['banList'][newID].append(name)
                                m2 = open(membersFile, 'w')
                                m2.write(json.dumps(d, indent=4))
                                m2.close()
                                with open(python_path + '/roles.py') as (file):
                                    s = [ row for row in file ]
                                    s[2] = 'banList = ' + str(updated) + '\n'
                                    f = open(python_path + '/roles.py', 'w')
                                    for i in s:
                                        f.write(i)
                                    f.close()
                    except:
                        ba.screenmessage(f"Using: /ban ClientID (optional-NickNameForIdentification)", clients=[clientID], transient=True)
                #SPECIAL
                elif m == '/special':
                    try:
                        clID = int(a[0])
                        updated = roles.special
                        ros = _ba.get_game_roster()
                        cmds = a[2:]
                        for i in ros:
                            if (i is not None) and (i != {}) and (i['client_id'] == clID):
                                name = i['players'][0]['name']
                                newID = i['account_id']
                                success = False
                                if a[1] == 'add':
                                    if newID not in updated:
                                        roles.special[newID] = cmds
                                        commandSuccess=True
                                    else:
                                        for cmd in cmds:
                                            if (cmd.startswith('/')) and (cmd not in roles.special[newID]):
                                                roles.special[newID].append(cmd)
                                                success = True
                                            else: sendError(f"{str(name)} already has perms to '{cmd}' !\n (Note: cmd should start with '/')",clientID)
                                            commandSuccess=True
                                        if success: _ba.chatmessage(f"Now {str(name)} can use {str(cmds)}...")
                                elif a[1] == 'remove':
                                    if (len(a) > 2) and (newID in updated):
                                        for cmd in cmds:
                                            if (cmd.startswith('/')) and (cmd not in roles.special[newID]):
                                                roles.special[newID].remove(cmd)
                                                success = True
                                            else: sendError(f"{str(name)} has no perms to '{cmd}' for you to remove again !\n (Note: cmd should start with '/')",clientID)
                                            commandSuccess=True
                                        if success: _ba.chatmessage(f"Now {str(name)} can't use {str(cmds)}...")
                                    if (len(a) < 3) and (newID in updated):
                                        roles.special.pop(newID)
                                        commandSuccess=True
                                    else: sendError(f"{str(name)} already don't have special perms !",clientID)
                                updated = roles.special
                                if (len(a) > 2) and (uniqueID in roles.owners):
                                    if commandSuccess:
                                        #Add them to members.json (log)
                                        m = open(membersFile, 'r')
                                        d = json.loads(m)
                                        if (newID not in d['special']): d['special'][newID] = []
                                        if (name not in d['special'][newID]): d['special'][newID].append(name)
                                        m2 = open(membersFile, 'w')
                                        m2.write(json.dumps(d, indent=4))
                                        m2.close()
                                        #Add them to roles.py
                                        with open(python_path + '/roles.py') as (file):
                                            s = [ row for row in file ]
                                            s[10] = 'special = ' + str(updated) + '\n'
                                            f = open(python_path + '/roles.py', 'w')
                                            for i in s:
                                                f.write(i)
                                            f.close()
                    except:
                        ba.screenmessage(f"Using: /special [ClientID] add/remove Cmds", clients=[clientID], transient=True)
                #PARTYNAME
                elif m == '/partyname':
                    if a == []:
                        ba.screenmessage(f"Usage: /partyname Name of party", clients=[clientID], transient=True)
                    else:
                        name = ''
                        for word in a:
                            name += word + ' '
                        try:
                            _ba.set_public_party_name(name)
                            ba.screenmessage(f"Party name changed to '{name}'.")
                            mysettings.server_name = name
                            commandSuccess=True
                        except:
                            sendError("failed to change party's name")
                #PARTY
                elif m == '/party':
                    if a == []:
                        ba.screenmessage(f"Usage: /party 0(pvt) or 1(pub)", clients=[clientID], transient=True)
                    elif (a[0] == '0') or (a[0].startswith('Pri')) or (a[0] == 'Pvt'):
                        try:
                            _ba.set_public_party_enabled(False)
                            _ba.chatmessage('Party is Private...')
                            commandSuccess=True
                        except:
                            sendError('failed to change',clientID)
                    elif a[0] == '1' or (a[0].startswith('Pub')):
                        try:
                            _ba.set_public_party_enabled(True)
                            _ba.chatmessage('Party is Public...')
                            commandSuccess=True
                        except:
                            sendError('failed to change',clientID)
                    else:
                        ba.screenmessage(f"Usage: /party 0(pvt) or 1(pub)", clients=[clientID], transient=True)
                #SET SCREEN TEXT COLOR
                elif m in ('/setscreentextcolor', '/settextcolor', '/setscreencolor'):
                    try:
                        if len(a) > 1: screenTextColor = (int(a[0]), int(a[1]), int(a[2]))
                        if (len(a) == 1) and (isinstance(a[0], int)): screenTextColor = tuple(a[0])
                        commandSuccess = True
                    except:
                        ba.screenmessage('Usage: /say <text to send>', transient=True, clients=[clientID])
                #SET CHAT COOL DOWN TIME
                elif m in ('/setchatcooldowntime', '/setchatcdtime', '/setchattime'):
                    try:
                        chatCoolDownTime = int(a[0])
                        _ba.chatmessage(f"Chat Cool Down Time had set to {str(a[0])} seconds...")
                        commandSuccess = True
                    except:
                        ba.screenmessage('Usage: /setchatcooldowntime <time in seconds>', transient=True, clients=[clientID])
                #PAUSE
                elif m == '/pause':
                    activity.globalsnode.paused = activity.globalsnode.paused == False
                    commandSuccess=True
                #SETTINGS
                elif m == '/settings':
                    if True: #try:
                        success = False
                        if a[0] == 'powerups':
                            if len(a) <= 2:
                                sendError(f"Invalid key !, Try checking by '/help settings'",clientID)
                            else:
                                for k,v in powerups.items():
                                    if str(k) == str(a[1]):
                                        if str(a[2]) == 'enable':
                                            if powerups[k] != True:
                                                powerups[k] = True
                                                commandSuccess=True
                                            else: sendError(f"This Setting is already enabled !",clientID)
                                        if str(a[2]) == 'disable':
                                            if powerups[k] != False:
                                                powerups[k] = False
                                                commandSuccess=True
                                            else: sendError(f"This Setting is already disabled !",clientID)
                                    else: sendError(f"Invalid key !, Try checking by '/help settings'",clientID)
                        else:
                            if len(a) > 1:
                                for k,v in settings.items():

                                    if str(k) == str(a[0]):
                                        if str(a[1]) == 'enable':
                                            if settings[k] != True:
                                                settings[k] = True
                                                commandSuccess=True
                                            else: sendError(f"This Setting is already enabled !",clientID)
                                        if str(a[1]) == 'disable':
                                            if settings[k] != False:
                                                settings[k] = False
                                                commandSuccess=True
                                            else: sendError(f"This Setting is already disabled !",clientID)
                                    else: sendError(f"Invalid key !, Try checking by '/help settings'",clientID)
                            else:
                                ba.screenmessage(f"Invalid key !, Try checking by '/help settings'",clientID)
                        with open(python_path + '/administrator_setup.py') as (file):
                            s = [ row for row in file ]
                            s[0] = 'settings = ' + str(settings) + '\n'
                            s[1] = 'powerups = ' + str(powerups) + '\n'
                            f = open(python_path + '/settings.py', 'w')
                            for i in s:
                                f.write(i)
                            f.close()
                    '''except:
                        ba.screenmessage(f"Using: /settings [setting] [subSetting(optional)] enable/disable", clients=[clientID], transient=True)'''
                else:
                    pass

c = chatOptions()
def cmd(clientID: int, msg: str):
    if settings['enableCoinSystem']:
        import coinSystem
    if _ba.get_foreground_host_activity() is not None:
        c.opt(msg, clientID)
        if commandSuccess:
            #send the Command Message
            cmdMsg = f"{str(client_str)} - {str(msg)}"
            if settings['hideCmds']: ba.screenmessage(cmdMsg,color=(0,0,1))
            if commandByCoin:
                coinSystem.addCoins(uniqueID, costOfCommand * -1)
                _ba.chatmessage(f"Success! That cost you {tic}{str(costOfCommand)}")
            else:
                with ba.Context(_ba.get_foreground_host_activity()):
                    ba.screenmessage(reply, color=(0.1,1,0.1))
                    #_ba.chatmessage(reply)
            #Update Logs...
            now = datetime.now()
            logMsg = now.strftime(f"%S:%M:%h - %d %b %y ||{uniqueID}|| {cmdMsg} \n")
            print(logMsg)
            log_list = get_cmd_logs_as_list()
            log_list.insert(0, logMsg)
            with open(cmdLogFile, 'w') as f:
                for i in log_list:
                    f.write(i)
                f.close()
    return