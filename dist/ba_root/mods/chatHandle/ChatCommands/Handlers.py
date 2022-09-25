# Released under the MIT License. See LICENSE for details.

from playersData import pdata
import ba
import ba.internal





def clientid_to_accountid(clientid):
	"""
	Transform Clientid To Accountid 
	
	Parameters:
		clientid : int
	
	Returns:
		None 
	"""
	for i in ba.internal.get_game_roster():
		if i['client_id'] == clientid:
			return i['account_id']
	return None





def check_permissions(accountid, command):
	"""
	Checks The Permission To Player To Executive Command
	
	Parameters:
		accountid : str
		command : str
	
	Returns:
		Boolean
	"""
	roles = pdata.get_roles()

	if is_server(accountid):
		return True

	for role in roles:
		if accountid in roles[role]["ids"]  and "ALL" in roles[role]["commands"]:
			return True

		elif accountid in roles[role]["ids"] and command in roles[role]["commands"]:
			return True
	return False


def is_server(accid):
	for i in ba.internal.get_game_roster():
		if i['account_id']==accid and i['client_id']==-1:
			return True