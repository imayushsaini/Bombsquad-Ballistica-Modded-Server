# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard

if TYPE_CHECKING:
    from typing import Any, Union, Sequence, Optional


class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class BountyGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Bounty'
    description = 'Score Maximum Stars To Win'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [ba.IntChoiceSetting(
                'Time Limit',
                choices=[
                    ('30 Seconds', 30),
                    ('1 Minute', 60),
                    ('1½ Minute', 90),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600)],
                default=120,
            ),
            ba.FloatChoiceSetting(
                'Respawn Times',
                choices=[
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
        self._scoreboard = Scoreboard()
        self._score_to_win: Optional[int] = None
        self._dingsound = ba.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False))

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.TO_THE_DEATH)

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Collect Stars of your enemies.'

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'Collect Stars of your enemies.'

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()

        # Base kills needed to win on the size of the largest team.
        self._update_scoreboard()

    def spawn_player(self, player: Player) -> ba.Actor:
        
        spaz = self.spawn_player_spaz(player)

        assert spaz.node
        mathnode = ba.newnode('math',
                              owner=spaz.node,
                              attrs={
                                  'input1': (0, 1.4, 0),
                                  'operation': 'add'
                              })
        spaz.node.connectattr('torso_position', mathnode, 'input2')
        players_star = ba.newnode('text',
                                  owner=spaz.node,
                                  attrs={
                                      'text': '*',
                                      'in_world': True,
                                      'color': (1, 1, 0.4),
                                      'scale': 0.02,
                                      'h_align': 'center'
                                  })
        player.tag = players_star
        mathnode.connectattr('output', players_star, 'position')
        return spaz

    def _update_stars(self, player: Player) -> None:
    	oldstar = player.tag.text.count("*")
    	if player.is_alive():
    		if oldstar < 3:
    			player.tag.text = "*" * (oldstar + 1)
    		elif oldstar == 3:
    			player.tag.text = "**\n**"
    		elif oldstar == 4:
    			player.tag.text = "**\n***"
    		else:
    			player.tag.text = player.tag.text

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

            killer = msg.getkillerplayer(Player)
            if killer is None:
                return None

            try:
            	star = player.tag.text.count("*")
            except:
            	star = 0

            # Handle team-kills.
            if killer.team is player.team:

                # In free-for-all, killing yourself loses you a point.
                if isinstance(self.session, ba.FreeForAllSession):
                    new_score = player.team.score - 1
                    if not self._allow_negative_scores:
                        new_score = max(0, new_score)
                    player.team.score = new_score

                # In teams-mode it gives a point to the other team.
                else:
                    ba.playsound(self._dingsound)
                    for team in self.teams:
                        if team is not killer.team:
                            team.score += star
                            if not killer == player:
                                self._update_stars(killer)

            # Killing someone on another team nets a kill.
            else:
                killer.team.score += star
                self._update_stars(killer)
                ba.playsound(self._dingsound)

                # In FFA show scores since its hard to find on the scoreboard.
                if isinstance(killer.actor, PlayerSpaz) and killer.actor:
                    killer.actor.set_score_text("+ 1",
                                                color=killer.team.color,
                                                flash=True)

            self._update_scoreboard()

            # If someone has won, set a timer to end shortly.
            # (allows the dust to clear and draws to occur if deaths are
            # close enough)

        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            None)

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
