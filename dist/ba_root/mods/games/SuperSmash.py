"""DeathMatch game and support classes."""
# Created by: byANG3L #
# YT: https://www.youtube.com/c/JoseANG3LYT #

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import random
from ba import _math
from bastd.actor.spazfactory import SpazFactory
from bastd.actor.scoreboard import Scoreboard
from bastd.game import elimination
from bastd.game.elimination import Icon, Player, Team
from bastd.actor.bomb import Bomb, Blast
from bastd.actor.playerspaz import PlayerSpaz

if TYPE_CHECKING:
	from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional

class Icon(Icon):
	def update_for_lives(self) -> None:
		"""Update for the target player's current lives."""
		if self._player:
			lives = self._player.lives
		else:
			lives = 0
		if self._show_lives:
			if lives > 1:
				self._lives_text.text = 'x' + str(lives - 1)
			else:
				self._lives_text.text = ''
		if lives == 0:
			self._name_text.opacity = 0.2
			assert self.node
			self.node.color = (0.7, 0.3, 0.3)
			self.node.opacity = 0.2

class PowBox(Bomb):

	def __init__(self,
				 position: Sequence[float] = (0.0, 1.0, 0.0),
				 velocity: Sequence[float] = (0.0, 0.0, 0.0)) -> None:

		Bomb.__init__(self,
					  position,
					  velocity,
					  bomb_type='tnt',
					  blast_radius=2.5,
					  source_player=None,
					  owner=None)
		self.set_pow_text()

	def set_pow_text(self) -> None:
		m = ba.newnode('math',
					   owner=self.node,
					   attrs={'input1': (0, 0.7, 0),
							  'operation': 'add'})
		self.node.connectattr('position', m, 'input2')

		self._pow_text = ba.newnode('text',
									owner=self.node,
									attrs={'text':'POW!',
										   'in_world': True,
										   'shadow': 1.0,
										   'flatness': 1.0,
										   'color': (1, 1, 0.4),
										   'scale':0.0,
										   'h_align':'center'})
		m.connectattr('output', self._pow_text, 'position')
		ba.animate(self._pow_text, 'scale', {0: 0.0, 1.0: 0.01})

	def pow(self) -> None:
		self.explode()

	def handlemessage(self, m: Any) -> Any:
		if isinstance(m, ba.PickedUpMessage):
			self._heldBy = m.node
		elif isinstance(m, ba.DroppedMessage):
			ba.timer(0.6, self.pow)
		Bomb.handlemessage(self, m)

class PlayerSpaz_Smash(PlayerSpaz):
	multiplyer = 1
	is_dead = False

	def oob_effect(self) -> None:
		if self.is_dead:
			return
		self.is_dead = True
		if self.multiplyer > 1.25:
			blast_type = 'tnt'
			radius = min(self.multiplyer * 5, 20)
		else:
			# penalty for killing people with low multiplyer
			blast_type = 'ice'
			radius = 7.5
		Blast(position=self.node.position,
			  blast_radius=radius,
			  blast_type=blast_type).autoretain()

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, ba.HitMessage):
			if not self.node:
				return None
			if self.node.invincible:
				ba.playsound(SpazFactory.get().block_sound,
							 1.0,
							 position=self.node.position)
				return True

			# If we were recently hit, don't count this as another.
			# (so punch flurries and bomb pileups essentially count as 1 hit)
			local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
			assert isinstance(local_time, int)
			if (self._last_hit_time is None
					or local_time - self._last_hit_time > 1000):
				self._num_times_hit += 1
				self._last_hit_time = local_time

			mag = msg.magnitude * self.impact_scale
			velocity_mag = msg.velocity_magnitude * self.impact_scale
			damage_scale = 0.22

			# If they've got a shield, deliver it to that instead.
			if self.shield:
				if msg.flat_damage:
					damage = msg.flat_damage * self.impact_scale
				else:
					# Hit our spaz with an impulse but tell it to only return
					# theoretical damage; not apply the impulse.
					assert msg.force_direction is not None
					self.node.handlemessage(
						'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
						msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
						velocity_mag, msg.radius, 1, msg.force_direction[0],
						msg.force_direction[1], msg.force_direction[2])
					damage = damage_scale * self.node.damage

				assert self.shield_hitpoints is not None
				self.shield_hitpoints -= int(damage)
				self.shield.hurt = (
					1.0 -
					float(self.shield_hitpoints) / self.shield_hitpoints_max)

				# Its a cleaner event if a hit just kills the shield
				# without damaging the player.
				# However, massive damage events should still be able to
				# damage the player. This hopefully gives us a happy medium.
				max_spillover = SpazFactory.get().max_shield_spillover_damage
				if self.shield_hitpoints <= 0:

					# FIXME: Transition out perhaps?
					self.shield.delete()
					self.shield = None
					ba.playsound(SpazFactory.get().shield_down_sound,
								 1.0,
								 position=self.node.position)

					# Emit some cool looking sparks when the shield dies.
					npos = self.node.position
					ba.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
							  velocity=self.node.velocity,
							  count=random.randrange(20, 30),
							  scale=1.0,
							  spread=0.6,
							  chunk_type='spark')

				else:
					ba.playsound(SpazFactory.get().shield_hit_sound,
								 0.5,
								 position=self.node.position)

				# Emit some cool looking sparks on shield hit.
				assert msg.force_direction is not None
				ba.emitfx(position=msg.pos,
						  velocity=(msg.force_direction[0] * 1.0,
									msg.force_direction[1] * 1.0,
									msg.force_direction[2] * 1.0),
						  count=min(30, 5 + int(damage * 0.005)),
						  scale=0.5,
						  spread=0.3,
						  chunk_type='spark')

				# If they passed our spillover threshold,
				# pass damage along to spaz.
				if self.shield_hitpoints <= -max_spillover:
					leftover_damage = -max_spillover - self.shield_hitpoints
					shield_leftover_ratio = leftover_damage / damage

					# Scale down the magnitudes applied to spaz accordingly.
					mag *= shield_leftover_ratio
					velocity_mag *= shield_leftover_ratio
				else:
					return True  # Good job shield!
			else:
				shield_leftover_ratio = 1.0

			if msg.flat_damage:
				damage = int(msg.flat_damage * self.impact_scale *
							 shield_leftover_ratio)
			else:
				# Hit it with an impulse and get the resulting damage.
				assert msg.force_direction is not None
				self.node.handlemessage(
					'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
					msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
					velocity_mag, msg.radius, 0, msg.force_direction[0],
					msg.force_direction[1], msg.force_direction[2])

				damage = int(damage_scale * self.node.damage)
			self.node.handlemessage('hurt_sound')

			# Play punch impact sound based on damage if it was a punch.
			if msg.hit_type == 'punch':
				self.on_punched(damage)

				# If damage was significant, lets show it.
				# if damage > 350:
				# 	assert msg.force_direction is not None
				# 	ba.show_damage_count('-' + str(int(damage / 10)) + '%',
				# 	 					 msg.pos, msg.force_direction)

				# Let's always add in a super-punch sound with boxing
				# gloves just to differentiate them.
				if msg.hit_subtype == 'super_punch':
					ba.playsound(SpazFactory.get().punch_sound_stronger,
								 1.0,
								 position=self.node.position)
				if damage > 500:
					sounds = SpazFactory.get().punch_sound_strong
					sound = sounds[random.randrange(len(sounds))]
				else:
					sound = SpazFactory.get().punch_sound
				ba.playsound(sound, 1.0, position=self.node.position)

				# Throw up some chunks.
				assert msg.force_direction is not None
				ba.emitfx(position=msg.pos,
						  velocity=(msg.force_direction[0] * 0.5,
									msg.force_direction[1] * 0.5,
									msg.force_direction[2] * 0.5),
						  count=min(10, 1 + int(damage * 0.0025)),
						  scale=0.3,
						  spread=0.03)

				ba.emitfx(position=msg.pos,
						  chunk_type='sweat',
						  velocity=(msg.force_direction[0] * 1.3,
									msg.force_direction[1] * 1.3 + 5.0,
									msg.force_direction[2] * 1.3),
						  count=min(30, 1 + int(damage * 0.04)),
						  scale=0.9,
						  spread=0.28)

				# Momentary flash.
				hurtiness = damage * 0.003
				punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
							msg.pos[1] + msg.force_direction[1] * 0.02,
							msg.pos[2] + msg.force_direction[2] * 0.02)
				flash_color = (1.0, 0.8, 0.4)
				light = ba.newnode(
					'light',
					attrs={
						'position': punchpos,
						'radius': 0.12 + hurtiness * 0.12,
						'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
						'height_attenuated': False,
						'color': flash_color
					})
				ba.timer(0.06, light.delete)

				flash = ba.newnode('flash',
									attrs={
										'position': punchpos,
										'size': 0.17 + 0.17 * hurtiness,
										'color': flash_color
									})
				ba.timer(0.06, flash.delete)

			if msg.hit_type == 'impact':
				assert msg.force_direction is not None
				ba.emitfx(position=msg.pos,
						  velocity=(msg.force_direction[0] * 2.0,
									msg.force_direction[1] * 2.0,
									msg.force_direction[2] * 2.0),
						  count=min(10, 1 + int(damage * 0.01)),
						  scale=0.4,
						  spread=0.1)
			if self.hitpoints > 0:

				# It's kinda crappy to die from impacts, so lets reduce
				# impact damage by a reasonable amount *if* it'll keep us alive
				if msg.hit_type == 'impact' and damage > self.hitpoints:
					# Drop damage to whatever puts us at 10 hit points,
					# or 200 less than it used to be whichever is greater
					# (so it *can* still kill us if its high enough)
					newdamage = max(damage - 200, self.hitpoints - 10)
					damage = newdamage
				self.node.handlemessage('flash')

				# If we're holding something, drop it.
				if damage > 0.0 and self.node.hold_node:
					self.node.hold_node = None
				# self.hitpoints -= damage
				self.multiplyer += min(damage / 2000, 0.15)
				if damage/2000 > 0.05:
					self.set_score_text(str(int((self.multiplyer-1)*100))+'%')
				# self.node.hurt = 1.0 - float(
				# 	self.hitpoints) / self.hitpoints_max
				self.node.hurt = 0.0

				# If we're cursed, *any* damage blows us up.
				if self._cursed and damage > 0:
					ba.timer(
						0.05,
						ba.WeakCall(self.curse_explode,
									msg.get_source_player(ba.Player)))

				# If we're frozen, shatter.. otherwise die if we hit zero
				# if self.frozen and (damage > 200 or self.hitpoints <= 0):
				# 	self.shatter()
				# elif self.hitpoints <= 0:
				# 	self.node.handlemessage(
				# 		ba.DieMessage(how=ba.DeathType.IMPACT))

			# If we're dead, take a look at the smoothed damage value
			# (which gives us a smoothed average of recent damage) and shatter
			# us if its grown high enough.
			# if self.hitpoints <= 0:
			# 	damage_avg = self.node.damage_smoothed * damage_scale
			# 	if damage_avg > 1000:
			# 		self.shatter()

		elif isinstance(msg, ba.DieMessage):
			self.oob_effect()
			super().handlemessage(msg)
		elif isinstance(msg, ba.PowerupMessage):
			if msg.poweruptype == 'health':
				if self.multiplyer > 2:
					self.multiplyer *= 0.5
				else:
					self.multiplyer *= 0.75
				self.multiplyer = max(1, self.multiplyer)
				self.set_score_text(str(int((self.multiplyer-1)*100))+"%")
			super().handlemessage(msg)
		else:
			super().handlemessage(msg)

class Player(ba.Player['Team']):
	"""Our player type for this game."""

	def __init__(self) -> None:
		self.lives = 0
		self.icons: List[Icon] = []


class Team(ba.Team[Player]):
	"""Our team type for this game."""

	def __init__(self) -> None:
		self.survival_seconds: Optional[int] = None
		self.spawn_order: List[Player] = []

# ba_meta export game
class SuperSmash(ba.TeamGameActivity[Player, Team]):

	name = 'Super Smash'
	description = 'Knock everyone off the map.'
	scoreconfig = ba.ScoreConfig(label='Survived',
								 scoretype=ba.ScoreType.SECONDS,
								 none_is_winner=True)

	# Print messages when players die since it matters here.
	announce_player_deaths = True

	@classmethod
	def get_available_settings(
			cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
		settings = [
			ba.IntSetting(
				'Lives (0 = Unlimited)',
				min_value=0,
				default=3,
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
			ba.BoolSetting('Epic Mode', default=False),
		]
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
		return (issubclass(sessiontype, ba.DualTeamSession)
				or issubclass(sessiontype, ba.FreeForAllSession))

	@classmethod
	def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
		maps = ba.getmaps('melee')
		for m in ['Lake Frigid', 'Hockey Stadium', 'Football Stadium']:
			# remove maps without bounds
			maps.remove(m)
		return maps

	def __init__(self, settings: dict):
		super().__init__(settings)
		self.lives = int(settings['Lives (0 = Unlimited)'])
		self.time_limit_only = (self.lives == 0)
		if self.time_limit_only:
			settings['Time Limit'] = max(60, settings['Time Limit'])

		self._epic_mode = bool(settings['Epic Mode'])
		self._time_limit = float(settings['Time Limit'])

		self._start_time: Optional[float] = 1.0

		# Base class overrides.
		self.slow_motion = self._epic_mode
		self.default_music = (ba.MusicType.EPIC if self._epic_mode else
							  ba.MusicType.SURVIVAL)

	def get_instance_description(self) -> Union[str, Sequence]:
		return 'Knock everyone off the map.'

	def get_instance_description_short(self) -> Union[str, Sequence]:
		return 'Knock off the map.'

	def on_begin(self) -> None:
		super().on_begin()
		self._start_time = ba.time()
		self.setup_standard_time_limit(self._time_limit)
		self.setup_standard_powerup_drops(enable_tnt=False)
		self._pow = None
		self._tnt_drop_timer = ba.timer(1.0 * 0.30,
										ba.WeakCall(self._drop_pow_box),
										repeat=True)
		self._update_icons()
		if len(self._get_living_teams()) < 2:
			self._round_end_timer = ba.Timer(0.5, self.end_game)
		
	def _get_living_teams(self) -> List[Team]:
		return [
			team for team in self.teams
			if len(team.players) > 0 and any(player.lives > 0
							for player in team.players)
		]		

	def _drop_pow_box(self) -> None:
		if self._pow is not None and self._pow:
			return
		if len(self.map.tnt_points) == 0:
			return
		pos = random.choice(self.map.tnt_points)
		pos = (pos[0], pos[1] + 1, pos[2])
		self._pow = PowBox(position=pos, velocity=(0.0, 1.0, 0.0))

	def on_player_join(self, player: Player) -> None:

		if self.has_begun():
			if (all(teammate.lives == 0 for teammate in player.team.players)
					and player.team.survival_seconds is None):
				player.team.survival_seconds = 0
			ba.screenmessage(
				ba.Lstr(resource='playerDelayedJoinText',
						subs=[('${PLAYER}', player.getname(full=True))]),
				color=(0, 1, 0),
			)
			return

		player.lives = self.lives
		# create our icon and spawn
		player.icons = [Icon(player,
							position=(0.0, 50),
							scale=0.8)]
		if player.lives > 0 or self.time_limit_only:
			self.spawn_player(player)

		# dont waste time doing this until begin
		if self.has_begun():
			self._update_icons()

	def on_player_leave(self, player: Player) -> None:
		super().on_player_leave(player)
		player.icons = None

		# update icons in a moment since our team
		# will be gone from the list then
		ba.timer(0.0, self._update_icons)

		if len(self._get_living_teams()) < 2:
			self._round_end_timer = ba.Timer(0.5, self.end_game)

	def _update_icons(self) -> None:
		# pylint: disable=too-many-branches

		# In free-for-all mode, everyone is just lined up along the bottom.
		if isinstance(self.session, ba.FreeForAllSession):
			count = len(self.teams)
			x_offs = 85
			xval = x_offs * (count - 1) * -0.5
			for team in self.teams:
				if len(team.players) > 1:
					print('WTF have', len(team.players), 'players in ffa team')
				elif len(team.players) == 1:
					player = team.players[0]
					if len(player.icons) != 1:
						print(
							'WTF have',
							len(player.icons),
							'icons in non-solo elim')
					for icon in player.icons:
						icon.set_position_and_scale((xval, 30), 0.7)
						icon.update_for_lives()
					xval += x_offs

		# In teams mode we split up teams.
		else:		
			for team in self.teams:
				if team.id == 0:
					xval = -50
					x_offs = -85
				else:
					xval = 50
					x_offs = 85
				for player in team.players:
					if len(player.icons) != 1:
						print(
							'WTF have',
							len(player.icons),
							'icons in non-solo elim')
					for icon in player.icons:
						icon.set_position_and_scale((xval, 30), 0.7)
						icon.update_for_lives()
					xval += x_offs

	# overriding the default character spawning..
	def spawn_player(self, player: Player) -> ba.Actor:
		if isinstance(self.session, ba.DualTeamSession):
			position = self.map.get_start_position(player.team.id)
		else:
			# otherwise do free-for-all spawn locations
			position = self.map.get_ffa_start_position(self.players)
		angle = None

		name = player.getname()
		light_color = _math.normalized_color(player.color)
		display_color = _ba.safecolor(player.color, target_intensity=0.75)

		spaz = PlayerSpaz_Smash(color=player.color,
								highlight=player.highlight,
								character=player.character,
								player=player)

		player.actor = spaz
		assert spaz.node

		# If this is co-op and we're on Courtyard or Runaround, add the
		# material that allows us to collide with the player-walls.
		# FIXME: Need to generalize this.
		if isinstance(self.session, ba.CoopSession) and self.map.getname() in [
				'Courtyard', 'Tower D'
		]:
			mat = self.map.preloaddata['collide_with_wall_material']
			assert isinstance(spaz.node.materials, tuple)
			assert isinstance(spaz.node.roller_materials, tuple)
			spaz.node.materials += (mat, )
			spaz.node.roller_materials += (mat, )

		spaz.node.name = name
		spaz.node.name_color = display_color
		spaz.connect_controls_to_player()
		spaz.equip_boxing_gloves()
        
		# Move to the stand position and add a flash of light.
		spaz.handlemessage(
			ba.StandMessage(
				position,
				angle if angle is not None else random.uniform(0, 360)))
		_ba.playsound(self._spawn_sound, 1, position=spaz.node.position)
		light = _ba.newnode('light', attrs={'color': light_color})
		spaz.node.connectattr('position', light, 'position')
		ba.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
		_ba.timer(0.5, light.delete)

		# If we have any icons, update their state.
		for icon in player.icons:
			icon.handle_player_spawned()

		return spaz

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, ba.PlayerDiedMessage):

			# Augment standard behavior.
			super().handlemessage(msg)

			player = msg.getplayer(Player)

			player.lives -= 1

			# if we have any icons, update their state
			for icon in player.icons:
				icon.handle_player_died()

			# play big death sound on our last death
			# or for every one in solo mode
			if player.lives == 0:
				ba.playsound(SpazFactory.get().single_player_death_sound)

			# if we hit zero lives we're dead and the game might be over
			if player.lives == 0 and not self.time_limit_only:

				# if the whole team is dead, make note of how long they lasted
				if all(
					teammate.lives == 0 for teammate in player.team.players):

					# log the team survival
					# if we're the last player on the team
					player.team.survival_seconds = int(ba.time() -
													   self._start_time)

					# if someone has won, set a timer to end shortly
					# (allows the dust to settle and draws to occur
					# if deaths are close enough)
					if len(self._get_living_teams()) < 2:
						self._round_end_timer = ba.timer(1.0, self.end_game)

			# we still have lives; yay!
			else:
				self.respawn_player(player)

		else:
			return super().handlemessage(msg)
		return None

	def _get_living_teams(self) -> List[Team]:
		return [
			team for team in self.teams
			if len(team.players) > 0 and any(player.lives > 0
											 for player in team.players)
		]

	def end_game(self) -> None:
		if self.has_ended():
			return
		results = ba.GameResults()
		self._vs_text = None  # Kill our 'vs' if its there.
		for team in self.teams:
			results.set_team_score(team, team.survival_seconds)
		self.end(results=results)
