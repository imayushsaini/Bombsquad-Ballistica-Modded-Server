from __future__ import annotations

#Volley Ball (updated)
#Made for 1.6 by your friend: @[Just] Freak#4999

"""Defines Volley Ball mini-game"""




## This thing was originally made for 1.4 by someone (but had errors/bugs/missing features) so I edited/ported to 1.6/added all useful features :D
## I suggest to join this discord servers:
## https://discord.gg/ucyaesh
## https://discord.gg/NCvfPG2N9A


## Made on Android with the help of Terminal.py
## https://github.com/FreakOPP/BombSquad-Mods-byFREAK/blob/main/Utilities/Terminal.py


## MY (Freak's) comments are double-tagged btw ##

## UPDATED:
"""
- Fixed Puck's mass/size/positions/texture/effects
- Fixed Goal positions
- Better center wall
- Added 1 more map
- Added more customisable options
- Map lights locators are now looped (thus reducing the size of the file and lengthy work...)
- Merged map & minigame in one file
- Puck spawns according to scored team (if right team scored, ball will spawn on left side)
- Also puck now spawns in airrr
- Server support added :)
- Fixed **LOTS** of errors/bugs
"""










# ba_meta require api 6

from typing import TYPE_CHECKING

import bastd, _ba, ba, random
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


class Puck(ba.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.8, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, VolleyBallGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': activity.puck_model,
                                   'color_texture': activity.puck_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.6,
                                   'model_scale': 0.4,
                                   'body_scale': 1.07,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        
        ## Since it rolls on spawn, lets make gravity
        ## to 0, and when another node (bomb/spaz)
        ## touches it. It'll act back as our normie puck!
        ba.animate(self.node, 'gravity_scale', {0:-0.1, 2:1}, False)
        ## When other node touches, it realises its new gravity_scale
        ## Jugad for now...
        
        


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
class VolleyBallGame(ba.TeamGameActivity[Player, Team]):
    """Volley Ball game."""

    name = 'Volley Ball'
    description = 'Score some goals.\nbyFREAK'
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
        ba.BoolSetting('Epic Mode', True),
        ba.BoolSetting('Night Mode', False),
        ba.BoolSetting('Icy Floor', True),
        ba.BoolSetting('Disable Punch', False),
        ba.BoolSetting('Disable Bombs', False),
        ba.BoolSetting('Enable Bottom Credits', True),
    ]
    default_music = ba.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Open Field','Closed Arena']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = ba.getsound('cheer')
        self._chant_sound = ba.getsound('crowdChant')
        self._foghorn_sound = ba.getsound('foghorn')
        self._swipsound = ba.getsound('swip')
        self._whistle_sound = ba.getsound('refWhistle')
        self.puck_model = ba.getmodel('shield')
        self.puck_tex = ba.gettexture('gameCircleIcon')
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
                    
                    
        self._wall_material=ba.Material()
        self._fake_wall_material=ba.Material()
        self._wall_material.add_actions(
            
            actions=(
                ('modify_part_collision', 'friction', 100000),
             ))
        self._wall_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=(
                ('modify_part_collision', 'collide', False),
            ))

        self._wall_material.add_actions(
            conditions=(('we_are_younger_than', 100),
            'and',
            ('they_have_material',shared.object_material)),
            actions=(
                ('modify_part_collision', 'collide', False),
            ))
        self._wall_material.add_actions(
            conditions=('they_have_material',shared.footing_material),
            actions=(
                ('modify_part_collision', 'friction', 9999.5),
            ))
        self._wall_material.add_actions(
            conditions=('they_have_material', bastd.actor.bomb.BombFactory.get().blast_material),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)
                
            ))
        self._fake_wall_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
                
            ))
        self.blocks=[]


        self._net_wall_material=ba.Material()
        self._net_wall_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
                
            ))

        self._net_wall_material.add_actions(
            conditions=('they_have_material', shared.object_material),
            actions=(
                ('modify_part_collision', 'collide', True),
            ))
        self._net_wall_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(
                ('modify_part_collision', 'collide', True),
            ))
        self._net_wall_material.add_actions(
            conditions=('we_are_older_than', 1),
            actions=(
                ('modify_part_collision', 'collide', True),
            ))
        self.net_blocc=[]


        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._score_to_win = int(settings['Score to Win'])
        self._punchie_ = bool(settings['Disable Punch'])
        self._night_mode = bool(settings['Night Mode'])
        self._bombies_ = bool(settings['Disable Bombs'])
        self._time_limit = float(settings['Time Limit'])
        self._icy_flooor = bool(settings['Icy Floor'])
        self.credit_text = bool(settings['Enable Bottom Credits'])
        self._epic_mode = bool(settings['Epic Mode'])
        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.TO_THE_DEATH)

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
        if self._night_mode:
            ba.getactivity().globalsnode.tint = (0.5, 0.7, 1)
        else:
            pass
        self._puck_spawn_pos = self.map.get_flag_position(None)
        self._spawn_puck()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions = []
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position':(5,0,0),
                               'scale': defs.boxes['goal1'],
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position':(-5,0,0),
                               'scale': defs.boxes['goal2'],
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._update_scoreboard()
        ba.playsound(self._chant_sound)
        import base64
        exec(base64.b64decode("aWYgc2VsZi5jcmVkaXRfdGV4dDoKICAgICMjIFBlb3BsZSBzdGVhbGVkIGNyZWRpdHMgc28gdGhhdHMgd2h5IEkgZW5jb2RlZCB0aGlzLi4uCiAgICAjIyBFdmVuIHRobyB0aGVyZSBpcyBhIG9wdGlvbiwgdGhleSBjaGFuZ2VkIGNyZWF0ZWQgYnkKICAgICMjIGxpa2Ugd3RmIGlzIHRoaWVyIHByb2JsZW0/PwogICAgCiAgICAjIyBBbnl3YXlzIGhhdmUgYSBnb29kIGRheSEKICAgIHQgPSBiYS5uZXdub2RlKCd0ZXh0JywKICAgICAgICAgICAgICAgYXR0cnM9eyAndGV4dCc6IkNyZWF0ZWQgYnkg7oGIRnJlYWt1XG5Wb2xsZXlCYWxsIDEuNiIsICMjIERpc2FibGUgJ0VuYWJsZSBCb3R0b20gQ3JlZGl0cycgd2hlbiBtYWtpbmcgcGxheWxpc3QsIE5vIG5lZWQgdG8gZWRpdCB0aGlzIGxvdmVseS4uLgogICAgICAgICdzY2FsZSc6MC43LAogICAgICAgICdwb3NpdGlvbic6KDAsMCksICNMZXRzIGhvcGUgaGUgdXNlcyBUViBib3JkZXIgb2Ygc2V0dGluZ3M+R3JhcGhpY3MKICAgICAgICAnc2hhZG93JzowLjUsCiAgICAgICAgJ2ZsYXRuZXNzJzoxLjIsCiAgICAgICAgJ2NvbG9yJzooMSwgMSwgMSksCiAgICAgICAgJ2hfYWxpZ24nOidjZW50ZXInLAogICAgICAgICd2X2F0dGFjaCc6J2JvdHRvbSd9KQ==").decode('UTF-8'))
        shared = SharedObjects.get()
        self.blocks.append(ba.NodeActor(ba.newnode('region',attrs={'position': (0,2.4,0),'scale': (1,6,20),'type': 'box','materials': (self._fake_wall_material, )})))
        
        self.net_blocc.append(ba.NodeActor(ba.newnode('region',attrs={'position': (0,0,0),'scale': (0.6,2.4,20),'type': 'box','materials': (self._net_wall_material, )})))

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



                ## Spawn puck on opponent's Area
                if team.id == 0: # left side scored
                    self._puck_spawn_pos= (5, -0.3, 0)
                elif team.id == 1: # right side scored
                    self._puck_spawn_pos= (-5, -0.3, 0)
                else: # incase, this dude is oversmart and using 3+ teams...
                    self._puck_spawn_pos= (0, 0.2, 0)
                ## Easy pizzy
                
                
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(ba.CelebrateMessage(2.0))

                # If we've got the player from the scoring team that last
                # touched us, give them points.
                if (scoring_team.id in self._puck.last_players_to_touch
                        and self._puck.last_players_to_touch[scoring_team.id]):
                    self.stats.player_scored(
                        self._puck.last_players_to_touch[scoring_team.id],
                        50,
                        big_message=True)

                # End game if we won.
                if team.score >= self._score_to_win:
                    self.end_game()

        ba.playsound(self._foghorn_sound)
        ba.playsound(self._cheer_sound)

        self._puck.scored = True

        # Kill the puck (it'll respawn itself shortly).
        ba.emitfx(position= ba.getcollision().position, count=int(6.0 + 7.0 * 12), scale=3, spread=0.5, chunk_type='spark')
        ba.timer(0.7, self._kill_puck)


        ba.cameraflash(duration=7.0)
        self._update_scoreboard()

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)

    def on_transition_in(self) -> None:
        super().on_transition_in()
        activity = ba.getactivity()
        if self._icy_flooor:
            activity.map.is_hockey = True
        else:
            return

    def _update_scoreboard(self) -> None:
        winscore = self._score_to_win
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score, winscore)

    # overriding the default character spawning..
    def spawn_player(self, player: Player) -> ba.Actor:
        spaz = self.spawn_player_spaz(player)

        if self._bombies_:
            ## We wantthe button to work, justno bombs...
            spaz.bomb_count = 0
            ## Imagine not being able to swipe those colorful buttons ;(


        if self._punchie_:
            spaz.connect_controls_to_player(enable_punch=False)

        return spaz

    def handlemessage(self, msg: Any) -> Any:

        # Respawn dead players if they're still in the game.
        if isinstance(msg, ba.PlayerDiedMessage):
            # Augment standard behavior...
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))

        # Respawn dead pucks.
        elif isinstance(msg, PuckDiedMessage):
            if not self.has_ended():
                ba.timer(2.2, self._spawn_puck)
        else:
            super().handlemessage(msg)

    def _flash_puck_spawn(self) -> None:
        ## Effect >>>>>> Flashly
        ba.emitfx(position= self._puck_spawn_pos, count=int(6.0 + 7.0 * 12), scale=1.7, spread=0.4, chunk_type='spark')

    def _spawn_puck(self) -> None:
        ba.playsound(self._swipsound)
        ba.playsound(self._whistle_sound)
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)

