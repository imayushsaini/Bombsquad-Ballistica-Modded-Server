# Released under the MIT License. See LICENSE for details.
# Made by Learn .py on discord

# ba_meta require api 9
# ba_meta require asset-package a-18011215.basket_punch.test260723b

from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import math, random # the duo
import os
import urllib.request
import bauiv1 as bui
import bascenev1 as bs
import _babase
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor import playerspaz as ps
from bascenev1lib.actor.bomb import Bomb, Blast
from bascenev1lib import maps

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


__asset_package__ = 'a-18011215.basket_punch.test260723b'

from bascenev1._assetwrap import AssetDir                                                                                                                     

if TYPE_CHECKING:
    import bascenev1

    class AudioGroup:
        """Asset-group type; see source for the full list."""

        anklebreak: bascenev1.Sound
        catch: bascenev1.Sound
        clean: bascenev1.Sound
        connect: bascenev1.Sound
        rattlebones: bascenev1.Sound
        rebound: bascenev1.Sound
        squeak1: bascenev1.Sound
        squeak2: bascenev1.Sound
        squeak3: bascenev1.Sound

    class ModelsGroup:
        """Asset-group type; see source for the full list."""

        basketback: bascenev1.Mesh
        basketball: bascenev1.Mesh
        basketcollide: bascenev1.Mesh
        basketpole: bascenev1.Mesh
        basketrings: bascenev1.Mesh
        none: bascenev1.Mesh
        volleyball_net: bascenev1.Mesh

    class TextureGroup:
        """Asset-group type; see source for the full list."""

        basket: bascenev1.Texture
        basketback: bascenev1.Texture
        basketball: bascenev1.Texture
        basketballball: bascenev1.Texture
        basketpole: bascenev1.Texture
        basketrings: bascenev1.Texture
        basketstadiumpreview: bascenev1.Texture

    #: The ``audio`` group - 9 assets (``anklebreak``, ``catch``, ``clean``,
    #: ``connect``, ``rattlebones``, and 4 more). Full list in source.
    audio: AudioGroup

    #: The ``models`` group - 7 assets (``basketback``, ``basketball``,
    #: ``basketcollide``, ``basketpole``, ``basketrings``, and 2 more). Full
    #: list in source.
    models: ModelsGroup

    #: The ``texture`` group - 7 assets (``basket``, ``basketback``,
    #: ``basketball``, ``basketballball``, ``basketpole``, and 2 more). Full
    #: list in source.
    texture: TextureGroup

_TREE = {
    'audio': {
        'anklebreak': 's',
        'catch': 's',
        'clean': 's',
        'connect': 's',
        'rattlebones': 's',
        'rebound': 's',
        'squeak1': 's',
        'squeak2': 's',
        'squeak3': 's',
    },
    'models': {
        'basketback': 'm',
        'basketball': 'm',
        'basketcollide': 'm',
        'basketpole': 'm',
        'basketrings': 'm',
        'none': 'm',
        'volleyball_net': 'm',
    },
    'texture': {
        'basket': 't',
        'basketback': 't',
        'basketball': 't',
        'basketballball': 't',
        'basketpole': 't',
        'basketrings': 't',
        'basketstadiumpreview': 't',
    },
}


if not TYPE_CHECKING:
    audio = AssetDir(__asset_package__, _TREE['audio'], 'audio')
    models = AssetDir(__asset_package__, _TREE['models'], 'models')
    texture = AssetDir(__asset_package__, _TREE['texture'], 'texture')

bsuSpaz = None

# Do not touch these values you can modify them when creating the game.
STEALING_RANGE = 1.9 # default
PICKUP_RANGE = STEALING_RANGE


def getlanguage(text, sub: str = ''):
    lang = bs.app.lang.language
    translate = {
        "Name":
        {"Spanish": "Cesta",
         "English": "Basket Punch v1.1",
         "Portuguese": "Cesta"},
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

    languages = ['Spanish', 'Portuguese', 'English']
    if lang not in languages:
        lang = 'English'

    if text not in translate:
        return text
    return translate[text][lang]


class BallDiedMessage:
    def __init__(learn, ball: Ball):
        learn.ball = ball


class Ball(bs.Actor):
    def __init__(learn, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = learn.getactivity()

        learn._spawn_pos = (position[0], position[1] + 0.5, position[2])
        learn.last_players_to_touch: Dict[int, Player] = {}
        learn.scored = False

        assert activity is not None
        assert isinstance(activity, BasketGame)

        pmats = [shared.object_material, activity.ball_material]
        learn.node = bs.newnode('prop',
                               delegate=learn,
                               attrs={
                                   'mesh': activity.ball_mesh,
                                   'color_texture': activity.ball_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.3,
                                   'mesh_scale': activity.ball_size,
                                   'body_scale': 1.07,
                                   'gravity_scale': 1,
                                   'is_area_of_interest': True,
                                   'position': learn._spawn_pos,
                                   'materials': pmats
                               })

        learn.light = bs.newnode(
            'light',
            attrs={
                'position': learn.node.position,
                'radius': 0.5,
                'intensity': 0.1,
                'height_attenuated': False,
                'color': (1.0, 0.647, 0.0),
            },
        )

    def handlemessage(learn, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            assert learn.node
            learn.node.delete()
            activity = learn._activity()
            if activity and not msg.immediate:
                activity.handlemessage(BallDiedMessage(learn))

        elif isinstance(msg, bs.OutOfBoundsMessage):
            assert learn.node
            learn.node.position = learn._spawn_pos
            learn.node.velocity = (0.0, 0.0, 0.0)

        elif isinstance(msg, bs.HitMessage):
            assert learn.node
            assert msg.force_direction is not None
            learn.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = learn._activity()
                if activity:
                    if s_player in activity.players:
                        learn.last_players_to_touch[s_player.team.id] = s_player
        else:
            super().handlemessage(msg)


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(learn) -> None:
        learn.score = 0


class Points:
    postes = dict()
    # 10.736066818237305, 0.3002409040927887, 0.5281256437301636
    postes['pal_0'] = (10.64702320098877, 0.0000000000000000, 0.0000000000000000)
    postes['pal_1'] = (-10.64702320098877, 0.0000000000000000, 0.0000000000000000)

# ba_meta export bascenev1.GameActivity
class BasketGame(bs.TeamGameActivity[Player, Team]):

    name = getlanguage('Name')
    description = getlanguage('Info')
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=3,
            default=9,
            increment=3,
        ),
        bs.IntChoiceSetting(
            'Custom Time',
            choices=[
                ('2 Minute', 120),
                ('4 Minutes', 240),
                ('8 Minutes', 480),
            ],
            default=120,
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
        bs.FloatSetting(
            'Ball size (m)',
            min_value=0.15,
            default=0.25,
            max_value=0.35,
            increment=0.05,
        ),
        bs.FloatSetting(
            'Steal Hitbox (m)',
            min_value=1.8,
            default=1.9,
            max_value=2.4,
            increment=0.05,
        ),
        bs.BoolSetting('Tutorial', default=True),
        bs.BoolSetting(getlanguage('S: Powerups'), default=True),
        bs.BoolSetting(getlanguage('S: Velocity'), default=False),
        bs.BoolSetting('Epic Mode', default=False),
    ]
    default_music = bs.MusicType.HOCKEY

    @classmethod
    def supports_session_type(cls, sessiontype: Type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return ['Basket']

    def __init__(learn, settings: dict):
        global STEALING_RANGE
        super().__init__(settings)
        shared = SharedObjects.get()
        learn._scoreboard = Scoreboard()
        learn._cheer_sound = bs.getsound('cheer')
        learn._chant_sound = bs.getsound('crowdChant')
        learn._foghorn_sound = bs.getsound('foghorn')
        learn._swipsound = bs.getsound('swip')
        learn._whistle_sound = bs.getsound('refWhistle')
        learn.ball_mesh = bs.getmesh('shield')
        learn.ball_tex = texture.basket
        learn._ball_sound = audio.rebound
        learn.time_limit = settings['Custom Time']
        learn._powerups = bool(settings[getlanguage('S: Powerups')])
        learn._speed = bool(settings[getlanguage('S: Velocity')])
        learn.ball_size = float(settings['Ball size (m)'])
        STEALING_RANGE = float(settings['Steal Hitbox (m)'])
        learn._epic_mode = bool(settings['Epic Mode'])
        learn.tutorial = settings['Tutorial']
        learn.slow_motion = learn._epic_mode

        learn.owner = None
        learn.shooting = False
        learn.passing = False
        learn.can_score = True
        learn.blockable = True
        learn.last_touched = None
        learn.deactivated = True
        learn.begginning_x = 0
        learn.protected = False
        learn.blocked = False
        learn.seconds = 0
        learn.minutes = 0
        learn.last_ball_y = 0.0
        learn.mi = False
        learn.timer = None
        learn.help = None
        learn.text = None
        learn.tutorial_p = False
        learn.tutorial_t = False
        learn.tutorial_d = False

        learn.ball_material = bs.Material()
        learn.ball_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 1e7)))
        learn.ball_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', True))
        learn.ball_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        learn.ball_material.add_actions(conditions=('they_have_material',
                                                   shared.footing_material),
                                       actions=('impact_sound',
                                                learn._ball_sound, 0.4, 5))

        # Keep track of which player last touched the ball
        learn.ball_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect',
                      learn._handle_ball_player_collide),
                     ('modify_node_collision', 'collide', False),))

        learn._score_region_material = bs.Material()
        learn._score_region_material.add_actions(
            conditions=('they_have_material', learn.ball_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', learn._handle_score)))
        learn._ball_spawn_pos: Optional[Sequence[float]] = None
        learn._score_regions: Optional[List[bs.NodeActor]] = None
        learn._ball: Optional[Ball] = None
        learn._score_to_win = int(settings['Score to Win'])
        learn.help_timer = 0

    def get_instance_description(learn) -> Union[str, Sequence]:
        return getlanguage('Info-Short', sub=learn._score_to_win)

    def get_instance_description_short(learn) -> Union[str, Sequence]:
        return getlanguage('Info-Short', sub=learn._score_to_win)

    def on_begin(learn) -> None:
        super().on_begin()

        def do():
            activity = bs.getactivity()
            learn._ball.node.velocity = (0, 0, 0)
            learn._ball.node.position = learn._ball_spawn_pos

            team0 = []
            team1 = []

            loser = None

            for p in activity.players:
                if not p.actor or not p.actor.node.exists():
                    continue


                if p.team.id == 0:
                    team0.append(p)
                else:
                    team1.append(p)

            mid0 = len(team0) // 2
            mid1 = len(team1) // 2

            for p in team0[:mid0]:
                if p is None:
                    continue
                p.actor.node.handlemessage(
                    bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                )

            for p in team0[mid0:]:
                p.actor.node.handlemessage(
                    bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                )

            for p in team1[:mid1]:
                p.actor.node.handlemessage(
                    bs.StandMessage(position=(10.6, 0, 0), angle=270)
                )

            for p in team1[mid1:]:
                p.actor.node.handlemessage(
                    bs.StandMessage(position=(10.6, 0, 0), angle=270)
                )

            learn.deactivated = False

        bs.timer(0.1, do)

        learn.setup_standard_time_limit(0)
        learn._ball_spawn_pos = learn.map.get_flag_position(None)
        learn._spawn_ball()
        learn.start_timer_timers()
        learn.help = bs.newnode('image',
                               delegate=learn,
                               attrs={
                                   'texture': bs.gettexture('black'),
                                   'tint_texture': bs.gettexture('buttonPickUp'),
                                   'tint_color': (0, 1, 0),
                                   'vr_depth': 400,
                                   'tint2_color': (0, 1, 0),
                                   'position': (0, -0.35),  # Coordonnées dans le monde (x, y, z)
                                   'mask_texture': bs.gettexture('buttonPickUp'),
                                   'opacity': 0.65,
                                   'absolute_scale': False,  # <--- C'EST ÇA QUI CHANGE TOUT
                                   'scale': [0.07],
                               })
        learn.text = bs.newnode('text', owner=learn.help
                          ,attrs={
                'text': "Grab the ball to start controlling it.",
                'in_world': False,
                'shadow': 0,
                'color': (0.5,1,0.5,0.65),
                'flatness': 1.0,
                'scale': 0.9,
                'h_align': 'center',
                'v_align': 'bottom',
                'h_attach': 'center',
                'v_attach': 'bottom',
                'position': (0, 30)
            })
        bs.animate(learn.help, 'opacity', {0: 0, 5: 0.65})
        bs.animate_array(learn.text, 'color', 4, {0: (0,0,0,0), 5: (0.5,1,0.5,0.65)})


        learn.inter_game = bs.Timer(0.04, learn.basket, repeat=True)
        learn.outer_game = bs.Timer(1/240, learn.process_dribbling, repeat=True)
        learn.timer_game = bs.Timer(1.0, learn.game_time, repeat=True)

        if hasattr(learn.map, 'node') and learn.map.node.exists():
            learn.map.node.collision_mesh = bs.getcollisionmesh('basketCollide')

        learn._score_regions = []
        for name in ['goal1', 'goal2']:
            box = learn.map.defs.boxes.get(name)
            if box:
                region = bs.newnode('region', attrs={
                    'position': box[0:3],
                    'scale': box[6:9],
                    'type': 'box',
                    'materials': [learn._score_region_material]
                })
                learn._score_regions.append(bs.NodeActor(region))

        learn._update_scoreboard()
        learn._chant_sound.play()

        for team_id in range(len(learn.teams)):
            if hasattr(learn, 'postes'):
                learn.postes(team_id)

    def game_time(learn):
        activity = bs.getactivity()
        learn.checker = None
        if learn.timer is None:
            learn.timer = bs.newnode('text', attrs={
                'text': "X : XX",
                'in_world': False,
                'shadow': 0,
                'color': (1,1,1,0.5),
                'flatness': 1.0,
                'scale': 0.9,
                'h_align': 'center',
                'v_align': 'top',
                'h_attach': 'center',
                'v_attach': 'top',
                'position': (0, -30)
            })
            learn.seconds = 0
            learn.minutes = int(learn.time_limit / 60)
        else:
            if not learn.deactivated:
                learn.seconds -= 1
            if learn.seconds <= 0 and not learn.deactivated:
                learn.minutes -= 1
                if learn.minutes > 0:
                    learn.seconds = 59
            learn.timer.text = f"{learn.minutes} : {0 if learn.seconds < 10 else ""}{learn.seconds}"
            if learn.seconds <= 1 and learn.minutes < 1 and not learn.shooting:
                learn.deactivated = True
                learn.timer.text = "0 : 00"
                bs.timer(0.5, learn.end_game)
            if learn.seconds <= 1 and learn.minutes == int(learn.time_limit / 120) and not learn.mi:
                def show():
                    if learn.mi:
                        return
                    learn.mi = True
                    learn.deactivated = True
                    present_sky_color = bs.getactivity().globalsnode.tint
                    sky_color = bs.getactivity().globalsnode
                    bs.animate_array(sky_color, 'tint', 3,
                                     {0: present_sky_color, 0.6: (-100,-100,-100), 4: (-100,-100,-100), 4.1: (-1,-1,-1), 7.15: present_sky_color})
                    mi = bs.newnode('text', attrs={
                        'text': "HALF TIME",
                        'in_world': False,
                        'shadow': 0,
                        'color': (1, 1, 1, 0.5),
                        'flatness': 1.0,
                        'scale': 3.8,
                        'h_align': 'center',
                        'v_align': 'top',
                        'h_attach': 'center',
                        'v_attach': 'top',
                        'position': (0, -280)
                    })
                    mi2 = bs.newnode('text', attrs={
                        'text': "THE GAME BECOMES HARDER",
                        'in_world': False,
                        'shadow': 0,
                        'color': (1, 1, 1, 0.5),
                        'flatness': 1.0,
                        'scale': 0.8,
                        'h_align': 'center',
                        'v_align': 'top',
                        'position': (0, -100)
                    })
                    bs.animate_array(mi, 'color', 4, {0: (1,1,1,0.1), 4: (1,1,1,0.7), 4.2: (0,0,0,0)})
                    bs.animate_array(mi2, 'color', 4, {0: (1, 1, 1, 0.1), 4: (1, 1, 1, 0.7), 6: (1, 0, 0, 0.7), 7: (0, 0, 0, 0)})
                    learn.seconds = 59
                    learn.minutes = int(learn.time_limit / 120) - 1
                    learn.timer.text = f"{int(learn.time_limit / 120)} : 00"

                    for p in activity.players:
                        if not p.actor or not p.actor.node.exists():
                            continue

                    def backup_time():
                        learn.deactivated = False
                        learn.owner = None
                        learn._ball.node.position = learn._ball_spawn_pos
                        scorer = None
                        team0 = []
                        team1 = []

                        for p in activity.players:
                            if not p.actor or not p.actor.node.exists():
                                continue

                            if p is scorer:
                                continue

                            if p.team.id == 0:
                                team0.append(p)
                            else:
                                team1.append(p)

                        mid0 = len(team0) // 2
                        mid1 = len(team1) // 2

                        for p in team0[:mid0]:
                            if p == scorer:
                                continue
                            if p is None:
                                continue
                            p.actor.node.handlemessage(
                                bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                            )

                        for p in team0[mid0:]:
                            if p == scorer:
                                continue
                            p.actor.node.handlemessage(
                                bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                            )

                        for p in team1[:mid1]:
                            if p == scorer:
                                continue
                            p.actor.node.handlemessage(
                                bs.StandMessage(position=(10.6, 0, 0), angle=270)
                            )

                        for p in team1[mid1:]:
                            if p == scorer:
                                continue
                            p.actor.node.handlemessage(
                                bs.StandMessage(position=(10.6, 0, 0), angle=270)
                            )
                    bs.timer(4.5, backup_time)
                show()



    def ball_free_anim(learn):
        node = learn._ball.node
        loc = bs.newnode('locator', owner=node,

                         attrs={'shape': 'circleOutline',

                                'color': (1, 1, 1),

                                'opacity': 1,

                                'draw_beauty': True,

                                'additive': True})

        node.connectattr('position', loc, 'position')

        bs.animate_array(loc, 'size', 1, {0: [0], 0.55: [1.5], 1: [0.0]})
        bs.animate(loc, 'opacity', {0: 0, 0.5: 0.7, 0.8: 1, 1: 0})
        bs.timer(1, loc.delete)

    def ball_took_anim(learn):
        node = learn._ball.node
        loc = bs.newnode('locator', owner=node,

                         attrs={'shape': 'circleOutline',

                                'color': learn.owner.actor.node.color,

                                'opacity': 1,

                                'draw_beauty': True,

                                'additive': False})

        node.connectattr('position', loc, 'position')

        bs.animate_array(loc, 'size', 1, {0: [0], 0.55: [1.5], 1: [0.0]})
        bs.animate(loc, 'opacity', {0: 0, 0.5: 0.7, 0.8: 1, 1: 0})
        bs.timer(1, loc.delete)

    def basket(learn):

        if learn.deactivated or not learn._ball or not learn._ball.node.exists():
            return

        learn._ball.light.position = learn._ball.node.position
        learn.update_mvp_logic()
        learn.process_red_scoring()
        learn.process_blue_scoring()
        learn.process_nearest_player()
        learn.process_nearest_blocker()
        learn.process_nearest_stealer()

    def update_mvp_logic(learn):

        activity = bs.getactivity()
        if not activity:
            return

        best_player = None
        best_mvp = 5

        for p in activity.players:
            if not p.actor or not p.actor.node.exists():
                continue

            mvp = getattr(p.actor, 'mvp', 0)

            if mvp > best_mvp:
                best_mvp = mvp
                best_player = p


        for p in activity.players:
            if not p.actor or not p.actor.node.exists():
                continue
            if p.actor.bar is None:
                p.actor.bar = bs.newnode(
                    'shield',
                    owner=p.actor.node,
                    attrs={
                        'position': p.actor.node.position,
                        'radius': 0.001,
                        'color': (0, 0, 0),
                    }
                )
                p.actor.node.connectattr('position', p.actor.bar, 'position')
                p.actor.per = 0
                p.actor.bar.always_show_health_bar = True
            else:
                p.actor.bar.hurt = 1.0 - (float(p.actor.per) / 100)

            if p is best_player:
                if p.actor.per >= 98:
                    p.actor.node.name = "ULT"
                    p.actor.bar.always_show_health_bar = False
                else:
                    p.actor.node.name = f"MVP : {best_mvp}"
                    p.actor.bar.always_show_health_bar = True
            else:
                if p.actor.per >= 98:
                    p.actor.node.name = "ULT"
                    p.actor.bar.always_show_health_bar = False
                else:
                    p.actor.node.name = ""
                    p.actor.bar.always_show_health_bar = True

    def process_red_scoring(learn):
        if learn.deactivated or learn.owner or learn.passing or not learn.can_score:
            # On met tout de même à jour la position pour le prochain tick
            # même si on ne score pas, pour ne pas fausser le calcul suivant
            learn.last_ball_y = learn._ball.node.position[1]
            return

        ball_node = learn._ball.node
        pos = ball_node.position

        # 1. Calcul de la direction : est-ce que ça descend ?
        # Si y_actuel < y_precedent, la balle descend.
        is_falling = pos[1] < learn.last_ball_y

        # Mise à jour pour le prochain tick
        learn.last_ball_y = pos[1]

        # 2. Tes autres conditions
        dist_horizontal = math.dist((10.5, 0, 0), (pos[0], 0, pos[2]))
        is_in_zone = dist_horizontal <= 0.75
        # On élargit un peu la zone Y de détection pour être sûr de capter le passage
        is_above_rim = 1.7 < pos[1] < 2.5

        if is_in_zone and is_above_rim and learn.last_touched and learn.last_touched.team.id == 0:
            Blast(
                position=(10.5, 2.1, 0),
                velocity=(0, -5, 0),
                blast_radius=2.25,
                blast_type='ice',
                source_player=None,
            )
            final_color = learn.last_touched.actor.node.color
            glb = bs.getactivity().globalsnode
            base_color = (0.57, 0.57, 0.57)
            bs.animate_array(glb, 'vignette_outer', 3, {0: base_color, 0.1: (
                final_color[0] / 1.2, final_color[1] / 1.2, final_color[2] / 1.2), 1: base_color})
            sound_node = bs.newnode('sound', attrs={
                'sound': audio.clean,
                'volume': 7,
                'loop': False
            })
            bs.animate(sound_node, 'volume', {0: 50, 2: 50, 4: 0})
            bs.timer(5, sound_node.delete)
            dist = math.dist((10.5, 2.1, 0), learn.begginning_x)
            if dist >= 6 or dist >= 5.5 and abs(learn.begginning_x[0] - 10.5) <= 2:
                special = 3
            else:
                special = 2
            if special == 3:
                bs.getsound("announceThree").play(volume=3)
            else:
                bs.getsound("announceTwo").play(volume=1.75)
            learn.deactivated = True
            thrower_id = learn.last_touched.team.id
            learn.last_touched.actor.mvp += special
            learn.last_touched.actor.per = min(100, learn.last_touched.actor.per + (8 if special == 2 else 15) * (special / 3))
            learn.last_touched.team.score += 1 * special
            scoring_team = learn.last_touched.team
            if (thrower_id in learn._ball.last_players_to_touch
                    and learn._ball.last_players_to_touch[scoring_team.id]):
                learn.stats.player_scored(
                    learn._ball.last_players_to_touch[scoring_team.id],
                    100 * special, big_message=True)

                if scoring_team.score >= learn._score_to_win:
                    learn.end_game()

            # learn._foghorn_sound.play()
            learn._cheer_sound.play()

            learn._ball.scored = True

            # Kill the ball (it'll respawn itlearn shortly).
            bs.timer(1.0, learn._flash_ball_spawn)
            def do():
                if not learn._ball: return
                activity = bs.getactivity()
                learn._ball.node.velocity = (0, 0, 0)
                learn._ball.node.position = learn._ball_spawn_pos

                team0 = []
                team1 = []

                scorer = learn.last_touched
                loser = None

                for p in activity.players:
                    if not p.actor or not p.actor.node.exists():
                        continue

                    if p is scorer:
                        continue

                    if p.team.id == 0:
                        team0.append(p)
                    else:
                        team1.append(p)

                mid0 = len(team0) // 2
                mid1 = len(team1) // 2

                for p in team0[:mid0]:
                    if p == scorer:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                    )

                for p in team0[mid0:]:
                    if p == scorer:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                    )

                for p in team1[:mid1]:
                    if p == scorer:
                        continue

                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(10.6, 0, 0), angle=270)
                    )

                for p in team1[mid1:]:
                    if p == scorer:
                        continue
                    if p is None:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(10.6, 0, 0), angle=270)
                    )

                scorer.actor.node.handlemessage(
                    bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                )
                learn.deactivated = False

            bs.timer(2.0, do)

            learn.last_touched.actor.node.handlemessage('celebrate', 2000)
            def give_back():
                if not learn.last_touched: return
                learn.last_touched.actor.connect_controls_to_player()
            def stun_scorer():
                if not learn.last_touched: return
                learn.last_touched.actor.disconnect_controls_from_player()
                bs.timer(1, give_back)
            bs.timer(2, stun_scorer)

            light = bs.newnode('light',
                               attrs={
                                   'position': learn._ball.node.position,
                                   'height_attenuated': False,
                                   'color': (1, 0.5, 0)
                               })
            bs.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
            bs.timer(1.0, light.delete)

            bs.cameraflash(duration=10.0)
            learn._update_scoreboard()


    def process_blue_scoring(learn):
        if learn.deactivated or learn.owner or learn.passing or not learn.can_score:
            learn.last_ball_y = learn._ball.node.position[1]
            return

        ball_node = learn._ball.node
        pos = ball_node.position

        # 1. Calcul de la direction : est-ce que ça descend ?
        # Si y_actuel < y_precedent, la balle descend.
        is_falling = pos[1] < learn.last_ball_y

        # Mise à jour pour le prochain tick
        learn.last_ball_y = pos[1]

        # 2. Tes autres conditions
        dist_horizontal = math.dist((-10.5, 0, 0), (pos[0], 0, pos[2]))
        is_in_zone = dist_horizontal <= 0.75
        # On élargit un peu la zone Y de détection pour être sûr de capter le passage
        is_above_rim = 1.7 < pos[1] < 2.5

        if is_in_zone and is_above_rim and learn.last_touched and learn.last_touched.team.id == 1:
            Blast(
                position=(-10.5, 2.1, 0),
                velocity=(0, -5, 0),
                blast_radius=2.25,
                blast_type='ice',
                source_player=None,
            )
            final_color = learn.last_touched.actor.node.color
            glb = bs.getactivity().globalsnode
            base_color = (0.57, 0.57, 0.57)
            bs.animate_array(glb, 'vignette_outer', 3, {0: base_color, 0.1: (
                final_color[0] / 1.2, final_color[1] / 1.2, final_color[2] / 1.2), 1: base_color})
            sound_node = bs.newnode('sound', attrs={
                'sound': audio.clean,
                'volume': 7,
                'loop': False
            })
            bs.animate(sound_node, 'volume', {0: 50, 4: 0})
            bs.timer(5, sound_node.delete)
            dist = math.dist((-10.5, 2.1, 0), learn.begginning_x)
            if dist >= 6 or dist >= 5.5 and abs(learn.begginning_x[0] - 10.5) <= 2:
                special = 3
            else:
                special = 2
            if special == 3:
                bs.getsound("announceThree").play(volume=3)
            else:
                bs.getsound("announceTwo").play(volume=1.5)
            learn.deactivated = True
            thrower_id = learn.last_touched.team.id
            learn.last_touched.actor.mvp += special
            learn.last_touched.actor.per = min(100, learn.last_touched.actor.per + (8 if special == 2 else 15) * (special / 3))
            learn.last_touched.team.score += 1 * special
            scoring_team = learn.last_touched.team
            if (thrower_id in learn._ball.last_players_to_touch
                    and learn._ball.last_players_to_touch[scoring_team.id]):
                learn.stats.player_scored(
                    learn._ball.last_players_to_touch[scoring_team.id],
                    100 * special, big_message=True)

                if scoring_team.score >= learn._score_to_win:
                    learn.end_game()

            # learn._foghorn_sound.play()
            learn._cheer_sound.play()

            learn._ball.scored = True

            # Kill the ball (it'll respawn itlearn shortly).
            bs.timer(1.0, learn._flash_ball_spawn)
            def do():
                activity = bs.getactivity()
                learn._ball.node.velocity = (0, 0, 0)
                learn._ball.node.position = learn._ball_spawn_pos

                team0 = []
                team1 = []

                scorer = learn.last_touched
                loser = None

                for p in activity.players:
                    if not p.actor or not p.actor.node.exists():
                        continue

                    if p is scorer:
                        continue

                    if p.team.id == 0:
                        team0.append(p)
                    else:
                        team1.append(p)

                mid0 = len(team0) // 2
                mid1 = len(team1) // 2

                for p in team0[:mid0]:
                    if p == scorer:
                        continue
                    if p is None:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                    )

                for p in team0[mid0:]:
                    if p == scorer:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(-10.6, 0, 0), angle=90)
                    )

                for p in team1[:mid1]:
                    if p == scorer:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(10.6, 0, 0), angle=270)
                    )

                for p in team1[mid1:]:
                    if p == scorer:
                        continue
                    p.actor.node.handlemessage(
                        bs.StandMessage(position=(10.6, 0, 0), angle=270)
                    )


                scorer.actor.node.handlemessage(
                    bs.StandMessage(position=(10.6, 0, 0), angle=90)
                )
                learn.deactivated = False

            bs.timer(2.0, do)

            learn.last_touched.actor.node.handlemessage('celebrate', 2000)
            def give_back():
                if not learn.last_touched: return
                learn.last_touched.actor.connect_controls_to_player()
            def stun_scorer():
                if not learn.last_touched: return
                learn.last_touched.actor.disconnect_controls_from_player()
                bs.timer(1, give_back)
            bs.timer(2, stun_scorer)

            light = bs.newnode('light',
                               attrs={
                                   'position': learn._ball.node.position,
                                   'height_attenuated': False,
                                   'color': (1, 0.5, 0)
                               })
            bs.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
            bs.timer(1.0, light.delete)

            bs.cameraflash(duration=10.0)
            learn._update_scoreboard()



    def process_nearest_player(learn):
        if learn.deactivated:
            return
        if learn.owner:
            return
        activity = bs.getactivity()
        closest_player = None
        learn.help_timer -= 1/60
        closest_distance = 9999
        learn._ball.node.velocity = (learn._ball.node.velocity[0] * 0.9, learn._ball.node.velocity[1], learn._ball.node.velocity[2] * 0.9)

        # Trouver le joueur le plus proche
        for p in activity.players:
            if not p.actor or not p.actor.node.exists():
                continue
            p.actor.node.hold_node = None

            distance = math.dist(p.actor.node.position, learn._ball.node.position)
            if distance < closest_distance:
                closest_player = p
                closest_distance = distance

        not_scoring = (math.dist((-10.6, 2, 0), learn._ball.node.position) > 1.2 and math.dist((10.6, 2, 0), learn._ball.node.position) > 1.2)

        if closest_player and closest_distance <= PICKUP_RANGE and closest_player.actor.node.pickup_pressed and learn.owner is None and closest_player.actor.flash_timer <= 0 and not learn.shooting and not_scoring:
            learn.owner = closest_player #plus simple a dev apres
            audio.catch.play()
            learn.last_touched = closest_player
            learn.ball_took_anim()
            learn._ball.last_players_to_touch[closest_player.team.id] = closest_player
            closest_player.actor.flash_timer = 0.25
            if not learn.tutorial_p and learn.tutorial:
                bs.animate(learn.help, 'opacity', {0: 0.65, 1: 0})
                learn.tutorial_p = True
                bs.animate_array(learn.text, 'color', 4, {0: (0.5, 1, 0.5, 0.65), 1: (0,0,0,0)})
                if learn.tutorial_d and learn.tutorial_t:
                    bs.timer(1, learn.help.delete)

                if not learn.tutorial_t:
                    learn.text.text = 'Punch to shoot the ball.\n Looking at a friend can also pass !'
                    learn.help.tint_color = (0,0,1)
                    learn.help.tint_texture = bs.gettexture('buttonPunch')
                    learn.help.mask_texture = bs.gettexture('buttonPunch')
                    bs.animate(learn.help, 'opacity', {0: 0.65, 0.5: 0, 1: 0.65})
                    bs.animate_array(learn.text, 'color', 4, {0: (0.5, 1, 0.5, 0.65), 1: (0.5, 0.5, 1, 0.65)})






    def process_nearest_blocker(learn):
        if learn.deactivated:
            return
        if learn.owner:
            return
        if not learn.blockable:
            return
        activity = bs.getactivity()
        closest_player = None
        closest_distance = 9999
        learn._ball.node.velocity = (learn._ball.node.velocity[0] * 0.9, learn._ball.node.velocity[1], learn._ball.node.velocity[2] * 0.9)

        # Trouver le joueur le plus proche
        for p in activity.players:
            if not p.actor or not p.actor.node.exists():
                continue
            if learn.last_touched == p:
                continue
            p.actor.node.hold_node = None

            distance = math.dist(p.actor.node.position, learn._ball.node.position)
            if distance < closest_distance:
                closest_player = p
                closest_distance = distance
        if closest_player is None:
            return


        if closest_player.actor.node.bomb_pressed and learn.shooting and closest_player.actor.express_timer <= 0 and learn.blockable or closest_player.actor.node.bomb_pressed and learn.passing:
            closest_player.actor.express_timer = 0.05
            not_scoring = (math.dist((-10.6, 2, 0), learn._ball.node.position) > 2 and math.dist((10.6, 2, 0),learn._ball.node.position) > 2)
            if math.dist(closest_player.actor.node.position, learn._ball.node.position) < 4 and not_scoring and abs(closest_player.actor.node.position[0] - learn._ball.node.position[0]) <= (1.25 if not learn.mi else 1):
                closest_player.actor.express_timer = 12
                closest_player.actor.node.handlemessage('hurt_sound')
                tex = bs.gettexture('bombButton')
                closest_player.actor.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000.0)
                closest_player.actor.node.mini_billboard_2_start_time = t_ms
                closest_player.actor.node.mini_billboard_2_end_time = (
                        t_ms + 12000
                )
                learn.last_touched.actor.node.handlemessage('knockout', 100)
                learn.last_touched.actor.flash_timer = 0.5
                closest_player.actor.on_jump_press()
                closest_player.actor.on_jump_release()
                closest_player.actor.mvp += 5
                closest_player.actor.per = min(100, closest_player.actor.per + 12)

                for i in range(100):
                    closest_player.actor.node.hold_node = learn._ball.node
                learn.last_touched.actor.flash_timer = 0.5
                fwd = closest_player.actor.node.position_forward
                p_pos = closest_player.actor.node.torso_position
                dir_vec = (fwd[0] - p_pos[0], fwd[1] - p_pos[1], fwd[2] - p_pos[2])
                length = math.sqrt(dir_vec[0] ** 2 + dir_vec[1] ** 2 + dir_vec[2] ** 2) ** 0.5
                dir_norm = (dir_vec[0] / length, 0.0, dir_vec[2] / length)

                in_front = (
                    p_pos[0] - dir_norm[0] * 100,
                    p_pos[1],
                    p_pos[2] - dir_norm[2] * 100
                )
                direction = (bs.Vec3(in_front) - bs.Vec3(p_pos)).normalized()
                vel = (direction * 5)
                learn._ball.node.velocity = (vel.x, vel.y, vel.z)
                closest_player.actor.node.hockey = True
                closest_player.actor.connect_controls_to_player(enable_jump=False)
                learn.blocked = True

                def back():
                    learn._ball.node.velocity = (vel.x, vel.y, vel.z)
                    closest_player.actor.node.hockey = False
                    learn.owner = closest_player


                bs.timer(0.15, back)

                def own():
                    if learn.last_touched == closest_player:
                        learn.owner = closest_player
                bs.timer(1.3, own)

                def can_jump():
                    closest_player.actor.connect_controls_to_player()
                    learn.blocked = False

                bs.timer(1.2, can_jump)


                duration = 0.05
                fps = 240
                frames = int(duration * fps)
                dt = 1 / fps
                step = 0
                start_pos_learn = (closest_player.actor.node.position[0], closest_player.actor.node.position[1] - 1.1,
                                  closest_player.actor.node.position[2])
                learn.swap_timer = None

                def lerp(a, b, t):
                    return (
                        a[0] + (b[0] - a[0]) * t,
                        a[1] + (b[1] - a[1]) * t,
                        a[2] + (b[2] - a[2]) * t
                    )

                def do_swap():
                    nonlocal step

                    t = step / frames

                    pos = closest_player.actor.node.torso_position
                    fwd = learn._ball.node.position

                    dx = fwd[0] - pos[0]
                    dz = fwd[2] - pos[2]

                    length = math.sqrt(dx * dx + dz * dz)
                    if length > 0.0001:
                        dx /= length
                        dz /= length

                    angle = math.degrees(math.atan2(-dx, -dz))

                    closest_player.actor.node.handlemessage(
                        bs.StandMessage(
                            position=lerp(start_pos_learn, (learn._ball.node.position[0], learn._ball.node.position[1] - 1, learn._ball.node.position[2]), t), angle=angle))
                    explosion = bs.newnode('explosion',
                                           attrs={'position': closest_player.actor.node.position,
                                                  'color': closest_player.actor.node.color,
                                                  'radius': 0.5, 'big': False})
                    bs.timer(2, explosion.delete)

                    step += 1
                    if step >= frames:
                        learn.owner = closest_player
                        learn.swap_timer = None


                learn.swap_timer = bs.Timer(dt, do_swap, repeat=True)

    def parabola(learn, begin, end, start_time, duration, end_owner=None, perfect=False):
        learn.parabola_timer = None
        learn.owner.actor.node.hold_node = None
        learn.owner = None
        distance = math.dist(begin, end)
        height = (distance / 2.4) if not perfect else 7 # BAHAHA
        if perfect:
            learn.blockable = False
        else:
            learn.blockable = True



        def shot():
            t = (bs.time() - start_time) * duration
            t = max(0, min(1, t))
            if not perfect:
                if t >= 1 or (learn.blocked and not perfect) or learn._ball.node.position[0] > 12 or learn._ball.node.position[
                    0] < -12 or learn._ball.node.position[2] > 7.5 or learn._ball.node.position[2] < -7.5:
                    learn.parabola_timer = None
                    learn.shooting = False
                    learn.passing = False
                    if not learn.blocked:
                        learn._ball.node.velocity = (learn._ball.node.velocity[0] / 2, learn._ball.node.velocity[1]/1.25,
                                              learn._ball.node.velocity[2] / 3)
                    if end_owner:
                        learn.owner = end_owner
                    return
            else:
                if t >= 1:
                    learn.parabola_timer = None
                    learn.shooting = False
                    learn.passing = False
                    learn.last_touched.actor.per = 0
                    if not learn.blocked:
                        learn._ball.node.velocity = (learn._ball.node.velocity[0] / 2, learn._ball.node.velocity[1]/1.25,
                                              learn._ball.node.velocity[2] / 3)
                    return
            if perfect:
                learn.last_touched.actor.per /= 1.01
            explosion = bs.newnode('explosion',
                                   attrs={'position': (learn._ball.node.position[0] + random.uniform(-0.5, 0.5), learn._ball.node.position[1] + random.uniform(-0.1, 0.1), learn._ball.node.position[2] + random.uniform(-0.5, 0.5)) if perfect else learn._ball.node.position, 'color': (end_owner.actor.node.color if end_owner else (0.1,0.1,0.1)) if not perfect else learn.last_touched.actor.node.color,
                                          'radius': 0.4 if not perfect else random.uniform(0.1, 0.7), 'big': False if not perfect else True})
            bs.timer(2, explosion.delete)
            if end_owner:
                fin = end_owner.actor.node.position
            else:
                fin = end
            x = begin[0] + (fin[0] - begin[0]) * t
            y = begin[1] + (fin[1] - begin[1]) * t + (height if not end_owner else 3) * 4 * t * (1 - t)
            z = begin[2] + (fin[2] - begin[2]) * t

            learn._ball.node.position = (x,y,z)

        learn.parabola_timer = bs.Timer(1/360, shot, repeat = True)



    def process_nearest_stealer(learn):

        if learn.deactivated:
            return
        if not learn.owner:
            return
        if learn.shooting:
            return
        activity = bs.getactivity()
        closest_player = None
        closest_distance = 9999
        can_start = False

        # Trouver le joueur le plus proche
        for p in activity.players:
            if not p.actor or not p.actor.node.exists() or p == learn.owner:
                continue
            p.actor.node.hold_node = None
            if len(activity.players) > 1:
                can_start = True

            distance = math.dist(p.actor.node.position, learn._ball.node.position)
            if distance < closest_distance:
                closest_player = p
                closest_distance = distance

        if not can_start:
            return

        is_ready = closest_player.actor.flash_timer <= 0

        if closest_player and closest_distance <= STEALING_RANGE and closest_player.actor.node.pickup_pressed and is_ready:
            dx = learn.owner.actor.node.move_left_right
            dz = -learn.owner.actor.node.move_up_down

            if abs(dx) < 0.1 and abs(dz) < 0.1:
                vel = learn.owner.actor.node.velocity
                dx = vel[0]
                dz = vel[2]

            length = math.hypot(dx, dz)
            if length < 0.1:
                return

            dx /= length
            dz /= length

            speed = math.hypot(learn.owner.actor.node.velocity[0], learn.owner.actor.node.velocity[2])
            boost = max(140, min(speed * 60, 180))
            boost /= 2

            bs.emitfx(
                position=learn.owner.actor.node.position,
                velocity=(dx * 2.5, -1.0, dz * 2.5),
                chunk_type='spark',
                count=6,
                scale=boost / 160,
                spread=0.3
            )

            pos = learn.owner.actor.node.position
            for i in range(6):
                learn.owner.actor.node.handlemessage(
                    'impulse',
                    pos[0], pos[1] + 0.2 + i * 0.1, pos[2],
                    0, 0, 0,
                    boost,
                    boost,
                    0, 0,
                    dx, 0, dz
                )
            if learn.protected and learn.owner.actor.node.invincible:
                closest_player.actor.flash_timer = 1
                learn.owner.actor.flash_timer -= 2
                closest_player.actor.node.handlemessage('knockout', (300 if closest_player.actor.mvp <= learn.owner.actor.mvp else 375) if not learn.mi else 500)
                sfx = random.choice([audio.anklebreak,audio.rattlebones, audio.connect])
                learn.owner.actor.per = min(100, learn.owner.actor.per + 8)
                closest_player.actor.per = max(0, closest_player.actor.per - 8)
                sfx.play(volume=1.75)
                learn.protected = False
                if learn.owner:
                    learn.owner.actor.node.invincible = False
                return
            learn.owner.actor.node.hold_node = None
            # Punit l'owner présent
            learn.owner.actor.node.handlemessage('knockout', 150)
            learn.owner.actor.flash_timer = 1.5
            audio.catch.play()
            # Changer owner
            learn.owner = closest_player #plus simple a dev apres
            learn.last_touched = closest_player
            learn.ball_took_anim()
            learn._ball.last_players_to_touch[closest_player.team.id] = closest_player
            learn.last_touched = closest_player
            closest_player.actor.flash_timer = 1.5




    def process_dribbling(learn):
        if learn.owner is None:
            return

        if learn.owner:
            if learn.help and learn.tutorial:
                if learn.owner.actor.node.punch_pressed:
                    if not learn.tutorial_t:
                        learn.tutorial_t = True
                        # Si le bomb n'est pas encore fait, on affiche le message pour le bomb
                        if not learn.tutorial_d:
                            learn.text.text = 'Press bomb to dribble when you have the ball (2x).\nWithout the ball you can block a mid-air ball.'
                            learn.help.tint_color = (1, 0, 0)
                            learn.help.tint_texture = bs.gettexture('buttonBomb')
                            learn.help.mask_texture = bs.gettexture('buttonBomb')
                            bs.animate(learn.help, 'opacity', {0: 0.65, 0.5: 0, 1: 0.65})
                            bs.animate_array(learn.text, 'color', 4, {0: (1, 0.5, 0.5, 0.65), 1: (1, 0.5, 0.5, 0.65)})

                    # Vérification de fin globale
                    if learn.tutorial_d and learn.tutorial_t:
                        learn.text.text = 'Now you know the basics !\n Have fun !'
                        bs.animate_array(learn.text, 'color', 4,
                                         {0: (1, 0.5, 0.5, 0.65), 1: (0.5, 1, 0.5, 0.65), 2: (0.5, 0.5, 1, 0.65),
                                          4: (0, 0, 0, 0)})
                        bs.animate(learn.help, 'opacity', {0: 0.65, 2: 0})
                        bs.timer(4.0, learn.help.delete)

                # 2. Gestion du BOMB
                if learn.owner.actor.node.bomb_pressed:
                    if not learn.tutorial_d:
                        learn.tutorial_d = True
                        # Si le punch n'est pas encore fait, on affiche le message pour le punch
                        if not learn.tutorial_t:
                            learn.text.text = 'Punch to shoot the ball.'
                            learn.help.tint_color = (0, 0, 1)
                            learn.help.tint_texture = bs.gettexture('buttonPunch')
                            learn.help.mask_texture = bs.gettexture('buttonPunch')
                            bs.animate(learn.help, 'opacity', {0: 0.65, 0.5: 0, 1: 0.65})
                            bs.animate_array(learn.text, 'color', 4, {0: (0.5, 1, 0.5, 0.65), 1: (0.5, 0.5, 1, 0.65)})

                    # Vérification de fin globale
                    if learn.tutorial_t and learn.tutorial_d:
                        learn.text.text = 'Now you know the basics !\n Have fun !'
                        bs.animate_array(learn.text, 'color', 4,
                                         {0: (1, 0.5, 0.5, 0.65), 1: (0.5, 1, 0.5, 0.65), 2: (0.5, 0.5, 1, 0.65),
                                          4: (0, 0, 0, 0)})
                        bs.animate(learn.help, 'opacity', {0: 0.65, 2: 0})
                        bs.timer(4, learn.help.delete)
            learn.owner.actor.impact_scale = 0
            n = learn.owner.actor.node
            if n.position[0] > 12.5 or n.position[
                    0] < -12.5 or n.position[2] > 8 or n.position[2] < -8:
                learn.owner.actor.node.handlemessage(bs.StandMessage(position=((-10.6, 0, 0) if learn.owner.team.id == 0 else (10.6, 0, 0))))
                learn.owner.actor.per = max(0, learn.owner.actor.per - 5)
                learn.owner.actor.mvp -= 3
                learn.owner.actor.node.handlemessage('knockout', 80)
                learn.owner = None
                learn._ball.node.position = learn._ball_spawn_pos

            if learn.owner.actor.node.invincible:
                person = learn.owner
                def _():
                    person.actor.node.invincible = False
                bs.timer(1, _)
            owner = learn.owner
            if not learn.shooting:
                learn.owner.actor.node.hold_node = None
            fwd = owner.actor.node.position_forward
            p_pos = owner.actor.node.torso_position
            dir_vec = (fwd[0] - p_pos[0], fwd[1] - p_pos[1], fwd[2] - p_pos[2])
            length = math.sqrt(dir_vec[0] ** 2 + dir_vec[1] ** 2 + dir_vec[2] ** 2) ** 0.5

            if length <= 0.0001:
                dir_norm = (0.0, 0.0, 1.0)
            else:
                dir_norm = (dir_vec[0] / length, 0.0, dir_vec[2] / length)

            right_norm = (-dir_norm[2], 0.0, dir_norm[0])

            dist = -1.1

            in_front = (
                p_pos[0] + (dir_norm[0] * dist) + (right_norm[0] * dist * 1.2),
                (abs(math.sin(bs.time() * (8 if learn.owner.actor.node.run > 0 else 4)) * 0.8) + p_pos[1]) if not learn.shooting else p_pos[1] + 0.7,
                p_pos[2] + (dir_norm[2] * dist) + (right_norm[2] * dist * 1.2)
            )
            learn._ball.node.position = in_front

            def dribble():
                if not learn.owner:
                    return
                if learn._ball.node.position[1] < learn.owner.actor.node.position[1] + .25 and learn.owner.actor.ultra_timer <= 0:
                    learn.owner.actor.ultra_timer = 0.1
                    audio.rebound.play(volume = 0.4)
                    learn.owner.actor.node.handlemessage('celebrate_r', 500)

            dribble()

            if owner.actor.node.bomb_pressed and not learn.shooting and not learn.protected and learn.owner.actor._tech_timer <= 0:
                learn.protected = True
                learn.owner.actor.node.hockey = True
                learn.owner.actor._uses += 1
                learn.owner.actor._tech_timer = 0.25
                audio = random.choice([audio.squeak1, audio.squeak2, audio.squeak3])
                audio.play(random.uniform(0.2, 0.6))
                if learn.owner.actor._uses >= 2:
                    learn.owner.actor._tech_timer = 9
                    tex = bs.gettexture('buttonBomb')
                    owner.actor.node.mini_billboard_3_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    owner.actor.node.mini_billboard_3_start_time = t_ms
                    owner.actor.node.mini_billboard_3_end_time = (
                            t_ms + 9000
                    )
                    learn.owner.actor._uses = 0
                    learn.owner.actor.node.hockey = False
                learn.owner.actor.node.invincible = True
                persone = learn.owner
                personel = 0
                activity = bs.getactivity()
                for p in activity.players:
                    if not p.actor or not p.actor.node.exists():
                        continue
                    if p.team.id == 0:
                        personel += 1
                def normal():
                    if learn.owner is not None:
                        learn.owner.actor.node.hockey = False
                    else:
                        persone.actor.node.hockey = False
                def unprotect():
                    if learn.owner:
                        learn.protected = False
                        learn.owner.actor.node.invincible = False
                        if learn.owner.actor._uses >= 2:
                            learn.owner.actor._uses = 0
                    else:
                        persone.actor._tech_timer = 1
                        persone.actor.node.invincible = False
                        if persone.actor._uses >= 3:
                            persone.actor._uses = 0

                duration = 0.05
                closest_player = learn.owner
                fps = 360
                frames = int(duration * fps)
                dt = 1 / fps
                step = 0
                start_pos_learn = (closest_player.actor.node.position[0], closest_player.actor.node.position[1] - 1.1,
                                  closest_player.actor.node.position[2])
                base_pos = learn._ball.node.position
                learn.swap_timer = None

                fwd = closest_player.actor.node.position_forward
                p_pos = closest_player.actor.node.position
                dir_vec = (fwd[0] - p_pos[0], fwd[1] - p_pos[1], fwd[2] - p_pos[2])
                length = math.sqrt(dir_vec[0] ** 2 + dir_vec[1] ** 2 + dir_vec[2] ** 2) ** 0.5
                dir_norm = (dir_vec[0] / length, dir_vec[1] / length, dir_vec[2] / length)
                dribbles = closest_player.actor._uses + 1

                pos2 = (p_pos[0] - dir_norm[0] * (16 / dribbles),
                       p_pos[1] - 1.1,
                       p_pos[2] - dir_norm[2] * (25 / dribbles))

                def lerp(a, b, t):
                    return (
                        a[0] + (b[0] - a[0]) * t,
                        a[1] + (b[1] - a[1]) * t,
                        a[2] + (b[2] - a[2]) * t
                    )

                def do_swap():
                    nonlocal step

                    t = step / frames

                    pos = closest_player.actor.node.torso_position
                    fwd = closest_player.actor.node.position_forward

                    dx = fwd[0] - pos[0]
                    dz = fwd[2] - pos[2]

                    length = math.sqrt(dx * dx + dz * dz)
                    if length > 0.0001:
                        dx /= length
                        dz /= length

                    angle = math.degrees(math.atan2(dx, dz))

                    closest_player.actor.node.handlemessage(
                        bs.StandMessage(
                            position=lerp(start_pos_learn, pos2, t), angle=angle))
                    learn._ball.node.position = lerp(base_pos, pos2, t)
                    explosion = bs.newnode('explosion',
                                           attrs={'position': closest_player.actor.node.position,
                                                  'color': (closest_player.actor.node.color[0]/2, closest_player.actor.node.color[1]/2,closest_player.actor.node.color[2]/2),
                                                  'radius': 0.35, 'big': False})
                    bs.timer(1, explosion.delete)

                    step += 1
                    if step >= frames:
                        learn.owner = closest_player
                        learn.swap_timer = None
                    else:
                        learn.owner = None

                learn.swap_timer = bs.Timer(dt, do_swap, repeat=True)
                bs.timer(0.2, normal)
                bs.timer(0.35, unprotect)



            if owner.actor.node.punch_pressed and owner.actor.per >= 98 and 1 > 2:
                learn.shooting = True
                learn.protected = True
                step = 0

                owner.actor.disconnect_controls_from_player()
                owner.actor.node.hold_node = learn._ball.node
                learn.begginning_x = learn._ball.node.position
                pos = owner.actor.node.torso_position
                fwd = bs.Vec3(10.6, p_pos[1], 0) if learn.owner.team.id == 0 else bs.Vec3(-10.6, p_pos[1], 0)

                dx = fwd[0] - pos[0]
                dz = fwd[2] - pos[2]

                length = math.sqrt(dx * dx + dz * dz)
                if length > 0.0001:
                    dx /= length
                    dz /= length

                angle = math.degrees(math.atan2(dx, dz))
                owner.actor.node.handlemessage(bs.StandMessage(position=(owner.actor.node.position[0], owner.actor.node.position[1] - 1, owner.actor.node.position[2]), angle=angle))
                before = owner.actor.node.color
                present_sky_color = bs.getactivity().globalsnode.tint
                sky_color = bs.getactivity().globalsnode
                bs.animate_array(sky_color, 'tint', 3,
                                 {0: present_sky_color, 0.6: (0.8, 0.8, 0.8), 1.2: (0.7,0.7,0.7), 1.8: (.5,.5,.5), 2: present_sky_color})
                def calculate_to_throw():
                    if not self.owner:
                        return
                    learn.slow_motion = False
                    bs.getsound("explosion04").play()
                    learn.protected = False
                    learn.last_touched = owner

                    #1 marque gauche ; 0 marque droite

                    if learn.owner.team.id == 0:
                        target = bs.Vec3(10.6, p_pos[1], 0)
                    else:
                        target = bs.Vec3(-10.6, p_pos[1], 0)

                    dist = math.dist(target, learn.last_touched.actor.node.position)
                    cible = (target[0], 2, target[2])
                    begin = learn._ball.node.position
                    end = cible
                    start_time = bs.time()
                    duration = 0.7 if dist > 10 else 1
                    learn.owner.actor.node.handlemessage('knockout', 20)
                    learn.owner.actor.connect_controls_to_player()
                    learn.parabola(begin, end, start_time, duration, perfect=True)

                def jump():
                    learn.owner.actor.on_jump_press()
                    learn.owner.actor.on_jump_release()
                    learn.slow_motion = True

                    def do_jump():
                        learn.owner.actor.node.handlemessage(
                            'impulse',
                            learn.owner.actor.node.position[0],
                            learn.owner.actor.node.position[1],
                            learn.owner.actor.node.position[2],
                            0, 0, 0, 95, 95, 0, 0, 0, 1, 0
                        )
                    for i in range(3):
                        bs.timer(0.1 * i, do_jump)


                def lightning():
                    nonlocal step
                    bs.animate_array(owner.actor.node, 'color', 3, {0: before, 0.05: (4,4,4), 0.15: (4,4,4), 0.6: before})
                    bs.getsound("clack").play()
                    mat2 = bs.Material()
                    mat2.add_actions(
                        actions=(
                            ('modify_node_collision', 'collide', False),
                        )
                    )
                    box = bs.newnode(
                        'prop',
                        attrs={
                            'body': 'puck',
                            'position': (owner.actor.node.position[0] + (0.87 if owner.team.id == 1 else -0.87), owner.actor.node.position[1]+0.25, owner.actor.node.position[2]),
                            'mesh_scale': 1,
                            'mesh': bs.getmesh('textbox' if random.random() < 0.5 else 'textbox2'),
                            'color_texture': bs.gettexture('starimg'),
                            'reflection': 'soft',
                            'reflection_scale': [random.uniform(0,1)],
                            'shadow_size': 0.5,
                            'gravity_scale': 0,
                            'materials': [mat2],
                        },
                    )
                    begin = box.position
                    end = (box.position[0], box.position[1]+0.5, box.position[2])
                    bs.animate_array(box, 'position', 3, {0: begin, 0.5: end, 0.6: begin})
                    bs.timer(0.6, box.delete)
                    step += 1
                    if step != 3:
                        bs.timer(0.6, lightning)
                    else:
                        bs.timer(0.7, calculate_to_throw)
                        bs.timer(0.3, jump)
                lightning()

            if owner.actor.node.punch_pressed and not learn.shooting and not owner.actor.node.pickup_pressed and owner.actor.per < 9800:
                learn.shooting = True
                learn.protected = True
                learn.owner.actor.flash_timer = 2
                bs.getsound('swish').play(0.4)

                owner.actor.disconnect_controls_from_player()
                owner.actor.node.hold_node = learn._ball.node
                learn.begginning_x = learn._ball.node.position
                activity = bs.getactivity()
                learn.passing = False

                if learn.owner.actor._tech_timer <= 0 and len(activity.players) > 1:
                    fwd = owner.actor.node.position_forward
                    p_pos = owner.actor.node.torso_position
                    dir_vec = (fwd[0] - p_pos[0], fwd[1] - p_pos[1], fwd[2] - p_pos[2])
                    length = math.sqrt(dir_vec[0] ** 2 + dir_vec[1] ** 2 + dir_vec[2] ** 2) ** 0.5
                    dir_norm = (dir_vec[0] / length, dir_vec[1] / length, dir_vec[2] / length)

                    player_pos = bs.Vec3(owner.actor.node.torso_position)
                    forward_point = bs.Vec3(owner.actor.node.position_forward)

                    forward = (player_pos - forward_point).normalized()


                    player = learn.owner
                    if not activity:
                        return

                    best_teammate = None
                    highest_precision = -2.0  # Le dot product va de -1 à 1, donc -2 est une valeur sûre pour démarrer
                    minimum_precision = 0.5

                    for p in activity.players:
                        if p is player:
                            continue

                        if not p.actor or not p.actor.node.exists() or p.team is not player.team:
                            continue

                        target = bs.Vec3(p.actor.node.position)
                        player_pos = bs.Vec3(player.actor.node.position)

                        to_target = (target - player_pos).normalized()
                        dot = forward.dot(to_target)


                        # Comparaison : on cherche le dot product le plus élevé (le plus proche de 1.0)
                        if highest_precision < dot and dot > minimum_precision:
                            highest_precision = dot
                            best_teammate = p

                    if best_teammate:
                        dist_from_mate = math.dist(best_teammate.actor.node.position, owner.actor.node.position)
                        learn.passing = True
                        learn.shooting = True
                        learn.owner.actor._tech_timer = 1
                        learn.owner.actor.flash_timer = 1
                        learn.owner.actor.node.handlemessage('knockout', 20)
                        learn.owner.actor.connect_controls_to_player()
                        learn.parabola(learn.owner.actor.node.position, best_teammate.actor.node.position, bs.time(), 1.3, end_owner=best_teammate)
                def calculate_to_throw():
                    learn.protected = False
                    learn.last_touched = owner
                    fwd = owner.actor.node.position_forward
                    p_pos = owner.actor.node.torso_position
                    dir_vec = (fwd[0] - p_pos[0], fwd[1] - p_pos[1], fwd[2] - p_pos[2])
                    length = math.sqrt(dir_vec[0] ** 2 + dir_vec[1] ** 2 + dir_vec[2] ** 2) ** 0.5
                    dir_norm = (dir_vec[0] / length, dir_vec[1] / length, dir_vec[2] / length)

                    player_pos = bs.Vec3(owner.actor.node.torso_position)
                    forward_point = bs.Vec3(owner.actor.node.position_forward)

                    forward = (player_pos - forward_point).normalized()

                    #1 marque gauche ; 0 marque droite

                    if learn.owner.team.id == 0:
                        target = bs.Vec3(10.6, p_pos[1], 0)
                    else:
                        target = bs.Vec3(-10.6, p_pos[1], 0)
                    to_target = (target - player_pos).normalized()

                    dot = forward.dot(to_target)
                    dist = math.dist(target, player_pos)
                    precision = dot * 100  # pct



                    def spin(start_time, duration):
                        if not learn._ball: return
                        if learn._ball.scored: return
                        if not learn.mi: return

                        side = 0 if learn._ball.node.position[0] > 0 else 1

                        start_pos = learn._ball.node.position

                        fade_time = 0.2
                        start_radius = 0.57
                        if random.random() < (0.8 if not learn.mi else 0.4):
                            shrink_speed = 0.15
                        else:
                            shrink_speed = -0.15

                        learn.spin_timer = None
                        learn.shooting = True

                        def spun():
                            if not learn._ball: return
                            if learn._ball.scored: return

                            t = bs.time() - start_time

                            if t >= duration or learn.blocked:
                                learn.blocked = False
                                learn.spin_timer = None
                                learn.shooting = False
                                return

                            angle = t * 4

                            # rayon qui diminue lentement
                            radius = max(0.05, start_radius - t * shrink_speed)

                            circle_x = (10.3 + math.cos(angle) * radius) if side == 0 else (
                                        -10.3 + math.cos(angle) * radius)
                            circle_y = target[1] + 1.55
                            circle_z = target[2] + math.sin(angle) * radius

                            if t < fade_time:
                                fade = t / fade_time

                                x = start_pos[0] + (circle_x - start_pos[0]) * fade
                                y = start_pos[1] + (circle_y - start_pos[1]) * fade
                                z = start_pos[2] + (circle_z - start_pos[2]) * fade
                            else:
                                x = circle_x
                                y = circle_y
                                z = circle_z

                            learn._ball.node.position = (x, y, z)

                        learn.spin_timer = bs.Timer(1 / 360, spun, repeat=True)

                    if dot > (0.35 if not learn.mi else 0.6) and dist <= 7 or dot >= (0.5 if not learn.mi else 0.7) and dist <= 10.75 or dot > (0.61 if not learn.mi else 0.75) and dist <= 13:
                        # Il regarde le but
                        if not learn.mi:
                            cible = (target[0], 2, target[2])
                            if random.random() <= 0.25 and precision <= 47:
                                cible = (target[0] + random.uniform(-1, 0), random.uniform(1, 4),
                                         target[2] + random.uniform(-1, 1))
                            elif random.random() <= 0.65 and precision <= 65:
                                cible = (target[0], 2, target[2] + random.uniform(-0.6, 0.6))
                                bs.timer(0.8, lambda: spin(bs.time(), 2))
                        else:
                            cible = (target[0], 2, target[2])
                            if random.random() <= 0.5 and precision <= 68:
                                cible = (target[0] + random.uniform(-1, 0), random.uniform(1, 5),
                                         target[2] + random.uniform(-1, 1))
                            if random.random() <= 0.4 and precision >= 68:
                                cible = (target[0], 2, target[2] + random.uniform(-0.6, 0.6))
                                bs.timer(0.8, lambda: spin(bs.time(), 2))
                    else:
                        cible = (
                            p_pos[0] - dir_norm[0] * 20,
                            p_pos[1] - 0.5,
                            p_pos[2] - dir_norm[2] * 20
                        )
                        if random.random() <= 0.8 and precision <= 75 and dist <= 7:
                            cible = (target[0] + random.uniform(-1, 0), random.uniform(1, 5),
                                     target[2] + random.uniform(-1, 1))
                        if random.random() <= 0.4 and precision >= 75 and dist <= 7:
                            cible = (target[0], 2, target[2] + random.uniform(-0.6, 0.6))
                            bs.timer(0.8, lambda: spin(bs.time(), 2))
                    #(begin, end, start_time, duration)
                    begin = learn._ball.node.position
                    if dist <= 2.4:
                        learn.can_score = False
                        bs.timer(0.7, lambda: setattr(learn, 'can_score', True))
                        cible = (
                            p_pos[0] - dir_norm[0] * 10,
                            p_pos[1] - 0.5,
                            p_pos[2] - dir_norm[2] * 10
                        )
                    end = cible
                    start_time = bs.time()
                    duration = 1.2 if dist < 6.5 else 0.9
                    learn.owner.actor.node.handlemessage('knockout', 20)
                    learn.owner.actor.connect_controls_to_player()
                    learn.parabola(begin, end, start_time, duration)
                def jump():
                    learn.owner.actor.on_jump_press()
                    learn.owner.actor.on_jump_release()

                    def do_jump():
                        learn.owner.actor.node.handlemessage(
                            'impulse',
                            learn.owner.actor.node.position[0],
                            learn.owner.actor.node.position[1],
                            learn.owner.actor.node.position[2],
                            0, 0, 0, 95, 95, 0, 0, 0, 2, 0
                        )

                    bs.timer(0.1, do_jump)
                    bs.timer(0.2, do_jump)
                    for i in range(2):
                        bs.timer(0.1 * i, do_jump)

                if not learn.passing:
                    bs.timer(0.3, jump)
                    bs.timer(0.6, calculate_to_throw)




            #perte de balle si il s'évanoui
            if owner.actor.node.knockout > 0 and learn.owner:
                learn.owner.actor.per = max(0, learn.owner.actor.per - 7)
                learn.owner = None
                learn.ball_free_anim()



    def on_team_join(learn, team: Team) -> None:
        learn._update_scoreboard()

    def _handle_ball_player_collide(learn) -> None:
        collision = bs.getcollision()
        try:
            ball = collision.sourcenode.getdelegate(Ball, True)
            player = collision.opposingnode.getdelegate(PlayerSpaz,
                                                        True).getplayer(
                                                            Player, True)
        except bs.NotFoundError:
            return

        learn._ball.last_players_to_touch[player.team.id] = player

    def _kill_ball(learn) -> None:
        learn._ball = None

    def _handle_score(learn, team_index: int = None) -> None:
        assert learn._ball is not None
        assert learn._score_regions is not None

        if learn._ball.scored:
            return

        region = bs.getcollision().sourcenode
        index = 0
        for index in range(len(learn._score_regions)):
            if region == learn._score_regions[index].node:
                break

        if team_index is not None:
            index = team_index

        for team in learn.teams:
            if team.id == index:
                scoring_team = team
                team.score += 1

                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(bs.CelebrateMessage(2.0))

                if (scoring_team.id in learn._ball.last_players_to_touch
                        and learn._ball.last_players_to_touch[scoring_team.id]):
                    learn.stats.player_scored(
                        learn._ball.last_players_to_touch[scoring_team.id],
                        100, big_message=True)

                if team.score >= learn._score_to_win:
                    learn.end_game()


        # learn._foghorn_sound.play()
        learn._cheer_sound.play()

        learn._ball.scored = True

        # Kill the ball (it'll respawn itlearn shortly).
        bs.timer(1.0, learn._kill_ball)

        light = bs.newnode('light',
                           attrs={
                               'position': bs.getcollision().position,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        bs.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
        bs.timer(1.0, light.delete)

        bs.cameraflash(duration=10.0)
        learn._update_scoreboard()

    def end_game(learn) -> None:
        results = bs.GameResults()
        for team in learn.teams:
            results.set_team_score(team, team.score)
        learn.end(results=results)

    def _update_scoreboard(learn) -> None:
        winscore = learn._score_to_win
        for id, team in enumerate(learn.teams):
            learn._scoreboard.set_team_value(team, team.score, winscore)
            # learn.postes(id)

    def spawn_player(learn, player: Player) -> bs.Actor:
        if bsuSpaz is None:
            spaz = learn.spawn_player_spaz(player)
        else:
            ps.PlayerSpaz = bsuSpaz.BskSpaz
            spaz = learn.spawn_player_spaz(player)
            ps.PlayerSpaz = bsuSpaz.OldPlayerSpaz

        if learn._speed:
            spaz.node.hockey = True
        spaz.shield = bs.newnode(
            'shield',
            owner=spaz.node,
            attrs={'color': (0.3, 0.2, 2.0), 'radius': 0.0001},
        )

        spaz.node.connectattr('position_center', spaz.shield, 'position')
        spaz.shield_hitpoints = spaz.shield_hitpoints_max = 1e20
        spaz.bar = None
        spaz.flash_timer = 0
        spaz._tech_timer = 0
        spaz.express_timer = 0
        spaz.ultra_timer = 0
        spaz.impact_scale = 0
        spaz._punch_power_scale = 0
        spaz.mvp = 0
        spaz._uses = 0
        spaz.per = 0
        spaz.bomb_count = 0
        spaz.angle = 0
        spaz.rotation_direction = 0
        spaz.last_angle = 0
        spaz.total_rotation = 0

        def check_270_rotation():
            if spaz.node.exists():

                pos = spaz.node.position if spaz.node.exists() else (0,0,0)
                fwd = spaz.node.position_forward if spaz.node.exists() else (0,0,0)

                dx = fwd[0] - pos[0]
                dz = fwd[2] - pos[2]

                length = math.sqrt(dx * dx + dz * dz)
                if length > 0.0001:
                    dx /= length
                    dz /= length

                spaz.angle = math.degrees(math.atan2(-dx, -dz))  # trust
                current_angle = spaz.angle

                delta = current_angle - spaz.last_angle
                if delta > 180:
                    delta -= 360
                if delta < -180:
                    delta += 360

                current_dir = 1 if delta > 0 else -1

                if spaz.rotation_direction != 0 and current_dir != spaz.rotation_direction:
                    spaz.total_rotation = 0

                spaz.rotation_direction = current_dir

                spaz.total_rotation += abs(delta)

                if spaz.total_rotation >= 200:
                    audio = random.choice([audio.squeak1, audio.squeak2, audio.squeak3])
                    audio.play(volume=random.uniform(0.1, 0.4))
                    spaz.total_rotation = 0

                spaz.last_angle = current_angle

        spaz.check_timer2 = bs.Timer(1/120, check_270_rotation, repeat=True)

        return spaz

    def start_timer_timers(learn):
        """
        Lance un timer qui décrémente les timers du Spaz à chaque tick.
        """
        learn._timers_timer = bs.Timer(1 / 60.0, learn._update_spaz_timers, repeat=True)

    def _update_spaz_timers(learn):
        """
        Fonction appelée 60 fois par seconde pour réduire les compteurs.
        """
        # On itère sur tous les joueurs actifs
        activity = bs.getactivity()
        if not activity:
            return

        for player in activity.players:
            spaz = player.actor

            # On vérifie que le spaz existe et est vivant
            if spaz and spaz.node and spaz.node.exists():
                # Liste des attributs à décrémenter
                attrs = ['flash_timer', '_tech_timer', 'express_timer', 'ultra_timer']

                for attr in attrs:
                    val = getattr(spaz, attr, 0)
                    if val > 0:
                        # On réduit de 1/60 (soit environ 0.0166) par tick
                        setattr(spaz, attr, max(0, val - (1 / 60.0)))


    def handlemessage(learn, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)
            learn.respawn_player(msg.getplayer(Player))
        elif isinstance(msg, BallDiedMessage):
            if not learn.has_ended():
                bs.timer(3.0, learn._spawn_ball)
        else:
            super().handlemessage(msg)

    # this function called when player leave.
    def on_player_leave(learn, player: Player) -> None:
        # Augment default behavior.
        if player == learn.owner:
            learn.owner = None

    def postes(learn, team_id: int):
        if not hasattr(learn._map, 'poste_'+str(team_id)):
            setattr(learn._map, 'poste_'+str(team_id),
                    Palos(team=team_id,
                          position=Points.postes['pal_' +
                                                 str(team_id)]).autoretain())

    def _flash_ball_spawn(learn) -> None:
        light = bs.newnode('light',
                           attrs={
                               'position': learn._ball_spawn_pos,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        bs.animate(light, 'intensity', {0.0: 0, 0.25: 1, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)

    def _spawn_ball(learn) -> None:
        learn._swipsound.play()
        learn._whistle_sound.play()
        learn._flash_ball_spawn()
        assert learn._ball_spawn_pos is not None
        learn._ball = Ball(position=learn._ball_spawn_pos)
        learn._ball.node.color_texture = texture.basket
        def up():
            learn._ball.node.velocity = (0, 8, 0)
        bs.timer(0.5, up)
        def set():
            learn.deactivated = False
        bs.timer(2, set)


class Aro(bs.Actor):
    def __init__(learn, team: int = 0,
                 position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        act = learn.getactivity()
        shared = SharedObjects.get()
        setattr(learn, 'team', team)
        setattr(learn, 'locs', [])

        # Material Para; Traspasar Objetos
        learn.no_collision = bs.Material()
        learn.no_collision.add_actions(
            actions=(('modify_part_collision', 'collide', False)))

        learn.collision = bs.Material()
        learn.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        # Score
        learn._score_region_material = bs.Material()
        learn._score_region_material.add_actions(
            conditions=('they_have_material', act.ball_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', learn._annotation)))

        learn._spawn_pos = (position[0], position[1], position[2])
        learn._materials_region0 = [learn.no_collision]

        mesh = None
        tex = bs.gettexture('null')

        pmats = [learn.no_collision]
        learn.node = bs.newnode('prop',
                               delegate=learn,
                               attrs={
                                   'mesh': mesh,
                                   'color_texture': tex,
                                   'body': 'box',
                                   'reflection': 'soft',
                                   'reflection_scale': [1.5],
                                   'shadow_size': 0.1,
                                   'position': learn._spawn_pos,
                                   'materials': pmats})

        learn.scale = scale = 1.4
        bs.animate(learn.node, 'mesh_scale', {0:  0})

        pos = (position[0], position[1]+0.6, position[2])
        learn.regions: List[bs.Node] = [
            bs.newnode('region',
                       attrs={'position': position,
                              'scale': (0.6, 0.05, 0.6),
                              'type': 'box',
                              'materials': learn._materials_region0}),

            bs.newnode('region',
                       attrs={'position': pos,
                              'scale': (0.5, 0.3, 0.9),
                              'type': 'box',
                              'materials': [learn.no_collision]})
        ]
        learn.regions[0].connectattr('position', learn.node, 'position')
        # learn.regions[0].connectattr('position', learn.regions[1], 'position')

        locs_count = 9
        pos = list(position)

        try:
            id = 0 if team == 1 else 1
            color = act.teams[id].color
        except:
            color = (1, 1, 1)

        while locs_count > 1:
            scale = (1.5 * 0.1 * locs_count) + 0.8

            learn.locs.append(bs.newnode('locator',
                                        owner=learn.node,
                                        attrs={'shape': 'circleOutline',
                                               'position': (0,-100,0),
                                               'color': color,
                                               'opacity': 0,
                                               'size': [scale],
                                               'draw_beauty': True,
                                               'additive': False}))

            pos[1] -= 0.1
            locs_count -= 1

    def _annotation(learn):
        assert len(learn.regions) >= 2
        ball = learn.getactivity()._ball

        if ball:
            p = learn.regions[0].position
            ball.node.position = p
            ball.node.velocity = (0.0, 0.0, 0.0)

        act = learn.getactivity()
        act._handle_score(learn.team)

    def handlemessage(learn, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if learn.node.exists():
                learn.node.delete()
        else:
            super().handlemessage(msg)


class Cuadro(bs.Actor):
    def __init__(learn, team: int = 0,
                 position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        act = learn.getactivity()
        shared = SharedObjects.get()
        setattr(learn, 'locs', [])

        learn.collision = bs.Material()
        learn.collision.add_actions(
            actions=(('modify_part_collision', 'collide', False)))

        pos = (position[0], position[1]+0.9, position[2]+1.5)
        learn.region: bs.Node = bs.newnode('region',
                                          attrs={'position': (0,-100,0),
                                                 'scale': (0, 0, 0),
                                                 'type': 'box',
                                                 'materials': [learn.collision,
                                                               shared.footing_material]})

        # learn.shield = bs.newnode('shield', attrs={'radius': 1.0, 'color': (0,10,0)})
        # learn.region.connectattr('position', learn.shield, 'position')

        position = (position[0], position[1], position[2]+0.09)
        pos = list(position)
        oldpos = list(position)
        old_count = 14

        count = old_count
        count_y = 9

        try:
            id = 0 if team == 1 else 1
            color = act.teams[id].color
        except:
            color = (1, 1, 1)

        while (count_y != 1):

            while (count != 1):
                pos[2] += 0.19

                learn.locs.append(
                    bs.newnode('locator',
                               owner=learn.region,
                               attrs={'shape': 'circle',
                                      'position': (0,-100,0),
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

    def handlemessage(learn, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if learn.node.exists():
                learn.node.delete()
        else:
            super().handlemessage(msg)


class Palos(bs.Actor):
    def __init__(learn, team: int = 0,
                 position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = learn.getactivity()
        learn._pos = position
        learn.aro = None
        learn.cua = None

        # Material Para; Traspasar Objetos
        learn.no_collision = bs.Material()
        learn.no_collision.add_actions(
            actions=(('modify_part_collision', 'collide', False)))

        #
        learn.collision = bs.Material()
        learn.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        # Spawn just above the provided point.
        learn._spawn_pos = (position[0], position[2]+2.5, position[2])

        mesh = models.none
        tex = bs.gettexture('flagPoleColor')

        pmats = [learn.no_collision]
        learn.node = bs.newnode('prop',
                               delegate=learn,
                               attrs={
                                   'mesh': mesh,
                                   'color_texture': tex,
                                   'body': 'puck',
                                   'reflection': 'soft',
                                   'reflection_scale': [2.6],
                                   'shadow_size': 0,
                                   'is_area_of_interest': True,
                                   'position': learn._spawn_pos,
                                   'materials': pmats
                               })
        learn.scale = scale = 4.0
        bs.animate(learn.node, 'mesh_scale', {0:  scale})

        learn.loc = bs.newnode('locator',
                              owner=learn.node,
                              attrs={'shape': 'circle',
                                     'position': position,
                                     'color': (1, 1, 0),
                                     'opacity': 0,
                                     'draw_beauty': False,
                                     'additive': True})

        learn._y = _y = 0.30
        _x = -0.25 if team == 1 else 0.25
        _pos = (position[0]+_x, position[1]-1.5 + _y, position[2])
        learn.region = bs.newnode('region',
                                 attrs={
                                     'position': _pos,
                                     'scale': (0, 0, 0),
                                     'type': 'box',
                                     'materials': [learn.no_collision]})
        learn.region.connectattr('position', learn.node, 'position')

        _y = learn._y
        position = learn._pos
        if team == 0:
            pos = (position[0]-0.8, position[1] + 2.0 + _y, position[2])
        else:
            pos = (position[0]+0.8, position[1] + 2.0 + _y, position[2])

        if learn.aro is None:
            learn.aro = Aro(team, pos).autoretain()

        if learn.cua is None:
            pos = (position[0], position[1] + 1.8 + _y, position[2]-1.4)
            learn.cua = Cuadro(team, pos).autoretain()

    def handlemessage(learn, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if learn.node.exists():
                learn.node.delete()
        else:
            super().handlemessage(msg)




class BasketMap(maps.FootballStadium):
    name = 'BasketBall Stadium'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return []

    def __init__(learn) -> None:
        super().__init__()

        gnode = bs.getactivity().globalsnode
        gnode.tint = [(0.806, 0.8, 1.0476), (1.3, 1.2, 1.0)][0]
        gnode.ambient_color = (1.3, 1.2, 1.0)
        gnode.vignette_outer = (0.57, 0.57, 0.57)
        gnode.vignette_inner = (0.9, 0.9, 0.9)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5

class MGdefs():
    points, boxes = {}, {}
    points['ffaSpawn1'] = (0.14306, 0.80567, -5.0723) + (6.98794, 0.05, 0.14176)
    points['ffaSpawn2'] = (-0.09544, 0.80566, 5.21226) + (6.98794, 0.05, 0.05231)
    points['flag1'] = (-8.09005, 0.80567, 0.00816)
    points['flag2'] = (8.06579, 0.80567, 0.0181)
    points['flagDefault'] = (0.02633, 0.80567, 0.0181)
    points['powerupSpawn1'] = (-6.63926, 0.80567, -5.24116)
    points['powerupSpawn2'] = (-6.59951, 0.80566, 5.2579)
    points['powerupSpawn3'] = (6.65517, 0.80567, -4.90567)
    points['powerupSpawn4'] = (6.69964, 0.80566, 5.28176)
    points['spawn1'] = (-2.38337, 0.80567, 0.00697) + (0.89267, 0.05, 2.67802)
    points['spawn2'] = (2.46605, 0.80567, -0.07253) + (0.89267, 0.05, 2.67802)
    points['tnt1'] = (0.0096, 0.80567, -2.37324)
    boxes['area_of_interest_bounds'] = (0.00168, 4.16213, 6.15152) + (0, 0, 0) + (27.4963, 0.53218, 12.39414)
    boxes['goal1'] = (10.5, -9999, 0) + (0, 0, 0) + (0.33202, 0.33804, 0.01551)
    boxes['goal2'] = (-10.5, -9999, 0) + (0, 0, 0) + (0.36506, 0.36899, 0.01641)
    boxes['levelBounds'] = (0.00168, 2.72106, 0.13982) + (0, 0, 0) + (211.96724, 73.4671, 129.78224)
    boxes['edgeBox'] = (0.00168, 2.72106, 0.13982) + (0, 0, 0) + (211.96724, 73.4671, 129.78224)
    boxes['wall1'] = (0.0, 8.90055, 7.58755) + (0, 0, 0) + (12.55005, 9.05964, 0.31267)
    boxes['wall2'] = (0.0, 8.90055, -7.57936) + (0, 0, 0) + (12.55005, 9.05964, 0.31267)
    boxes['wall3'] = (-12.17371, 8.90055, 0.07441) + (0, 0, 0) + (0.31267, 9.05964, 12.55005)
    boxes['wall4'] = (12.13353, 8.90055, 0.03423) + (0, 0, 0) + (0.31267, 9.05964, 12.55005)
    boxes['map_bounds'] = (0.2608783669, 4.899663734, -3.543675157) + \
                          (0.0, 0.0, 0.0) + (29.23565494, 14.19991443, 29.92689344)

class Basket(bs.Map):
    defs = MGdefs()
    name = "Basket"

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'basketStadiumPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data = {}
        data['modelPole'] = models.basketpole
        data['modelBack'] = models.basketback
        data['modelRings'] = models.basketrings
        data['collide_mesh'] = models.basketcollide
        data['texPole'] = texture.basketpole
        data['ringsTex'] = texture.basketrings
        data['backTex'] = texture.basketback
        data['bgModel'] = bs.getmesh("thePadBG")
        data['bgTex'] = bs.gettexture("menuBG")
        return data

    def __init__(learn):
        super().__init__()
        shared = SharedObjects.get()
        learn.collision = bs.Material()
        learn.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))
        learn.node = bs.newnode('terrain', delegate=learn, attrs={
            'mesh': learn.preloaddata['modelPole'],
            'collide_mesh': learn.preloaddata['collide_mesh'],
            'color_texture': learn.preloaddata['texPole'],
            'materials': [learn.collision, shared.footing_material]})

        learn.back = bs.newnode('terrain', delegate=learn, attrs={
            'mesh': learn.preloaddata['modelBack'],
            'color_texture': learn.preloaddata['backTex'],
            'materials': [learn.collision,shared.footing_material]})

        learn.rings = bs.newnode('terrain', delegate=learn, attrs={
            'mesh': learn.preloaddata['modelRings'],
            'color_texture': learn.preloaddata['ringsTex'],
            'materials': [learn.collision,shared.footing_material]})

        learn.bg = bs.newnode('terrain', attrs={
            'mesh': learn.preloaddata['bgModel'],
            'lighting': False,
            'background': True,
            'color_texture': learn.preloaddata['bgTex']})

        g = bs.getactivity().globalsnode
        g.tint = (0.7,0.7,0.7)
        g.ambient_color = (1, 1, 1)
        g.vignette_outer = (0.7, 0.7, 0.7)
        g.vignette_inner = (0.9, 0.9, 0.9)
        g.vr_camera_offset = (0, -4.2, -1.1)
        g.vr_near_clip = 0.5

bs._map.register_map(Basket)

bs._map.register_map(BasketMap)

# ba_meta export babase.Plugin
class justlearn(babase.Plugin):
    def __init__(learn):
        learn.installer = ModInstaller()
        learn.installer.run_full_install()


import os
import urllib.request


class ModInstaller:
    def __init__(self) -> None:
        self.base_url = "https://raw.githubusercontent.com/Scriptz1/Learn.py-Installer/main/"

        # On définit la racine propre (en enlevant les '..')
        base_app_dir = os.path.abspath(babase.env()["python_directory_app"] + '/../')

        self.dirs = {
            'audio': os.path.join(base_app_dir, 'audio'),
            'models': os.path.join(base_app_dir, 'meshes'),  # Attention: meshes ou models selon ta version
            'collision': os.path.join(base_app_dir, 'meshes'),
            'tex': os.path.join(base_app_dir, 'textures')
        }

        self.files_to_install = [
            # ('catch.ogg', 'audio'), ('squeak1.ogg', 'audio'), ('squeak2.ogg', 'audio'),
            # ('squeak3.ogg', 'audio'), ('rebound.ogg', 'audio'), ('clean.ogg', 'audio'),
            # ('rattlebones.ogg', 'audio'), ('anklebreak.ogg', 'audio'), ('connect.ogg', 'audio'),
            ('basketCollide.cob', 'collision'), 
            # ('basketRings.bob', 'models'),
            # ('basketPole.bob', 'models'), ('basketBack.bob', 'models'),
            # ('basketball.bob', 'models'), ('none.bob', 'models'),
            ('basketStadiumPreview.dds', 'tex')
            # ('basket.dds', 'tex'), ('basketPole.dds', 'tex'),
            # , ('basketRings.dds', 'tex'),
            # ('basketballball.dds', 'tex'), ('basketBack.dds', 'tex')
        ]

    def run_full_install(self) -> None:
        def _do_install():
            try:
                # 1. Vérification : manque-t-il quelque chose ?
                missing_files = []
                for filename, folder_type in self.files_to_install:
                    dest_path = os.path.join(self.dirs[folder_type], filename)
                    if not os.path.exists(dest_path):
                        missing_files.append((filename, folder_type, dest_path))

                if not missing_files:
                    print("Tout est déjà installé, pas d'action nécessaire.")
                    return

                # 2. Installation des manquants
                bui.screenmessage("Installing Missing Assets...", color=(0, 1, 0.2))
                for filename, folder_type, dest_path in missing_files:
                    target_dir = self.dirs[folder_type]
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir, exist_ok=True)

                    print(f"Downloading {filename}...")
                    urllib.request.urlretrieve(self.base_url + filename, dest_path)

                bui.screenmessage("Installation Success !", color=(0, 1, 0.3))
                bui.getsound('ding').play(volume=2)

            except Exception as e:
                print(f"INSTALL ERROR: {e}")
                bui.screenmessage("Failed to install!", color=(1, 0, 0))
                bui.getsound('kronk2').play(volume=2)

        bs.apptimer(2.5, _do_install)

