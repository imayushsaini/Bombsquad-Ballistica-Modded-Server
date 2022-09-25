# Released under the MIT License. See LICENSE for details.
#
"""Hot Bomb game by SEBASTIAN2059 and zPanxo"""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import random

import ba,_ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.gameutils import SharedObjects
from ba._messages import StandMessage
from bastd.actor.bomb import Bomb, Blast
from bastd.actor.spaz import Spaz, PickupMessage, PunchHitMessage, BombDiedMessage
from bastd.actor.popuptext import PopupText

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class BallDiedMessage:
    """Inform something that a ball has died."""

    def __init__(self, ball: Ball):
        self.ball = ball

class ExplodeHitMessage:
    """Tell an object it was hit by an explosion."""

class Ball(ba.Actor):
    """A lovely bomb mortal"""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0),timer: int = 5,d_time=0.2,color=(1,1,1)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()
        
        self.explosion_material = ba.Material()
        self.explosion_material.add_actions(
            conditions=('they_have_material', shared.object_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('message', 'our_node', 'at_connect', ExplodeHitMessage()),
            ),
        )
        
        ba.playsound(ba.getsound('scamper01'),volume=0.4)
        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, HotBombGame)
        pmats = [shared.object_material, activity.ball_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': activity.ball_model,
                                   'color_texture': activity.ball_tex,
                                   'body': activity.ball_body,
                                   'body_scale': 1.0 if activity.ball_body == 'sphere' else 0.8,
                                   'density':1.0 if activity.ball_body == 'sphere' else 1.2,
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        self._animate = None 
        self.scale = 1.0 if activity.ball_body == 'sphere' else 0.8
        
        if self.activity._impulse_bomb:
            self.node.extra_acceleration = (0,-20,0)
        
        self.color_l = (1,1,1)
        self.light = ba.newnode('light', owner=self.node, attrs={
                                        'color':color,
                                        'volume_intensity_scale': 0.4,
                                        'intensity':0.5,
                                        'radius':0.10})
        self.node.connectattr('position', self.light,'position')
        self.animate_light = None
        
        self._particles = ba.Timer(0.1,call=ba.WeakCall(self.particles),repeat=True)
        self._sound_effect = ba.Timer(4,call=ba.WeakCall(self.sound_effect),repeat=True)


        self.d_time = d_time
        
        if timer is not None:
            timer = int(timer)
        self._timer = timer
        self._counter: Optional[ba.Node]
        if self._timer is not None:
            self._count = self._timer
            self._tick_timer = ba.Timer(1.0,
                                        call=ba.WeakCall(self._tick),
                                        repeat=True)
            m = ba.newnode('math', owner=self.node, attrs={'input1': (0, 0.6, 0), 'operation': 'add'})
            self.node.connectattr('position', m, 'input2')
            self._counter = ba.newnode('text',
                                      owner=self.node,
                                      attrs={'text':str(timer),
                                             'in_world':True,
                                             'shadow':1.0,
                                             'flatness':0.7,
                                             'color':(1,1,1),
                                             'scale':0.013,
                                             'h_align':'center'})
            m.connectattr('output', self._counter, 'position')
        else:
            self._counter = None
            
    def particles(self):
        if self.node:
            ba.emitfx(position=self.node.position,
                                      velocity=(0,3,0),
                                      count=9,
                                      scale=2.5,
                                      spread=0.2,
                                      chunk_type='sweat')
            
    def sound_effect(self):
        if self.node:
            ba.playsound(ba.getsound('scamper01'),volume=0.4)
            
    
    def explode(self,color=(3,1,0)) -> None:
        sound = random.choice(['explosion01','explosion02','explosion03','explosion04','explosion05'])
        ba.playsound(ba.getsound(sound),volume=1)
        ba.emitfx(position=self.node.position,
                          velocity=(0,10,0),
                          count=100,
                          scale=1.0,
                          spread=1.0,
                          chunk_type='spark')
        explosion = ba.newnode('explosion',
                               attrs={
                                   'position': self.node.position,
                                   'velocity': (0,0,0),
                                   'radius': 2.0,
                                   'big': False,
                                   'color':color
                                    })
        if color == (5,1,0):
            color = (1,0,0)
            self.activity._handle_score(1)
        else:
            color=(0,0,1)
            self.activity._handle_score(0)
        scorch = ba.newnode('scorch',
                                attrs={
                                    'position': self.node.position,
                                    'size': 1.0,
                                    'big': True,
                                    'color':color,
                                    'presence':1
                                })
    
        # Set our position a bit lower so we throw more things upward.
        rmats = (self.explosion_material,)
        self.region = ba.newnode(
            'region',
            delegate=self,
            attrs={
                'position': (self.node.position[0], self.node.position[1] - 0.1, self.node.position[2]),
                'scale': (2.0, 2.0, 2.0),
                'type': 'sphere',
                'materials': rmats
            },
        )
        ba.timer(0.05, self.region.delete)
                                  
    def _tick(self) -> None:
        c = self.color_l
        c2 = (2.5,1.5,0)
        if c[2] != 0:
            c2 = (0,2,3)
        if self.node:
            if self._count == 1:    
                pos = self.node.position
                color = (5,1,0) if pos[0] < 0 else (0,1,5)
                self.explode(color=color)
                return
            if self._count > 0:
                self._count -= 1
                assert self._counter
                self._counter.text = str(self._count)
                ba.playsound(ba.getsound('tick'))
            if self._count == 1:
                self._animate = ba.animate(self.node,'model_scale',{0:self.scale,0.1:1.5,0.2:self.scale},loop=True)
                self.animate_light = ba.animate_array(self.light,'color',3,{0:c,0.1:c2,0.2:c},loop=True)
            else:
                self._animate = ba.animate(self.node,'model_scale',{0:self.scale,0.5:1.5,1.0:self.scale},loop=True)
                self.animate_light = ba.animate_array(self.light,'color',3,{0:c,0.2:c2,0.5:c,1.0:c},loop=True)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(BallDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, ba.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, ba.PickedUpMessage):
            d = self.d_time
            def damage():
                if (msg is not None and msg.node.exists()
                        and msg.node.getdelegate(PlayerSpaz).hitpoints > 0):
                    spaz = msg.node.getdelegate(PlayerSpaz)
                    spaz.node.color = (spaz.node.color[0]-0.1,spaz.node.color[1]-0.1,spaz.node.color[2]-0.1)
                    if spaz.hitpoints > 10000:
                        ba.playsound(ba.getsound('fuse01'),volume=0.3)
                        spaz.hitpoints -= 10000
                        spaz._last_hit_time = None
                        spaz._num_time_shit = 0
                        spaz.node.hurt = 1.0 - float(spaz.hitpoints) / spaz.hitpoints_max
                    else:
                        spaz.handlemessage(ba.DieMessage())
                    ba.emitfx(
                        position=msg.node.position,
                        velocity=(0, 3, 0),
                        count=20 if d == 0.2 else 25 if d == 0.1 else 30 if d == 0.05 else 15,
                        scale=1.0,
                        spread=0.2,
                        chunk_type='sweat')
                else:
                    self.damage_timer = None

            self.damage_timer = ba.Timer(self.d_time, damage, repeat=True)
            #
            if self.activity._impulse_bomb:
                self.node.extra_acceleration = (0,27,0) if self.activity.ball_body == 'box' else (0,45,0)

        elif isinstance(msg, ba.DroppedMessage):
            from ba import _math
            spaz = msg.node.getdelegate(PlayerSpaz)
            self.damage_timer = None
            if self.activity._impulse_bomb:
                self.node.extra_acceleration = (0, -8, 0) if self.activity.ball_body == 'box' else (0, -20, 0)

        elif isinstance(msg, ba.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
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
            node = ba.getcollision().opposingnode
            assert self.node
            nodepos = self.region.position
            mag = 2000.0
            
            node.handlemessage(
                ba.HitMessage(pos=nodepos,
                              velocity=(0, 0, 0),
                              magnitude=mag,
                              hit_type='explosion',
                              hit_subtype='normal',
                              radius=2.0))
            self.handlemessage(ba.DieMessage())
        else:
            super().handlemessage(msg)

###HUMAN###
class NewPlayerSpaz(PlayerSpaz):
    
    move_mult = 1.0
    reload = True
    extra_jump = True
    ###calls
    
    def impulse(self):
        self.reload = False
        p = self.node
        self.node.handlemessage("impulse", p.position[0], p.position[1]+40, p.position[2],
                                0, 0, 0, 
                                160, 0, 0, 0, 
                                0, 205, 0)
        ba.timer(0.4,self.refresh)
        
    def refresh(self):
        self.reload = True
        
    def on_bomb_press(self) -> None:
        if not self.node:
            return

        if self._dead or self.frozen:
            return
        if self.node.knockout > 0.0:
            return
        t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        assert isinstance(t_ms, int)
        if t_ms - self.last_bomb_time_ms >= self._bomb_cooldown:
            self.last_bomb_time_ms = t_ms
            self.node.bomb_pressed = True
            if not self.node.hold_node:
                self.drop_bomb()
                
        self._turbo_filter_add_press('bomb')

    def on_bomb_release(self) -> None:
        if not self.node:
            return
        self.node.bomb_pressed = False
    
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
            ba.playsound(ba.getsound('penguinHit1'),volume=0.3)
            bomb = NewBomb(position=(pos[0], pos[1] + 0.7, pos[2]),
                        velocity=(vel[0], vel[1], vel[2]),
                        bomb_type = bomb_type,
                        radius = 1.0,
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
                ba.WeakCall(self.handlemessage, BombDiedMessage()))
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
                collision = ba.getcollision()
                opposingnode = collision.opposingnode
                opposingbody = collision.opposingbody
            except ba.NotFoundError:
                return True
            if opposingnode.getnodetype() == 'spaz':
                player = opposingnode.getdelegate(PlayerSpaz,True).getplayer(Player, True)
                if player.actor.shield:
                    return None
            super().handlemessage(msg)
        return super().handlemessage(msg)
        
        
class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


lang = ba.app.lang.language
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
    b_count = ['Nada','Pocos','Muchos']
    shield = 'Inmortalidad'
    bomb = 'Habilitar Bananas'
    impulse_bomb = 'Modo Globo'
    boxing_gloves = 'Equipar Guantes de Boxeo'
    difficulty = 'Dificultad'
    difficulty_o = ['Fácil','Difícil','Chernobyl']
    wall_color = 'Color de la Red'
    w_c = ['Verde','Rojo','Naranja','Amarillo','Celeste','Azul','Rosa','Gris']
    ball_body = 'Tipo de Hot Bomb'
    body = ['Esfera','Cubo']
   
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
    b_count = ['None','Few','Many']
    shield = 'Immortality'
    bomb = 'Enable Bananas'
    impulse_bomb = 'Balloon Mode'
    difficulty = 'Difficulty'
    difficulty_o = ['Easy','Hard','Chernobyl']
    wall_color = 'Mesh Color'
    w_c = ['Green','Red','Orange','Yellow','Light blue','Blue','Ping','Gray']
    ball_body = 'Type of Hot Bomb'
    body = ['Sphere','Box']
   

# ba_meta export game
class HotBombGame(ba.TeamGameActivity[Player, Team]):
    """New game."""

    name = name
    description = description
    available_settings = [
        ba.IntSetting(
            'Score to Win',
            min_value=1,
            default=5,
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
                ('Longer', 3.0),
            ],
            default=0.5,
        
        ),
        ba.FloatChoiceSetting(
            difficulty,
            choices=[
                (difficulty_o[0], 0.15),
                (difficulty_o[1], 0.04),
                (difficulty_o[2], 0.01),
            ],
            default=0.15,
        
        ),
        ba.IntChoiceSetting(
            bomb_timer,
            choices=[(str(choice)+'s',choice) for choice in range(2,11)],
            default=5,

        ),    
        ba.IntChoiceSetting(
            num_bones,
            choices=[
                (b_count[0], 0),
                (b_count[1], 2),
                (b_count[2], 5),
            ],
            default=2,
            
        ),
        ba.IntChoiceSetting(
            ball_body,
            choices=[(b, body.index(b)) for b in body],
            default=0,
        ),
        ba.IntChoiceSetting(
            wall_color,
            choices=[(color,w_c.index(color)) for color in w_c],
            default=0,

        ),
        ba.BoolSetting('Epic Mode', default=False),
        ba.BoolSetting(space_wall, default=True),
        ba.BoolSetting(bomb, default=True),
        ba.BoolSetting(impulse_bomb, default=False),
        ba.BoolSetting(shield, default=False),
        
    ]
    default_music = ba.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('hotbomb')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._bomb_timer = int(settings[bomb_timer])
        self._space_under_wall = bool(settings[space_wall])      
        self._num_bones = int(settings[num_bones])
        self._shield = bool(settings[shield])
        self._bomb = bool(settings[bomb])
        self._impulse_bomb = bool(settings[impulse_bomb])
        self.damage_time = float(settings[difficulty])
        self._epic_mode = bool(settings['Epic Mode'])
        self._wall_color = int(settings[wall_color])
        self._ball_body = int(settings[ball_body])
        
        self.bodys = ['sphere','crate']
        self.models = ['bombSticky','powerupSimple']
        
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = ba.getsound('cheer')
        self._chant_sound = ba.getsound('crowdChant')
        self._foghorn_sound = ba.getsound('foghorn')
        self._swipsound = ba.getsound('swip')
        self._whistle_sound = ba.getsound('refWhistle')
        self.ball_model = ba.getmodel(self.models[self._ball_body])
        self.ball_body = self.bodys[self._ball_body]
        self.ball_tex = ba.gettexture('powerupCurse')
        self._ball_sound = ba.getsound('splatter')
        
        self.last_point = None
        self.colors = [(0.25,0.5,0.25), (1, 0.15, 0.15), (1, 0.5, 0), (1, 1, 0),
                       (0.2, 1, 1), (0.1, 0.1, 1), (1, 0.3, 0.5),(0.5, 0.5, 0.5)]
        #
        self.slow_motion = self._epic_mode
        
        self.ball_material = ba.Material()
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
        self.ball_material.add_actions(conditions=('they_have_material',
                                                   shared.footing_material),
                                       actions=('impact_sound',
                                                self._ball_sound, 0.2, 4))

        # Keep track of which player last touched the ball
        self.ball_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect',
                      self._handle_ball_player_collide), ))

        # We want the ball to kill powerups; not get stopped by them
        self.ball_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', ba.DieMessage())))
                     
        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.ball_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        #####
        self._check_region_material = ba.Material()
        self._check_region_material.add_actions(
            conditions=('they_have_material', self.ball_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._reset_count)))
        
        self._reaction_material = ba.Material()
        self._reaction_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._reaction)))
                     
        self._reaction_material.add_actions(
            conditions=('they_have_material', HealthFactory.get().health_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', True)))
        
        self._collide=ba.Material()
        self._collide.add_actions(conditions=(('they_are_different_node_than_us', ),
                                                'and',
                                                ('they_have_material', shared.player_material),), actions=(('modify_part_collision', 'collide', True)))
                     
        self._wall_material=ba.Material()
        self._wall_material.add_actions(conditions=('we_are_older_than', 1), actions=(('modify_part_collision', 'collide', True)))
        
        self.ice_material = ba.Material()
        self.ice_material.add_actions(actions=('modify_part_collision','friction',0.05))
        
        self._ball_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
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
        shared = SharedObjects.get()
        act = ba.getactivity().map
        ###
        self.setup_standard_time_limit(self._time_limit)
        self._ball_spawn_pos = (random.choice([-5,5]),4,0)
        ba.timer(5,self._spawn_ball)
        ba.timer(0.1,self.update_ball,repeat=True)
        HealthBox(position=(-1,3.5,-5+random.random()*10))
        HealthBox(position=(1,3.5,-5+random.random()*10))
        ###
        g = 0
        while g < self._num_bones:
            b = 0
            Torso(position=(-6+random.random()*12,3.5,-5+random.random()*10))
            while b < 6:
                Bone(position=(-6+random.random()*12,2,-5+random.random()*10),style=b)
                b += 1
            g += 1
        ########################
        self.wall_color = self.colors[self._wall_color]
        e = ba.newnode('locator',attrs={'shape':'box','position':(-6.65-0.459-0.06,0.5,0.5),
                'color':self.wall_color,'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':[14.7,2,16]})
        if self._space_under_wall:
            f = ba.newnode('locator',attrs={'shape':'box','position':(0,-13.51,0.5),
                'color':self.wall_color,'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':[0.3,30,13]})
        else:
            g = ba.newnode('locator',attrs={'shape':'box','position':(0,-35.489-0.51,0.5),
                'color':self.wall_color,'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':[0.3,75,13]})
        scale = (0.3,1.5,13)
        pos = (0,0.75,0.5)
        if self._space_under_wall:
            scale = (0.3,0.75,13)
            pos = (0,1.11,0.5)
        z5 = ba.newnode('region',attrs={'position': pos,'scale': scale,'type': 'box','materials': (self._wall_material,self._reaction_material)})
        ####RESET-REGION#########
        pos = (0,5.3,0)
        size = (0.01,15,12) #(0,6,12)
        ba.newnode('region',attrs={'position': pos,'scale': size,'type': 'box',
                                   'materials': [self._check_region_material,self._reaction_material]})
                                   
        ba.newnode('region',attrs={'position': pos,'scale': (0.3,15,12),'type': 'box',
                                   'materials': [self._collide]})
        
        self._update_scoreboard()
        ba.playsound(self._chant_sound)
    
    def _reaction(self):
        node: ba.Node = ba.getcollision().opposingnode
        ba.playsound(ba.getsound('hiss'),volume=0.75)
                
        node.handlemessage("impulse",node.position[0],node.position[1],node.position[2],
                                    -node.velocity[0]*2,-node.velocity[1],-node.velocity[2],
                                    100,100,0,0,-node.velocity[0],-node.velocity[1],-node.velocity[2])
                                    
        ba.emitfx(position=node.position,count=20,scale=1.5,spread=0.5,chunk_type='sweat')
        
    def spawn_player(self, player: Player) -> ba.Actor:
        position = self.get_position(player)
        name = player.getname()
        display_color = _ba.safecolor(player.color, target_intensity=0.75)
        actor = NewPlayerSpaz(color=player.color,
                              highlight=player.highlight,
                              character=player.character,
                              player=player)
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
            actor.shield.color = (0,0,0)
            actor.shield.radius = 0.1
            actor.shield_hitpoints = actor.shield_hitpoints_max = 100000
        
        #Move to the stand position and add a flash of light.
        actor.handlemessage(
            StandMessage(
                position,
                random.uniform(0, 360)))
        ba.playsound(ba.getsound('spawn'),volume=0.6)
        return actor
        
    def on_team_join(self, team: Team) -> None:
        self._update_scoreboard()

    def _handle_ball_player_collide(self) -> None:
        collision = ba.getcollision()
        try:
            ball = collision.sourcenode.getdelegate(Ball, True)
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(
                                                            Player, True)
        except ba.NotFoundError:
            return

        ball.last_players_to_touch[player.team.id] = player

    def _kill_ball(self) -> None:
        self._ball = None
        
    def _reset_count(self) -> None:
        """reset counter of ball."""

        assert self._ball is not None
        assert self._score_regions is not None

        if self._ball.scored:
            return
        
        ba.playsound(ba.getsound('laser'))
        self._ball._count = self._bomb_timer + 1
        if self._ball.light.color[0] == 0:
            self._ball.light.color = (2,0,0)
        else:
            self._ball.light.color = (0,0,3)
            
    def update_ball(self):
        if not self._ball: return
        if not self._ball.node: return
        gnode = ba.getactivity().globalsnode
        
        if self._ball.node.position[0] > 0:
            self._ball.node.color_texture = ba.gettexture('powerupIceBombs')
            ba.animate_array(gnode,'vignette_outer',3,{1.0:(0.4, 0.4, 0.9)})
            self._ball.color_l = (0,0,3.5)
            self._ball._counter.color = (0,0,5)
        else:
            self._ball.node.color_texture = ba.gettexture('powerupPunch')
            ba.animate_array(gnode,'vignette_outer',3,{1.0:(0.6,0.45,0.45)})
            self._ball.color_l = (2.5,0,0)
            self._ball._counter.color = (1.2,0,0)

    def _handle_score(self,index=0) -> None:
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
                        player.actor.handlemessage(ba.CelebrateMessage(2.0))

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
                        player.actor.handlemessage(ba.DieMessage())
        
        ba.playsound(self._foghorn_sound)
        ba.playsound(self._cheer_sound)

        ba.cameraflash(duration=10.0)
        self._update_scoreboard()

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)

    def _update_scoreboard(self) -> None:
        winscore = self._score_to_win
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score, winscore)

    def handlemessage(self, msg: Any) -> Any:

        # Respawn dead players if they're still in the game.
        if isinstance(msg, ba.PlayerDiedMessage):
            
            player = msg.getplayer(Player)
            spaz = player.actor
            spaz.node.color = (-1,-1,-1)
            spaz.node.color_mask_texture = ba.gettexture('bonesColorMask')
            spaz.node.color_texture = ba.gettexture('bonesColor')
            spaz.node.head_model = ba.getmodel('bonesHead')
            spaz.node.hand_model = ba.getmodel('bonesHand')
            spaz.node.torso_model = ba.getmodel('bonesTorso')
            spaz.node.pelvis_model = ba.getmodel('bonesPelvis')
            spaz.node.upper_arm_model = ba.getmodel('bonesUpperArm')
            spaz.node.forearm_model = ba.getmodel('bonesForeArm')
            spaz.node.upper_leg_model = ba.getmodel('bonesUpperLeg')
            spaz.node.lower_leg_model = ba.getmodel('bonesLowerLeg')
            spaz.node.toes_model = ba.getmodel('bonesToes')
            spaz.node.style = 'bones'
            # Augment standard behavior...
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))

        # Respawn dead balls.
        elif isinstance(msg, BallDiedMessage):
            if not self.has_ended():
                try:
                    if self._ball._count == 1:
                        ba.timer(3.0, self._spawn_ball)
                except Exception:
                    return
        else:
            super().handlemessage(msg)

    def _flash_ball_spawn(self,pos,color=(1,0,0)) -> None:
        light = ba.newnode('light',
                           attrs={
                               'position': pos,
                               'height_attenuated': False,
                               'color': color
                           })
        ba.animate(light, 'intensity', {0.0: 0, 0.25: 0.2, 0.5: 0}, loop=True)
        ba.timer(1.0, light.delete)

    def _spawn_ball(self) -> None:
        timer = self._bomb_timer
        ba.playsound(self._swipsound)
        ba.playsound(self._whistle_sound)
        pos = (random.choice([5,-5]),2,0)
        if self.last_point != None:
            if self.last_point == 0:
                pos = (-5,2,0)
            else:
                pos = (5,2,0)
        
        color = (0,0,1*2) if pos[0] == 5 else (1*1.5,0,0)
        texture = 'powerupPunch' if pos[0] == -5 else 'powerupIceBombs'
        counter_color = (1,0,0) if pos[0] == -5 else (0,0,5)
        #self._flash_ball_spawn(pos,color)
        self._ball = Ball(position=pos,timer=timer,d_time=self.damage_time,color=color)
        self._ball.node.color_texture = ba.gettexture(texture)
        self._ball._counter.color = counter_color
        
    def get_position(self, player: Player) -> ba.Actor:
        position = (0,1,0)
        team = player.team.id
        if team == 0:
            position = (random.randint(-7,-3),0.25,random.randint(-5,5))
            angle = 90
        else:
            position = (random.randint(3,7),0.25,random.randint(-5,5))
            angle = 270
        return position
    
    def respawn_player(self,
                       player: PlayerType,
                       respawn_time: Optional[float] = None) -> None:
        import _ba
        from ba._general import Call, WeakCall
        
        assert player
        if respawn_time is None:
            respawn_time = 3.0
            # teamsize = len(player.team.players)
            # if teamsize == 1:
                # respawn_time = 3.0
            # elif teamsize == 2:
                # respawn_time = 5.0
            # elif teamsize == 3:
                # respawn_time = 6.0
            # else:
                # respawn_time = 7.0

        # If this standard setting is present, factor it in.
        if 'Respawn Times' in self.settings_raw:
            respawn_time *= self.settings_raw['Respawn Times']

        # We want whole seconds.
        assert respawn_time is not None
        respawn_time = round(max(1.0, respawn_time), 0)

        if player.actor and not self.has_ended():
            from bastd.actor.respawnicon import RespawnIcon
            player.customdata['respawn_timer'] = _ba.Timer(
                respawn_time, WeakCall(self.spawn_player_if_exists, player))
            player.customdata['respawn_icon'] = RespawnIcon(
                player, respawn_time)
    
    def spawn_player_if_exists(self, player: PlayerType) -> None:
        """
        A utility method which calls self.spawn_player() *only* if the
        ba.Player provided still exists; handy for use in timers and whatnot.

        There is no need to override this; just override spawn_player().
        """
        if player:
            self.spawn_player(player)

        
    def spawn_player_spaz(self, player: PlayerType) -> None:
        position = (0,1,0)
        angle = None
        team = player.team.id
        if team == 0:
            position = (random.randint(-7,-3),0.25,random.randint(-5,5))
            angle = 90
        else:
            position = (random.randint(3,7),0.25,random.randint(-5,5))
            angle = 270
        
        return super().spawn_player_spaz(player, position, angle)

#####New-Bomb#####
class ExplodeMessage:
    """Tells an object to explode."""
    
class ImpactMessage:
    """Tell an object it touched something."""

class NewBomb(ba.Actor):
    
    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 bomb_type: str = '',
                 radius: float = 2.0,
                 source_player: ba.Player = None,
                 owner: ba.Node = None):
                 
        super().__init__()
        
        shared = SharedObjects.get()
        # Material for powerups.
        self.bomb_material = ba.Material()
        self.explode_material = ba.Material()
                     
        self.bomb_material.add_actions(
            conditions=(
                ('we_are_older_than', 200),
                'and',
                ('they_are_older_than', 200),
                'and',
                ('eval_colliding', ),
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
            actions=(('modify_part_collision', 'collide',True),
                     ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._touch_player)))
        
        self._source_player = source_player
        self.owner = owner
        self.bomb_type = bomb_type
        self.radius = radius
        
        owner_color = self.owner.source_player._team.color
        
        if self.bomb_type == 'banana':
            self.node: ba.Node = ba.newnode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'color_texture': ba.gettexture('powerupBomb'),
                'model': ba.getmodel('penguinTorso'),
                'model_scale':0.7,
                'body_scale':0.7,
                'density':3,
                'reflection': 'soft',
                'reflection_scale': [1.0],
                'shadow_size': 0.3,
                'body': 'sphere',
                'owner': owner,
                'materials': (shared.object_material,self.bomb_material)})
                
            ba.animate(self.node,'model_scale',{0:0,0.2:1,0.26:0.7})
            self.light = ba.newnode('light', owner=self.node, attrs={
                                            'color':owner_color,
                                            'volume_intensity_scale': 2.0,
                                            'intensity':1,
                                            'radius':0.1})
            self.node.connectattr('position', self.light,'position')
            
        self.spawn: ba.Timer = ba.Timer(
            10.0,self._check,repeat=True)
    
    def _impact(self) -> None:
        node = ba.getcollision().opposingnode
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
            self.explode_region = ba.newnode(
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
                ba.playsound(ba.getsound('stickyImpact'),volume=0.35)
                a = ba.emitfx(position=self.node.position,
                                              velocity=(0,1,0),
                                              count=15,
                                              scale=1.0,
                                              spread=0.1,
                                              chunk_type='spark')
                scorch = ba.newnode('scorch',
                                attrs={
                                    'position': self.node.position,
                                    'size': 1.0,
                                    'big': False,
                                    'color':(1,1,0)
                                })
                                
                ba.animate(scorch,'size',{0:1.0,5:0})
                ba.timer(5,scorch.delete)
                

            ba.timer(0.05, self.explode_region.delete)
            ba.timer(0.001, ba.WeakCall(self.handlemessage, ba.DieMessage()))
        
    def _touch_player(self):
        node = ba.getcollision().opposingnode
        collision = ba.getcollision()
        try:
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(
                                                            Player, True)
        except ba.NotFoundError:
            return
        
        if self.bomb_type == 'banana':
            color = player.team.color
            owner_team = self.owner.source_player._team
            if (node is self.owner):
                return
            if player.team == owner_team:
                return
            player.actor.node.handlemessage('knockout', 500.0)
            ba.animate_array(player.actor.node,'color',3,{0:color,0.1:(1.5,1,0),0.5:(1.5,1,0),0.6:color})
    
    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, ExplodeMessage):
            self._explode()
        elif isinstance(msg, ImpactMessage):
            self._impact()
        elif isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()
        elif isinstance(msg, ba.OutOfBoundsMessage):
            if self.node:
                self.node.delete()
                
######Object#####
class HealthFactory:
    """Wraps up media and other resources used by ba.Bombs.

    category: Gameplay Classes

    A single instance of this is shared between all bombs
    and can be retrieved via bastd.actor.bomb.get_factory().

    Attributes:

       health_model
          The ba.Model of a standard health.
          
       health_tex
          The ba.Texture for health.

       activate_sound
          A ba.Sound for an activating ??.

       health_material
          A ba.Material applied to health.
    """

    _STORENAME = ba.storagename()

    @classmethod
    def get(cls) -> HealthFactory:
        """Get/create a shared EggFactory object."""
        activity = ba.getactivity()
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
        
        self.health_model = ba.getmodel('egg')
        
        self.health_tex = ba.gettexture('eggTex1')
        
        self.health_sound = ba.getsound('activateBeep')
        
        # Set up our material so new bombs don't collide with objects
        # that they are initially overlapping.
        self.health_material = ba.Material()

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

class HealthBox(ba.Actor):
    
    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'powerupHealth'):
        super().__init__()
        
        shared = SharedObjects.get()
        factory = HealthFactory.get()
        self.healthbox_material = ba.Material()
        self.healthbox_material.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', True)))
        self.node: ba.Node = ba.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': ba.gettexture(texture),
            'model': ba.getmodel('powerup'),
            'light_model':ba.getmodel('powerupSimple'),
            'model_scale':1,
            'body': 'crate',
            'body_scale':1,
            'density':1,
            'damping':0,
            'gravity_scale':1,
            'reflection': 'powerup',
            'reflection_scale': [0.5],
            'shadow_size': 0.0,
            'materials': (shared.object_material,self.healthbox_material,factory.health_material)})
            
        self.light = ba.newnode('light', owner=self.node, attrs={
                                        'color':(1,1,1),
                                        'volume_intensity_scale': 0.4,
                                        'intensity':0.7,
                                        'radius':0.0})
        self.node.connectattr('position', self.light,'position')
            
        self.spawn: ba.Timer = ba.Timer(
            10.0,self._check,repeat=True)

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ba.OutOfBoundsMessage):
            if self.node:
                self.node.delete()
        elif isinstance(msg, ba.HitMessage):
            try:
                spaz = msg._source_player
                spaz.actor.node.handlemessage(ba.PowerupMessage(poweruptype='health'))
                t_color = spaz.team.color
                spaz.actor.node.color = t_color
                ba.playsound(ba.getsound('healthPowerup'),volume=0.5)
                ba.animate(self.light,'radius',{0:0.0,0.1:0.2,0.7:0})
            except:
                pass

        elif isinstance(msg, ba.DroppedMessage):
            spaz = msg.node.getdelegate(PlayerSpaz)
            self.regen_timer = None

class Torso(ba.Actor):
    
    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'bonesColor'):
        super().__init__()
        
        shared = SharedObjects.get()

        self.node: ba.Node = ba.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': ba.gettexture(texture),
            'model': ba.getmodel('bonesTorso'),
            'model_scale':1,
            'body': 'sphere',
            'body_scale':0.5,
            'density':6,
            'damping':0,
            'gravity_scale':1,
            'reflection': 'soft',
            'reflection_scale': [0],
            'shadow_size': 0.0,
            'materials': (shared.object_material,)})
            
        self.spawn: ba.Timer = ba.Timer(
            10.0,self._check,repeat=True)

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ba.OutOfBoundsMessage):
            if self.node:
                self.node.delete()

class Bone(ba.Actor):
    
    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'bonesColor',
                 style: int = 0):
        super().__init__()
        
        shared = SharedObjects.get()
        models = ['bonesUpperArm','bonesUpperLeg','bonesForeArm','bonesPelvis','bonesToes','bonesHand']
        bone = None
        model = 0
        for i in models:
            if model == style:
                bone = models[model]
            else:
                model += 1
        self.node: ba.Node = ba.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': ba.gettexture(texture),
            'model': ba.getmodel(bone),
            'model_scale':1.5,
            'body': 'crate',
            'body_scale':0.6,
            'density':2,
            'damping':0,
            'gravity_scale':1,
            'reflection': 'soft',
            'reflection_scale': [0],
            'shadow_size': 0.0,
            'materials': (shared.object_material,)})
            
        self.spawn: ba.Timer = ba.Timer(
            10.0,self._check,repeat=True)

    def _check(self) -> None:
        """Prevent the cube from annihilating."""

    def handlemessage(self, msg):
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ba.OutOfBoundsMessage):
            if self.node:
                self.node.delete()
                
######Object#####
class Box(ba.Actor):
    
    def __init__(self, position: Sequence[float] = (0, 1, 0),
                 velocity: Sequence[float] = (0, 0, 0),
                 texture: str = 'powerupCurse'):
        super().__init__()
        
        shared = SharedObjects.get()
        self.dont_collide=ba.Material()
        self.dont_collide.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', False)))

        self.node: ba.Node = ba.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'color_texture': ba.gettexture(texture),
            'model': ba.getmodel('powerup'),
            'light_model': ba.getmodel('powerupSimple'),
            'model_scale':4,
            'body': 'box',
            'body_scale':3,
            'density':9999,
            'damping':9999,
            'gravity_scale':0,
            'reflection': 'soft',
            'reflection_scale': [0.25],
            'shadow_size': 0.0,
            'materials': [self.dont_collide,]})
            
###Map###
class HotBombMap(ba.Map):
    """Stadium map for football games."""
    from bastd.mapdata import football_stadium as defs 

    name = 'Hot Bomb Map'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['hotbomb']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'footballStadiumPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('footballStadium'),
            'vr_fill_model': ba.getmodel('footballStadiumVRFill'),
            'collide_model': ba.getcollidemodel('footballStadiumCollide'),
            'tex': ba.gettexture('footballStadium')
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = ba.newnode(
            'terrain',
            delegate=self,
            attrs={
                'model': self.preloaddata['model'],
                'collide_model': self.preloaddata['collide_model'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material]
            })
        ba.newnode('terrain',
                   attrs={
                       'model': self.preloaddata['vr_fill_model'],
                       'lighting': False,
                       'vr_only': True,
                       'background': True,
                       'color_texture': self.preloaddata['tex']
                   })
                   
        #TEXT
        text = ba.newnode('text',
                              attrs={'position':(0,2.5,-6),
                                     'text':'Hot Bomb by\nSEBASTIAN2059 and zPanxo',
                                     'in_world':True,
                                     'shadow':1.0,
                                     'flatness':0.7,
                                     'color':(1.91,1.31,0.59),
                                     'opacity':0.25-0.15,
                                     'scale':0.013+0.007,
                                     'h_align':'center'})
        
        ####################################
        
        self._wall_material=ba.Material()
        self._wall_material.add_actions(conditions=('we_are_older_than', 1), actions=(('modify_part_collision', 'collide', True)))
        
        self._reaction_material = ba.Material()
        self._reaction_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('call', 'at_connect', self._reaction)))
        self._check_region_material = ba.Material()
        # self._check_region_material.add_actions(
            # conditions=('they_have_material', shared.object_material),
            # actions=(('modify_part_collision', 'collide',
                      # True), ('modify_part_collision', 'physical', False),
                     # ('call', 'at_connect', self._reset_count)))
        ####################################
        z = ba.newnode('region',attrs={'position': (11,5.5,0),'scale': (4.5,11,13),'type': 'box','materials': (self._wall_material,)})
        z1 = ba.newnode('region',attrs={'position': (-11,5.5,0),'scale': (4.5,11,13),'type': 'box','materials': (self._wall_material,)})
        z2 = ba.newnode('region',attrs={'position': (0,5.5,-6.1),'scale': (19,11,1),'type': 'box','materials': (self._wall_material,)})
        z3 = ba.newnode('region',attrs={'position': (0,5.5,6.5),'scale': (19,11,1),'type': 'box','materials': (self._wall_material,)})
        ####################################
        for i in [-5,-2.5,0,2.5,5]:
            pos = (11,6.5,0)
            Box(position=(pos[0]-0.5,pos[1]-5.5,pos[2]+i),texture='powerupPunch')
            Box(position=(pos[0]-0.5,pos[1]-3,pos[2]+i),texture='powerupPunch')
            Box(position=(pos[0]-0.5,pos[1]-0.5,pos[2]+i),texture='powerupPunch')
            pos = (-11,6.5,0)
            Box(position=(pos[0]+0.5,pos[1]-5.5,pos[2]+i),texture='powerupIceBombs')
            Box(position=(pos[0]+0.5,pos[1]-3,pos[2]+i),texture='powerupIceBombs')
            Box(position=(pos[0]+0.5,pos[1]-0.5,pos[2]+i),texture='powerupIceBombs')
        ####################################
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.3, 1.2, 1.0)
        gnode.ambient_color = (1.3, 1.2, 1.0)
        gnode.vignette_outer = (0.57, 0.57, 0.57)
        gnode.vignette_inner = (0.9, 0.9, 0.9)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5
    
    def _reaction(self):
        node: ba.Node = ba.getcollision().opposingnode
        ba.playsound(ba.getsound('hiss'),volume=0.75)
                
        node.handlemessage("impulse",node.position[0],node.position[1],node.position[2],
                                    -node.velocity[0],-node.velocity[1],-node.velocity[2],
                                    100,100,0,0,-node.velocity[0],-node.velocity[1],-node.velocity[2])
                                    
        ba.emitfx(position=node.position,count=20,scale=1.5,spread=0.5,chunk_type='sweat')
                                    
    def is_point_near_edge(self,
                           point: ba.Vec3,
                           running: bool = False) -> bool:
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5

ba._map.register_map(HotBombMap)