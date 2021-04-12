""" store functions executed when chat command are called """
import ba, _ba, json, random
from _ba import chatmessage as send
from _ba import screenmessage as screenmsg
from Currency.Handlers.bank_handler import *
from Currency.Handlers.ba_get_player_data import *
from Currency.Handlers.cooldown_manager import *
from .fun import get_random_donator, get_random_cash




def balance_call(userid, clientid):
	open_account(userid)
	
	users = get_bank_data()
	name = client_to_name(clientid)
	
	cash_amt = users[str(userid)]["cash"]
	bank_cash_amt = users[str(userid)]["bank_cash"]
	bank_space = users[str(userid)]["bank_space"]
	
	balance = '|| {} | Cash - {} | Bank- {}/{} ||'.format(str(name), str(cash_amt), str(bank_cash_amt),  str(bank_space))
	send(balance)



def beg_call(userid):
	open_account(userid)
	earned = get_random_cash()
	
	users = get_bank_data()
	user = users[str(userid)]
	
	user["cash"] += earned
	cash_amt = user["cash"]
	donator = get_random_donator()
	send(f'{donator} gave you {earned} now you have {cash_amt} coins')
	
	commit(users)


