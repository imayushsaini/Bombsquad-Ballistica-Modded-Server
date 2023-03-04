# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import json
import math
import random
from bastd.game.elimination import Icon
from bastd.actor.bomb import Bomb, Blast
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBox
from bastd.actor.flag import Flag, FlagPickedUpMessage
from bastd.actor.spazbot import SpazBotSet, BrawlerBotLite, SpazBotDiedMessage

if TYPE_CHECKING:
	from typing import Any, Sequence


lang = ba.app.lang.language
if lang == 'Spanish':
	name = 'Día de la Bandera'
	description = ('Recoge las banderas para recibir un premio.\n'
				   'Pero ten cuidado...')
	slow_motion_deaths = 'Muertes en Cámara Lenta'
	credits = 'Creado por MattZ45986 en Github | Actualizado por byANG3L'
	you_were = 'Estas'
	cursed_text = 'MALDITO'
	run = 'CORRE'
	climb_top = 'Escala a la cima'
	bomb_rain = '¡LLUVIA DE BOMBAS!'
	lame_guys = 'Chicos Ligeros'
	jackpot = '¡PREMIO MAYOR!'
	diedtxt = '¡'
	diedtxt2 = ' ha sido eliminado!'
else:
	name = 'Flag Day'
	description = 'Pick up flags to receive a prize.\nBut beware...'
	slow_motion_deaths = 'Slow Motion Deaths'
	credits = 'Created by MattZ45986 on Github | Updated by byANG3L'
	you_were = 'You were'
	cursed_text = 'CURSED'
	run = 'RUN'
	climb_top = 'Climb to the top'
	bomb_rain = 'BOMB RAIN!'
	lame_guys = 'Lame Guys'
	jackpot = '!JACKPOT!'
	diedtxt = ''
	diedtxt2 = ' died!'


class Icon(Icon):

	def __init__(
		self,
		player: Player,
		position: tuple[float, float],
		scale: float,
		show_lives: bool = True,
		show_death: bool = True,
		name_scale: float = 1.0,
		name_maxwidth: float = 115.0,
		flatness: float = 1.0,
		shadow: float = 1.0,
		dead: bool = False,
	):
		super().__init__(player,position,scale,show_lives,show_death,
			name_scale,name_maxwidth,flatness,shadow)
		if dead:
			self._name_text.opacity = 0.2
			self.node.color = (0.7, 0.3, 0.3)
			self.node.opacity = 0.2


class FlagBearer(PlayerSpaz):
	def handlemessage(self, msg: Any) -> Any:
		super().handlemessage(msg)
		if isinstance(msg, ba.PowerupMessage):
			activity = self.activity
			player = self.getplayer(Player)
			if not player.is_alive():
				return
			if activity.last_prize == 'curse':
				player.team.score += 25
				activity._update_scoreboard()
			elif activity.last_prize == 'land_mines':
				player.team.score += 15
				activity._update_scoreboard()
				self.connect_controls_to_player()
			elif activity.last_prize == 'climb':
				player.team.score += 50
				activity._update_scoreboard()
			if msg.poweruptype == 'health':
				activity.round_timer = None
				ba.timer(0.2, activity.setup_next_round)


class Player(ba.Player['Team']):
	"""Our player type for this game."""

	def __init__(self) -> None:
		self.dead = False
		self.icons: list[Icon] = []

class Team(ba.Team[Player]):
	"""Our team type for this game."""

	def __init__(self) -> None:
		self.score = 0


# ba_meta export game
class FlagDayGame(ba.TeamGameActivity[Player, Team]):
	"""A game type based on acquiring kills."""

	name = name
	description = description

	# Print messages when players die since it matters here.
	announce_player_deaths = True

	allow_mid_activity_joins = False

	@classmethod
	def get_available_settings(
		cls, sessiontype: type[ba.Session]
	) -> list[ba.Setting]:
		settings = [
			ba.BoolSetting(slow_motion_deaths, default=True),
			ba.BoolSetting('Epic Mode', default=False),
		]
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
		return (
			issubclass(sessiontype, ba.CoopSession)
			or issubclass(sessiontype, ba.DualTeamSession)
			or issubclass(sessiontype, ba.FreeForAllSession)
		)

	@classmethod
	def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
		return ['Courtyard']

	def __init__(self, settings: dict):
		super().__init__(settings)
		self.credits()
		self._scoreboard = Scoreboard()
		self._dingsound = ba.getsound('dingSmall')
		self._epic_mode = bool(settings['Epic Mode'])
		self._slow_motion_deaths = bool(settings[slow_motion_deaths])
		self.current_player: Player | None = None
		self.prize_recipient: Player | None = None
		self.bomb_survivor: Player | None = None
		self.bad_guy_cost: int = 0
		self.player_index: int = 0
		self.bombs: list = []
		self.queue_line: list = []
		self._bots: SpazBotSet | None = None
		self.light: ba.Node | None = None
		self.last_prize = 'none'
		self._flag: Flag | None = None
		self._flag2: Flag | None = None
		self._flag3: Flag | None = None
		self._flag4: Flag | None = None
		self._flag5: Flag | None = None
		self._flag6: Flag | None = None
		self._flag7: Flag | None = None
		self._flag8: Flag | None = None
		self.set = False
		self.round_timer: ba.Timer | None = None
		self.give_points_timer: ba.Timer | None = None

		self._jackpot_sound = ba.getsound('achievement')
		self._round_sound = ba.getsound('powerup01')
		self._dingsound = ba.getsound('dingSmall')

		# Base class overrides.
		self.slow_motion = self._epic_mode
		self.default_music = (
			ba.MusicType.EPIC if self._epic_mode else ba.MusicType.TO_THE_DEATH
		)

	def on_team_join(self, team: Team) -> None:
		if self.has_begun():
			self._update_scoreboard()

	def on_player_leave(self, player: Player) -> None:
		if player is self.current_player:
			self.setup_next_round()
		self._check_end_game()
		super().on_player_leave(player)
		self.queue_line.remove(player)
		self._update_icons()

	def on_begin(self) -> None:
		super().on_begin()
		for player in self.players:
			if player.actor:
				player.actor.handlemessage(ba.DieMessage())
				player.actor.node.delete()
			self.queue_line.append(player)
		self.spawn_player_spaz(
			self.queue_line[self.player_index % len(self.queue_line)],
			(0.0, 3.0, -2.0))
		self.current_player = self.queue_line[0]
		# Declare a set of bots (enemies) that we will use later
		self._bots = SpazBotSet()
		self.reset_flags()
		self._update_icons()
		self._update_scoreboard()

	def credits(self) -> None:
		ba.newnode(
			'text',
			attrs={
				'v_attach': 'bottom',
				'h_align': 'center',
				'vr_depth': 0,
				'color': (0, 0.2, 0),
				'shadow': 1.0,
				'flatness': 1.0,
				'position': (0,0),
				'scale': 0.8,
				'text': credits
			})

	def _update_icons(self) -> None:
		# pylint: disable=too-many-branches
		for player in self.queue_line:
			player.icons = []
			if player == self.current_player:
				xval = 0
				x_offs = -78
				player.icons.append(
					Icon(player,
						 position=(xval, 65),
						 scale=1.0,
						 name_maxwidth=130,
						 name_scale=0.8,
						 flatness=0.0,
						 shadow=0.5,
						 show_death=True,
						 show_lives=False))
			elif player.dead:
				xval = 65
				x_offs = 78
				player.icons.append(
					Icon(player,
						 position=(xval, 50),
						 scale=0.5,
						 name_maxwidth=75,
						 name_scale=1.0,
						 flatness=1.0,
						 shadow=1.0,
						 show_death=False,
						 show_lives=False,
						 dead=True))
				xval += x_offs * 0.56
			else:
				xval = -65
				x_offs = 78
				player.icons.append(
					Icon(player,
						 position=(xval, 50),
						 scale=0.5,
						 name_maxwidth=75,
						 name_scale=1.0,
						 flatness=1.0,
						 shadow=1.0,
						 show_death=False,
						 show_lives=False))
				xval -= x_offs * 0.56

	def give_prize(self, prize: int) -> None:
		if prize == 1:
			# Curse him aka make him blow up in 5 seconds
			# give them a nice message
			ba.screenmessage(you_were, color=(0.1, 0.1, 0.1))
			ba.screenmessage(cursed_text, color=(1.0, 0.0, 0.0))
			self.make_health_box((0.0, 0.0, 0.0))
			self.last_prize = 'curse'
			self.prize_recipient.actor.curse()
			# ba.timer(5.5, self.setup_next_round)
		if prize == 2:
			self.setup_rof()
			ba.screenmessage(run, color=(1.0, 0.2, 0.1))
			self.last_prize = 'ring_of_fire'
		if prize == 3:
			self.last_prize = 'climb'
			self.light = ba.newnode(
				'locator',
				attrs={
					'shape': 'circle',
					'position': (0.0, 3.0, -9.0),
					'color': (1.0, 1.0, 1.0),
					'opacity': 1.0,
					'draw_beauty': True,
					'additive': True
				})
			ba.screenmessage(climb_top, color=(0.5, 0.5, 0.5))
			ba.timer(3.0, ba.Call(self.make_health_box, (0.0, 6.0, -9.0)))
			self.round_timer = ba.Timer(10.0, self.setup_next_round)
		if prize == 4:
			self.last_prize = 'land_mines'
			self.make_health_box((6.0, 5.0, -2.0))
			self.make_land_mines()
			self.prize_recipient.actor.connect_controls_to_player(
				enable_bomb=False)
			self.prize_recipient.actor.node.handlemessage(
				ba.StandMessage(position=(-6.0, 3.0, -2.0)))
			self.round_timer = ba.Timer(7.0, self.setup_next_round)
		if prize == 5:
			# Make it rain bombs
			self.bomb_survivor = self.prize_recipient
			ba.screenmessage(bomb_rain, color=(1.0, 0.5, 0.16))
			# Set positions for the bombs to drop
			for bzz in range(-5,6):
				for azz in range(-5,2):
					# for each position make a bomb drop there
					self.make_bomb(bzz, azz)
			self.give_points_timer = ba.Timer(3.3, self.give_points)
			self.last_prize = 'bombrain'
		if prize == 6:
			self.setup_br()
			self.bomb_survivor = self.prize_recipient
			self.give_points_timer = ba.Timer(7.0, self.give_points)
			self.last_prize = 'bombroad'
		if prize == 7:
			# makes killing a bad guy worth ten points
			self.bad_guy_cost = 2
			ba.screenmessage(lame_guys, color=(1.0, 0.5, 0.16))
			# makes a set of nine positions
			for a in range(-1, 2):
				for b in range(-3, 0):
					# and spawns one in each position
					self._bots.spawn_bot(BrawlerBotLite, pos=(a, 2.5, b))
					# and we give our player boxing gloves and a shield
			self._player.equip_boxing_gloves()
			self._player.equip_shields()
			self.last_prize = 'lameguys'
		if prize == 8:
			ba.playsound(self._jackpot_sound)
			ba.screenmessage(jackpot, color=(1.0, 0.0, 0.0))
			ba.screenmessage(jackpot, color=(0.0, 1.0, 0.0))
			ba.screenmessage(jackpot, color=(0.0, 0.0, 1.0))
			team = self.prize_recipient.team
			# GIVE THEM A WHOPPING 50 POINTS!!!
			team.score += 50
			# and update the scores
			self._update_scoreboard()
			self.last_prize = 'jackpot'
			ba.timer(2.0, self.setup_next_round)

	def setup_next_round(self) -> None:
		if self._slow_motion_deaths:
			ba.getactivity().globalsnode.slow_motion = False
		if self.set:
			return
		if self.light:
			self.light.delete()
		for bomb in self.bombs:
			bomb.handlemessage(ba.DieMessage())
		self.kill_flags()
		self._bots.clear()
		self.reset_flags()
		self.current_player.actor.handlemessage(
			ba.DieMessage(how='game'))
		self.current_player.actor.node.delete()
		c = 0
		self.player_index += 1
		self.player_index %= len(self.queue_line)
		if len(self.queue_line) > 0:
			while self.queue_line[self.player_index].dead:
				if c > len(self.queue_line):
					return
				self.player_index += 1
				self.player_index %= len(self.queue_line)
				c += 1
			self.spawn_player_spaz(
				self.queue_line[self.player_index], (0.0, 3.0, -2.0))
			self.current_player = self.queue_line[self.player_index]
		self.last_prize = 'none'
		self._update_icons()

	def check_bots(self) -> None:
		if not self._bots.have_living_bots():
			self.setup_next_round()

	def make_land_mines(self) -> None:
		self.bombs = []
		for i in range(-11, 7):
			self.bombs.append(Bomb(
				position=(0.0, 6.0, i/2.0),
				bomb_type='land_mine',
				blast_radius=2.0))
			self.bombs[i+10].arm()

	def give_points(self) -> None:
		if self.bomb_survivor is not None and self.bomb_survivor.is_alive():
			self.bomb_survivor.team.score += 20
			self._update_scoreboard()
			self.round_timer = ba.Timer(1.0, self.setup_next_round)

	def make_health_box(self, position: Sequence[float]) -> None:
		if position == (0.0, 3.0, 0.0):
			position = (random.randint(-6, 6), 6, random.randint(-6, 4))
		elif position == (0,0,0):
			position = random.choice(
				((-7, 6, -5), (7, 6, -5), (-7, 6, 1), (7, 6, 1)))
		self.health_box = PowerupBox(
			position=position, poweruptype='health').autoretain()

	# called in prize #5
	def make_bomb(self, xpos: float, zpos: float) -> None:
		# makes a bomb at the given position then auto-retains it aka:
		# makes sure it doesn't disappear because there is no reference to it
		self.bombs.append(Bomb(position=(xpos, 12, zpos)))

	def setup_br(self) -> None:
		self.make_bomb_row(6)
		self.prize_recipient.actor.handlemessage(
			ba.StandMessage(position=(6.0, 3.0, -2.0)))

	def make_bomb_row(self, num: int) -> None:
		if not self.prize_recipient.is_alive():
			return
		if num == 0:
			self.round_timer = ba.Timer(1.0, self.setup_next_round)
			return
		for i in range(-11, 7):
			self.bombs.append(
				Bomb(position=(-3, 3, i/2.0),
					 velocity=(12, 0.0, 0.0),
					 bomb_type='normal',
					 blast_radius=1.2))
		ba.timer(1.0, ba.Call(self.make_bomb_row, num-1))

	def setup_rof(self) -> None:
		self.make_blast_ring(10)
		self.prize_recipient.actor.handlemessage(
			ba.StandMessage(position=(0.0, 3.0, -2.0)))

	def make_blast_ring(self, length: float) -> None:
		if not self.prize_recipient.is_alive():
			return
		if length == 0:
			self.setup_next_round()
			self.prize_recipient.team.score += 50
			self._update_scoreboard()
			return
		for angle in range(0, 360, 45):
			angle += random.randint(0, 45)
			angle %= 360
			x = length * math.cos(math.radians(angle))
			z = length * math.sin(math.radians(angle))
			blast = Blast(position=(x, 2.2, z-2), blast_radius=3.5)
		ba.timer(0.75, ba.Call(self.make_blast_ring, length-1))

	# a method to remake the flags
	def reset_flags(self) -> None:
		# remake the flags
		self._flag = Flag(
			position=(0.0, 3.0, 1.0), touchable=True, color=(0.0, 0.0, 1.0))
		self._flag2 = Flag(
			position=(0.0, 3.0, -5.0), touchable=True, color=(1.0, 0.0, 0.0))
		self._flag3 = Flag(
			position=(3.0, 3.0, -2.0), touchable=True, color=(0.0, 1.0, 0.0))
		self._flag4 = Flag(
			position=(-3.0, 3.0, -2.0), touchable=True, color=(1.0, 1.0, 1.0))
		self._flag5 = Flag(
			position=(1.8, 3.0, 0.2), touchable=True, color=(0.0, 1.0, 1.0))
		self._flag6 = Flag(
			position=(-1.8, 3.0, 0.2), touchable=True, color=(1.0, 0.0, 1.0))
		self._flag7 = Flag(
			position=(1.8, 3.0, -3.8), touchable=True, color=(1.0, 1.0, 0.0))
		self._flag8 = Flag(
			position=(-1.8, 3.0, -3.8), touchable=True, color=(0.0, 0.0, 0.0))

	# a method to kill the flags
	def kill_flags(self) -> None:
		# destroy all the flags by erasing all references to them,
		# indicated by None similar to null
		self._flag.node.delete()
		self._flag2.node.delete()
		self._flag3.node.delete()
		self._flag4.node.delete()
		self._flag5.node.delete() # 132, 210 ,12
		self._flag6.node.delete()
		self._flag7.node.delete()
		self._flag8.node.delete()

	def _check_end_game(self) -> None:
		for player in self.queue_line:
			if not player.dead:
				return
		self.end_game()

	def spawn_player_spaz(
		self,
		player: PlayerType,
		position: Sequence[float] = (0, 0, 0),
		angle: float | None = None,
	) -> PlayerSpaz:
		from ba import _math
		from ba._gameutils import animate
		from ba._coopsession import CoopSession

		angle = None
		name = player.getname()
		color = player.color
		highlight = player.highlight

		light_color = _math.normalized_color(color)
		display_color = ba.safecolor(color, target_intensity=0.75)

		spaz = FlagBearer(color=color,
						  highlight=highlight,
						  character=player.character,
						  player=player)

		player.actor = spaz
		assert spaz.node

		spaz.node.name = name
		spaz.node.name_color = display_color
		spaz.connect_controls_to_player()

		# Move to the stand position and add a flash of light.
		spaz.handlemessage(
			ba.StandMessage(
				position,
				angle if angle is not None else random.uniform(0, 360)))
		ba.playsound(self._spawn_sound, 1, position=spaz.node.position)
		light = ba.newnode('light', attrs={'color': light_color})
		spaz.node.connectattr('position', light, 'position')
		animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
		ba.timer(0.5, light.delete)
		return spaz

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, ba.PlayerDiedMessage):
			# give them a nice farewell
			if ba.time() < 0.5:
				return
			if msg.how == 'game':
				return
			player = msg.getplayer(Player)
			ba.screenmessage(
				diedtxt + str(player.getname()) + diedtxt2, color=player.color)
			player.dead = True
			if player is self.current_player:
				self.round_timer = None
				self.give_points_timer = None
				if not msg.how is ba.DeathType.FALL:
					if self._slow_motion_deaths:
						ba.getactivity().globalsnode.slow_motion = True
					time = 0.5
				else:
					time = 0.01
				# check to see if we can end the game
				self._check_end_game()
				ba.timer(time, self.setup_next_round)
		elif isinstance(msg, FlagPickedUpMessage):
			msg.flag.last_player_to_hold = msg.node.getdelegate(
				FlagBearer, True
			).getplayer(Player, True)
			self._player = msg.node.getdelegate(
				FlagBearer, True
			)
			self.prize_recipient = msg.node.getdelegate(
				FlagBearer, True
			).getplayer(Player, True)
			self.kill_flags()
			self.give_prize(random.randint(1, 8))
			ba.playsound(self._round_sound)
			self.current_player = self.prize_recipient
		elif isinstance(msg, SpazBotDiedMessage):
			# find out which team the last person to hold a flag was on
			team = self.prize_recipient.team
			# give them their points
			team.score += self.bad_guy_cost
			ba.playsound(self._dingsound, 0.5)
			# update the scores
			for team in self.teams:
				self._scoreboard.set_team_value(team, team.score)
			ba.timer(0.3, self.check_bots)
		return None

	def _update_scoreboard(self) -> None:
		for player in self.queue_line:
			if not player.dead:
				if player.team.score > 0:
					ba.playsound(self._dingsound)
				self._scoreboard.set_team_value(player.team, player.team.score)

	def end_game(self) -> None:
		if self.set:
			return
		self.set = True
		results = ba.GameResults()
		for team in self.teams:
			results.set_team_score(team, team.score)
		self.end(results=results)
