# Released under the MIT License. See LICENSE for details.
#
"""Elimination mini-game."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.spazfactory import SpazFactory
from bastd.actor.scoreboard import Scoreboard

if TYPE_CHECKING:
    from typing import (Any, Tuple, Dict, Type, List, Sequence, Optional,
                        Union)


class Icon(ba.Actor):
    """Creates in in-game icon on screen."""

    def __init__(self,
                 player: Player,
                 position: Tuple[float, float],
                 scale: float,
                 show_lives: bool = True,
                 show_death: bool = True,
                 name_scale: float = 1.0,
                 name_maxwidth: float = 115.0,
                 flatness: float = 1.0,
                 shadow: float = 1.0):
        super().__init__()

        self._player = player
        self._show_lives = show_lives
        self._show_death = show_death
        self._name_scale = name_scale
        self._outline_tex = ba.gettexture('characterIconMask')

        icon = player.get_icon()
        self.node = ba.newnode('image',
                               delegate=self,
                               attrs={
                                   'texture': icon['texture'],
                                   'tint_texture': icon['tint_texture'],
                                   'tint_color': icon['tint_color'],
                                   'vr_depth': 400,
                                   'tint2_color': icon['tint2_color'],
                                   'mask_texture': self._outline_tex,
                                   'opacity': 1.0,
                                   'absolute_scale': True,
                                   'attach': 'bottomCenter'
                               })
        self._name_text = ba.newnode(
            'text',
            owner=self.node,
            attrs={
                'text': ba.Lstr(value=player.getname()),
                'color': ba.safecolor(player.team.color),
                'h_align': 'center',
                'v_align': 'center',
                'vr_depth': 410,
                'maxwidth': name_maxwidth,
                'shadow': shadow,
                'flatness': flatness,
                'h_attach': 'center',
                'v_attach': 'bottom'
            })
        if self._show_lives:
            self._lives_text = ba.newnode('text',
                                          owner=self.node,
                                          attrs={
                                              'text': 'x0',
                                              'color': (1, 1, 0.5),
                                              'h_align': 'left',
                                              'vr_depth': 430,
                                              'shadow': 1.0,
                                              'flatness': 1.0,
                                              'h_attach': 'center',
                                              'v_attach': 'bottom'
                                          })
        self.set_position_and_scale(position, scale)

    def set_position_and_scale(self, position: Tuple[float, float],
                               scale: float) -> None:
        """(Re)position the icon."""
        assert self.node
        self.node.position = position
        self.node.scale = [70.0 * scale]
        self._name_text.position = (position[0], position[1] + scale * 52.0)
        self._name_text.scale = 1.0 * scale * self._name_scale
        if self._show_lives:
            self._lives_text.position = (position[0] + scale * 10.0,
                                         position[1] - scale * 43.0)
            self._lives_text.scale = 1.0 * scale

    def update_for_lives(self) -> None:
        """Update for the target player's current lives."""
        if self._player:
            lives = self._player.lives
        else:
            lives = 0
        if self._show_lives:
            if lives > 0:
                self._lives_text.text = 'x' + str(lives - 1)
            else:
                self._lives_text.text = ''
        if lives == 0:
            self._name_text.opacity = 0.2
            assert self.node
            self.node.color = (0.7, 0.3, 0.3)
            self.node.opacity = 0.2

    def handle_player_spawned(self) -> None:
        """Our player spawned; hooray!"""
        if not self.node:
            return
        self.node.opacity = 1.0
        self.update_for_lives()

    def handle_player_died(self) -> None:
        """Well poo; our player died."""
        if not self.node:
            return
        if self._show_death:
            ba.animate(
                self.node, 'opacity', {
                    0.00: 1.0,
                    0.05: 0.0,
                    0.10: 1.0,
                    0.15: 0.0,
                    0.20: 1.0,
                    0.25: 0.0,
                    0.30: 1.0,
                    0.35: 0.0,
                    0.40: 1.0,
                    0.45: 0.0,
                    0.50: 1.0,
                    0.55: 0.2
                })
            lives = self._player.lives
            if lives == 0:
                ba.timer(0.6, self.update_for_lives)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            self.node.delete()
            return None
        return super().handlemessage(msg)


class Player(ba.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.lives = 0
        self.icons: List[Icon] = []


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.survival_seconds: Optional[int] = None
        self.spawn_order: List[Player] = []


# ba_meta export game
class AllianceEliminationGame(ba.TeamGameActivity[Player, Team]):
    """Game type where last player(s) left alive win."""

    name = 'Alliance Elimination'
    description = 'Fight in groups of duo, trio, or more.\nLast remaining alive wins.'
    scoreconfig = ba.ScoreConfig(label='Survived',
                                 scoretype=ba.ScoreType.SECONDS,
                                 none_is_winner=True)
    # Show messages when players die since it's meaningful here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
            ba.IntSetting(
                'Lives Per Player',
                default=1,
                min_value=1,
                max_value=10,
                increment=1,
            ),
            ba.IntSetting(
                'Players Per Team In Arena',
                default=2,
                min_value=2,
                max_value=10,
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
            ba.BoolSetting('Epic Mode', default=False),
        ]
        if issubclass(sessiontype, ba.DualTeamSession):
            settings.append(
                ba.BoolSetting('Balance Total Lives', default=False))
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._start_time: Optional[float] = None
        self._vs_text: Optional[ba.Actor] = None
        self._round_end_timer: Optional[ba.Timer] = None
        self._epic_mode = bool(settings['Epic Mode'])
        self._lives_per_player = int(settings['Lives Per Player'])
        self._time_limit = float(settings['Time Limit'])
        self._balance_total_lives = bool(
            settings.get('Balance Total Lives', False))
        self._players_per_team_in_arena = int(
            settings['Players Per Team In Arena'])

        # Base class overrides:
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC
                              if self._epic_mode else ba.MusicType.SURVIVAL)

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Last team standing wins.' if isinstance(
            self.session, ba.DualTeamSession) else 'Last one standing wins.'

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'last team standing wins' if isinstance(
            self.session, ba.DualTeamSession) else 'last one standing wins'

    def on_player_join(self, player: Player) -> None:

        # No longer allowing mid-game joiners here; too easy to exploit.
        if self.has_begun():

            # Make sure their team has survival seconds set if they're all dead
            # (otherwise blocked new ffa players are considered 'still alive'
            # in score tallying).
            if (self._get_total_team_lives(player.team) == 0
                    and player.team.survival_seconds is None):
                player.team.survival_seconds = 0
            ba.screenmessage(
                ba.Lstr(resource='playerDelayedJoinText',
                        subs=[('${PLAYER}', player.getname(full=True))]),
                color=(0, 1, 0),
            )
            return

        player.lives = self._lives_per_player

        player.team.spawn_order.append(player)
        self._update_alliance_mode()

        # Don't waste time doing this until begin.
        if self.has_begun():
            self._update_icons()

    def on_begin(self) -> None:
        super().on_begin()
        self._start_time = ba.time()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()
        self._vs_text = ba.NodeActor(
            ba.newnode('text',
                       attrs={
                           'position': (0, 92),
                           'h_attach': 'center',
                           'h_align': 'center',
                           'maxwidth': 200,
                           'shadow': 0.5,
                           'vr_depth': 390,
                           'scale': 0.6,
                           'v_attach': 'bottom',
                           'color': (0.8, 0.8, 0.3, 1.0),
                           'text': ba.Lstr(resource='vsText')
                       }))

        # If balance-team-lives is on, add lives to the smaller team until
        # total lives match.
        if (isinstance(self.session, ba.DualTeamSession)
                and self._balance_total_lives and self.teams[0].players
                and self.teams[1].players):
            if self._get_total_team_lives(
                    self.teams[0]) < self._get_total_team_lives(self.teams[1]):
                lesser_team = self.teams[0]
                greater_team = self.teams[1]
            else:
                lesser_team = self.teams[1]
                greater_team = self.teams[0]
            add_index = 0
            while (self._get_total_team_lives(lesser_team) <
                   self._get_total_team_lives(greater_team)):
                lesser_team.players[add_index].lives += 1
                add_index = (add_index + 1) % len(lesser_team.players)

        self._update_icons()

        # We could check game-over conditions at explicit trigger points,
        # but lets just do the simple thing and poll it.
        ba.timer(1.0, self._update, repeat=True)

    def _update_alliance_mode(self) -> None:
        # For both teams, find the first player on the spawn order list with
        # lives remaining and spawn them if they're not alive.
        for team in self.teams:
            # Prune dead players from the spawn order.
            players_spawned = 0
            team.spawn_order = [p for p in team.spawn_order if p]
            for player in team.spawn_order:
                assert isinstance(player, Player)
                if player.lives > 0:
                    if not player.is_alive():
                        self.spawn_player(player)
                        self._update_icons()
                    players_spawned += 1
                    if players_spawned >= self._players_per_team_in_arena:
                        break

    def _update_icons(self) -> None:
        # pylint: disable=too-many-branches
        # First off, clear out all icons.
        for player in self.players:
            player.icons = []

        # Now for each team, cycle through our available players
        # adding icons.
        for team in self.teams:
            if team.id == 0:
                xval = -60
                x_offs = -78
            else:
                xval = 60
                x_offs = 78
            nplayers = self._players_per_team_in_arena
            test_lives = 1
            while True:
                players_with_lives = [
                    p for p in team.spawn_order
                    if p and p.lives >= test_lives
                ]
                if not players_with_lives:
                    break
                for player in players_with_lives:
                    player.icons.append(
                        Icon(player,
                             position=(xval, (36 if nplayers > 0 else 25)),
                             scale=0.9 if nplayers > 0 else 0.5,
                             name_maxwidth=85 if nplayers > 0 else 75,
                             name_scale=0.8 if nplayers > 0 else 1.0,
                             flatness=0.0 if nplayers > 0 else 1.0,
                             shadow=0.5 if nplayers > 0 else 1.0,
                             show_death=True if nplayers > 0 else False,
                             show_lives=False))
                    xval += x_offs * (0.85 if nplayers > 0 else 0.56)
                    nplayers -= 1
                test_lives += 1

    def _get_spawn_point(self, player: Player) -> Optional[ba.Vec3]:
        return None

    def spawn_player(self, player: Player) -> ba.Actor:
        actor = self.spawn_player_spaz(player, self._get_spawn_point(player))

        # If we have any icons, update their state.
        for icon in player.icons:
            icon.handle_player_spawned()
        return actor

    def _print_lives(self, player: Player) -> None:
        from bastd.actor import popuptext

        # We get called in a timer so it's possible our player has left/etc.
        if not player or not player.is_alive() or not player.node:
            return

        popuptext.PopupText('x' + str(player.lives - 1),
                            color=(1, 1, 0, 1),
                            offset=(0, -0.8, 0),
                            random_offset=0.0,
                            scale=1.8,
                            position=player.node.position).autoretain()

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
        player.icons = []

        # Remove us from spawn-order.
        if player in player.team.spawn_order:
            player.team.spawn_order.remove(player)

        # Update icons in a moment since our team will be gone from the
        # list then.
        ba.timer(0, self._update_icons)

        # If the player to leave was the last in spawn order and had
        # their final turn currently in-progress, mark the survival time
        # for their team.
        if self._get_total_team_lives(player.team) == 0:
            assert self._start_time is not None
            player.team.survival_seconds = int(ba.time() - self._start_time)

    def _get_total_team_lives(self, team: Team) -> int:
        return sum(player.lives for player in team.players)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)
            player: Player = msg.getplayer(Player)

            player.lives -= 1
            if player.lives < 0:
                ba.print_error(
                    "Got lives < 0 in Alliance Elimination; this shouldn't happen.")
                player.lives = 0

            # If we have any icons, update their state.
            for icon in player.icons:
                icon.handle_player_died()

            # Play big death sound on our last death
            # or for every one.
            if player.lives == 0:
                ba.playsound(SpazFactory.get().single_player_death_sound)

            # If we hit zero lives, we're dead (and our team might be too).
            if player.lives == 0:
                # If the whole team is now dead, mark their survival time.
                if self._get_total_team_lives(player.team) == 0:
                    assert self._start_time is not None
                    player.team.survival_seconds = int(ba.time() -
                                                       self._start_time)

            # Put ourself at the back of the spawn order.
            player.team.spawn_order.remove(player)
            player.team.spawn_order.append(player)

    def _update(self) -> None:
        # For both teams, find the first player on the spawn order
        # list with lives remaining and spawn them if they're not alive.
        for team in self.teams:
            # Prune dead players from the spawn order.
            team.spawn_order = [p for p in team.spawn_order if p]
            players_spawned = 0
            for player in team.spawn_order:
                assert isinstance(player, Player)
                if player.lives > 0:
                    if not player.is_alive():
                        self.spawn_player(player)
                        self._update_icons()
                    players_spawned += 1
                    if players_spawned >= self._players_per_team_in_arena:
                        break

        # If we're down to 1 or fewer living teams, start a timer to end
        # the game (allows the dust to settle and draws to occur if deaths
        # are close enough).
        if len(self._get_living_teams()) < 2:
            self._round_end_timer = ba.Timer(0.5, self.end_game)

    def _get_living_teams(self) -> List[Team]:
        return [
            team for team in self.teams
            if len(team.players) > 0 and any(player.lives > 0
                                             for player in team.players)
        ]

    def end_game(self) -> None:
        if self.has_ended():
            return
        results = ba.GameResults()
        self._vs_text = None  # Kill our 'vs' if its there.
        for team in self.teams:
            results.set_team_score(team, team.survival_seconds)
        self.end(results=results)
