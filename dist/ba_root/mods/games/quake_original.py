# Created By Idk
# Ported to 1.7 by Yan

# ba_meta require api 8
from __future__ import annotations

import random

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.powerupbox import PowerupBox as Powerup
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    pass


class TouchedToSpaz(object):
    pass


class TouchedToAnything(object):
    pass


class TouchedToFootingMaterial(object):
    pass


class QuakeBallFactory(object):
    """Components used by QuakeBall stuff

    category: Game Classes

    """
    _STORENAME = babase.storagename()

    @classmethod
    def get(cls) -> QuakeBallFactory:
        """Get/create a shared bascenev1lib.actor.bomb.BombFactory object."""
        activity = bs.getactivity()
        factory = activity.customdata.get(cls._STORENAME)
        if factory is None:
            factory = QuakeBallFactory()
            activity.customdata[cls._STORENAME] = factory
        assert isinstance(factory, QuakeBallFactory)
        return factory

    def __init__(self):
        shared = SharedObjects.get()

        self.ball_material = bs.Material()

        self.ball_material.add_actions(
            conditions=(
            (('we_are_younger_than', 5), 'or', ('they_are_younger_than', 50)),
            'and', ('they_have_material', shared.object_material)),
            actions=(('modify_node_collision', 'collide', False)))

        self.ball_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=(('modify_part_collision', 'use_node_collide', False)))

        self.ball_material.add_actions(
            actions=('modify_part_collision', 'friction', 0))

        self.ball_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'our_node', 'at_connect', TouchedToSpaz())))

        self.ball_material.add_actions(
            conditions=(
            ('they_dont_have_material', shared.player_material), 'and',
            ('they_have_material', shared.object_material)),
            actions=('message', 'our_node', 'at_connect', TouchedToAnything()))

        self.ball_material.add_actions(
            conditions=(
            ('they_dont_have_material', shared.player_material), 'and',
            ('they_have_material', shared.footing_material)),
            actions=(
            'message', 'our_node', 'at_connect', TouchedToFootingMaterial()))

    def give(self, spaz):
        spaz.punch_callback = self.shot
        self.last_shot = int(bs.time() * 1000)

    def shot(self, spaz):
        time = int(bs.time() * 1000)
        if time - self.last_shot > 0.6:
            self.last_shot = time
            p1 = spaz.node.position_center
            p2 = spaz.node.position_forward
            direction = [p1[0] - p2[0], p2[1] - p1[1], p1[2] - p2[2]]
            direction[1] = 0.0

            mag = 10.0 / babase.Vec3(*direction).length()
            vel = [v * mag for v in direction]
            QuakeBall(
                position=spaz.node.position,
                velocity=(vel[0] * 2, vel[1] * 2, vel[2] * 2),
                owner=spaz._player,
                source_player=spaz._player,
                color=spaz.node.color).autoretain()


class QuakeBall(bs.Actor):

    def __init__(self,
                 position=(0, 5, 0),
                 velocity=(0, 2, 0),
                 source_player=None,
                 owner=None,
                 color=(random.random(), random.random(), random.random()),
                 light_radius=0
                 ):
        super().__init__()

        shared = SharedObjects.get()
        b_shared = QuakeBallFactory.get()

        self.source_player = source_player
        self.owner = owner

        self.node = bs.newnode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'mesh': bs.getmesh('impactBomb'),
            'body': 'sphere',
            'color_texture': bs.gettexture('bunnyColor'),
            'mesh_scale': 0.2,
            'is_area_of_interest': True,
            'body_scale': 0.8,
            'materials': [shared.object_material,
                          b_shared.ball_material]})

        self.light_node = bs.newnode('light', attrs={
            'position': position,
            'color': color,
            'radius': 0.1 + light_radius,
            'volume_intensity_scale': 15.0})

        self.node.connectattr('position', self.light_node, 'position')
        self.emit_time = bs.Timer(0.015, bs.WeakCall(self.emit), repeat=True)
        self.life_time = bs.Timer(5.0, bs.WeakCall(self.handlemessage,
                                                   bs.DieMessage()))

    def emit(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=10,
            scale=0.4,
            spread=0.01,
            chunk_type='spark')

    def handlemessage(self, m):
        if isinstance(m, TouchedToAnything):
            node = bs.getcollision().opposingnode
            if node is not None and node.exists():
                v = self.node.velocity
                t = self.node.position
                hitdir = self.node.velocity
                m = self.node
                node.handlemessage(
                    bs.HitMessage(
                        pos=t,
                        velocity=v,
                        magnitude=babase.Vec3(*v).length() * 40,
                        velocity_magnitude=babase.Vec3(*v).length() * 40,
                        radius=0,
                        srcnode=self.node,
                        source_player=self.source_player,
                        force_direction=hitdir))

            self.node.handlemessage(bs.DieMessage())

        elif isinstance(m, bs.DieMessage):
            if self.node.exists():
                velocity = self.node.velocity
                explosion = bs.newnode('explosion', attrs={
                    'position': self.node.position,
                    'velocity': (
                    velocity[0], max(-1.0, velocity[1]), velocity[2]),
                    'radius': 1,
                    'big': False})

                bs.getsound(random.choice(
                    ['impactHard', 'impactHard2', 'impactHard3'])).play(),
                position = self.node.position

                self.emit_time = None
                self.light_node.delete()
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            self.node.handlemessage('impulse', m.pos[0], m.pos[1], m.pos[2],
                                    m.velocity[0], m.velocity[1], m.velocity[2],
                                    1.0 * m.magnitude,
                                    1.0 * m.velocity_magnitude, m.radius, 0,
                                    m.force_direction[0], m.force_direction[1],
                                    m.force_direction[2])

        elif isinstance(m, TouchedToSpaz):
            node = bs.getcollision().opposingnode
            if node is not None and node.exists() and node != self.owner \
                and node.getdelegate(object)._player.team != self.owner.team:
                node.handlemessage(bs.FreezeMessage())
                v = self.node.velocity
                t = self.node.position
                hitdir = self.node.velocity

                node.handlemessage(
                    bs.HitMessage(
                        pos=t,
                        velocity=(10, 10, 10),
                        magnitude=50,
                        velocity_magnitude=50,
                        radius=0,
                        srcnode=self.node,
                        source_player=self.source_player,
                        force_direction=hitdir))

            self.node.handlemessage(bs.DieMessage())

        elif isinstance(m, TouchedToFootingMaterial):
            bs.getsound('blip').play(),
            position = self.node.position
        else:
            super().handlemessage(m)


class Player(bs.Player['Team']):
    ...


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export bascenev1.GameActivity


class QuakeGame(bs.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Quake'
    description = 'Kill a set number of enemies to win.'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession) or issubclass(
            sessiontype, bs.FreeForAllSession
        )

    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        return ['Doom Shroom', 'Monkey Face', 'Football Stadium']

    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[babase.Setting]:
        settings = [
            bs.IntSetting(
                'Kills to Win Per Player',
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
                    ('Longer', 4.0),
                ],
                default=1.0,
            ),
            bs.IntChoiceSetting(
                'Graphics',
                choices=[
                    ('Normal', 1),
                    ('High', 2)
                ],
                default=1),
            bs.BoolSetting('Fast Movespeed', default=True),
            bs.BoolSetting('Enable Jump', default=False),
            bs.BoolSetting('Enable Pickup', default=False),
            bs.BoolSetting('Enable Bomb', default=False),
            bs.BoolSetting('Obstacles', default=False),
            bs.IntChoiceSetting(
                'Obstacles Shape',
                choices=[
                    ('Cube', 1),
                    ('Sphere', 2),
                    ('Puck', 3),
                    ('Egg', 4),
                    ('Random', 5),
                ],
                default=1),
            bs.BoolSetting('Obstacles Bounces Shots', default=False),
            bs.IntSetting(
                'Obstacle Count',
                min_value=1,
                default=16,
                increment=1,
            ),
            bs.BoolSetting('Random Obstacle Color', default=True),
            bs.BoolSetting('Epic Mode', default=False),
        ]
        return settings

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: int | None = None
        self._dingsound = bs.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(settings['Kills to Win Per Player'])
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False)
        )

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.TO_THE_DEATH
        )
        self.settings = settings

    def get_instance_description(self) -> str | Sequence:
        return 'Crush ${ARG1} of your enemies.', self._score_to_win

    def get_instance_description_short(self) -> str | Sequence:
        return 'kill ${ARG1} enemies', self._score_to_win

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.dingsound = bs.getsound('dingSmall')
        self.setup_standard_time_limit(self._time_limit)

        self.drop_shield()
        self.drop_shield_timer = bs.Timer(8.001, bs.WeakCall(self.drop_shield),
                                          repeat=True)

        shared = SharedObjects.get()
        if self.settings['Obstacles']:
            count = self.settings['Obstacle Count']
            map = bs.getactivity()._map.getname()
            for i in range(count):
                if map == 'Football Stadium':
                    radius = (random.uniform(-10, 1),
                              6,
                              random.uniform(-4.5, 4.5)) \
                        if i > count / 2 else (
                    random.uniform(10, 1), 6, random.uniform(-4.5, 4.5))
                else:
                    radius = (random.uniform(-10, 1),
                              6,
                              random.uniform(-8, 8)) \
                        if i > count / 2 else (
                    random.uniform(10, 1), 6, random.uniform(-8, 8))

                Obstacle(
                    position=radius,
                    graphics=self.settings['Graphics'],
                    random_color=self.settings['Random Obstacle Color'],
                    rebound=self.settings['Obstacles Bounces Shots'],
                    shape=int(self.settings['Obstacles Shape'])).autoretain()

        if self.settings['Graphics'] == 2:
            bs.getactivity().globalsnode.tint = (bs.getactivity(
            ).globalsnode.tint[0] - 0.6, bs.getactivity().globalsnode.tint[
                                                     1] - 0.6,
                                                 bs.getactivity().globalsnode.tint[
                                                     2] - 0.6)
            light = bs.newnode('light', attrs={
                'position': (9, 10, 0) if map == 'Football Stadium' else (
                6, 7, -2)
                if not map == 'Rampage' else (
                6, 11, -2) if not map == 'The Pad' else (6, 8.5, -2),
                'color': (0.4, 0.4, 0.45),
                'radius': 1,
                'intensity': 6,
                'volume_intensity_scale': 10.0})

            light2 = bs.newnode('light', attrs={
                'position': (-9, 10, 0) if map == 'Football Stadium' else (
                -6, 7, -2)
                if not map == 'Rampage' else (
                -6, 11, -2) if not map == 'The Pad' else (-6, 8.5, -2),
                'color': (0.4, 0.4, 0.45),
                'radius': 1,
                'intensity': 6,
                'volume_intensity_scale': 10.0})

        if len(self.teams) > 0:
            self._score_to_win = self.settings['Kills to Win Per Player'] * \
                                 max(1, max(len(t.players) for t in self.teams))
        else:
            self._score_to_win = self.settings['Kills to Win Per Player']
        self._update_scoreboard()

    def drop_shield(self):
        p = Powerup(
            poweruptype='shield',
            position=(
            random.uniform(-10, 10), 6, random.uniform(-5, 5))).autoretain()

        bs.getsound('dingSmall').play()

        p_light = bs.newnode('light', attrs={
            'position': (0, 0, 0),
            'color': (0.3, 0.0, 0.4),
            'radius': 0.3,
            'intensity': 2,
            'volume_intensity_scale': 10.0})

        p.node.connectattr('position', p_light, 'position')

        bs.animate(p_light, 'intensity', {0: 2, 8000: 0})

        def check_exists():
            if p is None or p.node.exists() == False:
                delete_light()
                del_checker()

        self._checker = bs.Timer(0.1, babase.Call(check_exists), repeat=True)

        def del_checker():
            if self._checker is not None:
                self._checker = None

        def delete_light():
            if p_light.exists():
                p_light.delete()

        bs.timer(6.9, babase.Call(del_checker))
        bs.timer(7.0, babase.Call(delete_light))

    def spawn_player(self, player: bs.Player):
        spaz = self.spawn_player_spaz(player)
        QuakeBallFactory().give(spaz)
        spaz.connect_controls_to_player(
            enable_jump=self.settings['Enable Jump'],
            enable_punch=True,
            enable_pickup=self.settings['Enable Pickup'],
            enable_bomb=self.settings['Enable Bomb'],
            enable_run=True,
            enable_fly=False)

        if self.settings['Fast Movespeed']:
            spaz.node.hockey = True
        spaz.spaz_light = bs.newnode('light', attrs={
            'position': (0, 0, 0),
            'color': spaz.node.color,
            'radius': 0.12,
            'intensity': 1,
            'volume_intensity_scale': 10.0})

        spaz.node.connectattr('position', spaz.spaz_light, 'position')

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

            killer = msg.getkillerplayer(Player)
            if hasattr(player.actor, 'spaz_light'):
                player.actor.spaz_light.delete()
            if killer is None:
                return None

            # Handle team-kills.
            if killer.team is player.team:

                # In free-for-all, killing yourself loses you a point.
                if isinstance(self.session, bs.FreeForAllSession):
                    new_score = player.team.score - 1
                    if not self._allow_negative_scores:
                        new_score = max(0, new_score)
                    player.team.score = new_score

                # In teams-mode it gives a point to the other team.
                else:
                    self._dingsound.play()
                    for team in self.teams:
                        if team is not killer.team:
                            team.score += 1

            # Killing someone on another team nets a kill.
            else:
                killer.team.score += 1
                self._dingsound.play()

                # In FFA show scores since its hard to find on the scoreboard.
                if isinstance(killer.actor, PlayerSpaz) and killer.actor:
                    killer.actor.set_score_text(
                        str(killer.team.score) + '/' + str(self._score_to_win),
                        color=killer.team.color,
                        flash=True,
                    )

            self._update_scoreboard()

            # If someone has won, set a timer to end shortly.
            # (allows the dust to clear and draws to occur if deaths are
            # close enough)
            assert self._score_to_win is not None
            if any(team.score >= self._score_to_win for team in self.teams):
                bs.timer(0.5, self.end_game)

        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.score, self._score_to_win
            )

    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)


class Obstacle(bs.Actor):

    def __init__(self,
                 position: tuple(float, float, float),
                 graphics: bool,
                 random_color: bool,
                 rebound: bool,
                 shape: int) -> None:
        super().__init__()

        shared = SharedObjects.get()
        if shape == 1:
            mesh = 'tnt'
            body = 'crate'
        elif shape == 2:
            mesh = 'bomb'
            body = 'sphere'
        elif shape == 3:
            mesh = 'puck'
            body = 'puck'
        elif shape == 4:
            mesh = 'egg'
            body = 'capsule'
        elif shape == 5:
            pair = random.choice([
                {'mesh': 'tnt', 'body': 'crate'},
                {'mesh': 'bomb', 'body': 'sphere'},
                {'mesh': 'puckModel', 'body': 'puck'},
                {'mesh': 'egg', 'body': 'capsule'}
            ])
            mesh = pair['mesh']
            body = pair['body']

        self.node = bs.newnode('prop', delegate=self, attrs={
            'position': position,
            'mesh': bs.getmesh(mesh),
            'body': body,
            'body_scale': 1.3,
            'mesh_scale': 1.3,
            'reflection': 'powerup',
            'reflection_scale': [0.7],
            'color_texture': bs.gettexture('bunnyColor'),
            'materials': [
                shared.footing_material if rebound else shared.object_material,
                shared.footing_material]})

        if graphics == 2:
            self.light_node = bs.newnode('light', attrs={
                'position': (0, 0, 0),
                'color': ((0.8, 0.2, 0.2) if i < count / 2 else (0.2, 0.2, 0.8))
                if not random_color else ((
                random.uniform(0, 1.1), random.uniform(0, 1.1),
                random.uniform(0, 1.1))),
                'radius': 0.2,
                'intensity': 1,
                'volume_intensity_scale': 10.0})

            self.node.connectattr('position', self.light_node, 'position')

    def handlemessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                if hasattr(self, 'light_node'):
                    self.light_node.delete()
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.handlemessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            self.node.handlemessage('impulse', m.pos[0], m.pos[1], m.pos[2],
                                    m.velocity[0], m.velocity[1], m.velocity[2],
                                    m.magnitude, m.velocity_magnitude, m.radius,
                                    0,
                                    m.velocity[0], m.velocity[1], m.velocity[2])
