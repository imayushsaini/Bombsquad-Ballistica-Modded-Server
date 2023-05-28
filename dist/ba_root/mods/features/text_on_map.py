# Released under the MIT License. See LICENSE for details.

""" TODO need to set coordinates of text node , move timer values to settings.json """

from ba._generated.enums import TimeType
import ba, _ba
import ba.internal
import setting
from stats import mystats
from datetime import datetime
import random
setti=setting.get_settings_data()
class textonmap:

    def __init__(self):
        data = setti['textonmap']
        left = data['bottom left watermark']
        top = data['top watermark']
        nextMap=""
        try:
            nextMap=ba.internal.get_foreground_host_session().get_next_game_description().evaluate()
        except:
            pass
        top = top.replace("@IP", _ba.our_ip).replace("@PORT", str(_ba.our_port))
        self.index = 0
        self.highlights = data['center highlights']["msg"]
        self.left_watermark(left)
        self.top_message(top)
        self.nextGame(nextMap)
        self.restart_msg()
        if hasattr(_ba, "season_ends_in_days"):
            if _ba.season_ends_in_days < 9:
                self.season_reset(_ba.season_ends_in_days)
        if setti["leaderboard"]["enable"]:
            self.leaderBoard()
        self.timer = ba.timer(8, ba.Call(self.highlights_), repeat=True)

    def highlights_(self):
        if setti["textonmap"]['center highlights']["randomColor"]:
            color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0))
        else:
            color=tuple(setti["textonmap"]["center highlights"]["color"])
        node = _ba.newnode('text',
                            attrs={
                                'text': self.highlights[self.index],
                                'flatness': 1.0,
                                'h_align': 'center',
                                'v_attach':'bottom',
                                'scale':1,
                                'position':(0,138),
                                'color':color
                            })

        self.delt = ba.timer(7,node.delete)
        self.index = int((self.index+1)%len(self.highlights))

    def left_watermark(self, text):
        node = _ba.newnode('text',
                            attrs={
                                'text': text,
                                'flatness': 1.0,
                                'h_align': 'left',
                                'v_attach':'bottom',
                                'h_attach':'left',
                                'scale':0.7,
                                'position':(25,67),
                                'color':(0.7,0.7,0.7)
                            })
    def nextGame(self,text):
        node = _ba.newnode('text',
                            attrs={
                                'text':"Next : "+text,
                                'flatness':1.0,
                                'h_align':'right',
                                'v_attach':'bottom',
                                'h_attach':'right',
                                'scale':0.7,
                                'position':(-25,16),
                                'color':(0.5,0.5,0.5)
                            })
    def season_reset(self,text):
        node = _ba.newnode('text',
                            attrs={
                                'text':"Season ends in: "+str(text)+" days",
                                'flatness':1.0,
                                'h_align':'right',
                                'v_attach':'bottom',
                                'h_attach':'right',
                                'scale':0.5,
                                'position':(-25,34),
                                'color':(0.6,0.5,0.7)
                            })
    def restart_msg(self):
        if hasattr(_ba,'restart_scheduled'):
            _ba.get_foreground_host_activity().restart_msg = _ba.newnode('text',
                                attrs={
                                    'text':"Server going to restart after this series.",
                                    'flatness':1.0,
                                    'h_align':'right',
                                    'v_attach':'bottom',
                                    'h_attach':'right',
                                    'scale':0.5,
                                    'position':(-25,54),
                                    'color':(1,0.5,0.7)
                                })

    def top_message(self, text):
        node = _ba.newnode('text',
                            attrs={
                                'text': text,
                                'flatness': 1.0,
                                'h_align': 'center',
                                'v_attach':'top',
                                'scale':0.7,
                                'position':(0,-70),
                                'color':(1,1,1)
                            })

    def leaderBoard(self):
        if len(mystats.top3Name) >2:
            if setti["leaderboard"]["barsBehindName"]:
                self.ss1=ba.newnode('image',attrs={'scale':(300,30),'texture':ba.gettexture('bar'),'position':(0,-80),'attach':'topRight','opacity':0.5,'color':(0.7,0.1,0)})
                self.ss1=ba.newnode('image',attrs={'scale':(300,30),'texture':ba.gettexture('bar'),'position':(0,-115),'attach':'topRight','opacity':0.5,'color':(0.6,0.6,0.6)})
                self.ss1=ba.newnode('image',attrs={'scale':(300,30),'texture':ba.gettexture('bar'),'position':(0,-150),'attach':'topRight','opacity':0.5,'color':(0.1,0.3,0.1)})

            self.ss1a=ba.newnode('text',attrs={'text':"#1 "+mystats.top3Name[0][:10]+"...",'flatness':1.0,'h_align':'left','h_attach':'right','v_attach':'top','v_align':'center','position':(-140,-80),'scale':0.7,'color':(0.7,0.4,0.3)})

            self.ss1a=ba.newnode('text',attrs={'text':"#2 "+mystats.top3Name[1][:10]+"...",'flatness':1.0,'h_align':'left','h_attach':'right','v_attach':'top','v_align':'center','position':(-140,-115),'scale':0.7,'color':(0.8,0.8,0.8)})

            self.ss1a=ba.newnode('text',attrs={'text':"#3 "+mystats.top3Name[2][:10]+"...",'flatness':1.0,'h_align':'left','h_attach':'right','v_attach':'top','v_align':'center','position':(-140,-150),'scale':0.7,'color':(0.2,0.6,0.2)})
