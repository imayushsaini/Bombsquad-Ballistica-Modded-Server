import random

donators_list = [
'Eggs broke and',
'pranav',
'your mom',
'saitama',
'one simp',
'idiot',
'mr smoothy'
]

def get_random_donator():
	return random.choice(donators_list)

def get_random_cash():
	return random.randrange(80)
