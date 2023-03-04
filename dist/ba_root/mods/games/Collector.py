# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

'''
	Gamemode: Collector
	Creator: TheMikirog
	Website: https://bombsquadjoyride.blogspot.com/

	This is a gamemode purely made by me just to spite unchallenged modders
	out there that put out crap to the market.
	We don't want gamemodes that are just the existing ones
	with some novelties! Gamers deserve more!

	In this gamemode you have to kill others in order to get their Capsules.
	Capsules can be collected and staked in your inventory,
	how many as you please.
	After you kill an enemy that carries some of them,
	they drop a respective amount of Capsules they carried + two more.
	Your task is to collect these Capsules,
	get to the flag and score them KOTH style.
	You can't score if you don't have any Capsules with you.
	The first player or team to get to the required ammount wins.
	This is a gamemode all about trying to stay alive
	and picking your battles in order to win.
	A rare skill in BombSquad, where everyone is overly aggressive.
'''

from __future__ import annotations

import weakref
from enum import Enum
from typing import TYPE_CHECKING

import ba
import random
from bastd.actor.flag import Flag
from bastd.actor.popuptext import PopupText
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
	from typing import Any, Sequence


lang = ba.app.lang.language
if lang == 'Spanish':
	name = 'Coleccionista'
	description = ('Elimina a tus oponentes para robar sus cápsulas.\n'
				  '¡Recolecta y anota en el punto de depósito!')
	description_ingame = 'Obtén ${ARG1} cápsulas de tus enemigos.'
	description_short = 'colecciona ${ARG1} cápsulas'
	tips = [(
		'¡Si tu oponente cae fuera del mapa, sus cápsulas desapareceran!\n'
		'No intestes matar a tus enemigos arrojándolos al vacio.'),
		'No te apresures. ¡Puedes perder tus cápsulas rápidamente!',
		('¡No dejes que el jugador con más cápsulas anote!\n'
		'¡Intenta atraparlo si puedes!'),
		('¡Las Capsulas de la Suerte te dan 4 cápsulas en lugar de 2'
		'y tienen un 8% de probabilidad de aparecer después de matar'),
		('¡No te quedes en un solo lugar! Muevete más rapido que tu enemigo, '
		'¡con suerte conseguirás algunas cápsulas!'),
	]
	capsules_to_win = 'Cápsulas para Ganar'
	capsules_death = 'Cápsulas al Morir'
	lucky_capsules = 'Cápsulas de la Suerte'
	bonus = '¡BONUS!'
	full_capacity = '¡Capacidad Completa!'
else:
	name = 'Collector'
	description = ('Kill your opponents to steal their Capsules.\n'
				  'Collect them and score at the Deposit point!')
	description_ingame = 'Score ${ARG1} capsules from your enemies.'
	description_short = 'collect ${ARG1} capsules'
	tips = [(
		'Making you opponent fall down the pit makes his Capsules wasted!\n'
		'Try not to kill enemies by throwing them off the cliff.'),
		'Don\'t be too reckless. You can lose your loot quite quickly!',
		('Don\'t let the leading player score his Capsules '
		'at the Deposit Point!\nTry to catch him if you can!'),
		('Lucky Capsules give 4 to your inventory and they have 8% chance '
		'of spawning after kill!'),
		('Don\'t camp in one place! Make your move first, '
		'so hopefully you get some dough!'),
	]
	capsules_to_win = 'Capsules to Win'
	capsules_death = 'Capsules on Death'
	lucky_capsules = 'Allow Lucky Capsules'
	bonus = 'BONUS!'
	full_capacity = 'Full Capacity!'


class FlagState(Enum):
	"""States our single flag can be in."""

	NEW = 0
	UNCONTESTED = 1
	CONTESTED = 2
	HELD = 3


class Player(ba.Player['Team']):
	"""Our player type for this game."""

	def __init__(self) -> None:
		self.time_at_flag = 0
		self.capsules = 0
		self.light = None


class Team(ba.Team[Player]):
	"""Our team type for this game."""

	def __init__(self) -> None:
		self.score = 0


# ba_meta export game
class CollectorGame(ba.TeamGameActivity[Player, Team]):

	name = name
	description = description
	tips = tips

	# Print messages when players die since it matters here.
	announce_player_deaths = True

	@classmethod
	def get_available_settings(
		cls, sessiontype: type[ba.Session]
	) -> list[ba.Setting]:
		settings = [
			ba.IntSetting(
				capsules_to_win,
				min_value=1,
				default=10,
				increment=1,
			),
			ba.IntSetting(
				capsules_death,
				min_value=1,
				max_value=10,
				default=2,
				increment=1,
			),
			ba.IntChoiceSetting(
				'Time Limit',
				choices=[
					('None', 0),
					('1 Minute', 60),
					('2 Minutes', 120),
					('5 Minutes', 300),
					('10 Minutes', 600),
					('20 Minutes', 1200),
				],
				default=0,
			),
			ba.FloatChoiceSetting(
				'Respawn Times',
				choices=[
					('Shorter', 0.25),
					('Short', 0.5),
					('Normal', 1.0),
					('Long', 2.0),
					('Longer', 4.0),
				],
				default=1.0,
			),
			ba.BoolSetting(lucky_capsules, default=True),
			ba.BoolSetting('Epic Mode', default=False),
		]
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
		return issubclass(sessiontype, ba.DualTeamSession) or issubclass(
			sessiontype, ba.FreeForAllSession
		)

	@classmethod
	def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
		return ba.getmaps('keep_away')

	def __init__(self, settings: dict):
		super().__init__(settings)
		shared = SharedObjects.get()
		self._scoreboard = Scoreboard()
		self._score_to_win: int | None = None
		self._swipsound = ba.getsound('swip')
		self._lucky_sound = ba.getsound('ding')

		self._flag_pos: Sequence[float] | None = None
		self._flag_state: FlagState | None = None
		self._flag: Flag | None = None
		self._flag_light: ba.Node | None = None
		self._scoring_team: weakref.ref[Team] | None = None
		self._time_limit = float(settings['Time Limit'])
		self._epic_mode = bool(settings['Epic Mode'])

		self._capsules_to_win = int(settings[capsules_to_win])
		self._capsules_death = int(settings[capsules_death])
		self._lucky_capsules = bool(settings[lucky_capsules])
		self._capsules: list[Any] = []

		self._capsule_model = ba.getmodel('bomb')
		self._capsule_tex = ba.gettexture('bombColor')
		self._capsule_lucky_tex = ba.gettexture('bombStickyColor')
		self._collect_sound = ba.getsound('powerup01')
		self._lucky_collect_sound = ba.getsound('cashRegister2')

		self._capsule_material = ba.Material()
		self._capsule_material.add_actions(
			conditions=('they_have_material', shared.player_material),
			actions=('call', 'at_connect', self._on_capsule_player_collide),
		)

		self._flag_region_material = ba.Material()
		self._flag_region_material.add_actions(
			conditions=('they_have_material', shared.player_material),
			actions=(
				('modify_part_collision', 'collide', True),
				('modify_part_collision', 'physical', False),
				(
					'call',
					'at_connect',
					ba.Call(self._handle_player_flag_region_collide, True),
				),
				(
					'call',
					'at_disconnect',
					ba.Call(self._handle_player_flag_region_collide, False),
				),
			),
		)

		# Base class overrides.
		self.slow_motion = self._epic_mode
		self.default_music = (
			ba.MusicType.EPIC if self._epic_mode else ba.MusicType.SCARY
		)

	def get_instance_description(self) -> str | Sequence:
		return description_ingame, self._score_to_win

	def get_instance_description_short(self) -> str | Sequence:
		return description_short, self._score_to_win

	def create_team(self, sessionteam: ba.SessionTeam) -> Team:
		return Team()

	def on_team_join(self, team: Team) -> None:
		self._update_scoreboard()

	def on_begin(self) -> None:
		super().on_begin()
		shared = SharedObjects.get()
		self.setup_standard_time_limit(self._time_limit)
		self.setup_standard_powerup_drops()

		# Base kills needed to win on the size of the largest team.
		self._score_to_win = self._capsules_to_win * max(
			1, max(len(t.players) for t in self.teams)
		)
		self._update_scoreboard()

		if isinstance(self.session, ba.FreeForAllSession):
			self._flag_pos = self.map.get_flag_position(random.randint(0, 1))
		else:
			self._flag_pos = self.map.get_flag_position(None)

		ba.timer(1.0, self._tick, repeat=True)
		self._flag_state = FlagState.NEW
		Flag.project_stand(self._flag_pos)
		self._flag = Flag(
			position=self._flag_pos, touchable=False, color=(1, 1, 1)
		)
		self._flag_light = ba.newnode(
			'light',
			attrs={
				'position': self._flag_pos,
				'intensity': 0.2,
				'height_attenuated': False,
				'radius': 0.4,
				'color': (0.2, 0.2, 0.2),
			},
		)
		# Flag region.
		flagmats = [self._flag_region_material, shared.region_material]
		ba.newnode(
			'region',
			attrs={
				'position': self._flag_pos,
				'scale': (1.8, 1.8, 1.8),
				'type': 'sphere',
				'materials': flagmats,
			},
		)
		self._update_flag_state()

	def _tick(self) -> None:
		self._update_flag_state()

		if self._scoring_team is None:
			scoring_team = None
		else:
			scoring_team = self._scoring_team()

		if not scoring_team:
			return

		if isinstance(self.session, ba.FreeForAllSession):
			players = self.players
		else:
			players = scoring_team.players

		for player in players:
			if player.time_at_flag > 0:
				self.stats.player_scored(
					player, 3, screenmessage=False, display=False
				)
				if player.capsules > 0:
					if self._flag_state != FlagState.HELD:
						return
					if scoring_team.score >= self._score_to_win:
						return

					player.capsules -= 1
					scoring_team.score += 1
					self._handle_capsule_storage((
						self._flag_pos[0],
						self._flag_pos[1]+1,
						self._flag_pos[2]
					), player)
					ba.playsound(
						self._collect_sound,
						0.8,
						position=self._flag_pos)

					self._update_scoreboard()
					if player.capsules > 0:
						assert self._flag is not None
						self._flag.set_score_text(
							str(self._score_to_win - scoring_team.score))

					# winner
					if scoring_team.score >= self._score_to_win:
						self.end_game()

	def end_game(self) -> None:
		results = ba.GameResults()
		for team in self.teams:
			results.set_team_score(team, team.score)
		self.end(results=results, announce_delay=0)

	def _update_flag_state(self) -> None:
		holding_teams = set(
			player.team for player in self.players if player.time_at_flag
		)
		prev_state = self._flag_state
		assert self._flag_light
		assert self._flag is not None
		assert self._flag.node
		if len(holding_teams) > 1:
			self._flag_state = FlagState.CONTESTED
			self._scoring_team = None
			self._flag_light.color = (0.6, 0.6, 0.1)
			self._flag.node.color = (1.0, 1.0, 0.4)
		elif len(holding_teams) == 1:
			holding_team = list(holding_teams)[0]
			self._flag_state = FlagState.HELD
			self._scoring_team = weakref.ref(holding_team)
			self._flag_light.color = ba.normalized_color(holding_team.color)
			self._flag.node.color = holding_team.color
		else:
			self._flag_state = FlagState.UNCONTESTED
			self._scoring_team = None
			self._flag_light.color = (0.2, 0.2, 0.2)
			self._flag.node.color = (1, 1, 1)
		if self._flag_state != prev_state:
			ba.playsound(self._swipsound)

	def _handle_player_flag_region_collide(self, colliding: bool) -> None:
		try:
			spaz = ba.getcollision().opposingnode.getdelegate(PlayerSpaz, True)
		except ba.NotFoundError:
			return

		if not spaz.is_alive():
			return

		player = spaz.getplayer(Player, True)

		# Different parts of us can collide so a single value isn't enough
		# also don't count it if we're dead (flying heads shouldn't be able to
		# win the game :-)
		if colliding and player.is_alive():
			player.time_at_flag += 1
		else:
			player.time_at_flag = max(0, player.time_at_flag - 1)

		self._update_flag_state()

	def _update_scoreboard(self) -> None:
		for team in self.teams:
			self._scoreboard.set_team_value(
				team, team.score, self._score_to_win
			)

	def _drop_capsule(self, player: Player) -> None:
		pt = player.node.position

		# Throw out capsules that the victim has + 2 more to keep the game running
		for i in range(player.capsules + self._capsules_death):
			# How far from each other these capsules should spawn
			w = 0.6
			# How much these capsules should fly after spawning
			s = 0.005 - (player.capsules * 0.01)
			self._capsules.append(
				Capsule(
					position=(pt[0] + random.uniform(-w, w),
							  pt[1] + 0.75 + random.uniform(-w, w),
							  pt[2]),
					velocity=(random.uniform(-s, s),
							  random.uniform(-s, s),
							  random.uniform(-s, s)),
					lucky=False))
		if random.randint(1, 12) == 1 and self._lucky_capsules:
			# How far from each other these capsules should spawn
			w = 0.6
			# How much these capsules should fly after spawning
			s = 0.005
			self._capsules.append(
				Capsule(
					position=(pt[0] + random.uniform(-w, w),
							  pt[1] + 0.75 + random.uniform(-w, w),
							  pt[2]),
					velocity=(random.uniform(-s, s),
							  random.uniform(-s, s),
							  random.uniform(-s, s)),
					lucky=True))

	def _on_capsule_player_collide(self) -> None:
		if self.has_ended():
			return
		collision = ba.getcollision()

		# Be defensive here; we could be hitting the corpse of a player
		# who just left/etc.
		try:
			capsule = collision.sourcenode.getdelegate(Capsule, True)
			player = collision.opposingnode.getdelegate(
				PlayerSpaz, True
			).getplayer(Player, True)
		except ba.NotFoundError:
			return

		if not player.is_alive():
			return

		if capsule.node.color_texture == self._capsule_lucky_tex:
			player.capsules += 4
			PopupText(
				bonus,
				color=(1, 1, 0),
				scale=1.5,
				position=capsule.node.position
			).autoretain()
			ba.playsound(
				self._lucky_collect_sound,
				1.0,
				position=capsule.node.position)
			ba.emitfx(
				position=capsule.node.position,
				velocity=(0, 0, 0),
				count=int(6.4+random.random()*24),
				scale=1.2,
				spread=2.0,
				chunk_type='spark');
			ba.emitfx(
				position=capsule.node.position,
				velocity=(0, 0, 0),
				count=int(4.0+random.random()*6),
				emit_type='tendrils');
		else:
			player.capsules += 1
			ba.playsound(
				self._collect_sound,
				0.6,
				position=capsule.node.position)
		# create a flash
		light = ba.newnode(
			'light',
			attrs={
				'position': capsule.node.position,
				'height_attenuated': False,
				'radius': 0.1,
				'color': (1, 1, 0)})

		# Create a short text informing about your inventory
		self._handle_capsule_storage(player.position, player)

		ba.animate(light, 'intensity', {
			0: 0,
			0.1: 0.5,
			0.2: 0
		}, loop=False)
		ba.timer(0.2, light.delete)
		capsule.handlemessage(ba.DieMessage())

	def _update_player_light(self, player: Player, capsules: int) -> None:
		if player.light:
			intensity = 0.04 * capsules
			ba.animate(player.light, 'intensity', {
				0.0: player.light.intensity,
				0.1: intensity
			})
			def newintensity():
				player.light.intensity = intensity
			ba.timer(0.1, newintensity)
		else:
			player.light = ba.newnode(
				'light',
				attrs={
					'height_attenuated': False,
					'radius': 0.2,
					'intensity': 0.0,
					'color': (0.2, 1, 0.2)
				})
			player.node.connectattr('position', player.light, 'position')

	def _handle_capsule_storage(self, pos: float, player: Player) -> None:
		capsules = player.capsules
		text = str(capsules)
		scale = 1.75 + (0.02 * capsules)
		if capsules > 10:
			player.capsules = 10
			text = full_capacity
			color = (1, 0.85, 0)
		elif capsules > 7:
			color = (1, 0, 0)
			scale = 2.4
		elif capsules > 5:
			color = (1, 0.4, 0.4)
			scale = 2.1
		elif capsules > 3:
			color = (1, 1, 0.4)
			scale = 2.0
		else:
			color = (1, 1, 1)
			scale = 1.9
		PopupText(
			text,
			color=color,
			scale=scale,
			position=(pos[0], pos[1]-1, pos[2])
		).autoretain()
		self._update_player_light(player, capsules)

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, ba.PlayerDiedMessage):
			super().handlemessage(msg)  # Augment default.
			# No longer can count as time_at_flag once dead.
			player = msg.getplayer(Player)
			player.time_at_flag = 0
			self._update_flag_state()
			self._drop_capsule(player)
			player.capsules = 0
			self._update_player_light(player, 0)
			self.respawn_player(player)
		else:
			return super().handlemessage(msg)


class Capsule(ba.Actor):

	def __init__(self,
				 position: Sequence[float] = (0.0, 1.0, 0.0),
				 velocity: Sequence[float] = (0.0, 0.5, 0.0),
				 lucky: bool = False):
		super().__init__()
		shared = SharedObjects.get()
		activity = self.getactivity()

		# spawn just above the provided point
		self._spawn_pos = (position[0], position[1], position[2])

		if lucky:
			ba.playsound(activity._lucky_sound, 1.0, self._spawn_pos)

		self.node = ba.newnode(
			'prop',
			attrs={
				'model': activity._capsule_model,
				'color_texture': activity._capsule_lucky_tex if lucky else (
					activity._capsule_tex),
				'body': 'crate' if lucky else 'capsule',
				'reflection': 'powerup' if lucky else 'soft',
				'body_scale': 0.65 if lucky else 0.3,
				'density':6.0 if lucky else 4.0,
				'reflection_scale': [0.15],
				'shadow_size': 0.65 if lucky else 0.6,
				'position': self._spawn_pos,
				'velocity': velocity,
				'materials': [
					shared.object_material, activity._capsule_material]
			},
			delegate=self)
		ba.animate(self.node, 'model_scale', {
			0.0: 0.0,
			0.1: 0.9 if lucky else 0.6,
			0.16: 0.8 if lucky else 0.5
		})
		self._light_capsule = ba.newnode(
			'light',
			attrs={
				'position': self._spawn_pos,
				'height_attenuated': False,
				'radius': 0.5 if lucky else 0.1,
				'color': (0.2, 0.2, 0) if lucky else (0.2, 1, 0.2)
			})
		self.node.connectattr('position', self._light_capsule, 'position')

	def handlemessage(self, msg: Any):
		if isinstance(msg, ba.DieMessage):
			self.node.delete()
			ba.animate(self._light_capsule, 'intensity', {
				0: 1.0,
				0.05: 0.0
			}, loop=False)
			ba.timer(0.05, self._light_capsule.delete)
		elif isinstance(msg, ba.OutOfBoundsMessage):
			self.handlemessage(ba.DieMessage())
		elif isinstance(msg, ba.HitMessage):
			self.node.handlemessage(
				'impulse',
				msg.pos[0], msg.pos[1], msg.pos[2],
				msg.velocity[0]/8, msg.velocity[1]/8, msg.velocity[2]/8,
				1.0*msg.magnitude, 1.0*msg.velocity_magnitude, msg.radius, 0,
				msg.force_direction[0], msg.force_direction[1],
				msg.force_direction[2])
		else:
			return super().handlemessage(msg)
