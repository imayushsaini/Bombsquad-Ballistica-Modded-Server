# Released under the MIT License. See LICENSE for details.

"""Egg game and support classes."""
#  The Egg Game - throw egg as far as you can
#  created in BCS (Bombsquad Consultancy Service) - opensource bombsquad mods for all 
#  discord.gg/ucyaesh    join now and give your contribution 
#  The Egg game by mr.smoothy
# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.gameutils import SharedObjects
from bastd.actor.flag import Flag
import math
import random
if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class PuckDiedMessage:
    """Inform something that a puck has died."""

    def __init__(self, puck: Puck):
        self.puck = puck


class Puck(ba.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch =None
        self.scored = False
        self.egg_model = ba.getmodel('egg')
        self.egg_tex_1 = ba.gettexture('eggTex1')
        self.egg_tex_2 = ba.gettexture('eggTex2')
        self.egg_tex_3 = ba.gettexture('eggTex3')
        self.eggtx=[self.egg_tex_1,self.egg_tex_2,self.egg_tex_3]
        regg=random.randrange(0,3)
        assert activity is not None
        assert isinstance(activity, EggGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': self.egg_model,
                                   'color_texture': self.eggtx[regg],
                                   'body': 'capsule',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.5,
                                   'body_scale':0.7,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        ba.animate(self.node, 'model_scale', {0: 0, 0.2: 0.7, 0.26: 0.6})

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
                        self.last_players_to_touch = s_player
        else:
            super().handlemessage(msg)


class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class EggGame(ba.TeamGameActivity[Player, Team]):
    """Egg game."""

    name = 'Epic Egg Game'
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
                ('40 Seconds', 40),
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
        return ba.getmaps('football')

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
        self._fake_wall_material=ba.Material()
        self.HIGHEST=0
        self._fake_wall_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
                
            ))
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
        # self.puck_material.add_actions(conditions=('they_have_material',
        #                                            shared.footing_material),
        #                                actions=('impact_sound',
        #                                         self._puck_sound, 0.2, 5))

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
        # self.puck_material.add_actions(
        #     conditions=('they_have_material',shared.footing_material)
        #     actions=(('modify_part_collision', 'collide',
        #               True), ('modify_part_collision', 'physical', True),
        #              ('call', 'at_connect', self._handle_egg_collision))
        # )
        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self.main_ground_material= ba.Material()
        
        self.main_ground_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_egg_collision)))

        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._pucks=[]
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

    def get_instance_description(self) -> Union[str, Sequence]:
        return "Throw Egg as far u can"

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return "Throw Egg as far u can"

    def on_begin(self) -> None:
        super().on_begin()
        if self._time_limit==0.0:
            self._time_limit=60
        self.setup_standard_time_limit(self._time_limit)
        # self.setup_standard_powerup_drops()
        self._puck_spawn_pos = self.map.get_flag_position(None)
        self._spawn_puck()
        self._spawn_puck()
        self._spawn_puck()
        self._spawn_puck()
        self._spawn_puck()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions = []
        pos=(11.88630542755127, 0.3009839951992035, 1.33331298828125)
        # mat=ba.Material()
        # mat.add_actions(
            
        #     actions=( ('modify_part_collision','physical',True),
        #               ('modify_part_collision','collide',True))
        #     )
        # self._score_regions.append(
        #     ba.NodeActor(
        #         ba.newnode('region',
        #                    attrs={
        #                        'position': pos,
        #                        'scale': (2,3,5),
        #                        'type': 'box',
        #                        'materials': [self._score_region_material]
        #                    })))
        # pos=(-11.88630542755127, 0.3009839951992035, 1.33331298828125)
        # self._score_regions.append(
        #     ba.NodeActor(
        #         ba.newnode('region',
        #                    attrs={
        #                        'position': pos,
        #                        'scale': (2,3,5),
        #                        'type': 'box',
        #                        'materials': [self._score_region_material]
        #                    })))
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': (-9.21,defs.boxes['goal2'][0:3][1],defs.boxes['goal2'][0:3][2]),
                               'scale': defs.boxes['goal2'][6:9],
                               'type': 'box',
                               'materials': (self._fake_wall_material, )
                           })))
        pos=(0,0.1,-5)
        self.main_ground=ba.newnode('region',attrs={'position': pos,'scale': (25,0.001,22),'type': 'box','materials': [self.main_ground_material]})
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

        puck.last_players_to_touch = player

    def _kill_puck(self) -> None:
        self._puck = None
    def _handle_egg_collision(self) -> None:

        no=ba.getcollision().opposingnode
        pos=no.position
        egg=no.getdelegate(Puck)
        source_player=egg.last_players_to_touch
        if source_player==None or pos[0]< -8 or not source_player.node.exists() :
            return


        try:
            col=source_player.team.color
            self.flagg=Flag(pos,touchable=False,color=col).autoretain()
            self.flagg.is_area_of_interest=True
            player_pos=source_player.node.position
            
            distance = math.sqrt( pow(player_pos[0]-pos[0],2) + pow(player_pos[2]-pos[2],2))
            
            
            dis_mark=ba.newnode('text',
                                    
                                    attrs={
                                        'text':str(round(distance,2))+"m",
                                        'in_world':True,
                                        'scale':0.02,
                                        'h_align':'center',
                                        'position':(pos[0],1.6,pos[2]),
                                        'color':col
                                    })
            ba.animate(dis_mark,'scale',{
                0.0:0, 0.5:0.01
            })
            if distance > self.HIGHEST:
                self.HIGHEST=distance
                self.stats.player_scored(
                        source_player,
                        10,
                        big_message=False)
            
            no.delete()
            ba.timer(2,self._spawn_puck)
            source_player.team.score=int(distance) 
            
        except():
            pass
    def spawn_player(self, player: Player) -> ba.Actor:
        
        
        zoo=random.randrange(-4,5)
        pos=(-11.204887390136719, 0.2998693287372589, zoo)
        spaz = self.spawn_player_spaz(
            player, position=pos, angle=90 )
        assert spaz.node

        # Prevent controlling of characters before the start of the race.
               
        return spaz
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

        # self._puck.scored = True

        # Change puck texture to something cool
        # self._puck.node.color_texture = self.puck_scored_tex
        # Kill the puck (it'll respawn itself shortly).
        ba.timer(1.0, self._kill_puck)

        # light = ba.newnode('light',
        #                    attrs={
        #                        'position': ba.getcollision().position,
        #                        'height_attenuated': False,
        #                        'color': (1, 0, 0)
        #                    })
        # ba.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
        # ba.timer(1.0, light.delete)

        ba.cameraflash(duration=10.0)
        self._update_scoreboard()

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)

    def _update_scoreboard(self) -> None:
        winscore = self._score_to_win
        # for team in self.teams:
        #     self._scoreboard.set_team_value(team, team.score, winscore)

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
        # light = ba.newnode('light',
        #                    attrs={
        #                        'position': self._puck_spawn_pos,
        #                        'height_attenuated': False,
        #                        'color': (1, 0, 0)
        #                    })
        # ba.animate(light, 'intensity', {0.0: 0, 0.25: 1, 0.5: 0}, loop=True)
        # ba.timer(1.0, light.delete)
        pass
    def _spawn_puck(self) -> None:
        # ba.playsound(self._swipsound)
        # ba.playsound(self._whistle_sound)
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        zoo=random.randrange(-5,6)
        pos=(-11.204887390136719, 0.2998693287372589, zoo)
        self._pucks.append (Puck(position=pos))
