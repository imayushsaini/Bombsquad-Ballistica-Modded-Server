# Released under the MIT License. See LICENSE for details.

#TODO need to set coordinates of text node , move timer values to settings.json 
from ba._enums import TimeType
import ba,_ba
import setting
class textonmap:
	def __init__(self):
		self.index=0;
		_textonmap=setting.get_setting()['textonmap']
		self.highlights=_textonmap['center highlights']
		left=_textonmap['bottom left watermark']
		top=_textonmap['top watermark']

		self.timerr=ba.Timer(8,ba.Call(self.highlights),repeat=True)

		self.left_watermark(left)
		self.top_message(top)


	def highlights(self):
		hg=_ba.newnode('text',
                            attrs={
                                'text': self.highlights[self.index],
                                
                                'flatness': 1.0,
                                'h_align': 'center',
                                'v_attach':'bottom',
                                'scale':1,
                                'position':(0,138),
                                'color':(1,1,1)
                            })
		self.delt=ba.Timer(7,hg.delete)
		self.index=int((self.index+1)%len(self.highlights))

	def left_watermark(self,text):
		hg=_ba.newnode('text',
                            attrs={
                                'text': text,
                                
                                'flatness': 1.0,
                                'h_align': 'left',  
                                'v_attach':'bottom',
                                'scale':1,
                                'position':(0,138),
                                'color':(1,1,1)
                            })
	def top_message(self,text):
		txt=_ba.newnode('text',
                            attrs={
                                'text': text,
                                
                                'flatness': 1.0,    
                                'h_align': 'center',
                                'v_attach':'top',
                                'scale':1,
                                'position':(0,138),
                                'color':(1,1,1)
                            })