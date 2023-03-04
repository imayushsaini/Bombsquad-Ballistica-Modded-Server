# Released under the MIT License. See LICENSE for details.
# BY Stary_Agent
"""Hockey game and support classes."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba,_ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class PuckDiedMessage:
    """Inform something that a puck has died."""

    def __init__(self, puck: Puck):
        self.puck = puck

def create_slope(self):
        shared = SharedObjects.get()
        x=5
        y=12
        for i in range(0,10):
            ba.newnode('region',attrs={'position': (x, y, -5.52),'scale': (0.2,0.1,6),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
            x= x+0.3
            y=y+0.1

class Puck(ba.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 13.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, HockeyGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': activity.puck_model,
                                   'color_texture': activity.puck_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'gravity_scale':0.3,
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        ba.animate(self.node, 'model_scale', {0: 0, 0.2: 1.3, 0.26: 1})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, ba.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

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
        else:
            super().handlemessage(msg)


class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class AirSoccerGame(ba.TeamGameActivity[Player, Team]):
    """Ice hockey game."""

    name = 'Epic Air Soccer'
    description = 'Score some goals.'
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
                ('Shorter', 0.1),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
            default=1.0,
        ),
    ]
    default_music = ba.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Creative Thoughts']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self.slow_motion = True
        self._scoreboard = Scoreboard()
        self._cheer_sound = ba.getsound('cheer')
        self._chant_sound = ba.getsound('crowdChant')
        self._foghorn_sound = ba.getsound('foghorn')
        self._swipsound = ba.getsound('swip')
        self._whistle_sound = ba.getsound('refWhistle')
        self.puck_model = ba.getmodel('bomb')
        self.puck_tex = ba.gettexture('landMine')
        self.puck_scored_tex = ba.gettexture('landMineLit')
        self._puck_sound = ba.getsound('metalHit')
        self.puck_material = ba.Material()
        self.puck_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 0.5)))
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', True))
        self.puck_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.footing_material),
                                       actions=('impact_sound',
                                                self._puck_sound, 0.2, 5))
        self._real_wall_material=ba.Material()
        self._real_wall_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))

        self._real_wall_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))
        self._goal_post_material=ba.Material()
        self._goal_post_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))

        self._goal_post_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)

            ))
        # Keep track of which player last touched the puck
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect',
                      self._handle_puck_player_collide), ))

        # We want the puck to kill powerups; not get stopped by them
        self.puck_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', ba.DieMessage())))
        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

    def get_instance_description(self) -> Union[str, Sequence]:
        if self._score_to_win == 1:
            return 'Score a goal.'
        return 'Score ${ARG1} goals.', self._score_to_win

    def get_instance_description_short(self) -> Union[str, Sequence]:
        if self._score_to_win == 1:
            return 'score a goal'
        return 'score ${ARG1} goals', self._score_to_win

    def on_begin(self) -> None:
        super().on_begin()

        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()
        self._puck_spawn_pos =(0,16.9,-5.5)
        self._spawn_puck()
        self.make_map()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions = []
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': (17,14.5,-5.52),
                               'scale': (1,3,1),
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': (-17,14.5,-5.52),
                               'scale': (1,3,1),
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._update_scoreboard()
        ba.playsound(self._chant_sound)

    def on_team_join(self, team: Team) -> None:
        self._update_scoreboard()

    def _handle_puck_player_collide(self) -> None:
        collision = ba.getcollision()
        try:
            puck = collision.sourcenode.getdelegate(Puck, True)
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(
                                                            Player, True)
        except ba.NotFoundError:
            return

        puck.last_players_to_touch[player.team.id] = player

    def make_map(self):
        shared = SharedObjects.get()
        _ba.get_foreground_host_activity()._map.leftwall.materials= [shared.footing_material,self._real_wall_material ]
        
        _ba.get_foreground_host_activity()._map.rightwall.materials=[shared.footing_material,self._real_wall_material ]
        
        _ba.get_foreground_host_activity()._map.topwall.materials=[shared.footing_material,self._real_wall_material ]
        floor=""
        for i in range(0,90):
            floor+="_ "
        # self.floorwall=ba.newnode('region',attrs={'position': (-18.65152479, 4.057427485, -5.52),'scale': (72,2,6),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        self.floorwall=ba.newnode('region',attrs={'position': (0, 5, -5.52),'scale': (35.4,0.2,2),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        ba.newnode('locator', attrs={'shape':'box', 'position':(0, 5, -5.52), 'color':(0,0,0), 'opacity':1,'draw_beauty':True,'additive':False,'size':(35.4,0.2,2)})
        
        # self.floor_text = ba.newnode('text',
        #                        attrs={
        #                            'text': floor,
        #                            'in_world': True,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'center',
        #                            'position':(0,5.2,-5)
        #                        })
        self.create_goal_post(-16.65,12.69)
        self.create_goal_post(-16.65,16.69)
        
        self.create_goal_post(16.65,12.69)
        self.create_goal_post(16.65,16.69)
       
        self.create_static_step(0,16.29)

        self.create_static_step(4.35,11.1)
        self.create_static_step(-4.35,11.1)

        self.create_vertical(10, 15.6)
        self.create_vertical(-10, 15.6)
    
    def create_static_step(self,x,y):
        floor=""
        for i in range(0,7):
            floor+="_ "
        shared = SharedObjects.get()
        step={}
        step["r"]=ba.newnode('region',attrs={'position': (x, y, -5.52),'scale': (3,0.1,6),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        ba.newnode('locator', attrs={'shape':'box', 'position':( x, y,  -5.52), 'color':(1,1,0), 'opacity':1,'draw_beauty':True,'additive':False,'size':(3,0.1,2)})
        
        # step["t"]=ba.newnode('text',
        #                        attrs={
        #                            'text': floor,
        #                            'in_world': True,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'left',
        #                            'position':(x-1.2,y,-5.52)
        #                        })
        return step
    def create_goal_post(self,x,y):
        shared = SharedObjects.get()
        if x > 0:
            color = (1,0,0) #change to team specific color  
        else:
            color = (0,0,1)
        floor=""
        for i in range(0,4):
            floor+="_ "
        ba.newnode('region',attrs={'position': (x-0.2, y, -5.52),'scale': (1.8,0.1,6),'type': 'box','materials': [shared.footing_material,self._goal_post_material]})
        
        ba.newnode('locator', attrs={'shape':'box', 'position':( x-0.2, y,  -5.52), 'color': color, 'opacity':1,'draw_beauty':True,'additive':False,'size':(1.8,0.1,2)})
        # ba.newnode('text',
        #                        attrs={
        #                            'text': floor,
        #                            'in_world': True,
        #                            'color': color,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'left',
        #                            'position':(x-1.2,y,-5.52)
        #                        })

    def create_vertical(self,x,y):
        shared = SharedObjects.get()
        floor = ""
        for i in range(0,4):
            floor +="|\n"
        ba.newnode('region',attrs={'position': (x, y, -5.52),'scale': (0.1,2.8,1),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        ba.newnode('locator', attrs={'shape':'box', 'position':( x, y,  -5.52), 'color':(1,1,0), 'opacity':1,'draw_beauty':True,'additive':False,'size':(0.1,2.8,2)})
        
        # ba.newnode('text',
        #                        attrs={
        #                            'text': floor,
        #                            'in_world': True,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'left',
        #                            'position':(x,y+1,-5.52)
        #                        })

    def spawn_player_spaz(self,
                          player: Player,
                          position: Sequence[float] = None,
                          angle: float = None) -> PlayerSpaz:
        """Intercept new spazzes and add our team material for them."""
        if player.team.id==0:
            position=(-10.75152479, 5.057427485, -5.52)
        elif player.team.id==1:
            position=(8.75152479, 5.057427485, -5.52)


        spaz = super().spawn_player_spaz(player, position, angle)
        return spaz

    def _kill_puck(self) -> None:
        self._puck = None

    def _handle_score(self) -> None:
        """A point has been scored."""

        assert self._puck is not None
        assert self._score_regions is not None

        # Our puck might stick around for a second or two
        # we don't want it to be able to score again.
        if self._puck.scored:
            return

        region = ba.getcollision().sourcenode
        index = 0
        for index in range(len(self._score_regions)):
            if region == self._score_regions[index].node:
                break

        for team in self.teams:
            if team.id == index:
                scoring_team = team
                team.score += 1

                # Tell all players to celebrate.
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(ba.CelebrateMessage(2.0))

                # If we've got the player from the scoring team that last
                # touched us, give them points.
                if (scoring_team.id in self._puck.last_players_to_touch
                        and self._puck.last_players_to_touch[scoring_team.id]):
                    self.stats.player_scored(
                        self._puck.last_players_to_touch[scoring_team.id],
                        20,
                        big_message=True)

                # End game if we won.
                if team.score >= self._score_to_win:
                    self.end_game()

        ba.playsound(self._foghorn_sound)
        ba.playsound(self._cheer_sound)

        self._puck.scored = True

        # Change puck texture to something cool
        self._puck.node.color_texture = self.puck_scored_tex
        # Kill the puck (it'll respawn itself shortly).
        ba.timer(1.0, self._kill_puck)

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
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score, winscore)

    def handlemessage(self, msg: Any) -> Any:

        # Respawn dead players if they're still in the game.
        if isinstance(msg, ba.PlayerDiedMessage):
            # Augment standard behavior... 
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))

        # Respawn dead pucks.
        elif isinstance(msg, PuckDiedMessage):
            if not self.has_ended():
                ba.timer(3.0, self._spawn_puck)
        else:
            super().handlemessage(msg)

    def _flash_puck_spawn(self) -> None:
        light = ba.newnode('light',
                           attrs={
                               'position': self._puck_spawn_pos,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        ba.animate(light, 'intensity', {0.0: 0, 0.25: 1, 0.5: 0}, loop=True)
        ba.timer(1.0, light.delete)

    def _spawn_puck(self) -> None:
        ba.playsound(self._swipsound)
        ba.playsound(self._whistle_sound)
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)
