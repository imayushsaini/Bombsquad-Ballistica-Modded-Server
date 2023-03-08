# -*- coding: utf-8 -*-
# coding: utf-8

# ba_meta require api 7
from typing import Optional, Any, Dict, List, Type, Sequence
from ba._gameactivity import GameActivity
import ba,_ba
import ba.internal
import json
import os
import _thread
# from stats import mystats
os.environ['FLASK_APP'] = 'bombsquadflaskapi.py'
os.environ['FLASK_ENV'] = 'development'
from stats import mystats

stats={}
leaderboard={}
top200={}

class BsDataThread(object):
    def __init__(self):
        self.Timer = ba.Timer( 8,ba.Call(self.refreshStats),timetype = ba.TimeType.REAL,repeat = True)
        self.Timerr = ba.Timer( 10,ba.Call(self.startThread),timetype = ba.TimeType.REAL,repeat = True)

    def startThread(self):
        _thread.start_new_thread(self.refreshLeaderboard,())

    def refreshLeaderboard(self):
        global leaderboard
        global top200
        _t200={}

        lboard=mystats.get_all_stats()
        leaderboard=lboard
        try:
            entries = [(a['scores'], a['kills'], a['deaths'], a['games'], a['name'], a['aid'],a['last_seen']) for a in lboard.values()]
        except:
            print("stats reset is required , please clear out stats.json records , or download fresh stats.json from github")
            import _ba
            _ba.quit()
        entries.sort(key=lambda x: x[1] or 0, reverse=True)
        rank=0
        for entry in entries:
            rank+=1
            if rank >201:
                break
            _t200[entry[5]]={"rank":rank,"scores":int(entry[0]),"games":int(entry[3]),"kills":int(entry[1]),"deaths":int(entry[2]),"name_html":entry[4],"last_seen":entry[6]}
            top200=_t200

    def refreshStats(self):

        liveplayers={}
        nextMap=''
        currentMap=''
        global stats
        for i in ba.internal.get_game_roster():


            try:
                liveplayers[i['account_id']]={'name':i['players'][0]['name_full'],'client_id':i['client_id'],'device_id':i['display_string']}
            except:
                liveplayers[i['account_id']]={'name':"<in-lobby>",'clientid':i['client_id'],'device_id':i['display_string']}
        try:
            nextMap=ba.internal.get_foreground_host_session().get_next_game_description().evaluate()

            current_game_spec=ba.internal.get_foreground_host_session()._current_game_spec
            gametype: Type[GameActivity] =current_game_spec['resolved_type']

            currentMap=gametype.get_settings_display_string(current_game_spec).evaluate()
        except:
            pass
        minigame={'current':currentMap,'next':nextMap}
        # system={'cpu':"p.cpu_percent()",'ram':p.virtual_memory().percent}
        system={'cpu':"null",'ram':'null'}
        stats['system']=system
        stats['roster']=liveplayers
        stats['chats']=ba.internal.get_chat_messages()
        stats['playlist']=minigame
        stats['teamInfo']=self.getTeamInfo()

        #print(self.getTeamInfo());

    def getTeamInfo(self):
        data={}

        session=ba.internal.get_foreground_host_session()
        data['sessionType']=type(session).__name__
        teams=session.sessionteams
        for team in teams:
            data[team.id]={'name':team.name.evaluate(),
                           'color':list(team.color),
                           'score':team.customdata['score'],
                           'players':[]
                            }
            for player in team.players:
                teamplayer={'name':player.getname(),
                            'device_id':player.inputdevice.get_v1_account_name(True),
                            'inGame':player.in_game,
                            'character':player.character,
                            'account_id':player.get_v1_account_id()
                            }
                data[team.id]['players'].append(teamplayer)

        return data



BsDataThread()



import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', methods=['GET'])
def home():
    return '''Nothing here :)'''


# A route to return all of the available entries in our catalog.
@app.route('/getStats', methods=['GET'])
def api_all():
    return json.dumps(stats)

@app.route('/getLeaderboard',methods=['GET'])
def get_l():
    return json.dumps(leaderboard)

@app.route('/getTop200',methods=['GET'])
def get_top200():
    return json.dumps(top200)


class InitalRun:
    def __init__(self):
        print("start flask")
        flask_run = _thread.start_new_thread(app.run, ("0.0.0.0",5000,False ))

def enable():
    InitalRun()
# SAMPLE OUTPUT
# {'system': {'cpu': 80, 'ram': 34}, 'roster': {}, 'chats': [], 'playlist': {'current': 'Meteor Shower @ Rampage', 'next': 'Assault @ Step Right Up'}, 'teamInfo': {'sessionType': 'DualTeamSession', 0: {'name': 'Blue', 'color': (0.1, 0.25, 1.0), 'score': 1, 'players': [{'name': 'Jolly', 'device_id': '\ue030PC295588', 'inGame': True, 'character': 'xmas', 'account_id': 'pb-IF4TVWwZUQ=='}]}, 1: {'name': 'Red', 'color': (1.0, 0.25, 0.2), 'score': 0, 'players': []}}}
