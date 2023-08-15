# Released under the MIT License. See LICENSE for details.
#
"""Hot Bomb game by SEBASTIAN2059 and zPanxo"""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import random

import _babase
import _bascenev1 as _bs
from typing import TYPE_CHECKING

import bascenev1 as bs
from bascenev1._messages import StandMessage
from bascenev1lib.actor.bomb import Bomb
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.spaz import PickupMessage, BombDiedMessage
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class BallDiedMessage:
    """Inform something that a ball has died."""

    def __init__(self, ball: Ball):
        self.ball = ball


class ExplodeHitMessage:
    """Tell an object it was hit by an explosion."""


class Ball(bs.Actor):
    """A lovely bomb mortal"""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0),
                 timer: int = 5, d_time=0.2, color=(1, 1, 1)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        self.explosion_material = bs.Material()
        self.explosion_material.add_actions(
            conditions=(
                'they_have_material', shared.object_material
            ),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('message', 'our_node', 'at_connect', ExplodeHitMessage()),
            ),
        )

        bs.getsound('scamper01').play(volume=0.4)
        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, HotBombGame)
        pmats = [shared.object_material, activity.ball_material]
        self.node = bs.newnode('prop',
                               delegate=self,
                               attrs={
                                   'mesh': activity.ball_mesh,
                                   'color_texture': activity.ball_tex,
                                   'body': activity.ball_body,
                                   'body_scale': 1.0 if activity.ball_body == 'sphere' else 0.8,
                                   'density': 1.0 if activity.ball_body == 'sphere' else 1.2,
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               }
                               )
        self._animate = None
        self.scale = 1.0 if activity.ball_body == 'sphere' else 0.8

        self.color_l = (1, 1, 1)
        self.light = bs.newnode('light',
                                owner=self.node,
                                attrs={
                                    'color': color,
                                    'volume_intensity_scale': 0.4,
                                    'intensity': 0.5,
                                    'radius': 0.10
                                }
                                )
        self.node.connectattr('position', self.light, 'position')
        self.animate_light = None

        self._particles = bs.Timer(0.1, call=bs.WeakCall(self.particles),
                                   repeat=True)
        self._sound_effect = bs.Timer(4, call=bs.WeakCall(self.sound_effect),
                                      repeat=True)

        self.d_time = d_time

        if timer is not None:
            timer = int(timer)
        self._timer = timer
        self._counter: Optional[bs.Node]
        if self._timer is not None:
            self._count = self._timer
            self._tick_timer = bs.Timer(1.0,
                                        call=bs.WeakCall(self._tick),
                                        repeat=True)
            m = bs.newnode('math', owner=self.node, attrs={
                'input1': (0, 0.6, 0), 'operation': 'add'})
            self.node.connectattr('position', m, 'input2')
            self._counter = bs.newnode(
                'text',
                owner=self.node,
                attrs={
                    'text': str(timer),
                    'in_world': True,
                    'shadow': 1.0,
                    'flatness': 0.7,
                    'color': (1, 1, 1),
                    'scale': 0.013,
                    'h_align': 'center'
                }
            )
            m.connectattr('output', self._counter, 'position')
        else:
            self._counter = None

    def particles(self):
        if self.node:
            bs.emitfx(
                position=self.node.position,
                velocity=(0, 3, 0),
                count=9,
                scale=2.5,
                spread=0.2,
                chunk_type='sweat'
            )

    def sound_effect(self):
        if self.node:
            bs.getsound('scamper01').play(volume=0.4)

    def explode(self, color=(3, 1, 0)) -> None:
        sound = random.choice(['explosion01', 'explosion02',
                               'explosion03', 'explosion04', 'explosion05'])
        bs.getsound(sound).play(volume=1)
        bs.emitfx(position=self.node.position,
                  velocity=(0, 10, 0),
                  count=100,
                  scale=1.0,
                  spread=1.0,
                  chunk_type='spark')
        explosion = bs.newnode(
            'explosion',
            attrs={
                'position': self.node.position,
                'velocity': (0, 0, 0),
                'radius': 2.0,
                'big': False,
                'color': color
            }
        )
        bs.timer(1.0, explosion.delete)
        if color == (5, 1, 0):
            color = (1, 0, 0)
            self.activity._handle_score(1)
        else:
            color = (0, 0, 1)
            self.activity._handle_score(0)

        scorch = bs.newnode(
            'scorch',
            attrs={
                'position': self.node.position,
                'size': 1.0,
                'big': True,
                'color': color,
                'presence': 1
            }
        )

        # Set our position a bit lower so we throw more things upward.
        rmats = (self.explosion_material,)
        self.region = bs.newnode(
            'region',
            delegate=self,
            attrs={
                'position': (self.node.position[0], self.node.position[1] - 0.1,
                             self.node.position[2]),
                'scale': (2.0, 2.0, 2.0),
                'type': 'sphere',
                'materials': rmats
            },
        )
        bs.timer(0.05, self.region.delete)

    def _tick(self) -> None:
        c = self.color_l
        c2 = (2.5, 1.5, 0)
        if c[2] != 0:
            c2 = (0, 2, 3)
        if self.node:
            if self._count == 1:
                pos = self.node.position
                color = (5, 1, 0) if pos[0] < 0 else (0, 1, 5)
                self.explode(color=color)
                return
            if self._count > 0:
                self._count -= 1
                assert self._counter
                self._counter.text = str(self._count)
                bs.getsound('tick').play()
            if self._count == 1:
                self._animate = bs.animate(
                    self.node,
                    'mesh_scale',
                    {
                        0: self.node.mesh_scale,
                        0.1: 1.5,
                        0.2: self.scale
                    },
                    loop=True
                )
                self.animate_light = bs.animate_array(
                    self.light,
                    'color',
                    3,
                    {
                        0: c,
                        0.1: c2,
                        0.2: c
                    },
                    loop=True
                )
            else:
                self._animate = bs.animate(
                    self.node,
                    'mesh_scale',
                    {
                        0: self.node.mesh_scale,
                        0.5: 1.5,
                        1.0: self.scale
                    },
                    loop=True
                )
                self.animate_light = bs.animate_array(
                    self.light,
                    'color',
                    3,
                    {
                        0: c,
                        0.2: c2,
                        0.5: c,
                        1.0: c
                    },
                    loop=True
                )

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if not self.node:
                return
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(BallDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, bs.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, bs.PickedUpMessage):
            d = self.d_time

            def damage():
                if (msg is not None and msg.node.exists()
                    and msg.node.getdelegate(PlayerSpaz).hitpoints > 0):
                    spaz = msg.node.getdelegate(PlayerSpaz)
                    spaz.node.color = (spaz.node.color[0] - 0.1,
                                       spaz.node.color[1] - 0.1,
                                       spaz.node.color[2] - 0.1)
                    if spaz.node.hold_node != self.node:
                        self.handlemessage(bs.DroppedMessage(spaz.node))
                    if spaz.hitpoints > 10000:
                        bs.getsound('fuse01').play(volume=0.3)
                        spaz.hitpoints -= 10000
                        spaz._last_hit_time = None
                        spaz._num_time_shit = 0
                        spaz.node.hurt = 1.0 - float(
                            spaz.hitpoints) / spaz.hitpoints_max
                    else:
                        spaz.handlemessage(bs.DieMessage())
                    bs.emitfx(
                        position=msg.node.position,
                        velocity=(0, 3, 0),
                        count=20 if d == 0.2 else 25 if d == 0.1 else 30 if d == 0.05 else 15,
                        scale=1.0,
                        spread=0.2,
                        chunk_type='sweat')
                else:
                    self.damage_timer = None

            self.damage_timer = bs.Timer(self.d_time, damage, repeat=True)

        elif isinstance(msg, bs.DroppedMessage):
            spaz = msg.node.getdelegate(PlayerSpaz)
            self.damage_timer = None

        elif isinstance(msg, bs.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                                                  1.0 * msg.velocity_magnitude,
                msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            # If this hit came from a player, log them as the last to touch us.
            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = self._activity()
                if activity:
                    if s_player in activity.players:
                        self.last_players_to_touch[s_player.team.id] = s_player

        elif isinstance(msg, ExplodeHitMessage):
            node = bs.getcollision().opposingnode
            if not self.node:
                return
            nodepos = self.region.position
            mag = 2000.0

            node.handlemessage(
                bs.HitMessage(
                    pos=nodepos,
                    velocity=(0, 0, 0),
                    magnitude=mag,
                    hit_type='explosion',
                    hit_subtype='normal',
                    radius=2.0
                )
            )
            self.handlemessage(bs.DieMessage())
        else:
            super().handlemessage(msg)


### HUMAN###


class NewPlayerSpaz(PlayerSpaz):
    move_mult = 1.0
    reload = True
    extra_jump = True

    # calls

    def impulse(self):
        self.reload = False
        p = self.node
        self.node.handlemessage(
            "impulse",
            p.position[0], p.position[1] + 40, p.position[2],
            0, 0, 0,
            160, 0, 0, 0,
            0, 205, 0)
        bs.timer(0.4, self.refresh)

    def refresh(self):
        self.reload = True

    def drop_bomb(self) -> Optional[Bomb]:

        if (self.land_mine_count <= 0 and self.bomb_count <= 0) or self.frozen:
            return None
        assert self.node
        pos = self.node.position_forward
        vel = self.node.velocity

        if self.land_mine_count > 0:
            dropping_bomb = False
            self.set_land_mine_count(self.land_mine_count - 1)
            bomb_type = 'land_mine'
        else:
            dropping_bomb = True
            bomb_type = self.bomb_type

        if bomb_type == 'banana':
            bs.getsound('penguinHit1').play(volume=0.3)
            bomb = NewBomb(position=(pos[0], pos[1] + 0.7, pos[2]),
                           velocity=(vel[0], vel[1], vel[2]),
                           bomb_type=bomb_type,
                           radius=1.0,
                           source_player=self.source_player,
                           owner=self.node)
        else:
            bomb = Bomb(position=(pos[0], pos[1] - 0.0, pos[2]),
                        velocity=(vel[0], vel[1], vel[2]),
                        bomb_type=bomb_type,
                        blast_radius=self.blast_radius,
                        source_player=self.source_player,
                        owner=self.node).autoretain()

        assert bomb.node
        if dropping_bomb:
            self.bomb_count -= 1
            bomb.node.add_death_action(
                bs.WeakCall(self.handlemessage, BombDiedMessage()))
        self._pick_up(bomb.node)

        try:
            for clb in self._dropped_bomb_callbacks:
                clb(self, bomb)
        except Exception:
            return

        return bomb

    def on_jump_press(self) -> None:
        if not self.node:
            return
        self.node.jump_pressed = True
        self._turbo_filter_add_press('jump')

        if self.reload and self.extra_jump:
            self.impulse()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, PickupMessage):
            if not self.node:
                return None
            try:
                collision = bs.getcollision()
                opposingnode = collision.opposingnode
                opposingbody = collision.opposingbody
            except bs.NotFoundError:
                return True
            if opposingnode.getnodetype() == 'spaz':
                player = opposingnode.getdelegate(PlayerSpaz, True).getplayer(
                    Player, True)
                if player.actor.shield:
                    return None
            super().handlemessage(msg)
        return super().handlemessage(msg)


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


lang = bs.app.lang.language
if lang == 'Spanish':
    name = 'Hot Bomb'
    description = 'Consigue explotar la bomba en\nel equipo enemigo para ganar.'
    join_description = 'Deshazte de la bomba cuanto antes.'
    join_description_l = 'Deshazte de la bomba cuanto antes.'
    view_description = 'Estalla la bomba en el equipo rival'
    view_description_l = 'Estalla ${ARG1} veces la bomba en el equipo rival'
    bomb_timer = 'Temporizador'
    space_wall = 'Espacio Debajo de la Red'
    num_bones = 'Huesos Distractores'
    b_count = ['Nada', 'Pocos', 'Muchos']
    shield = 'Inmortalidad'
    bomb = 'Habilitar Bananas'
    boxing_gloves = 'Equipar Guantes de Boxeo'
    difficulty = 'Dificultad'
    difficulty_o = ['Fácil', 'Difícil', 'Chernobyl']
    wall_color = 'Color de la Red'
    w_c = ['Verde', 'Rojo', 'Naranja', 'Amarillo', 'Celeste', 'Azul', 'Rosa',
           'Gris']
    ball_body = 'Tipo de Hot Bomb'
    body = ['Esfera', 'Cubo']

else:
    name = 'Hot Bomb'
    description = 'Get the bomb to explode on\nthe enemy team to win.'
    join_description = 'Get rid of the bomb as soon as possible.'
    join_description_l = 'Get rid of the bomb as soon as possible.'
    view_description = 'Explode the bomb in the enemy team'
    view_description_l = 'Explode the bomb ${ARG1} times in the enemy team'
    bomb_timer = 'Timer'
    space_wall = 'Space Under the Mesh'
    num_bones = 'Distractor Bones'
    b_count = ['None', 'Few', 'Many']
    shield = 'Immortality'
    bomb = 'Enable Bananas'
    difficulty = 'Difficulty'
    difficulty_o = ['Easy', 'Hard', 'Chernobyl']
    wall_color = 'Mesh Color'
    w_c = ['Green', 'Red', 'Orange', 'Yellow', 'Light blue', 'Blue', 'Ping',
           'Gray']
    ball_body = 'Type of Hot Bomb'
    body = ['Sphere', 'Box']


# ba_meta export bascenev1.GameActivity
class HotBombGame(bs.TeamGameActivity[Player, Team]):
    """New game."""

    name = name
    description = description
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=5,
            increment=1,
        ),
        bs.IntChoiceSetting(
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
        bs.FloatChoiceSetting(
            'Respawn Times',
            choices=[
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 3.0),
            ],
            default=0.5,

        ),
        bs.FloatChoiceSetting(
            difficulty,
            choices=[
                (difficulty_o[0], 0.15),
                (difficulty_o[1], 0.04),
                (difficulty_o[2], 0.01),
            ],
            default=0.15,

        ),
        bs.IntChoiceSetting(
            bomb_timer,
            choices=[(str(choice) + 's', choice) for choice in range(2, 11)],
            default=5,

        ),
        bs.IntChoiceSetting(
            num_bones,
            choices=[
                (b_count[0], 0),
                (b_count[1], 2),
                (b_count[2], 5),
            ],
            default=2,

        ),
        bs.IntChoiceSetting(
            ball_body,
            choices=[(b, body.index(b)) for b in body],
            default=0,
        ),
        bs.IntChoiceSetting(
            wall_color,
            choices=[(color, w_c.index(color)) for color in w_c],
            default=0,

        ),
        bs.BoolSetting('Epic Mode', default=False),
        bs.BoolSetting(space_wall, default=True),
        bs.BoolSetting(bomb, default=True),
        bs.BoolSetting(shield, default=False),

    ]
    default_music = bs.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return ['Football Stadium']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._bomb_timer = int(settings[bomb_timer])
        self._space_under_wall = bool(settings[space_wall])
        self._num_bones = int(settings[num_bones])
        self._shield = bool(settings[shield])
        self._bomb = bool(settings[bomb])
        self.damage_time = float(settings[difficulty])
        self._epic_mode = bool(settings['Epic Mode'])
        self._wall_color = int(settings[wall_color])
        self._ball_body = int(settings[ball_body])

        self.bodys = ['sphere', 'crate']
        self.meshs = ['bombSticky', 'powerupSimple']

        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = bs.getsound('cheer')
        self._chant_sound = bs.getsound('crowdChant')
        self._foghorn_sound = bs.getsound('foghorn')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self.ball_mesh = bs.getmesh(self.meshs[self._ball_body])
        self.ball_body = self.bodys[self._ball_body]
        self.ball_tex = bs.gettexture('powerupCurse')
        self._ball_sound = bs.getsound('splatter')

        self.last_point = None
        self.colors = [(0.25, 0.5, 0.25), (1, 0.15, 0.15), (1, 0.5, 0),
                       (1, 1, 0),
                       (0.2, 1, 1), (0.1, 0.1, 1), (1, 0.3, 0.5),
                       (0.5, 0.5, 0.5)]
        #
        self.slow_motion = self._epic_mode

        self.ball_material = bs.Material()
        self.ball_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 0.5)))
        self.ball_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', True))
        self.ball_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        self.ball_material.add_actions(
            conditions=(
                'they_have_material', shared.footing_material
            ),
            actions=(
                'impact_sound', self._ball_sound, 0.2, 4
            )
        )

        # Keep track of which player last touched the ball
        self.ball_material.add_actions(
            conditions=(
                'they_have_material', shared.player_material
            ),
            actions=(
                ('call', 'at_connect', self._handle_ball_player_collide),
            )
        )

        # We want the ball to kill powerups; not get stopped by them
        self.ball_material.add_actions(
            conditions=(
                'they_have_material', PowerupBoxFactory.get().powerup_material),
            actions=(
                ('modify_part_collision', 'physical', False),
                ('message', 'their_node', 'at_connect', bs.DieMessage())
            )
        )

        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=(
                'they_have_material', self.ball_material
            ),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._handle_score)
            )
        )
        #####
        self._check_region_material = bs.Material()
        self._check_region_material.add_actions(
            conditions=(
                'they_have_material', self.ball_material
            ),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._reset_count)
            )
        )

        self._reaction_material = bs.Material()
        self._reaction_material.add_actions(
            conditions=(
                'they_have_material', shared.player_material
            ),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._reaction)
            )
        )

        self._reaction_material.add_actions(
            conditions=(
                'they_have_material', HealthFactory.get().health_material
            ),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
            )
        )

        self._collide = bs.Material()
        self._collide.add_actions(
            conditions=(
                ('they_are_different_node_than_us',),
                'and',
                ('they_have_material', shared.player_material),
            ),
            actions=(
                ('modify_part_collision', 'collide', True)
            )
        )

        self._wall_material = bs.Material()
        self._wall_material.add_actions(
            conditions=(
                'we_are_older_than', 1
            ),
            actions=(
                ('modify_part_collision', 'collide', True)
            )
        )

        self.ice_material = bs.Material()
        self.ice_material.add_actions(
            actions=(
                'modify_part_collision', 'friction', 0.05
            )
        )

        self._ball_spawn_pos: Optional[Sequence[float]] = None
        self._ball: Optional[Ball] = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

    def get_instance_description(self) -> Union[str, Sequence]:
        if self._score_to_win == 1:
            return join_description
        return join_description_l, self._score_to_win

    def get_instance_description_short(self) -> Union[str, Sequence]:
        if self._score_to_win == 1:
            return view_description
        return view_description_l, self._score_to_win

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self._ball_spawn_pos = (random.choice([-5, 5]), 4, 0)
        bs.timer(5, self._spawn_ball)
        bs.timer(0.1, self.update_ball, repeat=True)
        self.add_game_complements()
        self.add_map_complements()
        self._update_scoreboard()
        self._chant_sound.play()

    def _reaction(self):
        node: bs.Node = bs.getcollision().opposingnode
        bs.getsound('hiss').play(volume=0.75)

        node.handlemessage(
            "impulse",
            node.position[0], node.position[1], node.position[2],
            -node.velocity[0] * 2, -node.velocity[1], -node.velocity[2],
            100, 100, 0, 0,
            -node.velocity[0], -node.velocity[1], -node.velocity[2]
        )

        bs.emitfx(
            position=node.position,
            count=20,
            scale=1.5,
            spread=0.5,
            chunk_type='sweat'
        )

    def add_game_complements(self):
        HealthBox(
            position=(-1, 3.5, -5 + random.random() * 10)
        )
        HealthBox(
            position=(1, 3.5, -5 + random.random() * 10)
        )
        ###
        g = 0
        while g < self._num_bones:
            b = 0
            Torso(
                position=(
                -6 + random.random() * 12, 3.5, -5 + random.random() * 10)
            )
            while b < 6:
                Bone(
                    position=(
                    -6 + random.random() * 12, 2, -5 + random.random() * 10),
                    style=b
                )
                b += 1
            g += 1
        ########################
        self.wall_color = self.colors[self._wall_color]
        part_of_wall = bs.newnode(
            'locator',
            attrs={
                'shape': 'box',
                'position': (-7.169, 0.5, 0.5),
                'color': self.wall_color,
                'opacity': 1,
                'drawShadow': False,
                'draw_beauty': True,
                'additive': False,
                'size': [14.7, 2, 16]
            }
        )
        part_of_wall2 = bs.newnode(
            'locator',
            attrs={
                'shape': 'box',
                'position': (0, -13.51, 0.5) if self._space_under_wall else (
                0, -35.540, 0.5),
                'color': self.wall_color,
                'opacity': 1,
                'drawShadow': False,
                'draw_beauty': True,
                'additive': False,
                'size': [0.3, 30, 13] if self._space_under_wall else [0.3, 75,
                                                                      13]
            }
        )
        wall = bs.newnode(
            'region',
            attrs={
                'position': (0, 1.11, 0.5) if self._space_under_wall else (
                0, 0.75, 0.5),
                'scale': (0.3, 0.75, 13) if self._space_under_wall else (
                0.3, 1.5, 13),
                'type': 'box',
                'materials': (self._wall_material, self._reaction_material)
            }
        )
        # RESET REGION
        pos = (0, 5.3, 0)
        bs.newnode(
            'region',
            attrs={
                'position': pos,
                'scale': (0.001, 15, 12),
                'type': 'box',
                'materials': [self._check_region_material,
                              self._reaction_material]
            }
        )

        bs.newnode(
            'region',
            attrs={
                'position': pos,
                'scale': (0.3, 15, 12),
                'type': 'box',
                'materials': [self._collide]
            }
        )

    def add_map_complements(self):
        # TEXT
        text = bs.newnode('text',
                          attrs={'position': (0, 2.5, -6),
                                 'text': 'Hot Bomb by\nSEBASTIAN2059 and zPanxo',
                                 'in_world': True,
                                 'shadow': 1.0,
                                 'flatness': 0.7,
                                 'color': (1.91, 1.31, 0.59),
                                 'opacity': 0.25 - 0.15,
                                 'scale': 0.013 + 0.007,
                                 'h_align': 'center'})
        walls_data = {
            'w1': [
                (11, 5.5, 0),
                (4.5, 11, 13)
            ],
            'w2': [
                (-11, 5.5, 0),
                (4.5, 11, 13)
            ],
            'w3': [
                (0, 5.5, -6.1),
                (19, 11, 1)
            ],
            'w4': [
                (0, 5.5, 6.5),
                (19, 11, 1)
            ],
        }
        for i in walls_data:
            w = bs.newnode(
                'region',
                attrs={
                    'position': walls_data[i][0],
                    'scale': walls_data[i][1],
                    'type': 'box',
                    'materials': (self._wall_material,)
                }
            )

        for i in [-5, -2.5, 0, 2.5, 5]:
            pos = (11, 6.5, 0)
            Box(
                position=(pos[0] - 0.5, pos[1] - 5.5, pos[2] + i),
                texture='powerupPunch'
            )
            Box(
                position=(pos[0] - 0.5, pos[1] - 3, pos[2] + i),
                texture='powerupPunch'
            )
            Box(
                position=(pos[0] - 0.5, pos[1] - 0.5, pos[2] + i),
                texture='powerupPunch'
            )
            pos = (-11, 6.5, 0)
            Box(
                position=(pos[0] + 0.5, pos[1] - 5.5, pos[2] + i),
                texture='powerupIceBombs'
            )
            Box(
                position=(pos[0] + 0.5, pos[1] - 3, pos[2] + i),
                texture='powerupIceBombs'
            )
            Box(
                position=(pos[0] + 0.5, pos[1] - 0.5, pos[2] + i),
                texture='powerupIceBombs'
            )

    def spawn_player(self, player: Player) -> bs.Actor:
        position = self.get_position(player)
        name = player.getname()
        display_color = _babase.safecolor(player.color, target_intensity=0.75)
        actor = NewPlayerSpaz(
            color=player.color,
            highlight=player.highlight,
            character=player.character,
            player=player
        )
        player.actor = actor

        player.actor.node.name = name
        player.actor.node.name_color = display_color
        player.actor.bomb_type_default = 'banana'
        player.actor.bomb_type = 'banana'

        actor.connect_controls_to_player(enable_punch=True,
                                         enable_bomb=self._bomb,
                                         enable_pickup=True)
        actor.node.hockey = True
        actor.hitpoints_max = 100000
        actor.hitpoints = 100000
        actor.equip_boxing_gloves()
        if self._shield:
            actor.equip_shields()
            actor.shield.color = (0, 0, 0)
            actor.shield.radius = 0.1
            actor.shield_hitpoints = actor.shield_hitpoints_max = 100000

        # Move to the stand position and add a flash of light.
        actor.handlemessage(
            StandMessage(
                position,
                random.uniform(0, 360)))
        bs.getsound('spawn').play(volume=0.6)
        return actor

    def on_team_join(self, team: Team) -> None:
        self._update_scoreboard()

    def _handle_ball_player_collide(self) -> None:
        collision = bs.getcollision()
        try:
            ball = collision.sourcenode.getdelegate(Ball, True)
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(Player,
                                                                        True)
        except bs.NotFoundError:
            return

        ball.last_players_to_touch[player.team.id] = player

    def _kill_ball(self) -> None:
        self._ball = None

    def _reset_count(self) -> None:
        """reset counter of ball."""

        assert self._ball is not None

        if self._ball.scored:
            return

        bs.getsound('laser').play()
        self._ball._count = self._bomb_timer
        self._ball._counter.text = str(self._bomb_timer)
        self._ball._tick_timer = bs.Timer(
            1.0,
            call=bs.WeakCall(self._ball._tick),
            repeat=True
        )
        self._ball._animate = bs.animate(
            self._ball.node,
            'mesh_scale',
            {
                0: self._ball.node.mesh_scale,
                0.1: self._ball.scale
            }
        )
        if self._ball.light.color[0] == 0:
            self._ball.light.color = (2, 0, 0)
        else:
            self._ball.light.color = (0, 0, 3)

    def update_ball(self):
        if not self._ball:
            return
        if not self._ball.node:
            return
        gnode = bs.getactivity().globalsnode

        if self._ball.node.position[0] > 0:
            self._ball.node.color_texture = bs.gettexture('powerupIceBombs')
            bs.animate_array(gnode, 'vignette_outer', 3, {1.0: (0.4, 0.4, 0.9)})
            self._ball.color_l = (0, 0, 3.5)
            self._ball._counter.color = (0, 0, 5)
        else:
            self._ball.node.color_texture = bs.gettexture('powerupPunch')
            bs.animate_array(gnode, 'vignette_outer', 3,
                             {1.0: (0.6, 0.45, 0.45)})
            self._ball.color_l = (2.5, 0, 0)
            self._ball._counter.color = (1.2, 0, 0)

    def _handle_score(self, index=0) -> None:
        """A point has been scored."""

        assert self._ball is not None

        for team in self.teams:
            if team.id == index:
                scoring_team = team
                team.score += 1
                if index == 0:
                    self.last_point = 0
                else:
                    self.last_point = 1

                # Tell all players to celebrate.
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(bs.CelebrateMessage(2.0))

                # If we've got the player from the scoring team that last
                # touched us, give them points.
                if (scoring_team.id in self._ball.last_players_to_touch
                    and self._ball.last_players_to_touch[scoring_team.id]):
                    self.stats.player_scored(
                        self._ball.last_players_to_touch[scoring_team.id],
                        100,
                        big_message=True)

                # End game if we won.
                if team.score >= self._score_to_win:
                    self.end_game()

            elif team.id != index:

                # Tell all players to celebrate.
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(bs.DieMessage())

        self._foghorn_sound.play()
        self._cheer_sound.play()

        bs.cameraflash(duration=10.0)
        self._update_scoreboard()

    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)

    def _update_scoreboard(self) -> None:
        winscore = self._score_to_win
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score, winscore)

    def handlemessage(self, msg: Any) -> Any:

        # Respawn dead players if they're still in the game.
        if isinstance(msg, bs.PlayerDiedMessage):

            player = msg.getplayer(Player)
            spaz = player.actor
            spaz.node.color = (-1, -1, -1)
            spaz.node.color_mask_texture = bs.gettexture('bonesColorMask')
            spaz.node.color_texture = bs.gettexture('bonesColor')
            spaz.node.head_mesh = bs.getmesh('bonesHead')
            spaz.node.hand_mesh = bs.getmesh('bonesHand')
            spaz.node.torso_mesh = bs.getmesh('bonesTorso')
            spaz.node.pelvis_mesh = bs.getmesh('bonesPelvis')
            spaz.node.upper_arm_mesh = bs.getmesh('bonesUpperArm')
            spaz.node.forearm_mesh = bs.getmesh('bonesForeArm')
            spaz.node.upper_leg_mesh = bs.getmesh('bonesUpperLeg')
            spaz.node.lower_leg_mesh = bs.getmesh('bonesLowerLeg')
            spaz.node.toes_mesh = bs.getmesh('bonesToes')
            spaz.node.style = 'bones'
            # Augment standard behavior...
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))

        # Respawn dead balls.
        elif isinstance(msg, BallDiedMessage):
            if not self.has_ended():
                try:
                    if self._ball._count == 1:
                        bs.timer(3.0, self._spawn_ball)
                except Exception:
                    return
        else:
            super().handlemessage(msg)

    def _flash_ball_spawn(self, pos, color=(1, 0, 0)) -> None:
        light = bs.newnode('light',
                           attrs={
                               'position': pos,
                               'height_attenuated': False,
                               'color': color
                           })
        bs.animate(light, 'intensity', {0.0: 0, 0.25: 0.2, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)

    def _spawn_ball(self) -> None:
        timer = self._bomb_timer
        self._swipsound.play()
        self._whistle_sound.play()
        pos = (random.choice([5, -5]), 2, 0)
        if self.last_point != None:
            if self.last_point == 0:
                pos = (-5, 2, 0)
            else:
                pos = (5, 2, 0)

        color = (0, 0, 1 * 2) if pos[0] == 5 else (1 * 1.5, 0, 0)
        texture = 'powerupPunch' if pos[0] == -5 else 'powerupIceBombs'
        counter_color = (1, 0, 0) if pos[0] == -5 else (0, 0, 5)
        # self._flash_ball_spawn(pos,color)
        self._ball = Ball(position=pos, timer=timer, d_time=self.damage_time,
                          color=color)
        self._ball.node.color_texture = bs.gettexture(texture)
        self._ball._counter.color = counter_color

    def get_position(self, player: Player) -> bs.Actor:
        position = (0, 1, 0)
        team = player.team.id
        if team == 0:
            position = (random.randint(-7, -3), 0.25, random.randint(-5, 5))
            angle = 90
        else:
            position = (random.randint(3, 7), 0.25, random.randint(-5, 5))
            angle = 270
        return position

    def respawn_player(self,
                       player: PlayerType,
                       respawn_time: Optional[float] = None) -> None:
        from babase._general import WeakCall

        assert player
        if respawn_time is None:
            respawn_time = 3.0

        # If this standard setting is present, factor it in.
        if 'Respawn Times' in self.settings_raw:
            respawn_time *= self.settings_raw['Respawn Times']

        # We want whole seconds.
        assert respawn_time is not None
        respawn_time = round(max(1.0, respawn_time), 0)

        if player.actor and not self.has_ended():
            from bascenev1lib.actor.respawnicon import RespawnIcon
            player.customdata['respawn_timer'] = _bs.Timer(
                respawn_time, WeakCall(self.spawn_player_if_exists, player))
            player.customdata['respawn_icon'] = RespawnIcon(
                player, respawn_time)

    def spawn_player_if_exists(self, player: PlayerType) -> None:
        """
        A utility method which calls self.spawn_player() *only* if the
        bs.Player provided still exists; handy for use in timers and whatnot.

        There is no need to override this; just override spawn_player().
        """
        if player:
            self.spawn_player(player)

    def spawn_player_spaz(self, player: PlayerType) -> None:
        position = (0, 1, 0)
        angle = None
        team = player.team.id
        if team == 0:
            position = (random.randint(-7, -3), 0.25, random.randint(-5, 5))
            angle = 90
        else:
            position = (random.randint(3, 7), 0.25, random.randint(-5, 5))
            angle = 270

        return super().spawn_player_spaz(player, position, angle)


##### New-Bomb#####


class ExplodeMessage:
    """Tells an object to explode."""


class ImpactMessage:
    """Tell an object it touched something."""


class NewBomb(bs.Actor):

    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 bomb_type: str = '',
                 radius: float = 2.0,
                 source_player: bs.Player = None,
                 owner: bs.Node = None):

        super().__init__()

        shared = SharedObjects.get()
        # Material for powerups.
        self.bomb_material = bs.Material()
        self.explode_material = bs.Material()

        self.bomb_material.add_actions(
            conditions=(
                ('we_are_older_than', 200),
                'and',
                ('they_are_older_than', 200),
                'and',
                ('eval_colliding',),
                'and',
                (
                    ('they_have_material', shared.footing_material),
                    'or',
                    ('they_have_material', shared.object_material),
                ),
            ),
            actions=('message', 'our_node', 'at_connect', ImpactMessage()))

        self.explode_material.add_actions(
            conditions=('they_have_material',
                        shared.player_material),
            actions=(('modify_part_collision', 'collide', True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._touch_player)))

        self._source_player = source_player
        self.owner = owner
        self.bomb_type = bomb_type
        self.radius = radius

        owner_color = self.owner.source_player._team.color

        if self.bomb_type == 'banana':
            self.node: bs.Node = bs.newnode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'color_texture': bs.gettexture('powerupBomb'),
                'mesh': bs.getmesh('penguinTorso'),
                'mesh_scale': 0.7,
                'body_scale': 0.7,
                'density': 3,
                'reflection': 'soft',
                'reflection_scale': [1.0],
                'shadow_size': 0.3,
                'body': 'sphere',
                'owner': owner,
                'materials': (shared.object_material, self.bomb_material)})

            bs.animate(self.node, 'mesh_scale', {0: 0, 0.2: 1, 0.26: 0.7})
            self.light = bs.newnode('light', owner=self.node, attrs={
                'color': owner_color,
                'volume_intensity_scale': 2.0,
                'intensity': 1,
                'radius': 0.1})
            self.node.connectattr('position', self.light, 'position')

        self.spawn: bs.Timer = bs.Timer(
            10.0, self._check, repeat=True)

    def _impact(self) -> None:
        node = bs.getcollision().opposingnode
        node_delegate = node.getdelegate(object)
        if node:
            if (node is self.owner):
                return
            self.handlemessage(ExplodeMessage())

    def _explode(self):
        if self.node:
            # Set our position a bit lower so we throw more things upward.

            pos = self.node.position
            rmats = (self.explode_material,)
            self.explode_region = bs.newnode(
                'region',
                delegate=self,
                attrs={
                    'position': (pos[0], pos[1] - 0.1, pos[2]),
                    'scale': (self.radius, self.radius, self.radius),
                    'type': 'sphere',
                    'materials': rmats
                },
            )
            if self.bomb_type == 'banana':
                bs.getsound('stickyImpact').play(volume=0.35)
                a = bs.emitfx(position=self.node.position,
                              velocity=(0, 1, 0),
                              count=15,
                              scale=1.0,
                              spread=0.1,
                              chunk_type='spark')
                scorch = bs.newnode('scorch',
                                    attrs={
                                        'position': self.node.position,
                                        'size': 1.0,
                                        'big': False,
                                        'color': (1, 1, 0)
                                    })

                bs.animate(scorch, 'size', {0: 1.0, 5: 0})
                bs.timer(5, scorch.delete)

            bs.timer(0.05, self.explode_region.delete)
            bs.timer(0.001, bs.WeakCall(self.handlemessage, bs.DieMessage()))

    def _touch_player(self):
        node = bs.getcollision().opposingnode
        collision = bs.getcollision()
        try:
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(
                Player, True)
        except bs.NotFoundError:
            return

        if self.bomb_type == 'banana':
            color = player.team.color
            owner_team = self.owner.source_player._team
            if (node is self.owner):
                return
            if player.team == owner_team:
                return
            player.actor.node.handlemessage('knockout', 500.0)
            bs.animate_array(player.actor.node, 'color', 3, {
                0: color, 0.1: (1.5, 1, 0), 0.5: (1.5, 1, 0), 0.6: color})

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, ExplodeMessage):
            self._explode()
        elif isinstance(msg, ImpactMessage):
            self._impact()
        elif isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()
        elif isinstance(msg, bs.OutOfBoundsMessage):
            if self.node:
                self.node.delete()


###### Object#####


class HealthFactory:
    """Wraps up media and other resources used by bs.Bombs.

    category: Gameplay Classes

    A single instance of this is shared between all bombs
    and can be retrieved via bastd.actor.bomb.get_factory().

    Attributes:

       health_mesh
          The bs.mesh of a standard health.

       health_tex
          The bs.Texture for health.

       activate_sound
          A bs.Sound for an activating ??.

       health_material
          A bs.Material applied to health.
    """

    _STORENAME = bs.storagename()

    @classmethod
    def get(cls) -> HealthFactory:
        """Get/create a shared EggFactory object."""
        activity = bs.getactivity()
        factory = activity.customdata.get(cls._STORENAME)
        if factory is None:
            factory = HealthFactory()
            activity.customdata[cls._STORENAME] = factory
        assert isinstance(factory, HealthFactory)
        return factory

    def __init__(self) -> None:
        """Instantiate a BombFactory.

        You shouldn't need to do this; call get_factory()
        to get a shared instance.
        """
        shared = SharedObjects.get()

        self.health_mesh = bs.getmesh('egg')

        self.health_tex = bs.gettexture('eggTex1')

        self.health_sound = bs.getsound('activateBeep')

        # Set up our material so new bombs don't collide with objects
        # that they are initially overlapping.
        self.health_material = bs.Material()

        self.health_material.add_actions(
            conditions=(
                (
                    ('we_are_younger_than', 100),
                    'or',
                    ('they_are_younger_than', 100),
                ),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )

        # We want pickup materials to always hit us even if we're currently
        # not colliding with their node. (generally due to the above rule)
        self.health_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=('modify_part_collision', 'use_node_collide', False),
        )

        self.health_material.add_actions(actions=('modify_part_collision',
                                                  'friction', 0.3))


class HealthBox(bs.Actor):

    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'powerupHealth'):
        super().__init__()

        shared = SharedObjects.get()
        factory = HealthFactory.get()
        self.healthbox_material = bs.Material()
        self.healthbox_material.add_actions(
            conditions=(
                'they_are_different_node_than_us',
            ),
            actions=(
                ('modify_part_collision', 'collide', True)
            )
        )
        self.node: bs.Node = bs.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': bs.gettexture(texture),
            'mesh': bs.getmesh('powerup'),
            'light_mesh': bs.getmesh('powerupSimple'),
            'mesh_scale': 1,
            'body': 'crate',
            'body_scale': 1,
            'density': 1,
            'damping': 0,
            'gravity_scale': 1,
            'reflection': 'powerup',
            'reflection_scale': [0.5],
            'shadow_size': 0.0,
            'materials': (shared.object_material, self.healthbox_material,
                          factory.health_material)})

        self.light = bs.newnode('light', owner=self.node, attrs={
            'color': (1, 1, 1),
            'volume_intensity_scale': 0.4,
            'intensity': 0.7,
            'radius': 0.0})
        self.node.connectattr('position', self.light, 'position')

        self.spawn: bs.Timer = bs.Timer(
            10.0, self._check, repeat=True)

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, bs.OutOfBoundsMessage):
            if self.node:
                self.node.delete()
        elif isinstance(msg, bs.HitMessage):
            try:
                spaz = msg._source_player
                spaz.actor.node.handlemessage(
                    bs.PowerupMessage(poweruptype='health'))
                t_color = spaz.team.color
                spaz.actor.node.color = t_color
                bs.getsound('healthPowerup').play(volume=0.5)
                bs.animate(self.light, 'radius', {0: 0.0, 0.1: 0.2, 0.7: 0})
            except:
                pass

        elif isinstance(msg, bs.DroppedMessage):
            spaz = msg.node.getdelegate(PlayerSpaz)
            self.regen_timer = None


class Torso(bs.Actor):

    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'bonesColor'):
        super().__init__()

        shared = SharedObjects.get()

        self.node: bs.Node = bs.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': bs.gettexture(texture),
            'mesh': bs.getmesh('bonesTorso'),
            'mesh_scale': 1,
            'body': 'sphere',
            'body_scale': 0.5,
            'density': 6,
            'damping': 0,
            'gravity_scale': 1,
            'reflection': 'soft',
            'reflection_scale': [0],
            'shadow_size': 0.0,
            'materials': (shared.object_material,)})

        self.spawn: bs.Timer = bs.Timer(
            10.0, self._check, repeat=True)

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, bs.OutOfBoundsMessage):
            if self.node:
                self.node.delete()


class Bone(bs.Actor):

    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'bonesColor',
                 style: int = 0):
        super().__init__()

        shared = SharedObjects.get()
        meshs = ['bonesUpperArm', 'bonesUpperLeg', 'bonesForeArm',
                 'bonesPelvis', 'bonesToes', 'bonesHand']
        bone = None
        mesh = 0
        for i in meshs:
            if mesh == style:
                bone = meshs[mesh]
            else:
                mesh += 1
        self.node: bs.Node = bs.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': bs.gettexture(texture),
            'mesh': bs.getmesh(bone),
            'mesh_scale': 1.5,
            'body': 'crate',
            'body_scale': 0.6,
            'density': 2,
            'damping': 0,
            'gravity_scale': 1,
            'reflection': 'soft',
            'reflection_scale': [0],
            'shadow_size': 0.0,
            'materials': (shared.object_material,)})

        self.spawn: bs.Timer = bs.Timer(
            10.0, self._check, repeat=True)

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, bs.OutOfBoundsMessage):
            if self.node:
                self.node.delete()


###### Object#####


class Box(bs.Actor):

    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'powerupCurse'):
        super().__init__()

        shared = SharedObjects.get()
        self.dont_collide = bs.Material()
        self.dont_collide.add_actions(
            conditions=(
                'they_are_different_node_than_us',
            ),
            actions=(
                ('modify_part_collision', 'collide', False)
            )
        )

        self.node: bs.Node = bs.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': bs.gettexture(texture),
            'mesh': bs.getmesh('powerup'),
            'light_mesh': bs.getmesh('powerupSimple'),
            'mesh_scale': 4,
            'body': 'box',
            'body_scale': 3,
            'density': 9999,
            'damping': 9999,
            'gravity_scale': 0,
            'reflection': 'soft',
            'reflection_scale': [0.25],
            'shadow_size': 0.0,
            'materials': [self.dont_collide, ]})
