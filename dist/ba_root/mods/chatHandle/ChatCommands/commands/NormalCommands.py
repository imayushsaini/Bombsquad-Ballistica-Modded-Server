from .Handlers import send
import ba, _ba
import ba.internal
from stats import mystats
from ba._general import Call
import _thread
Commands = ['me', 'list', 'uniqeid']
CommandAliases = ['stats', 'score', 'rank', 'myself', 'l', 'id', 'pb-id', 'pb', 'accountid']



def ExcelCommand(command, arguments, clientid, accountid):
	"""
	Checks The Command And Run Function 
	
	Parameters:
		command : str 
		arguments : str 
		clientid : int 
		accountid : int 
	
	Returns:
		None
	"""
	if command in ['me', 'stats', 'score', 'rank', 'myself']:
		fetch_send_stats(accountid,clientid)
	
	elif command in ['list', 'l']:
		list(clientid)
		
	elif command in ['uniqeid', 'id', 'pb-id', 'pb' , 'accountid']:
		accountid_request(arguments, clientid, accountid)





def stats(ac_id,clientid):
	stats=mystats.get_stats_by_id(ac_id)
	if stats:
		reply="Score:"+str(stats["scores"])+"\nGames:"+str(stats["games"])+"\nKills:"+str(stats["kills"])+"\nDeaths:"+str(stats["deaths"])+"\nAvg.:"+str(stats["avg_score"])
	else:
		reply="Not played any match yet."

	_ba.pushcall(Call(send,reply,clientid),from_other_thread=True)
	
	
def fetch_send_stats(ac_id,clientid):
	_thread.start_new_thread(stats,(ac_id,clientid,))


def list(clientid):
	"""Returns The List Of Players Clientid and index"""
	
	p = u'{0:^16}{1:^15}{2:^10}'
	seprator = '\n______________________________\n'
	
	
	list = p.format('Name', 'Client ID' , 'Player ID')+seprator
	session = ba.internal.get_foreground_host_session()
	
	
	for index, player in enumerate(session.sessionplayers):
		list += p.format(player.getname(icon = False),
		player.inputdevice.client_id, index)+"\n"

	send(list, clientid)
	



def accountid_request(arguments, clientid, accountid):
	"""Returns The Account Id Of Players"""
	
	if arguments == [] or arguments == ['']:
		send(f"Your account id is {accountid} ", clientid)
		
	else:
		try:
			session = ba.internal.get_foreground_host_session()
			player = session.sessionplayers[int(arguments[0])]
			
			name = player.getname(full=True, icon=True)
			accountid = player.get_v1_account_id()
			
			send(f" {name}'s account id is '{accountid}' ", clientid)
		except:
			return
		
	