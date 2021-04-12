""" check given command and executive the the cmd function from data functions"""

import ba, _ba
from .Command_Objects.data_functions import *


def on_command(cmd, args, accountid, clientid):
	
	if cmd in ['coins', 'bal', 'balance', 'me']:
		balance_call(accountid, clientid)
		
	elif cmd == 'beg':
		beg_call(accountid)
