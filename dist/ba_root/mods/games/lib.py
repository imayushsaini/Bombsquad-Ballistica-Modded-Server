# Released under the MIT License. See LICENSE for details.
#
"""Defines the King of the Hill game."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import weakref
from enum import Enum
from typing import TYPE_CHECKING

import ba
from bastd.actor.flag import Flag
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects
from dataclasses import dataclass
if TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Union


class FlagState(Enum):
    """States our single flag can be in."""
    NEW = 0
    UNCONTESTED = 1
    CONTESTED = 2
    HELD = 3


class Player(ba.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.time_at_flag = 0
        self.lives = 0
        self.icons: list[Icon] = []
        self.death_time: Optional[float] = None
        self.distance_txt: Optional[ba.Node] = None
        self.last_region = 0
        self.lap = 0
        self.distance = 0.0
        self.finished = False
        self.rank: Optional[int] = None


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self, time_remaining=None) -> None:
        self.time_remaining = time_remaining
        self.survival_seconds: Optional[int] = None
        self.spawn_order: list[Player] = []
        self.score = 0
        self.time: Optional[float] = None
        self.lap = 0
        self.finished = False

    #def __init__(self):
    #    self.survival_seconds: Optional[int] = None
    #    self.spawn_order: list[Player] = []
    #    self.score = 0
    #    self.time: Optional[float] = None
    #    self.lap = 0
    #    self.finished = False



class kth(ba.TeamGameActivity[Player, Team]):
    """Game where a team wins by holding a 'hill' for a set amount of time."""

    name = 'King of the Hillx'
    description = 'Secure the flag for a set length of time.'
    available_settings = [
        ba.IntSetting(
            'Hold Time',
            min_value=10,
            default=30,
            increment=10,
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
    ]
    scoreconfig = ba.ScoreConfig(label='Time Held')

    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.MultiTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ba.getmaps('king_of_the_hill')

    def __init__(self, settings: dict):
        super().__init__(settings)
        

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Secure the flag for ${ARG1} seconds.', self._hold_time

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'secure the flag for ${ARG1} seconds', self._hold_time


    def on_begin(self) -> None:
        super().on_begin()
        shared = SharedObjects.get()
        

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, self._hold_time - team.time_remaining)
        self.end(results=results, announce_delay=0)


    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)  # Augment default.

# =====================================================================================================================================================================




from bastd.actor.spazfactory import SpazFactory


if TYPE_CHECKING:
    from typing import Any, Sequence, Optional, Union


class Icon(ba.Actor):
    """Creates in in-game icon on screen."""

    def __init__(self,
                 player: Player,
                 position: tuple[float, float],
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

    def set_position_and_scale(self, position: tuple[float, float],
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


class eli(ba.TeamGameActivity[Player, Team]):
    """Game type where last player(s) left alive win."""

    name = 'Eliminationx'
    description = 'Last remaining alive wins.'
    scoreconfig = ba.ScoreConfig(label='Survived',
                                 scoretype=ba.ScoreType.SECONDS,
                                 none_is_winner=True)
    # Show messages when players die since it's meaningful here.
    announce_player_deaths = True

    allow_mid_activity_joins = False

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [
            ba.IntSetting(
                'Lives Per Player',
                default=1,
                min_value=1,
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
            settings.append(ba.BoolSetting('Solo Mode', default=False))
            settings.append(
                ba.BoolSetting('Balance Total Lives', default=False))
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        
    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Last team standing wins.' if isinstance(
            self.session, ba.DualTeamSession) else 'Last one standing wins.'

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'last team standing wins' if isinstance(
            self.session, ba.DualTeamSession) else 'last one standing wins'

    def on_begin(self) -> None:
        super().on_begin()

# ========================


# ba_meta export game
class dm(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Death Matchx'
    description = 'Kill a set number of enemies to win.'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [
            ba.IntSetting(
                'Kills to Win Per Player',
                min_value=1,
                default=5,
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

        # In teams mode, a suicide gives a point to the other team, but in
        # free-for-all it subtracts from your own score. By default we clamp
        # this at zero to benefit new players, but pro players might like to
        # be able to go negative. (to avoid a strategy of just
        # suiciding until you get a good drop)
        if issubclass(sessiontype, ba.FreeForAllSession):
            settings.append(
                ba.BoolSetting('Allow Negative Scores', default=False))

        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Crush ${ARG1} of your enemies.', self._score_to_win

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'kill ${ARG1} enemies', self._score_to_win

 

    def on_begin(self) -> None:
        super().on_begin()


# ====================





# ba_meta export game
class ms(ba.TeamGameActivity[Player, Team]):
    """Minigame involving dodging falling bombs."""

    name = 'Meteor Showerx'
    description = 'Dodge the falling bombs.'
    available_settings = [ba.BoolSetting('Epic Mode', default=False)]
    scoreconfig = ba.ScoreConfig(label='Survived',
                                 scoretype=ba.ScoreType.MILLISECONDS,
                                 version='B')

    # Print messages when players die (since its meaningful in this game).
    announce_player_deaths = True

    # Don't allow joining after we start
    # (would enable leave/rejoin tomfoolery).
    allow_mid_activity_joins = False

    # We're currently hard-coded for one map.
    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ['Rampage']

    # We support teams, free-for-all, and co-op sessions.
    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession)
                or issubclass(sessiontype, ba.CoopSession))

    def __init__(self, settings: dict):
        super().__init__(settings)


    def on_begin(self) -> None:
        super().on_begin()

# =====================



@dataclass
class RaceMine:
    """Holds info about a mine on the track."""
    point: Sequence[float]
    mine: Optional[Bomb]


class RaceRegion(ba.Actor):
    """Region used to track progress during a race."""

    def __init__(self, pt: Sequence[float], index: int):
        super().__init__()
        activity = self.activity
        assert isinstance(activity, RaceGame)
        self.pos = pt
        self.index = index
        self.node = ba.newnode(
            'region',
            delegate=self,
            attrs={
                'position': pt[:3],
                'scale': (pt[3] * 2.0, pt[4] * 2.0, pt[5] * 2.0),
                'type': 'box',
                'materials': [activity.race_region_material]
            })



# ba_meta export game
class rg(ba.TeamGameActivity[Player, Team]):
    """Game of racing around a track."""

    name = 'Racex'
    description = 'Run real fast!'
    scoreconfig = ba.ScoreConfig(label='Time',
                                 lower_is_better=True,
                                 scoretype=ba.ScoreType.MILLISECONDS)

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [
            ba.IntSetting('Laps', min_value=1, default=3, increment=1),
            ba.IntChoiceSetting(
                'Time Limit',
                default=0,
                choices=[
                    ('None', 0),
                    ('1 Minute', 60),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600),
                    ('20 Minutes', 1200),
                ],
            ),
            ba.IntChoiceSetting(
                'Mine Spawning',
                default=4000,
                choices=[
                    ('No Mines', 0),
                    ('8 Seconds', 8000),
                    ('4 Seconds', 4000),
                    ('2 Seconds', 2000),
                ],
            ),
            ba.IntChoiceSetting(
                'Bomb Spawning',
                choices=[
                    ('None', 0),
                    ('8 Seconds', 8000),
                    ('4 Seconds', 4000),
                    ('2 Seconds', 2000),
                    ('1 Second', 1000),
                ],
                default=2000,
            ),
            ba.BoolSetting('Epic Mode', default=False),
        ]

        # We have some specific settings in teams mode.
        if issubclass(sessiontype, ba.DualTeamSession):
            settings.append(
                ba.BoolSetting('Entire Team Must Finish', default=False))
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.MultiTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ba.getmaps('race')

    def __init__(self, settings: dict):
        self._race_started = False
        super().__init__(settings)
        


    def get_instance_description(self) -> Union[str, Sequence]:
        if (isinstance(self.session, ba.DualTeamSession)
                and self._entire_team_must_finish):
            t_str = ' Your entire team has to finish.'
        else:
            t_str = ''

        if self._laps > 1:
            return 'Run ${ARG1} laps.' + t_str, self._laps
        return 'Run 1 lap.' + t_str

    def get_instance_description_short(self) -> Union[str, Sequence]:
        if self._laps > 1:
            return 'run ${ARG1} laps', self._laps
        return 'run 1 lap'

  

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)

 

    def on_begin(self) -> None:
        from bastd.actor.onscreentimer import OnScreenTimer
        super().on_begin()