import ba,_ba
from bastd.gameutils import SharedObjects
import random
from ba._gameactivity import GameActivity

import random
def factory(random_col:bool):
	act=_ba.get_foreground_host_activity()
	if not isinstance(act,GameActivity):
		return
	m=_ba.get_foreground_host_activity().map.get_def_bound_box('area_of_interest_bounds')
	part1=list(m)
	part2=list(m)
	half=(m[0]+m[3])/2
	part1[3]=half
	part2[0]=half
	ba.timer(0.3,ba.Call(create_fly,part1,random_col))
	ba.timer(1,ba.Call(create_fly,part2,random_col))
	ba.timer(0.12,ba.Call(create_fly,part1,random_col))
	ba.timer(0.88,ba.Call(create_fly,part2,random_col))
	ba.timer(1.8,ba.Call(create_fly,part1,random_col))
	ba.timer(3.3,ba.Call(create_fly,part2,random_col))
	ba.timer(4.78,ba.Call(create_fly,part1,random_col))
	ba.timer(2,ba.Call(create_fly,part2,random_col))
	ba.timer(6.3,ba.Call(create_fly,part1,random_col))
	ba.timer(3.3,ba.Call(create_fly,part2,random_col))
	ba.timer(4.78,ba.Call(create_fly,part1,random_col))
	ba.timer(2,ba.Call(create_fly,part2,random_col))
	ba.timer(6.3,ba.Call(create_fly,part1,random_col))
	ba.timer(3.5,ba.Call(create_fly,part2,random_col))
	ba.timer(4.28,ba.Call(create_fly,part1,random_col))
	ba.timer(2.2,ba.Call(create_fly,part2,random_col))
	ba.timer(6.1,ba.Call(create_fly,part1,random_col))

def create_fly(points,random_col):
	flies(points,random_col).autoretain()

class flies(ba.Actor):
	def __init__(self,m,random_col):
		super().__init__()
		shared = SharedObjects.get()

		if random_col:
			col=(random.uniform(0,1.2),random.uniform(0,1.2),random.uniform(0,1.2))
		else:
			col=(0.9,0.7,0.0)
		self.mat = ba.Material()
		self.mat.add_actions(
		            actions=(
		            	('modify_part_collision', 'collide', False),
		            	('modify_part_collision','physical',False),
		        ))

		
		self.node = ba.newnode('prop',
				                    delegate=self,
									attrs={
									'model':ba.getmodel('bomb'),
									'position':(2,4,2),
									'body':'capsule',
									'shadow_size':0.0,
									'color_texture':ba.gettexture('coin'),
									'reflection':'soft',
									'reflection_scale':[1.5],
									'materials':[shared.object_material,self.mat]

									})
		ba.animate(self.node,'model_scale',{0:0,1:0.19,5:0.10,10:0.0},loop=True)
		ba.animate_array(self.node,'position',3,self.generateKeys(m),loop=True)

		self.light=ba.newnode('light',owner=self.node,attrs={'intensity':0.6,
																'height_attenuated':True,
																'radius':0.2,
																'color':col})
		ba.animate(self.light,'radius',{0:0.0,20:0.4,70:0.1,100:0.3,150:0},loop=True)
		self.node.connectattr('position',self.light,'position')
	def handlemessage(self,msg):
		
		if isinstance(msg,ba.DieMessage):
			
			pass
			# self.node.delete()
		else:
			super().handlemessage(msg)

	def generateKeys(self,m):
		
		keys={}
		t=0
		
		last_x=random.randrange(int(m[0]),int(m[3]))
		last_y=random.randrange(int(m[1]),int(m[4]))
		if int(m[2])==int(m[5]):
			last_z=int(m[2])
		else:
			last_z=random.randrange(int(m[2]),int(m[5]))
		for i in range(0,7):
			x=self.generateRandom(int(m[0]),int(m[3]),last_x)
			last_x=x
			y=self.generateRandom(int(m[1]),int(m[4]),last_y)
			last_y=y
			z=self.generateRandom(int(m[2]),int(m[5]),last_z)
			last_z=z
			keys[t]=(x,abs(y),z)
			t +=30
		
		return keys
	def generateRandom(self,a,b,z):
		if a==b:
			return a

		while True:
			n= random.randrange(a,b)
			if abs(z-n) < 6:
				return n


