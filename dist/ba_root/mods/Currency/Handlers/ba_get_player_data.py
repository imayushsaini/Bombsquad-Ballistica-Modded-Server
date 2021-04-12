""" retruns information of given user using client_id """
import ba, _ba

def client_to_account(client_id):
	rost = _ba.get_game_roster()
	for i in rost:
		if i['client_id'] == client_id:
			return i['account_id']
	return None

def client_to_name(client_id):
	rost = _ba.get_game_roster()
	for i in rost:
		if i['client_id'] == client_id:
			return i['players'][0]['name_full']
	return None
  
 
def client_to_display_string(client_id):
	rost = _ba.get_game_roster()
	for i in rost:
		if i['client_id'] == client_id:
			return i['display_string']
	return None
