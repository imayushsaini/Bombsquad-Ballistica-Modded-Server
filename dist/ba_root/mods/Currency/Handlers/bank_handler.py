""" helperfunctions for save lot of lines of code """

import ba, _ba, json


bank_path = _ba.env()['python_directory_user']+'/Currency/Data/bank.json'




def open_account(accountid):
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



def get_bank_data():
	with open(bank_path, 'r') as f:
		users = json.load(f)
	return users



def commit(data):
	with open(bank_path, "w") as f:
		json.dump(data, f, indent=2)



