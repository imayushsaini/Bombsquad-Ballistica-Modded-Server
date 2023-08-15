"""New Duel / Created by: byANG3L"""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.game.elimination import Icon

if TYPE_CHECKING:
    from typing import Any, Type, List, Union, Sequence, Optional


class SuperSpaz(PlayerSpaz):

    def __init__(self,
                 player: bs.Player,
                 color: Sequence[float] = (1.0, 1.0, 1.0),
                 highlight: Sequence[float] = (0.5, 0.5, 0.5),
                 character: str = 'Spaz',
                 super_punch: bool = False,
                 powerups_expire: bool = True):
        super().__init__(player=player,
                         color=color,
                         highlight=highlight,
                         character=character,
                         powerups_expire=powerups_expire)
        self._super_punch = super_punch

    def handlemessage(self, msg: Any) -> Any:
        from bascenev1lib.actor.spaz import PunchHitMessage
        from bascenev1lib.actor.bomb import Blast
        if isinstance(msg, PunchHitMessage):
            super().handlemessage(msg)
            node = bs.getcollision().opposingnode
            if self._super_punch:
                if node.getnodetype() == 'spaz':
                    if not node.frozen:
                        node.frozen = True
                        node.handlemessage(babase.FreezeMessage())
                        bs.getsound('freeze').play()
                    bs.getsound('superPunch').play()
                    bs.getsound('punchStrong02').play()
                    Blast(position=node.position,
                          velocity=node.velocity,
                          blast_radius=0.0,
                          blast_type='normal').autoretain()
        else:
            return super().handlemessage(msg)
        return None


class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.icons: List[Icon] = []
        self.in_game: bool = False
        self.playervs1: bool = False
        self.playervs2: bool = False
        self.light: bool = False


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


lang = bs.app.lang.language
if lang == 'Spanish':
    enable_powerups = 'Habilitar Potenciadores'
    night_mode = 'Modo Noche'
    fight_delay = 'Tiempo entre Pelea'
    very_fast = 'Muy Rápido'
    fast = 'Rápido'
    normal = 'Normal'
    slow = 'Lento'
    very_slow = 'Muy Lento'
    none = 'Ninguno'
    super_punch = 'Super Golpe'
    box_mode = 'Modo Caja'
    boxing_gloves = 'Guantes de Boxeo'
else:
    enable_powerups = 'Enable Powerups'
    night_mode = 'Night Mode'
    fight_delay = 'Fight Delay'
    very_fast = 'Very Fast'
    fast = 'Fast'
    normal = 'Normal'
    slow = 'Slow'
    very_slow = 'Very Slow'
    super_punch = 'Super Punch'
    box_mode = 'Box Mode'
    boxing_gloves = 'Boxing Gloves'


# ba_meta export bascenev1.GameActivity


class NewDuelGame(bs.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Duel'
    description = 'Kill a set number of enemies to win.'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
        cls, sessiontype: Type[bs.Session]) -> List[babase.Setting]:
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
            bs.BoolSetting(enable_powerups, default=False),
            bs.BoolSetting(boxing_gloves, default=False),
            bs.BoolSetting(night_mode, default=False),
            bs.BoolSetting(super_punch, default=False),
            bs.BoolSetting(box_mode, default=False),
            bs.BoolSetting('Epic Mode', default=False),
            bs.BoolSetting('Allow Negative Scores', default=False),
        ]
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[bs.Session]) -> bool:
        return (issubclass(sessiontype, bs.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return bs.app.classic.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: Optional[int] = None
        self._dingsound = bs.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(
            settings['Kills to Win Per Player'])
        self._enable_powerups = bool(settings[enable_powerups])
        self._night_mode = bool(settings[night_mode])
        self._fight_delay: float = 0
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False))
        self._super_punch = bool(settings[super_punch])
        self._box_mode = bool(settings[box_mode])
        self._boxing_gloves = bool(settings[boxing_gloves])
        self._vs_text: Optional[bs.Actor] = None
        self.spawn_order: List[Player] = []
        self._players_vs_1: bool = False
        self._players_vs_2: bool = False
        self._first_countdown: bool = True
        self._count_1 = bs.getsound('announceOne')
        self._count_2 = bs.getsound('announceTwo')
        self._count_3 = bs.getsound('announceThree')
        self._boxing_bell = bs.getsound('boxingBell')

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (bs.MusicType.EPIC if self._epic_mode else
                              bs.MusicType.TO_THE_DEATH)

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Crush ${ARG1} of your enemies.', self._score_to_win

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'kill ${ARG1} enemies', self._score_to_win

    def on_player_join(self, player: Player) -> None:
        self.spawn_order.append(player)
        self._update_order()

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
        player.icons = []
        if player.playervs1:
            player.playervs1 = False
            self._players_vs_1 = False
            player.in_game = False
        elif player.playervs2:
            player.playervs2 = False
            self._players_vs_2 = False
            player.in_game = False
        if player in self.spawn_order:
            self.spawn_order.remove(player)
        bs.timer(0.2, self._update_order)

    def on_transition_in(self) -> None:
        super().on_transition_in()
        if self._night_mode:
            gnode = bs.getactivity().globalsnode
            gnode.tint = (0.3, 0.3, 0.3)

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        if self._enable_powerups:
            self.setup_standard_powerup_drops()
        self._vs_text = bs.NodeActor(
            bs.newnode('text',
                       attrs={
                           'position': (0, 105),
                           'h_attach': 'center',
                           'h_align': 'center',
                           'maxwidth': 200,
                           'shadow': 0.5,
                           'vr_depth': 390,
                           'scale': 0.6,
                           'v_attach': 'bottom',
                           'color': (0.8, 0.8, 0.3, 1.0),
                           'text': babase.Lstr(resource='vsText')
                       }))

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = (self._kills_to_win_per_player *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()
        bs.timer(1.0, self._update, repeat=True)

    def _update(self) -> None:
        if len(self.players) == 1:
            'self.end_game()'

    def spawn_player(self, player: PlayerType) -> bs.Actor:
        # pylint: disable=too-many-locals
        # pylint: disable=cyclic-import
        from babase import _math
        from bascenev1._coopsession import CoopSession
        from bascenev1lib.actor.spazfactory import SpazFactory
        factory = SpazFactory.get()
        name = player.getname()
        color = player.color
        highlight = player.highlight

        light_color = _math.normalized_color(color)
        display_color = babase.safecolor(color, target_intensity=0.75)
        spaz = SuperSpaz(color=color,
                         highlight=highlight,
                         character=player.character,
                         player=player,
                         super_punch=True if self._super_punch else False)

        player.actor = spaz
        assert spaz.node

        # If this is co-op and we're on Courtyard or Runaround, add the
        # material that allows us to collide with the player-walls.
        # FIXME: Need to generalize this.
        if isinstance(self.session, CoopSession) and self.map.getname() in [
            'Courtyard', 'Tower D'
        ]:
            mat = self.map.preloaddata['collide_with_wall_material']
            assert isinstance(spaz.node.materials, tuple)
            assert isinstance(spaz.node.roller_materials, tuple)
            spaz.node.materials += (mat,)
            spaz.node.roller_materials += (mat,)

        spaz.node.name = name
        spaz.node.name_color = display_color
        spaz.connect_controls_to_player()

        self._spawn_sound.play(1, position=spaz.node.position)
        light = bs.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        bs.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        bs.timer(0.5, light.delete)

        pos1 = [self.map.get_start_position(0), 90]
        pos2 = [self.map.get_start_position(1), 270]
        pos3 = []

        for x in self.players:
            if x.is_alive():
                if x is player:
                    continue
                p = x.actor.node.position
                if 0.0 not in (p[0], p[2]):
                    if p[0] <= 0:
                        pos3.append(pos2[0])
                    else:
                        pos3.append(pos1[0])

        spaz.handlemessage(
            bs.StandMessage(pos1[0] if player.playervs1 else pos2[0],
                            pos1[1] if player.playervs1 else pos2[1]))

        if any(pos3):
            spaz.handlemessage(bs.StandMessage(pos3[0]))

        if self._super_punch:
            spaz._punch_power_scale = factory.punch_power_scale_gloves = 10
            spaz.equip_boxing_gloves()
            lfx = bs.newnode(
                'light',
                attrs={
                    'color': color,
                    'radius': 0.3,
                    'intensity': 0.3})

            def sp_fx():
                if not spaz.node:
                    lfx.delete()
                    return
                bs.emitfx(position=spaz.node.position,
                          velocity=spaz.node.velocity,
                          count=5,
                          scale=0.5,
                          spread=0.5,
                          chunk_type='spark')
                bs.emitfx(position=spaz.node.position,
                          velocity=spaz.node.velocity,
                          count=2,
                          scale=0.8,
                          spread=0.3,
                          chunk_type='spark')
                if lfx:
                    spaz.node.connectattr('position', lfx, 'position')

            bs.timer(0.1, sp_fx, repeat=True)

        if self._box_mode:
            spaz.node.color_texture = bs.gettexture('tnt')
            spaz.node.color_mask_texture = bs.gettexture('tnt')
            spaz.node.color = (1, 1, 1)
            spaz.node.highlight = (1, 1, 1)
            spaz.node.head_mesh = None
            spaz.node.torso_mesh = bs.getmesh('tnt')
            spaz.node.style = 'cyborg'

        if self._boxing_gloves:
            spaz.equip_boxing_gloves()

        return spaz

    def _update_spawn(self) -> None:
        if self._players_vs_1 or self._players_vs_2:
            for player in self.players:
                if player.playervs1 or player.playervs2:
                    if not player.is_alive():
                        self.spawn_player(player)
                        # player.actor.disconnect_controls_from_player()

                        if self._night_mode:
                            if not player.light:
                                player.light = True
                                light = bs.newnode(
                                    'light',
                                    owner=player.node,
                                    attrs={
                                        'radius': 0.3,
                                        'intensity': 0.6,
                                        'height_attenuated': False,
                                        'color': player.color
                                    })
                                player.node.connectattr(
                                    'position', light, 'position')
                    else:
                        player.actor.disconnect_controls_from_player()

                    bs.timer(0.0, self._countdown)
                #  bs.timer(0.1, self._clear_all_objects)

    def _countdown(self) -> None:
        self._first_countdown = False
        if self._fight_delay == 0:
            for player in self.players:
                if player.playervs1 or player.playervs2:
                    if not player.is_alive():
                        return
                    else:
                        player.actor.connect_controls_to_player()
        else:
            bs.timer(self._fight_delay, self.count3)

    def start(self) -> None:
        self._count_text('FIGHT')
        self._boxing_bell.play()
        for player in self.players:
            if player.playervs1 or player.playervs2:
                if not player.is_alive():
                    return
                else:
                    player.actor.connect_controls_to_player()

    def count(self) -> None:
        self._count_text('1')
        self._count_1.play()
        bs.timer(self._fight_delay, self.start)

    def count2(self) -> None:
        self._count_text('2')
        self._count_2.play()
        bs.timer(self._fight_delay, self.count)

    def count3(self) -> None:
        self._count_text('3')
        self._count_3.play()
        bs.timer(self._fight_delay, self.count2)

    def _count_text(self, num: str) -> None:
        self.node = bs.newnode('text',
                               attrs={
                                   'v_attach': 'center',
                                   'h_attach': 'center',
                                   'h_align': 'center',
                                   'color': (1, 1, 0.5, 1),
                                   'flatness': 0.5,
                                   'shadow': 0.5,
                                   'position': (0, 18),
                                   'text': num
                               })
        if self._fight_delay == 0.7:
            bs.animate(self.node, 'scale',
                       {0: 0, 0.1: 3.9, 0.64: 4.3, 0.68: 0})
        elif self._fight_delay == 0.4:
            bs.animate(self.node, 'scale',
                       {0: 0, 0.1: 3.9, 0.34: 4.3, 0.38: 0})
        else:
            bs.animate(self.node, 'scale',
                       {0: 0, 0.1: 3.9, 0.92: 4.3, 0.96: 0})
        cmb = bs.newnode('combine', owner=self.node, attrs={'size': 4})
        cmb.connectattr('output', self.node, 'color')
        bs.animate(cmb, 'input0', {0: 1.0, 0.15: 1.0}, loop=True)
        bs.animate(cmb, 'input1', {0: 1.0, 0.15: 0.5}, loop=True)
        bs.animate(cmb, 'input2', {0: 0.1, 0.15: 0.0}, loop=True)
        cmb.input3 = 1.0
        bs.timer(self._fight_delay, self.node.delete)

    def _update_order(self) -> None:
        for player in self.spawn_order:
            assert isinstance(player, Player)
            if not player.is_alive():
                if not self._players_vs_1:
                    self._players_vs_1 = True
                    player.playervs1 = True
                    player.in_game = True
                    self.spawn_order.remove(player)
                    self._update_spawn()
                elif not self._players_vs_2:
                    self._players_vs_2 = True
                    player.playervs2 = True
                    player.in_game = True
                    self.spawn_order.remove(player)
                    self._update_spawn()
                self._update_icons()

    def _update_icons(self) -> None:
        # pylint: disable=too-many-branches

        for player in self.players:
            player.icons = []

            if player.in_game:
                if player.playervs1:
                    xval = -60
                    x_offs = -78
                elif player.playervs2:
                    xval = 60
                    x_offs = 78
                player.icons.append(
                    Icon(player,
                         position=(xval, 40),
                         scale=1.0,
                         name_maxwidth=130,
                         name_scale=0.8,
                         flatness=0.0,
                         shadow=0.5,
                         show_death=True,
                         show_lives=False))
            else:
                xval = 125
                xval2 = -125
                x_offs = 78
                for player in self.spawn_order:
                    player.icons.append(
                        Icon(player,
                             position=(xval, 25),
                             scale=0.5,
                             name_maxwidth=75,
                             name_scale=1.0,
                             flatness=1.0,
                             shadow=1.0,
                             show_death=False,
                             show_lives=False))
                    xval += x_offs * 0.56
                    player.icons.append(
                        Icon(player,
                             position=(xval2, 25),
                             scale=0.5,
                             name_maxwidth=75,
                             name_scale=1.0,
                             flatness=1.0,
                             shadow=1.0,
                             show_death=False,
                             show_lives=False))
                    xval2 -= x_offs * 0.56

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)

            if player.playervs1:
                player.playervs1 = False
                self._players_vs_1 = False
                player.in_game = False
                self.spawn_order.append(player)
            elif player.playervs2:
                player.playervs2 = False
                self._players_vs_2 = False
                player.in_game = False
                self.spawn_order.append(player)
            bs.timer(0.2, self._update_order)

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
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
