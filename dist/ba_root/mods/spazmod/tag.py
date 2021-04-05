
import pdata

def addtag(node,player):
	session_player=player.sessionplayer
	account_id=session_player.get_account_id()
	customtag=pdata.custom()['customtag']
	roles=pdata.roles()
	role=pdata.get_role(account_id)
	tag=None
	if account_id in customtag:
		tag=customtag[account_id]
	elif role:
		tag=roles[role]['tag']

	tag(node,tag)

def addrank(node,player):

class tag(object):
	def __init__(owner=None,tag="somthing"):
		mnode = ba.newnode('math',
                               owner=self.node,
                               attrs={
                                   'input1': (0, 1.4, 0),
                                   'operation': 'add'
                               })
		self.node.connectattr('torso_position', mnode, 'input2')
		self.tag_text = ba.newnode('text',
                                          owner=self.node,
                                          attrs={
                                              'text': tag,
                                              'in_world': True,
                                              'shadow': 1.0,
                                              'flatness': 1.0,
                                              'color': (1,1,1),
                                              'scale': 0.02,
                                              'h_align': 'center'
                                          })
		mnode.connectattr('output', self.tag_text, 'position')

class rank(object):
	def __init__(owner=None,rank=1):
		mnode = ba.newnode('math',
                               owner=self.node,
                               attrs={
                                   'input1': (0, 1.4, 0),
                                   'operation': 'add'
                               })
		self.node.connectattr('torso_position', mnode, 'input2')
		self.rank_text = ba.newnode('text',
                                          owner=self.node,
                                          attrs={
                                              'text': str(rank),
                                              'in_world': True,
                                              'shadow': 1.0,
                                              'flatness': 1.0,
                                              'color': (1,1,1),
                                              'scale': 0.02,
                                              'h_align': 'center'
                                          })
		mnode.connectattr('output', self.rank_text, 'position')




	

