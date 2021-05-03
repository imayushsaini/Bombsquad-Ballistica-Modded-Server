# Released under the MIT License. See LICENSE for details.

""" TODO need to set coordinates of text node , move timer values to settings.json """

from ba._enums import TimeType
import ba, _ba
import setting

class textonmap:
	
	def __init__(self):
		
		data = setting.get_settings_data()['textonmap']
		left = data['bottom left watermark']
		top = data['top watermark']
		
		self.index = 0
		self.highlights = data['center highlights']
		self.left_watermark(left)
		self.top_message(top)
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
								'scale':1,
								'position':(-480,20),
								'color':(1,1,1)
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
							