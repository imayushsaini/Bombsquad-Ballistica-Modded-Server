""" store functions executed when chat command are called """
import ba, _ba, json, random

from Currency.Handlers.bank_handler import *
from Currency.Handlers.ba_get_player_data import *
#from Currency.Handlers.cooldown_manager import *
from Currency.Handlers.CLstr import CLstr, Errorstr
from .fun import get_random_donator, get_random_cash





def balance_call(userid : str, clientid : int):
	open_account(userid)
	
	users = get_bank_data()
	name = client_to_name(clientid)
	
	cash_amt = users[str(userid)]["cash"]
	bank_cash_amt = users[str(userid)]["bank_cash"]
	bank_space = users[str(userid)]["bank_space"]
	
	balance = CLstr("English", "balance").format(str(name), str(cash_amt), str(bank_cash_amt),  str(bank_space))
	send(balance, clientid)



def beg_call(userid : str, clientid : int):
	open_account(userid)
	earned = get_random_cash()
	
	users = get_bank_data()
	
	users[str(userid)]["cash"] += earned
	cash = users[str(userid)]["cash"]
	donator = get_random_donator()
	
	send(CLstr("English", "beg").format(donator, earned, cash), clientid)
	commit(users)



def withdraw_call(userid : str, args : int, clientid : int):
	open_account(userid)
	
	users = get_bank_data()
	withd = int(args[0])
	
	if cheack_withd(userid, withd, clientid):
		return
	
	users[str(userid)]["cash"] += withd
	users[str(userid)]["bank_cash"] -= withd
	commit(users)
	send(CLstr("English", "withdraw").format(withd), clientid)



def deposit_call(userid : str, args : int, clientid : int):
	open_account(userid)
	
	users = get_bank_data()
	dep = int(args[0])
	
	if cheack_cash_and_space(userid, dep, clientid):
		return
	
	users[str(userid)]["cash"] -= dep
	users[str(userid)]["bank_cash"] += dep
	commit(users)
	send(CLstr("English", "deposit").format(dep), clientid)