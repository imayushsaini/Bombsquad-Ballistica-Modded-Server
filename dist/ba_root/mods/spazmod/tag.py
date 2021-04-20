
from PlayersData import pdata
import ba
def addtag(node,player):
	session_player=player.sessionplayer
	account_id=session_player.get_account_id()
	customtag_=pdata.get_custom()
	customtag=customtag_['customtag']
	roles=pdata.get_roles()
	role=pdata.get_role(account_id)
	tag=None
	if account_id in customtag:
		tag=customtag[account_id]
	elif role:
		tag=roles[role]['tag']

	Tag(node,tag)
from stats import mystats
def addrank(node,player):
	session_player=player.sessionplayer
	account_id=session_player.get_account_id()
	rank=mystats.getRank(account_id)

	if rank:
		Rank(node,rank)

class Tag(object):
	def __init__(self,owner=None,tag="somthing"):
		self.node=owner
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
                                              'scale': 0.01,
                                              'h_align': 'center'
                                          })
		mnode.connectattr('output', self.tag_text, 'position')

class Rank(object):
	def __init__(self,owner=None,rank=99):
		self.node=owner
		mnode = ba.newnode('math',
                               owner=self.node,
                               attrs={
                                   'input1': (0, 1.2, 0),
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
                                              'scale': 0.01,
                                              'h_align': 'center'
                                          })
		mnode.connectattr('output', self.rank_text, 'position')




	

