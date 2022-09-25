# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import ba, random, _ba
from math import cos, sin
from bastd.actor.bomb import Bomb, BombFactory, Blast, ExplodeMessage
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional, Callable

class DisconnectMessage():
    pass
class ConnectMessage():
    pass

class Box(ba.Actor):
    # should create our own node instead
    def __init__(self,
                 velocity: Sequence[float] = (0.0, 0.0, 0.0),
                 bomb_type: str = 'normal',
                 box_type: str = 'small',
                 bomb_scale: float = 1.0):
        super().__init__()
        shared = SharedObjects.get()
        factory = BombFactory.get()
        self.pos: Sequence[float] = ((-11.857367) + round(random.uniform(0, 23), 6),
                                      round(random.uniform(2, 9), 2),
                                      (-4.3599663) + round(random.uniform(0, 8), 6))
        self.random = self.force = self.ang = self.x = self.z = self.momentum = 0
        
        self.typee = box_type
        self._exploded, self.ground = False, False
        self._explode_callbacks: List[Callable[[Bomb, Blast], Any]] = []

        materials: Tuple[ba.Material, ...]
        materials = (factory.bomb_material, shared.footing_material,
                         shared.object_material)

        if box_type == 'small':
           self.data = {
               'walk_force': 9.35,
               'jump_force': 190,
               'walk_cd': 1474,
               'jump_cd': 1500,
               'light_color': (1, 0, 0.4),
               'points': 100,
               'texture': ba.gettexture('star'),
               'size': 0.9}
        elif box_type == 'large':
           self.data = {
               'walk_force': 13.3905,
               'jump_force': 260,
               'walk_cd': 900,
               'jump_cd': 3000,
               'light_color': (0, 0.2, 1.55),
               'points': 50,
               'texture': ba.gettexture('egg2'),
               'size': 1.2}

        self.node = ba.newnode('prop',
                                   delegate=self,
                                   attrs={
                                       'position': self.pos,
                                       'velocity': velocity,
                                       'model': ba.getmodel('powerup'),
                                       'light_model':  ba.getmodel('powerup'),
                                       'body': 'crate',
                                       'model_scale': self.data.get('size'),
                                       'body_scale': self.data.get('size'),
                                       'density':0.5,
                                       'gravity_scale': 0.5,
                                       'shadow_size': 0.5,
                                       'color_texture': self.data.get('texture'),
                                       'reflection': 'soft',
                                       'reflection_scale': [0.23],
                                       'materials': materials})
        self.light = ba.newnode('light',
                     attrs={
                     'color': self.data.get('light_color'),
                     'radius': 0.4
                     })
        self.node.connectattr('position',self.light,'position')
        self.move_used = self.highjump_used = self.jump_used = False
        ba.animate(self.node, 'model_scale', {0.0:0.0, 0.7:self.data.get('size')})
        ba.timer(1000*0.001, self.start_updating)

    def start_updating(self):
        self.move_timer = ba.Timer(100*0.001, ba.WeakCall(self.update_ai), repeat=True)
    def refresh(self, type_: str = 'move'):
        if type_ == 'move':
           self.move_used = False
        elif type_ == 'jump':
           self.jump_used = False
        elif type_ == 'highjump':
           self.highjump_used = False


    def move(self):
        try:
            if self.node.exists() and not self.move_used and self.node.position[1] < 1.0:
               self.move_used = True
               ba.timer(self.data.get('walk_cd')*0.001, lambda: self.refresh('move'))
               self.ang = random.randint(0,360)
               self.x = cos(self.ang) * self.data.get('walk_force')
               self.z = sin(self.ang) * self.data.get('walk_force')
               self.node.velocity = (self.x, 0, self.z)
        except: pass
    def high_jump(self):
        try:
            if self.node.exists() and not self.highjump_used:
               self.highjump_used = True
               ba.timer(10000*0.001, lambda: self.refresh('highjump'))
               self.node.handlemessage("impulse", self.node.position[0], self.node.position[1], self.node.position[2],
                                                  0.0, 0.0, 0.0,
                                                  self.data.get('jump_force')+70,0,0,0,0,1,0)
        except: pass
    def jump(self):
        try:
            if self.node.exists() and not self.jump_used:
               self.jump_used = True
               ba.timer(self.data.get('jump_cd')*0.001, lambda: self.refresh('jump'))
               self.node.handlemessage("impulse", self.node.position[0], self.node.position[1], self.node.position[2],
                                                  0.0, 0.0, 0.0,
                                                  self.data.get('jump_force'),0,0,0,0,1,0)
        except: pass
    def act_crazy(self):
        try:
            if self.node.exists():
               self.node.velocity = (self.node.velocity[0]+round(random.uniform(-2.0, 2.0),2), random.random()*1.5, self.node.velocity[2]+round(random.uniform(-2.0, 2.0),2))
               self.node.extra_acceleration = (self.node.velocity[0]*1.3, self.node.velocity[1]*45, self.node.velocity[2]*1.3)
        except: pass

    def update_ai(self):
        if not self.node.exists():
           self.update_ai = None
           return
        for p in self.activity.players:
            if p.actor.node.exists():
               if p.actor.node.hold_node == self.node:
                  self.act_crazy()
               else:
                 self.node.extra_acceleration = (0, 0, 0)
                 self.random = random.randint(1,4)
                 if self.random == 1: self.move()
                 elif self.random == 2: self.jump()
                 elif self.random == 3 and self.typee == 'large': self.high_jump()
        
    def on_expire(self) -> None:
        super().on_expire()
        self._explode_callbacks = []
    def respawn(self) -> None: pass
        
    def _handle_die(self) -> None:
      #  self.respawn()
        if self.node:
            self.light.delete()
            self.node.delete()
    def _handle_oob(self) -> None:
        self.handlemessage(ba.DieMessage())
    def add_explode_callback(self, call: Callable[[Bomb, Blast], Any]) -> None:
        self._explode_callbacks.append(call)
    def explode(self) -> None:
        if self._exploded:
            return
        self._exploded = True
        if self.node:
            blast = Blast(position=self.node.position,
                          velocity=self.node.velocity,
                          blast_radius=2.4,
                          blast_type='tnt',
                          hit_type='normal',
                          hit_subtype='tnt').autoretain()
            for callback in self._explode_callbacks:
                callback(self, blast)
        ba.timer(0.001, ba.WeakCall(self.handlemessage, ba.DieMessage()))
    def _add_material(self, material: ba.Material) -> None:
        if not self.node:
            return
        materials = self.node.materials
        if material not in materials:
            assert isinstance(materials, tuple)
            self.node.materials = materials + (material, )

    def _handle_hit(self, msg: ba.HitMessage) -> None:
        if msg.hit_subtype == 'tnt': return
        if not self._exploded and not msg.hit_type == 'punch':
            self.update_ai = None
            ba.timer(0.1 + random.random() * 0.1,
                     ba.WeakCall(self.handlemessage, ExplodeMessage()))
            killer = msg.get_source_player(ba.Player)
            if killer is not None:
               assert killer.team is not None
               self.activity.stats.player_scored(killer, self.data.get('points'), screenmessage=False, color=(killer.actor.node.color[0]+0.3, killer.actor.node.color[1]+0.3, killer.actor.node.color[2]+0.3))
               killer.team.score += self.data.get('points')
               ba.playsound(self.activity._dingsound)
               self.activity._update_scoreboard()
               self.move_timer = None
        if msg.srcnode: pass
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ExplodeMessage):
            self.explode()
        elif isinstance(msg, ba.HitMessage):
            self._handle_hit(msg)
        elif isinstance(msg, ba.DieMessage):
            ba.timer(random.randrange(1500,5020,50)*0.001, lambda: Box(box_type=self.typee).autoretain())
            self._handle_die()
        elif isinstance(msg, ba.OutOfBoundsMessage):
            self._handle_oob()
        else:
            super().handlemessage(msg)


class Player(ba.Player['Team']):
    ...
class Team(ba.Team[Player]):

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class CrazyBoxGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Crazy Box'
    description = 'Blow up the Crazy Boxes!'
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
            ba.IntSetting('Points to win per Player',min_value=50,default=800, increment=50),
            ba.IntSetting('Small Box Count',min_value=1,default=1, increment=1),
            ba.IntSetting('Large Box Count',min_value=1,default=2, increment=1),
            ba.IntChoiceSetting('Time Limit', choices=[('None', 0),('1 Minute', 60),('2 Minutes', 120),('5 Minutes', 300),('10 Minutes', 600),('20 Minutes', 1200)],default=0),
            ba.FloatChoiceSetting('Respawn Times',choices=[('Shorter', 0.25),('Short', 0.5),('Normal', 1.0),('Long', 2.0),('Longer', 4.0)], default=1.0),
            ba.BoolSetting('Epic Mode', default=False)
            ]
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
              or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Football Stadium']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.co = int(settings["Small Box Count"])
        self.c2 = int(settings["Large Box Count"])
        self._scoreboard = Scoreboard()
        self._score_to_win: Optional[int] = None
        self._dingsound = ba.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self.boxes_to_win = int(settings['Points to win per Player'])
        self._time_limit = float(settings['Time Limit'])
        self.region: List[ba.NodeActor] = []
        self.block_box_mat = ba.Material()
        self.block_box_mat.add_actions(conditions=('they_have_material', BombFactory.get().bomb_material),
                                       actions=(('modify_part_collision', 'collide', True),
                                               ('modify_part_collision', 'physical', True)))

        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.FORWARD_MARCH)

    def _setup_standard_tnt_drops(self) -> None:
        pass

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Blow up boxes and score ${ARG1} points to win!', self.boxes_to_win

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        for i in range(self.co):
          Box().autoretain()
        for a in range(self.c2):
          Box(box_type='large').autoretain()
        self.setup_standard_powerup_drops()
        b = self.map.defs.boxes['map_bounds']
        self.region.append(ba.NodeActor(ba.newnode('region', attrs={'position':(b[0], b[1]+10, b[2]), 'type':'box', 'scale': (b[6], 1.0, b[8]), 'materials': [self.block_box_mat]})))

        self._score_to_win = (self.boxes_to_win *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            self.respawn_player(player)
        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)
            if team.score >= self._score_to_win: ba.timer(500*0.001, self.end_game)

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)