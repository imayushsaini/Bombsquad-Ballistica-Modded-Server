from spazmod import tag
from spazmod import effects
import setting

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