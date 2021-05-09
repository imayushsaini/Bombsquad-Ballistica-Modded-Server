from spazmod import tag
from spazmod import effects
import setting

def update_name():
	import _ba
	from stats import mystats
	stat = mystats.get_all_stats()
	ros = _ba.get_game_roster()
	for i in ros:
		if i['account_id']:
			name = i['display_string']
			aid = i['account_id']
			if aid in stat:
				stat[aid]['name'] = name
	mystats.dump_stats(stat)

# all activites related to modify spaz by any how will be here
def main(spaz, node, player):
	_setting=setting.get_settings_data()
	if _setting['enablehptag']:
		tag.addhp(spaz)
	if _setting['enabletags']:
		tag.addtag(node,player)
	if _setting['enablerank']:
		tag.addrank(node,player)
	if _setting['enableeffects']:
		effects.Effect(spaz,player)
	update_name()