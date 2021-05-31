from chatHandle import handlechat

def filter_chat_message(msg, client_id):
	
	return handlechat.filter_chat_message(msg, client_id)


def on_app_launch():
	from tools import whitelist
	whitelist.Whitelist()

	#something

def score_screen_on_begin(_stats):
    pass
	#stats

def playerspaz_init(player):
    pass
	#add tag,rank,effect

