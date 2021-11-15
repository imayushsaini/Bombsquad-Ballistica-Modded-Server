# Released under the MIT License. See LICENSE for details.

""" TODO need to set coordinates of text node , move timer values to settings.json """

from ba._generated.enums import TimeType
import ba, _ba
import setting
from stats import mystats
from datetime import datetime
class textonmap:

	def __init__(self):
		setti=setting.get_settings_data()
		data = setti['textonmap']
		left = data['bottom left watermark']
		top = data['top watermark']

		nextMap=_ba.get_foreground_host_session().get_next_game_description().evaluate()

		self.index = 0
		self.highlights = data['center highlights']
		self.left_watermark(left)
		self.top_message(top)
		self.nextGame(nextMap)
		self.leaderBoard()

		
		


		self.timer = ba.timer(8, ba.Call(self.highlights_), repeat=True)

	def highlights_(self):
		node = _ba.newnode('text',
							attrs={
								'text': self.highlights[self.index],
								'flatness': 1.0,
								'h_align': 'center',
								'v_attach':'bottom',
								'scale':1,
								'position':(0,138),
								'color':(1,1,1)
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
							    'position':(-25,18),
							    'color':(0.5,0.5,0.5)
							})


	def top_message(self, text):
		node = _ba.newnode('text',
							attrs={
								'text': text,
								'flatness': 1.0,
								'h_align': 'center',
								'v_attach':'top',
								'scale':1,
								'position':(0,138),
								'color':(1,1,1)
							})

	def leaderBoard(self):
		if len(mystats.top3Name) >2:

			self.ss1=ba.newnode('image',attrs={'scale':(300,30),'texture':ba.gettexture('bar'),'position':(0,-80),'attach':'topRight','opacity':0.5,'color':(0.7,0.1,0)})
			self.ss1a=ba.newnode('text',attrs={'text':"#1 "+mystats.top3Name[0][:10]+"...",'flatness':1.0,'h_align':'left','h_attach':'right','v_attach':'top','v_align':'center','position':(-140,-80),'scale':0.7,'color':(0.7,0.4,0.3)})

			self.ss1=ba.newnode('image',attrs={'scale':(300,30),'texture':ba.gettexture('bar'),'position':(0,-115),'attach':'topRight','opacity':0.5,'color':(0.6,0.6,0.6)})
			self.ss1a=ba.newnode('text',attrs={'text':"#2 "+mystats.top3Name[1][:10]+"...",'flatness':1.0,'h_align':'left','h_attach':'right','v_attach':'top','v_align':'center','position':(-140,-115),'scale':0.7,'color':(0.8,0.8,0.8)})

			self.ss1=ba.newnode('image',attrs={'scale':(300,30),'texture':ba.gettexture('bar'),'position':(0,-150),'attach':'topRight','opacity':0.5,'color':(0.1,0.3,0.1)})
			self.ss1a=ba.newnode('text',attrs={'text':"#3 "+mystats.top3Name[2][:10]+"...",'flatness':1.0,'h_align':'left','h_attach':'right','v_attach':'top','v_align':'center','position':(-140,-150),'scale':0.7,'color':(0.2,0.6,0.2)})
