""" helperfunctions for save lot of lines of code """
import ba, _ba, json
from .ba_get_player_data import send
from .CLstr import Errorstr

bank_path = _ba.env()['python_directory_user']+'/Currency/Data/bank.json'



def get_bank_data():
	with open(bank_path, 'r') as f:
		users = json.load(f)
	return users



def commit(data):
	with open(bank_path, "w") as f:
		json.dump(data, f, indent=2)



def open_account(accountid : str):
	users = get_bank_data()
	
	if str(accountid) in users:
		return False
	else:
		users[str(accountid)] = {}
		users[str(accountid)]["cash"] = 0
		users[str(accountid)]["bank_space"] = 100
		users[str(accountid)]["bank_cash"] = 0
		commit(users)
	return True




def cheack_cash_and_space(userid, ammount : int, clientid : int):
	users = get_bank_data()
	
	cash_amt = users[str(userid)]["cash"]
	bank_space = users[str(userid)]["bank_space"]
	
	
	if bank_space < ammount:
		send(Errorstr("English", "short_space"), clientid)
		return True
	if cash_amt < ammount:
		send(Errorstr("English", "short_ammount"), clientid)
		return True



def cheack_withd(userid, ammount : int, clientid : int):
	users = get_bank_data()
	bank_cash = users[str(userid)]["bank_cash"]
	
	if bank_cash < ammount:
		send(Errorstr("English", "short_bank_cash"), clientid)
		return True



