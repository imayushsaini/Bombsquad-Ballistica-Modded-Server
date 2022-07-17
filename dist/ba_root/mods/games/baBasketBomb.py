# Released under the MIT License. See LICENSE for details.
# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba, _ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.gameutils import SharedObjects
from bastd.actor import playerspaz as ps
from bastd import maps

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union

bsuSpaz = None

def getlanguage(text, sub: str = ''):
    lang = _ba.app.lang.language
    translate = {
         "Name":
              {"Spanish": "Baloncesto",
               "English": "Basketbomb",
               "Portuguese": "Basketbomb"},
         "Info":
              {"Spanish": "Anota todas las canastas y sé el MVP.",
               "English": "Score all the baskets and be the MVP.",
               "Portuguese": "Marque cada cesta e seja o MVP."},
         "Info-Short":
            {"Spanish": f"Anota {sub} canasta(s) para ganar",
             "English": f"Score {sub} baskets to win",
             "Portuguese": f"Cestas de {sub} pontos para ganhar"},
         "S: Powerups":
              {"Spanish": "Aparecer Potenciadores",
               "English": "Powerups Spawn",
               "Portuguese": "Habilitar Potenciadores"},
         "S: Velocity":
            {"Spanish": "Activar velocidad",
             "English": "Enable speed",
             "Portuguese": "Ativar velocidade"},
         }
                
    languages = ['Spanish','Portuguese','English']
    if lang not in languages: lang = 'English'

    if text not in translate:
        return text
    return translate[text][lang]

class BallDiedMessage:
    def __init__(self, ball: Ball):
        self.ball = ball

class Ball(ba.Actor):
    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()
        velocty = (0.0, 8.0, 0.0)
        _scale = 1.2
        
        self._spawn_pos = (position[0], position[1] + 0.5, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False

        assert activity is not None
        assert isinstance(activity, BasketGame)
        
        pmats = [shared.object_material, activity.ball_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': activity.ball_model,
                                   'color_texture': activity.ball_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'body_scale': 1.0 * _scale,
                                   'reflection_scale': [1.3],
                                   'shadow_size': 1.0,
                                   'gravity_scale': 0.92,
                                   'density': max(0.4 * _scale, 0.3),
                                   'position': self._spawn_pos,
                                   'velocity': velocty,
                                   'materials': pmats})
        self.scale = scale = 0.25 * _scale
        ba.animate(self.node, 'model_scale', {0: 0, 0.2: scale*1.3, 0.26: scale})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(BallDiedMessage(self))

        elif isinstance(msg, ba.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos
            self.node.velocity = (0.0, 0.0, 0.0)

        elif isinstance(msg, ba.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = self._activity()
                if activity:
                    if s_player in activity.players:
                        self.last_players_to_touch[s_player.team.id] = s_player
        else:
            super().handlemessage(msg)


class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0

class Points:
    postes = dict()
    postes['pal_0'] = (10.64702320098877, 0.0000000000000000, 0.0000000000000000) #10.736066818237305, 0.3002409040927887, 0.5281256437301636
    postes['pal_1'] = (-10.64702320098877, 0.0000000000000000, 0.0000000000000000)

# ba_meta export game
class BasketGame(ba.TeamGameActivity[Player, Team]):
   
    name = getlanguage('Name')
    description = getlanguage('Info')
    available_settings = [
        ba.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
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
        ba.BoolSetting(getlanguage('S: Powerups'), default=True),
        ba.BoolSetting(getlanguage('S: Velocity'), default=False),
        ba.BoolSetting('Epic Mode', default=False),
    ]
    default_music = ba.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['BasketBall Stadium', 'BasketBall Stadium V2']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = ba.getsound('cheer')
        self._chant_sound = ba.getsound('crowdChant')
        self._foghorn_sound = ba.getsound('foghorn')
        self._swipsound = ba.getsound('swip')
        self._whistle_sound = ba.getsound('refWhistle')
        self.ball_model = ba.getmodel('shield')
        self.ball_tex = ba.gettexture('fontExtras3')
        self._ball_sound = ba.getsound('bunnyJump')
        self._powerups = bool(settings[getlanguage('S: Powerups')])
        self._speed = bool(settings[getlanguage('S: Velocity')])
        self._epic_mode = bool(settings['Epic Mode'])
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
                                                self._ball_sound, 0.2, 5))

        # Keep track of which player last touched the ball
        self.ball_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect',
                      self._handle_ball_player_collide), ))

        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.ball_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self._ball_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
        self._ball: Optional[Ball] = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

    def get_instance_description(self) -> Union[str, Sequence]:
        return getlanguage('Info-Short', sub=self._score_to_win)

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return getlanguage('Info-Short', sub=self._score_to_win)

    def on_begin(self) -> None:
        super().on_begin()

        self.setup_standard_time_limit(self._time_limit)
        
        if self._powerups:
            self.setup_standard_powerup_drops()
            
        self._ball_spawn_pos = self.map.get_flag_position(None)
        self._spawn_ball()

        defs = self.map.defs
        self._score_regions = []
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': defs.boxes['goal1'][0:3],
                               'scale': defs.boxes['goal1'][6:9],
                               'type': 'box',
                               'materials': []
                           })))
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': defs.boxes['goal2'][0:3],
                               'scale': defs.boxes['goal2'][6:9],
                               'type': 'box',
                               'materials': []
                           })))
        self._update_scoreboard()
        ba.playsound(self._chant_sound)

        for id, team in enumerate(self.teams):
            self.postes(id)

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

    def _handle_score(self, team_index: int = None) -> None:
        assert self._ball is not None
        assert self._score_regions is not None

        if self._ball.scored:
            return

        region = ba.getcollision().sourcenode
        index = 0
        for index in range(len(self._score_regions)):
            if region == self._score_regions[index].node:
                break

        if team_index is not None:
            index = team_index

        for team in self.teams:
            if team.id == index:
                scoring_team = team
                team.score += 1

                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(ba.CelebrateMessage(2.0))

                if (scoring_team.id in self._ball.last_players_to_touch
                        and self._ball.last_players_to_touch[scoring_team.id]):
                    self.stats.player_scored(
                        self._ball.last_players_to_touch[scoring_team.id],
                        100, big_message=True)

                if team.score >= self._score_to_win:
                    self.end_game()

        #ba.playsound(self._foghorn_sound)
        ba.playsound(self._cheer_sound)

        self._ball.scored = True

        # Kill the ball (it'll respawn itself shortly).
        ba.timer(1.0, self._kill_ball)

        light = ba.newnode('light',
                           attrs={
                               'position': ba.getcollision().position,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        ba.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
        ba.timer(1.0, light.delete)

        ba.cameraflash(duration=10.0)
        self._update_scoreboard()

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)

    def _update_scoreboard(self) -> None:
        winscore = self._score_to_win
        for id, team in enumerate(self.teams):
            self._scoreboard.set_team_value(team, team.score, winscore)
            #self.postes(id)
            
    def spawn_player(self, player: Player) -> ba.Actor:
        if bsuSpaz is None:
            spaz = self.spawn_player_spaz(player)
        else:
            ps.PlayerSpaz = bsuSpaz.BskSpaz
            spaz = self.spawn_player_spaz(player)
            ps.PlayerSpaz = bsuSpaz.OldPlayerSpaz
        
        if self._speed:
            spaz.node.hockey = True
        return spaz

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))
        elif isinstance(msg, BallDiedMessage):
            if not self.has_ended():
                ba.timer(3.0, self._spawn_ball)
        else:
            super().handlemessage(msg)

    def postes(self, team_id: int):
        if not hasattr(self._map, 'poste_'+str(team_id)):
            setattr(self._map, 'poste_'+str(team_id),
                Palos(team=team_id,
                      position=Points.postes['pal_' +
                      str(team_id)]).autoretain())

    def _flash_ball_spawn(self) -> None:
        light = ba.newnode('light',
                           attrs={
                               'position': self._ball_spawn_pos,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        ba.animate(light, 'intensity', {0.0: 0, 0.25: 1, 0.5: 0}, loop=True)
        ba.timer(1.0, light.delete)

    def _spawn_ball(self) -> None:
        ba.playsound(self._swipsound)
        ba.playsound(self._whistle_sound)
        self._flash_ball_spawn()
        assert self._ball_spawn_pos is not None
        self._ball = Ball(position=self._ball_spawn_pos)

class Aro(ba.Actor):
    def __init__(self, team: int = 0,
                 position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        act = self.getactivity()
        shared = SharedObjects.get()
        setattr(self, 'team', team)
        setattr(self, 'locs', [])
        
        # Material Para; Traspasar Objetos
        self.no_collision = ba.Material()
        self.no_collision.add_actions(
            actions=(('modify_part_collision', 'collide', False)))

        self.collision = ba.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        # Score
        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', act.ball_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._annotation)))

        self._spawn_pos = (position[0], position[1], position[2])
        self._materials_region0 = [self.collision,
                                   shared.footing_material]
        
        model = None
        tex = ba.gettexture('null')
        
        pmats = [self.no_collision]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': model,
                                   'color_texture': tex,
                                   'body': 'box',
                                   'reflection': 'soft',
                                   'reflection_scale': [1.5],
                                   'shadow_size': 0.1,
                                   'position': self._spawn_pos,
                                   'materials': pmats})
                               
        self.scale = scale = 1.4
        ba.animate(self.node, 'model_scale', {0:  0})

        pos = (position[0], position[1]+0.6, position[2])
        self.regions: List[ba.Node] = [
            ba.newnode('region',
                attrs={'position': position,
                       'scale': (0.6, 0.05, 0.6),
                       'type': 'box',
                       'materials': self._materials_region0}),
                       
            ba.newnode('region',
                attrs={'position': pos,
                       'scale': (0.5, 0.3, 0.9),
                       'type': 'box',
                       'materials': [self._score_region_material]})
            ]
        self.regions[0].connectattr('position', self.node, 'position')
        #self.regions[0].connectattr('position', self.regions[1], 'position')

        locs_count = 9
        pos = list(position)
        
        try:
            id = 0 if team == 1 else 1
            color = act.teams[id].color
        except: color = (1,1,1)
        
        while locs_count > 1:
            scale = (1.5 * 0.1 * locs_count) + 0.8

            self.locs.append(ba.newnode('locator',
                owner=self.node,
                attrs={'shape': 'circleOutline',
                       'position': pos,
                       'color': color,
                       'opacity': 1.0,
                       'size': [scale],
                       'draw_beauty': True,
                       'additive': False}))
            
            pos[1] -= 0.1
            locs_count -= 1
        
    def _annotation(self):
        assert len(self.regions) >= 2
        ball = self.getactivity()._ball
        
        if ball:
            p = self.regions[0].position
            ball.node.position = p
            ball.node.velocity = (0.0, 0.0, 0.0)

        act = self.getactivity()
        act._handle_score(self.team)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            if self.node.exists():
                self.node.delete()
        else:
            super().handlemessage(msg)

class Cuadro(ba.Actor):
    def __init__(self, team: int = 0,
                 position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        act = self.getactivity()
        shared = SharedObjects.get()
        setattr(self, 'locs', [])

        self.collision = ba.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        pos = (position[0], position[1]+0.9, position[2]+1.5)
        self.region: ba.Node =  ba.newnode('region',
                attrs={'position': pos,
                       'scale': (0.5, 2.7, 2.5),
                       'type': 'box',
                       'materials': [self.collision,
                                     shared.footing_material]})
        
        #self.shield = ba.newnode('shield', attrs={'radius': 1.0, 'color': (0,10,0)})
        #self.region.connectattr('position', self.shield, 'position')

        position = (position[0], position[1], position[2]+0.09)
        pos = list(position)
        oldpos = list(position)
        old_count = 14
        
        count = old_count
        count_y = 9

        try:
            id = 0 if team == 1 else 1
            color = act.teams[id].color
        except: color = (1,1,1)

        while(count_y != 1):

            while(count != 1):
                pos[2] += 0.19
                
                self.locs.append(
                    ba.newnode('locator',
                        owner=self.region,
                        attrs={'shape': 'circle',
                               'position': pos,
                               'size': [0.5],
                               'color': color,
                               'opacity': 1.0,
                               'draw_beauty': True,
                               'additive': False}))
                count -= 1

            
            count = old_count
            pos[1] += 0.2
            pos[2] = oldpos[2]
            count_y -= 1
        
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            if self.node.exists():
                self.node.delete()
        else:
            super().handlemessage(msg)

class Palos(ba.Actor):
    def __init__(self, team: int = 0,
                 position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()
        self._pos = position
        self.aro = None
        self.cua = None

        # Material Para; Traspasar Objetos
        self.no_collision = ba.Material()
        self.no_collision.add_actions(
            actions=(('modify_part_collision', 'collide', False)))

        # 
        self.collision = ba.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[2]+2.5, position[2])
        
        model = ba.getmodel('flagPole')
        tex = ba.gettexture('flagPoleColor')
        
        pmats = [self.no_collision]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': model,
                                   'color_texture': tex,
                                   'body': 'puck',
                                   'reflection': 'soft',
                                   'reflection_scale': [2.6],
                                   'shadow_size': 0,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        self.scale = scale = 4.0
        ba.animate(self.node, 'model_scale', {0:  scale})

        self.loc = ba.newnode('locator',
            owner=self.node,
            attrs={'shape': 'circle',
                   'position': position,
                   'color': (1,1,0),
                   'opacity': 1.0,
                   'draw_beauty': False,
                   'additive': True})

        self._y = _y = 0.30
        _x = -0.25 if team == 1 else 0.25
        _pos = (position[0]+_x, position[1]-1.5 + _y, position[2])
        self.region = ba.newnode('region',
                           attrs={
                               'position': _pos,
                               'scale': (0.4, 8, 0.4),
                               'type': 'box',
                               'materials': [self.collision]})
        self.region.connectattr('position', self.node, 'position')

        _y = self._y
        position = self._pos
        if team == 0:
            pos = (position[0]-0.8, position[1] + 2.0 + _y, position[2])
        else: pos = (position[0]+0.8, position[1] + 2.0 + _y, position[2])
        
        if self.aro is None:
            self.aro = Aro(team, pos).autoretain()
            
        if self.cua is None:
            pos = (position[0], position[1] + 1.8 + _y, position[2]-1.4)
            self.cua = Cuadro(team, pos).autoretain()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            if self.node.exists():
                self.node.delete()
        else:
            super().handlemessage(msg)        
