# Released under the MIT License. See LICENSE for details.

from _ba import chatmessage as cmsg,          screenmessage as smsg
from .handlers import sess_players
import ba, _ba

cmnds = ['me', 'list', 'uniqeid']

cmnd_aliases = ['stats', 'score', 'rank', 'myself', 'l', 'id', 'pb-id', 'pb', 'accountid']


def exec_cmd(cmnd, arg, clid, pbid):
	
	if cmnd in ['me', 'stats', 'score', 'rank', 'myself']:
		stats_call()
	
	elif cmnd in ['list', 'l']:
		list_call(clid)
		
	elif cmnd in ['uniqeid', 'id', 'pb-id', 'pb' , 'accountid']:
		show_id_call(arg, pbid, clid)





def stats_call():
	pass



def list_call(clid):
	seprator = '______________________________'
	lst = u'{0:^16}{1:^15}{2:^10}'.format('name', 'client_id' , 'player_id') + f'\n{seprator}\n'
	
	for i in sess_players():
		lst += u'{0:^16}{1:^15}{2:^10}\n'.format(i.getname(icon = False), str(i.inputdevice.client_id), str(i.id))
	smsg(lst, color = (0,2.55,2.55), transient = True , clients = [clid])
	


def show_id_call(arg, acid, clid):
	if arg == [] or arg == ['']:
		cmsg(f'Your account id is {acid} ')
	else:
		try:
			rq_client = sess_players()[int(arg[0])]
			name = rq_client.getname(full=True , icon=True)
			acid = rq_client.get_account_id()
			smsg(f" {name}'s account id is '{acid}' ", color = (0,2.55,2.55), transient = True , clients = [clid])
		except:
			return
		
	