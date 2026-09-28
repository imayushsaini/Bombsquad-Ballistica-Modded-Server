# Released under the MIT License. See LICENSE for details.
# BY Stary_Agent
"""Air soccer game."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class PuckDiedMessage:
    """Inform something that a puck has died."""

    def __init__(self, puck: Puck):
        self.puck = puck


def create_slope(self):
    shared = SharedObjects.get()
    x = 5
    y = 12
    for i in range(0, 10):
        bs.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (0.2, 0.1, 6),
                   'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        x = x+0.3
        y = y+0.1


class Puck(bs.Actor):
    """A lovely ball."""

    def __init__(self, position: Sequence[float] = (0.0, 13.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        pmats = [shared.object_material, activity.puck_material]
        self.node = bs.newnode('prop',
                               delegate=self,
                               attrs={
                                   'mesh': activity.puck_mesh,
                                   'color_texture': activity.puck_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'gravity_scale': 0.3,
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        bs.animate(self.node, 'mesh_scale', {0: 0, 0.2: 1.3, 0.26: 1})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, bs.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, bs.HitMessage):
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


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export bascenev1.GameActivity
class AirSoccerGame(bs.TeamGameActivity[Player, Team]):
    """Air soccer game."""

    name = 'Epic Air Soccer'
    description = 'Score some goals.'
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
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
                ('Shorter', 0.1),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
            default=1.0,
        ),
    ]
    default_music = bs.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return ['Creative Thoughts']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self.slow_motion = True
        self._scoreboard = Scoreboard()
        self._cheer_sound = bs.getsound('cheer')
        self._chant_sound = bs.getsound('crowdChant')
        self._foghorn_sound = bs.getsound('foghorn')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self.puck_mesh = bs.getmesh('bomb')
        self.puck_tex = bs.gettexture('landMine')
        self.puck_scored_tex = bs.gettexture('landMineLit')
        self._puck_sound = bs.getsound('metalHit')
        self.puck_material = bs.Material()
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
        self._real_wall_material = bs.Material()
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
        self._goal_post_material = bs.Material()
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
                     ('message', 'their_node', 'at_connect', bs.DieMessage())))
        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[bs.NodeActor]] = None
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
        self._puck_spawn_pos = (0, 16.9, -5.5)
        self._spawn_puck()
        self.make_map()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions = []
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode('region',
                           attrs={
                               'position': (17, 14.5, -5.52),
                               'scale': (1, 3, 1),
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode('region',
                           attrs={
                               'position': (-17, 14.5, -5.52),
                               'scale': (1, 3, 1),
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._update_scoreboard()
        self._chant_sound.play()

    def on_team_join(self, team: Team) -> None:
        self._update_scoreboard()

    def _handle_puck_player_collide(self) -> None:
        collision = bs.getcollision()
        try:
            puck = collision.sourcenode.getdelegate(Puck, True)
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(
                                                            Player, True)
        except bs.NotFoundError:
            return

        puck.last_players_to_touch[player.team.id] = player

    def make_map(self):
        shared = SharedObjects.get()
        bs.get_foreground_host_activity()._map.leftwall.materials = [
            shared.footing_material, self._real_wall_material]

        bs.get_foreground_host_activity()._map.rightwall.materials = [
            shared.footing_material, self._real_wall_material]

        bs.get_foreground_host_activity()._map.topwall.materials = [
            shared.footing_material, self._real_wall_material]
        self.floorwall = bs.newnode('region', attrs={'position': (0, 5, -5.52), 'scale': (
            35.4, 0.2, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        bs.newnode('locator', attrs={'shape': 'box', 'position': (
            0, 5, -5.52), 'color': (0, 0, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (35.4, 0.2, 2)})

        self.create_goal_post(-16.65, 12.69)
        self.create_goal_post(-16.65, 16.69)

        self.create_goal_post(16.65, 12.69)
        self.create_goal_post(16.65, 16.69)

        self.create_static_step(0, 16.29)

        self.create_static_step(4.35, 11.1)
        self.create_static_step(-4.35, 11.1)

        self.create_vertical(10, 15.6)
        self.create_vertical(-10, 15.6)

    def create_static_step(self, x, y):
        floor = ""
        for i in range(0, 7):
            floor += "_ "
        shared = SharedObjects.get()
        step = {}
        step["r"] = bs.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (
            3, 0.1, 6), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        bs.newnode('locator', attrs={'shape': 'box', 'position': (
            x, y,  -5.52), 'color': (1, 1, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (3, 0.1, 2)})

        return step

    def create_goal_post(self, x, y):
        shared = SharedObjects.get()
        if x > 0:
            color = (1, 0, 0)  # change to team specific color
        else:
            color = (0, 0, 1)
        floor = ""
        for i in range(0, 4):
            floor += "_ "
        bs.newnode('region', attrs={'position': (x-0.2, y, -5.52), 'scale': (1.8, 0.1, 6),
                   'type': 'box', 'materials': [shared.footing_material, self._goal_post_material]})

        bs.newnode('locator', attrs={'shape': 'box', 'position': (
            x-0.2, y,  -5.52), 'color': color, 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (1.8, 0.1, 2)})

    def create_vertical(self, x, y):
        shared = SharedObjects.get()
        floor = ""
        for i in range(0, 4):
            floor += "|\n"
        bs.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (0.1, 2.8, 1),
                   'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        bs.newnode('locator', attrs={'shape': 'box', 'position': (
            x, y,  -5.52), 'color': (1, 1, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (0.1, 2.8, 2)})

    def spawn_player_spaz(self,
                          player: Player,
                          position: Sequence[float] = None,
                          angle: float = None) -> PlayerSpaz:
        """Intercept new spazzes and add our team material for them."""
        if player.team.id == 0:
            position = (-10.75152479, 5.057427485, -5.52)
        elif player.team.id == 1:
            position = (8.75152479, 5.057427485, -5.52)

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

        region = bs.getcollision().sourcenode
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
                        player.actor.handlemessage(bs.CelebrateMessage(2.0))

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

        self._foghorn_sound.play()
        self._cheer_sound.play()

        self._puck.scored = True

        # Change puck texture to something cool
        self._puck.node.color_texture = self.puck_scored_tex
        # Kill the puck (it'll respawn itself shortly).
        bs.timer(1.0, self._kill_puck)

        light = bs.newnode('light',
                           attrs={
                               'position': bs.getcollision().position,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        bs.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
        bs.timer(1.0, light.delete)

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
            # Augment standard behavior...
            super().handlemessage(msg)
            self.respawn_player(msg.getplayer(Player))

        # Respawn dead pucks.
        elif isinstance(msg, PuckDiedMessage):
            if not self.has_ended():
                bs.timer(3.0, self._spawn_puck)
        else:
            super().handlemessage(msg)

    def _flash_puck_spawn(self) -> None:
        light = bs.newnode('light',
                           attrs={
                               'position': self._puck_spawn_pos,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        bs.animate(light, 'intensity', {0.0: 0, 0.25: 1, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)

    def _spawn_puck(self) -> None:
        self._swipsound.play()
        self._whistle_sound.play()
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)


class mapdefs:
    points = {}
    # noinspection PyDictCreation
    boxes = {}
    boxes['area_of_interest_bounds'] = (-1.045859963, 12.67722855,
                                        -5.401537075) + (0.0, 0.0, 0.0) + (
                                            42.46156851, 20.94044653, 0.6931564611)
    points['ffa_spawn1'] = (-9.295167711, 8.010664315,
                            -5.44451005) + (1.555840357, 1.453808816, 0.1165648888)
    points['ffa_spawn2'] = (7.484707127, 8.172681752, -5.614479365) + (
        1.553861796, 1.453808816, 0.04419853907)
    points['ffa_spawn3'] = (9.55724115, 11.30789446, -5.614479365) + (
        1.337925849, 1.453808816, 0.04419853907)
    points['ffa_spawn4'] = (-11.55747023, 10.99170684, -5.614479365) + (
        1.337925849, 1.453808816, 0.04419853907)
    points['ffa_spawn5'] = (-1.878892369, 9.46490571, -5.614479365) + (
        1.337925849, 1.453808816, 0.04419853907)
    points['ffa_spawn6'] = (-0.4912812943, 5.077006397, -5.521672101) + (
        1.878332089, 1.453808816, 0.007578097856)
    points['flag1'] = (-11.75152479, 8.057427485, -5.52)
    points['flag2'] = (9.840909039, 8.188634282, -5.52)
    points['flag3'] = (-0.2195258696, 5.010273907, -5.52)
    points['flag4'] = (-0.04605809154, 12.73369108, -5.52)
    points['flag_default'] = (-0.04201942896, 12.72374492, -5.52)
    boxes['map_bounds'] = (-0.8748348681, 9.212941713, -5.729538885) + (
        0.0, 0.0, 0.0) + (42.09666006, 26.19950145, 7.89541168)
    points['powerup_spawn1'] = (1.160232442, 6.745963662, -5.469115985)
    points['powerup_spawn2'] = (-1.899700206, 10.56447241, -5.505721177)
    points['powerup_spawn3'] = (10.56098871, 12.25165669, -5.576232453)
    points['powerup_spawn4'] = (-12.33530337, 12.25165669, -5.576232453)
    points['spawn1'] = (-9.295167711, 8.010664315,
                        -5.44451005) + (1.555840357, 1.453808816, 0.1165648888)
    points['spawn2'] = (7.484707127, 8.172681752,
                        -5.614479365) + (1.553861796, 1.453808816, 0.04419853907)
    points['spawn_by_flag1'] = (-9.295167711, 8.010664315, -5.44451005) + (
        1.555840357, 1.453808816, 0.1165648888)
    points['spawn_by_flag2'] = (7.484707127, 8.172681752, -5.614479365) + (
        1.553861796, 1.453808816, 0.04419853907)
    points['spawn_by_flag3'] = (-1.45994593, 5.038762459, -5.535288724) + (
        0.9516389866, 0.6666414677, 0.08607244075)
    points['spawn_by_flag4'] = (0.4932087091, 12.74493212, -5.598987003) + (
        0.5245740665, 0.5245740665, 0.01941146064)


class CreativeThoughts(bs.Map):
    """Freaking map by smoothy."""

    defs = mapdefs

    name = 'Creative Thoughts'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return [
            'melee', 'keep_away', 'team_flag'
        ]

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'alwaysLandPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'mesh': bs.getmesh('alwaysLandLevel'),
            'bottom_mesh': bs.getmesh('alwaysLandLevelBottom'),
            'bgmesh': bs.getmesh('alwaysLandBG'),
            'collision_mesh': bs.getcollisionmesh('alwaysLandLevelCollide'),
            'tex': bs.gettexture('alwaysLandLevelColor'),
            'bgtex': bs.gettexture('alwaysLandBGColor'),
            'vr_fill_mound_mesh': bs.getmesh('alwaysLandVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound')
        }
        return data

    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        return bs.MusicType.FLYING

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -3.7, 2.5))
        shared = SharedObjects.get()
        self._fake_wall_material = bs.Material()
        self._real_wall_material = bs.Material()
        self._fake_wall_material.add_actions(
            conditions=(('they_are_younger_than', 9000), 'and',
                        ('they_have_material', shared.player_material)),
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
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': bs.gettexture("rampageBGColor")
            })

        self.leftwall = bs.newnode('region', attrs={'position': (-17.75152479, 13, -5.52), 'scale': (
            0.1, 15.5, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        self.rightwall = bs.newnode('region', attrs={'position': (17.75, 13, -5.52), 'scale': (
            0.1, 15.5, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        self.topwall = bs.newnode('region', attrs={'position': (0, 21.0, -5.52), 'scale': (
            35.4, 0.2, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        bs.newnode('locator', attrs={'shape': 'box', 'position': (-17.75152479, 13, -5.52), 'color': (
            0, 0, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (0.1, 15.5, 2)})
        bs.newnode('locator', attrs={'shape': 'box', 'position': (17.75, 13, -5.52), 'color': (
            0, 0, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (0.1, 15.5, 2)})
        bs.newnode('locator', attrs={'shape': 'box', 'position': (0, 21.0, -5.52), 'color': (
            0, 0, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (35.4, 0.2, 2)})

        gnode = bs.getactivity().globalsnode
        gnode.happy_thoughts_mode = True
        gnode.shadow_offset = (0.0, 8.0, 5.0)
        gnode.tint = (1.3, 1.23, 1.0)
        gnode.ambient_color = (1.3, 1.23, 1.0)
        gnode.vignette_outer = (0.64, 0.59, 0.69)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
        gnode.vr_near_clip = 1.0
        self.is_flying = True

        # throw out some tips on flying
        txt = bs.newnode('text',
                         attrs={
                             'text': babase.Lstr(resource='pressJumpToFlyText'),
                             'scale': 1.2,
                             'maxwidth': 800,
                             'position': (0, 200),
                             'shadow': 0.5,
                             'flatness': 0.5,
                             'h_align': 'center',
                             'v_attach': 'bottom'
                         })
        cmb = bs.newnode('combine',
                         owner=txt,
                         attrs={
                             'size': 4,
                             'input0': 0.3,
                             'input1': 0.9,
                             'input2': 0.0
                         })
        bs.animate(cmb, 'input3', {3.0: 0, 4.0: 1, 9.0: 1, 10.0: 0})
        cmb.connectattr('output', txt, 'color')
        bs.timer(10.0, txt.delete)


try:
    bs.register_map(CreativeThoughts)
except:
    pass
