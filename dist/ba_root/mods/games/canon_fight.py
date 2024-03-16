# Porting to api 8 made easier by baport.(https://github.com/bombsquad-community/baport)
# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)
from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
import random
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.bomb import BombFactory
from bascenev1lib.actor.bomb import Bomb

from bascenev1lib.game.deathmatch import DeathMatchGame,Player,Team

if TYPE_CHECKING:
    from typing import Any, Union, Sequence, Optional





# ba_meta export bascenev1.GameActivity
class CanonFightGame(DeathMatchGame):
    """A game type based on acquiring kills."""

    name = 'Canon Fight'
    description = 'Kill a set number of enemies to win.'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[bs.Session]) -> list[babase.Setting]:
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
            bs.BoolSetting('Epic Mode', default=False),
        ]

        # In teams mode, a suicide gives a point to the other team, but in
        # free-for-all it subtracts from your own score. By default we clamp
        # this at zero to benefit new players, but pro players might like to
        # be able to go negative. (to avoid a strategy of just
        # suiciding until you get a good drop)
        if issubclass(sessiontype, bs.FreeForAllSession):
            settings.append(
                bs.BoolSetting('Allow Negative Scores', default=False))

        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return (issubclass(sessiontype, bs.DualTeamSession)
                or issubclass(sessiontype, bs.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        return ["Step Right Up"]

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: Optional[int] = None
        self._dingsound = bs.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(
            settings['Kills to Win Per Player'])
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False))

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (bs.MusicType.EPIC if self._epic_mode else
                              bs.MusicType.TO_THE_DEATH)

        self.wtindex=0
        self.wttimer = bs.timer(5, babase.Call(self.wt_), repeat=True)
        self.wthighlights=["Created by Mr.Smoothy","hey smoothy youtube","smoothy#multiverse"]

    def wt_(self):
        node = bs.newnode('text',
                            attrs={
                            'text': self.wthighlights[self.wtindex],
                            'flatness': 1.0,
                            'h_align': 'center',
                            'v_attach':'bottom',
                            'scale':0.7,
                            'position':(0,20),
                            'color':(0.5,0.5,0.5)
                            })

        self.delt = bs.timer(4,node.delete)
        self.wtindex = int((self.wtindex+1)%len(self.wthighlights))

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Crush ${ARG1} of your enemies.', self._score_to_win

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'kill ${ARG1} enemies', self._score_to_win

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = (self._kills_to_win_per_player *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()
        self.create_canon_A()
        self.create_canon_B()
        self.create_wall()

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

            killer = msg.getkillerplayer(Player)
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
                    killer.actor.set_score_text(str(killer.team.score) + '/' +
                                                str(self._score_to_win),
                                                color=killer.team.color,
                                                flash=True)

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
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)

    def end_game(self) -> None:
        results = bs.GameResults()
        self.delete_text_nodes()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
    def delete_text_nodes(self):
        self.canon.delete()
        self.canon_.delete()
        self.canon2.delete()
        self.canon_2.delete()
        self.curve.delete()
        self.curve2.delete()

    def _handle_canon_load_A(self):
        try:
            bomb = bs.getcollision().opposingnode.getdelegate(Bomb,True)
            # pos=bomb.position
            owner=bomb.owner
            type=bomb.bomb_type
            source_player=bomb.get_source_player(bs.Player)
            bs.getcollision().opposingnode.delete()

            # bomb.delete()
            self.launch_bomb_byA(owner,type,source_player,2)
        except bs.NotFoundError:
            # This can happen if the flag stops touching us due to being
            # deleted; that's ok.
            return
    def _handle_canon_load_B(self):
        try:
            bomb = bs.getcollision().opposingnode.getdelegate(Bomb,True)
            # pos=bomb.position
            owner=bomb.owner
            type=bomb.bomb_type
            source_player=bomb.get_source_player(bs.Player)
            bs.getcollision().opposingnode.delete()

            # bomb.delete()
            self.launch_bomb_byB(owner,type,source_player,2)
        except bs.NotFoundError:
            # This can happen if the flag stops touching us due to being
            # deleted; that's ok.
            return
    def launch_bomb_byA(self,owner,type,source_player,count):
        if count>0:
            y=random.randrange(2,9,2)
            z=random.randrange(-4,6)
            self.fake_explosion( (-5.708631629943848, 7.437141418457031, -4.525400638580322))

            Bomb(position=(-6,7.5,-4),bomb_type=type,owner=owner,source_player=source_player,velocity=(19,y,z)).autoretain()
            bs.timer(0.6,babase.Call(self.launch_bomb_byA,owner,type,source_player,count-1))
        else:
            return
    def launch_bomb_byB(self,owner,type,source_player,count):
        if count>0:
            y=random.randrange(2,9,2)
            z=random.randrange(-4,6)
            self.fake_explosion( (5.708631629943848, 7.437141418457031, -4.525400638580322))

            Bomb(position=(6,7.5,-4),bomb_type=type,owner=owner,source_player=source_player,velocity=(-19,y,z)).autoretain()
            bs.timer(0.6,babase.Call(self.launch_bomb_byB,owner,type,source_player,count-1))
        else:
            return

    def fake_explosion(self, position: Sequence[float]):
        explosion = bs.newnode('explosion',
                   attrs={'position': position,
                          'radius': 1, 'big': False})
        bs.timer(0.4, explosion.delete)
        sounds = ['explosion0'+str(n) for n in range(1,6)]
        sound = random.choice(sounds)
        bs.getsound(sound).play()



    def create_canon_A(self):
        shared = SharedObjects.get()
        canon_load_mat=bs.Material()
        factory = BombFactory.get()

        canon_load_mat.add_actions(

            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)

            ))
        canon_load_mat.add_actions(
            conditions=('they_have_material', factory.bomb_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True),
                ('call','at_connect',babase.Call(self._handle_canon_load_A))
            ),
            )
        self.ud_1_r=bs.newnode('region',attrs={'position': (-8.908631629943848, 7.337141418457031, -4.525400638580322),'scale': (2,1,1),'type': 'box','materials': [canon_load_mat ]})

        self.node = bs.newnode('shield',
                                    delegate=self,
                                    attrs={
                                    'position':(-8.308631629943848, 7.337141418457031, -4.525400638580322),
                                    'color': (0.3, 0.2, 2.8),
                                    'radius': 1.3
                                    })
        self.canon=bs.newnode('text',
                               attrs={
                                   'text': '___________',
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color':(0.3,0.3,0.8),
                                   'scale':0.019,
                                   'h_align': 'left',
                                   'position':(-8.388631629943848, 7.837141418457031, -4.525400638580322)
                               })
        self.canon_=bs.newnode('text',
                               attrs={
                                   'text': '_________',
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color':(0.3,0.3,0.8),
                                   'scale':0.019,
                                   'h_align': 'left',
                                   'position':(-7.888631629943848, 7.237141418457031, -4.525400638580322)
                               })
        self.curve=bs.newnode('text',
                               attrs={
                                   'text': '/\n',
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color':(0.3,0.3,0.8),
                                   'scale':0.019,
                                   'h_align': 'left',
                                   'position':(-8.788631629943848, 7.237141418457031, -4.525400638580322)
                               })
    def create_canon_B(self):
        shared = SharedObjects.get()
        canon_load_mat=bs.Material()
        factory = BombFactory.get()

        canon_load_mat.add_actions(

            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)

            ))
        canon_load_mat.add_actions(
            conditions=('they_have_material', factory.bomb_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True),
                ('call','at_connect',babase.Call(self._handle_canon_load_B))
            ),
            )
        self.ud_1_r2=bs.newnode('region',attrs={'position': (8.908631629943848+0.81, 7.327141418457031, -4.525400638580322),'scale': (2,1,1),'type': 'box','materials': [canon_load_mat ]})

        self.node2 = bs.newnode('shield',
                                    delegate=self,
                                    attrs={
                                    'position':(8.308631629943848+0.81, 7.327141418457031, -4.525400638580322),
                                    'color': (2.3, 0.2, 0.3),
                                    'radius': 1.3
                                    })
        self.canon2=bs.newnode('text',
                               attrs={
                                   'text': '___________',
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color':(0.8,0.3,0.3),
                                   'scale':0.019,
                                   'h_align': 'right',
                                   'position':(8.388631629943848+0.81, 7.837141418457031, -4.525400638580322)
                               })
        self.canon_2=bs.newnode('text',
                               attrs={
                                   'text': '_________',
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color':(0.8,0.3,0.3),
                                   'scale':0.019,
                                   'h_align': 'right',
                                   'position':(7.888631629943848+0.81, 7.237141418457031, -4.525400638580322)
                               })
        self.curve2=bs.newnode('text',
                               attrs={
                                   'text': '\\',
                                   'in_world': True,
                                   'shadow': 1.0,
                                   'flatness': 1.0,
                                   'color':(0.8,0.3,0.3),
                                   'scale':0.019,
                                   'h_align': 'right',
                                   'position':(8.788631629943848+0.81, 7.237141418457031, -4.525400638580322)
                               })
    def create_wall(self):
        shared = SharedObjects.get()
        factory = BombFactory.get()
        mat=bs.Material()
        mat.add_actions(
                    conditions=('they_have_material',shared.player_material),
                    actions=(
                        ('modify_part_collision', 'collide', True),
                        ('modify_part_collision','physical',True)
                         ))
        mat.add_actions(
                    conditions=(
                        ('they_have_material',factory.bomb_material)),
                    actions=(
                        ('modify_part_collision', 'collide', False)
                         ))
        self.wall=bs.newnode('region',attrs={'position': (0.61877517104148865, 4.312626838684082, -8.68477725982666),'scale': (3,7,27),'type': 'box','materials': [mat ]})
