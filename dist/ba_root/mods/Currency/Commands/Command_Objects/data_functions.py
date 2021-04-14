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
	
	PlayerData = get_player_data(userid)
	
	balance = CLstr("English", "balance").format(str(name), str(PlayerData[0]), str(PlayerData[1]),  str(PlayerData[2]))
	send(balance, clientid)




def beg_call(userid : str, clientid : int):
	open_account(userid)
	earned = get_random_cash()
	
	update_bank(userid, earned, "cash", type_only=True)
	cash = get_player_data(userid)[0]
	donator = get_random_donator()
	
	send(CLstr("English", "beg").format(donator, earned, cash), clientid)




def withdraw_call(userid : str, args : int, clientid : int):
	open_account(userid)
	withd = int(args[0])
	
	if cheack_withd(userid, withd, clientid):
		return
	
	update_bank(userid, withd)
	
	send(CLstr("English", "withdraw").format(withd), clientid)




def deposit_call(userid : str, args : int, clientid : int):
	open_account(userid)
	dep = int(args[0])
	
	if cheack_cash_and_space(userid, dep, clientid):
		return
	
	update_bank(userid, dep, "bank")
	
	send(CLstr("English", "deposit").format(dep), clientid)