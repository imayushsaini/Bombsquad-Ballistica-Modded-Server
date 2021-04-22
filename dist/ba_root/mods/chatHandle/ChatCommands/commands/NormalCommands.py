from .Handlers import send
import ba, _ba


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
		stats()
	
	elif command in ['list', 'l']:
		list(clientid)
		
	elif command in ['uniqeid', 'id', 'pb-id', 'pb' , 'accountid']:
		accountid_request(arguments, clientid, accountid)





def stats():
	""" Stats """
	return




def list(clientid):
	"""Returns The List Of Players Clientid and index"""
	
	p = u'{0:^16}{1:^15}{2:^10}'
	seprator = '\n______________________________\n'
	
	
	list = p.format('Name', 'Client ID' , 'Player ID')+seprator
	session = _ba.get_foreground_host_session()
	
	
	for i in session.sessionplayers:
		list += p.format(i.getname(icon = False),
		i.inputdevice.client_id, i.id)
	
	send(list, clientid)
	



def accountid_request(arguments, clientid, accountid):
	"""Returns The Account Id Of Players"""
	
	if arguments == [] or arguments == ['']:
		send(f"Your account id is {accountid} ", clientid)
		
	else:
		try:
			session = _ba.get_foreground_host_session()
			player = session.sessionplayers[int(arguments[0])]
			
			name = player.getname(full=True, icon=True)
			accountid = player.get_account_id()
			
			send(f" {name}'s account id is '{accountid}' ", clientid)
		except:
			return
		
	