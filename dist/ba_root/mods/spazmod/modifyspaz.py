from spazmod import tag
from spazmod import effects
import setting
from random import randint

import _ba,ba
import ba.internal
_setting=setting.get_settings_data()

def update_name():
	import ba.internal
	from stats import mystats
	stat = mystats.get_all_stats()
	ros = ba.internal.get_game_roster()
	for i in ros:
		if i['account_id']:
			name = i['display_string']
			aid = i['account_id']
			if aid in stat:
				stat[aid]['name'] = name
	mystats.dump_stats(stat)

# all activites related to modify spaz by any how will be here
def main(spaz, node, player):
	
	if _setting['enablehptag']:
		tag.addhp(spaz)
	if _setting['enabletags']:
		tag.addtag(node,player)
	if _setting['enablerank']:
		tag.addrank(node,player)
	if _setting['enableeffects']:
		effects.Effect(spaz,player)
	

	#update_name()  will add threading here later . it was adding delay on game start 

def getCharacter(player,character):
	
	if _setting["sameCharacterForTeam"]:
		
		if "character" in player.team.sessionteam.customdata:
			
			return player.team.sessionteam.customdata["character"]
	
	return character


def getRandomCharacter(otherthen):
	characters=list(ba.app.spaz_appearances.keys())
	invalid_characters=["Snake Shadow","Lee","Zola","Butch","Witch","Middle-Man","Alien","OldLady","Wrestler","Gretel","Robot"]
	
	while True:
		val=randint(0,len(characters)-1)
		ch=characters[val]
		if ch not in invalid_characters and ch not in otherthen:
			return ch


def setTeamCharacter():
	if not _setting["sameCharacterForTeam"]:
		return
	used=[]
	teams=ba.internal.get_foreground_host_session().sessionteams
	if len(teams) < 10:
		for team in teams:
			character=getRandomCharacter(used)
			used.append(character)
			team.name=character
			team.customdata["character"]=character
			
