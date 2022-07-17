# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import math
import random
from bastd.actor import spawner
from bastd.actor.bomb import BombFactory
from bastd.actor.spazfactory import SpazFactory
from bastd.gameutils import SharedObjects
from bastd.actor.bomb import ExplodeHitMessage
from ba._gameutils import show_damage_count
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.powerupbox import PowerupBox
from bastd.actor.spazbot import SpazBotSet, ExplodeyBotNoTimeLimit

if TYPE_CHECKING:
    from typing import Any, Union, Sequence, Optional


class Blast(ba.Actor):

    def __init__(self,
                 position: Sequence[float] = (0.0, 1.0, 0.0),
                 blast_radius: float = 2.0,
                 color: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()

        shared = SharedObjects.get()
        factory = BombFactory.get()

        self.radius = blast_radius

        rmats = (factory.blast_material, shared.attack_material)
        self.node = ba.newnode(
            'region',
            delegate=self,
            attrs={
                'position': (position[0], position[1] - 0.1, position[2]),
                'scale': (self.radius, self.radius, self.radius),
                'type': 'sphere',
                'materials': rmats
            },
        )
        ba.timer(0.05, self.node.delete)

        explosion = ba.newnode('explosion',
                               attrs={
                                   'position': position,
                                   'radius': self.radius * 0.8,
                                   'color': (color[0] * 0.3,
                                             color[1] * 0.3,
                                             color[2] * 0.3),
                                   'big': True
                               })
        ba.timer(1.0, explosion.delete)

        light = ba.newnode('light',
                           attrs={
                               'position': position,
                               'volume_intensity_scale': 10.0,
                               'color': (1, 0.3, 0.1)
                           })
        scl = random.uniform(0.6, 0.9) * 3.0
        scorch_radius = self.radius * 1.4
        light_radius = self.radius * 0.6
        iscale = 0.8
        ba.animate(
            light, 'intensity', {
                0: 2.0 * iscale,
                scl * 0.02: 0.1 * iscale,
                scl * 0.025: 0.2 * iscale,
                scl * 0.05: 17.0 * iscale,
                scl * 0.06: 5.0 * iscale,
                scl * 0.08: 4.0 * iscale,
                scl * 0.2: 0.6 * iscale,
                scl * 2.0: 0.00 * iscale,
                scl * 3.0: 0.0
            })
        ba.animate(
            light, 'radius', {
                0: light_radius * 0.2,
                scl * 0.05: light_radius * 0.55,
                scl * 0.1: light_radius * 0.3,
                scl * 0.3: light_radius * 0.15,
                scl * 1.0: light_radius * 0.05
            })
        ba.timer(scl * 3.0, light.delete)

        scorch = ba.newnode('scorch',
                            attrs={
                                'position': position,
                                'size': scorch_radius * 0.5,
                                'color': (color[0] * 0.6,
                                          color[1] * 0.6,
                                          color[2] * 0.6),
                                'big': True
                            })
        ba.animate(scorch, 'presence', {3.000: 1, 13.000: 0})
        ba.timer(13.0, scorch.delete)

        lpos = light.position
        ba.playsound(factory.random_explode_sound(), position=lpos)
        ba.playsound(factory.random_explode_sound(), position=lpos)
        ba.playsound(factory.debris_fall_sound, position=lpos)
        ba.camerashake(intensity=5.0)

        def _extra_boom() -> None:
            ba.playsound(factory.random_explode_sound(), position=lpos)
        ba.timer(0.25, _extra_boom)

        def _extra_debris_sound() -> None:
            ba.playsound(factory.debris_fall_sound, position=lpos)
            ba.playsound(factory.wood_debris_fall_sound, position=lpos)
        ba.timer(0.4, _extra_debris_sound)

#        ba.emitfx(position=position,
          #        count=100,
        #          scale=1.8,
           #       spread=5,
       #           chunk_type='spark')
    #    ba.emitfx(position=position,
        #          count=100,
       #           spread=5,
     #             scale=2,
          #        chunk_type='ice',
    #              emit_type='stickers')
        ba.emitfx(position=position,
                  count=1000,
                  spread=500,
                  scale=10,
                  chunk_type='slime')
    #    ba.emitfx(position=position,
   #               count=20,
       #           scale=1,
      #            spread=500,
        #          chunk_type='sweat',
       #           emit_type='tendrils')

    def handlemessage(self, msg: Any) -> Any:
        assert not self.expired

        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ExplodeHitMessage):
            node = ba.getcollision().opposingnode
            assert self.node
            nodepos = self.node.position
            mag = 2000.0
            mag *= 2.0

            node.handlemessage(
                ba.HitMessage(pos=nodepos,
                              velocity=(0, 0, 0),
                              magnitude=mag,
                              hit_type='explosion',
                              hit_subtype='normal',
                              radius=self.radius))
        else:
            return super().handlemessage(msg)
        return None


class TNTBox(ba.Actor):

    def __init__(self,
                 team_id: ba.Team,
                 modeltype: float = None,
                 position: Sequence[float] = None,
                 hitpoints: float = 1000,
                 team: str = None):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()
        spaz = SpazFactory.get()

        self.team = team_id
        self.modeltype = modeltype
        self.team_str = team
        self.teamcolor = team_id.color
        self.position = position
        self.hitpoints = hitpoints
        self.hitpoints_max = hitpoints
        self._width = 240
        self._width_max = 240
        self._height = 35
        self._bar_width = 240
        self._bar_height = 35
        self._bar_tex = self._backing_tex = ba.gettexture('bar')
        self._cover_tex = ba.gettexture('uiAtlas')
        self._model = ba.getmodel('meterTransparent')

        if team == 'team 1':
            self.bar_posx = -200 - 120
        else:
            self.bar_posx = 200 - 120

        self.box_material = ba.Material()
        no_collide_material = ba.Material()
        self.box_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=('modify_part_collision', 'collide', False),
        )

        if modeltype == 1:
            self.node = ba.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': (position[0], position[1] + 2.5, position[2]),
                    'model': ba.getmodel('tnt'),
                    'light_model': ba.getmodel('tnt'),
                    'body': 'crate',
                    'body_scale': 3.3,
                    'model_scale': 3.35,
                    'shadow_size': 0.3,
                    'color_texture': ba.gettexture('tickets'),
                    'is_area_of_interest': True,
                    'reflection': 'soft',
                    'reflection_scale': [0.23],
                    'materials': [self.box_material, shared.footing_material]
                    })
        elif modeltype == 2:
            self.node = ba.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': (position[0], position[1] + 1.5, position[2]),
                    'model': ba.getmodel('tnt'),
                    'light_model': ba.getmodel('tnt'),
                    'body': 'crate',
                    'body_scale': 1,
                    'model_scale': 1,
                    'shadow_size': 0.3,
                    'color_texture': ba.gettexture('tnt'),
                    'is_area_of_interest': True,
                    'reflection': 'soft',
                    'reflection_scale': [0.23],
                    'materials': [self.box_material, shared.footing_material]
                    })
        elif modeltype == 3:
            self.node = ba.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': (position[0], position[1] + 1.5, position[2]),
                    'model': ba.getmodel('puck'),
                    'body': 'puck',
                    'body_scale': 1,
                    'model_scale': 1,
                    'shadow_size': 1.0,
                    'color_texture': ba.gettexture('puckColor'),
                    'is_area_of_interest': True,
                    'reflection': 'soft',
                    'reflection_scale': [0.23],
                    'materials': [self.box_material, shared.footing_material]
                    })
        elif modeltype == 4:
            self.node = ba.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': (position[0], position[1] + 1.5, position[2]),
                    'model': ba.getmodel('frostyPelvis'),
                    'body': 'sphere',
                    'body_scale': 2.5,
                    'model_scale': 2.5,
                    'shadow_size': 0.3,
                    'color_texture': ba.gettexture('frostyColor'),
                    'is_area_of_interest': True,
                    'reflection': 'soft',
                    'reflection_scale': [1.0],
                    'materials': [self.box_material, shared.footing_material]
                    })

        ba.animate(self.node, 'model_scale', {
            0: 0,
            0.2: self.node.model_scale * 1.1,
            0.26: self.node.model_scale})

        light = ba.newnode(
            'light',
            owner=self.node,
            attrs={
                'radius': 0.28,
                'color': self.teamcolor
            })
        self.node.connectattr('position', light, 'position')

        self._scoreboard()
        self._update()

    def animate_model(self) -> None:
        if not self.node:
            return None
        ba.animate(self.node, 'model_scale', {
            0: self.node.model_scale,
            0.08: self.node.model_scale * 0.9,
            0.15: self.node.model_scale})
        if self.modeltype in [1,2]:
            ba.emitfx(position=self.node.position,
                      velocity=self.node.velocity,
                      count=int(6 + random.random() * 10),
                      scale=0.5,
                      spread=0.4,
                      chunk_type='splinter')
        elif self.modeltype == 3:
            ba.emitfx(position=self.node.position,
                      velocity=self.node.velocity,
                      count=int(4 + random.random() * 4),
                      scale=0.5,
                      spread=0.3,
                      chunk_type='metal')
        else:
            ba.emitfx(position=self.node.position,
                      velocity=self.node.velocity,
                      count=int(4 + random.random() * 4),
                      scale=0.5,
                      spread=0.3,
                      chunk_type='ice')

    def do_damage(self, msg: Any) -> None:
        if not self.node:
            return None
        damage = msg.magnitude
        self.hitpoints -= int(damage)
        if self.hitpoints <= 0:
            self.hitpoints = 0
            Blast(
                position=self.node.position,
                blast_radius=20.0,
                color=self.teamcolor).autoretain()
            self.node.delete()

    def _update(self) -> None:
        self._score_text.node.text = str(self.hitpoints)
        self._bar_width = self.hitpoints * self._width_max / self.hitpoints_max
        cur_width = self._bar_scale.input0
        ba.animate(self._bar_scale, 'input0', {
            0.0: cur_width,
            0.1: self._bar_width
        })
        cur_x = self._bar_position.input0
        if self.team_str == 'team 1':
            ba.animate(self._bar_position, 'input0', {
                0.0: cur_x,
                0.1: self.bar_posx*0.265 - self._bar_width / 2
            })
        else:
            ba.animate(self._bar_position, 'input0', {
                0.0: cur_x,
                0.1: self.bar_posx + self._bar_width / 2
            })

    def show_damage_msg(self, msg: Any) -> None:
        if not self.node:
            return None
        damage = msg.magnitude
        self.show_damage_count('-' + str(int(damage)),
                             self.node.position,
                             (msg.force_direction[0]*0.2,
                              msg.force_direction[1]*0.2,
                              msg.force_direction[2]*0.2,))

    def show_damage_count(self, damage: str, position: Sequence[float],
                          direction: Sequence[float]) -> None:
        """Pop up a damage count at a position in space.

        Category: Gameplay Functions
        """
        lifespan = 1.0
        app = ba.app

        # FIXME: Should never vary game elements based on local config.
        #  (connected clients may have differing configs so they won't
        #  get the intended results).
        do_big = app.ui.uiscale is ba.UIScale.SMALL or app.vr_mode
        txtnode = ba.newnode('text',
                              attrs={
                                  'text': damage,
                                  'in_world': True,
                                  'h_align': 'center',
                                  'flatness': 1.0,
                                  'shadow': 1.0 if do_big else 0.7,
                                  'color': (1, 0.25, 0.25, 1),
                                  'scale': 0.035 if do_big else 0.03
                              })
        # Translate upward.
        tcombine = ba.newnode('combine', owner=txtnode, attrs={'size': 3})
        tcombine.connectattr('output', txtnode, 'position')
        v_vals = []
        pval = 0.0
        vval = 0.07
        count = 6
        for i in range(count):
            v_vals.append((float(i) / count, pval))
            pval += vval
            vval *= 0.5
        p_start = position[0]
        p_dir = direction[0]
        ba.animate(tcombine, 'input0',
                {i[0] * lifespan: p_start + p_dir * i[1]
                 for i in v_vals})
        p_start = position[1]
        p_dir = direction[1]
        ba.animate(tcombine, 'input1',
                {i[0] * lifespan: p_start + p_dir * i[1]
                 for i in v_vals})
        p_start = position[2]
        p_dir = direction[2]
        ba.animate(tcombine, 'input2',
                {i[0] * lifespan: p_start + p_dir * i[1]
                 for i in v_vals})
        ba.animate(txtnode, 'opacity', {0.7 * lifespan: 1.0, lifespan: 0.0})
        ba.timer(lifespan, txtnode.delete)

    def _scoreboard(self) -> None:
        self._backing = ba.NodeActor(
            ba.newnode('image',
                       attrs={
                           'position': (self.bar_posx + self._width / 2, -35),
                           'scale': (self._width, self._height),
                           'opacity': 0.7,
                           'color': (self.teamcolor[0] * 0.2,
                                     self.teamcolor[1] * 0.2,
                                     self.teamcolor[2] * 0.2),
                           'vr_depth': -3,
                           'attach': 'topCenter',
                           'texture': self._backing_tex
                       }))
        self._bar = ba.NodeActor(
            ba.newnode('image',
                       attrs={
                           'opacity': 1.0,
                           'color': self.teamcolor,
                           'attach': 'topCenter',
                           'texture': self._bar_tex
                       }))
        self._bar_scale = ba.newnode('combine',
                                     owner=self._bar.node,
                                     attrs={
                                         'size': 2,
                                         'input0': self._bar_width,
                                         'input1': self._bar_height
                                     })
        self._bar_scale.connectattr('output', self._bar.node, 'scale')
        self._bar_position = ba.newnode(
            'combine',
            owner=self._bar.node,
            attrs={
                'size': 2,
                'input0': self.bar_posx + self._bar_width / 2,
                'input1': -35
            })
        self._bar_position.connectattr('output', self._bar.node, 'position')
        self._cover = ba.NodeActor(
            ba.newnode('image',
                       attrs={
                           'position': (self.bar_posx + 120, -35),
                           'scale':
                               (self._width * 1.15, self._height * 1.6),
                           'opacity': 1.0,
                           'color': (self.teamcolor[0] * 1.1,
                                     self.teamcolor[1] * 1.1,
                                     self.teamcolor[2] * 1.1),
                           'vr_depth': 2,
                           'attach': 'topCenter',
                           'texture': self._cover_tex,
                           'model_transparent': self._model
                       }))
        self._score_text = ba.NodeActor(
            ba.newnode('text',
                       attrs={
                           'position': (self.bar_posx + 120, -35),
                           'h_attach': 'center',
                           'v_attach': 'top',
                           'h_align': 'center',
                           'v_align': 'center',
                           'maxwidth': 130,
                           'scale': 0.9,
                           'text': '',
                           'shadow': 0.5,
                           'flatness': 1.0,
                           'color': (1,1,1,0.8)
                       }))

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.HitMessage):
            self.animate_model()
            self.do_damage(msg)
            # self.show_damage_msg(msg)
            self._update()
        elif isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()
        elif isinstance(msg, ba.OutOfBoundsMessage):
            if self.node:
                self.node.position = self.position
                self.node.velocity = (0,0,0)
        else:
            super().handlemessage(msg)

class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0
        self.can_attack: bool = False
        self.tnt: Optional[TNTBox] = None


# ba_meta export game
class TNTTeamGame(ba.TeamGameActivity[Player, Team]):
    """Football game for teams mode."""

    name = 'Heist'
    description = 'Get the enemies Ticket Vault!'
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [
            ba.IntSetting(
                'TNT Hitpoints',
                min_value=1000,
                default=25000,
                increment=1000,
            ),
            ba.FloatChoiceSetting(
                'Model Type',
                choices=[
                    ('TNT Big', 1),
                    ('TNT', 2),
                    ('Puck', 3),
                    ('Snowball', 4),
                ],
                default=1,
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
        # We only support two-team play.
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('team_flag')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._time_limit = float(settings['Time Limit'])
        self._tnt_hitpoints = int(settings['TNT Hitpoints'])
        self._model_type = float(settings['Model Type'])
        self._tntbox_pos = [(-11, 2.5, 0.0), (11.0, 2.5, 0.0)]
        self.team_index = 1
        self.create_team_index = 1
        self._bots = SpazBotSet()

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Get the enemies Ticket Vault!'

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'Get the enemies Ticket Vault!'

    def on_team_join(self, team: Team) -> None:
        # Can't do this in create_team because the team's color/etc. have
        # not been wired up yet at that point.
        self._spawn_tnt_for_team(team)

    def _spawn_tnt_for_team(self, team: Team) -> None:
        team.tnt = TNTBox(team_id=team,
                          modeltype=self._model_type,
                          position=self.map.get_flag_position(team.id),
                          hitpoints=self._tnt_hitpoints,
                          team='team ' + str(self.team_index)).autoretain()
        self.team_index += 1

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        ba.timer(0.05, self._update, repeat=True)
        ba.timer(10.0, self.custom_drop, repeat=True)
        # self.setup_standard_powerup_drops()

    def custom_drop(self):
        pos = self.map.get_flag_position(None)
        def spawn_punch():
            PowerupBox(
                position=(pos[0], pos[1] + 2.0, pos[2]),
                poweruptype='punch',
                expire=False).autoretain()
        def spawn_shield():
            PowerupBox(
                position=(pos[0], pos[1] + 2.0, pos[2]),
                poweruptype='shield',
                expire=False).autoretain()
        def spawn_explodeybot():
            self._bots._spawn_bot(
                ExplodeyBotNoTimeLimit,
                pos=(pos[0], pos[1] + 1.0, pos[2]),
                on_spawn_call=None)
        custom = random.choice([spawn_punch, spawn_shield, spawn_explodeybot])
        spawner.Spawner(
            pt=pos,
            spawn_time=3.0,
            send_spawn_message=False,
            spawn_callback=custom)

    def _update(self) -> None:
        if not self.teams[0].tnt.node:
            self.teams[1].score = 1
        if not self.teams[1].tnt.node:
            self.teams[0].score = 1
        if self.teams[0].score > 0 or self.teams[1].score > 0:
            ba.timer(1.0, self.end_game)

    def spawn_player(self, player: Player) -> ba.Actor:
        team: Team = player.team
        spaz = self.spawn_player_spaz(player)
        spaz.connect_controls_to_player(enable_bomb=False)
        return spaz


    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            self.respawn_player(player)
        else:
            return super().handlemessage(msg)
        return None

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results, announce_delay=0.8)
