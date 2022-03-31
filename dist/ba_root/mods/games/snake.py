#snake
# Released under the MIT License. See LICENSE for details.
#
"""Snake game by SEBASTIAN2059"""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor import bomb as stdbomb

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional

class ScoreMessage:
    """It will help us with the scores."""
    def __init__(self,player: Player):
        self.player = player
        
    def getplayer(self):
        return self.player

class Player(ba.Player['Team']):
    """Our player type for this game."""
    def __init__(self) -> None:
        
        self.mines = []
        self.actived = None

class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0

lang = ba.app.lang.language
if lang == 'Spanish':
    description = 'Sobrevive a un número determinado de minas para ganar.'
    join_description = 'Corre y no te dejes matar.'
    view_description = 'sobrevive ${ARG1} minas'
   
else:
    description = 'Survive a set number of mines to win.'
    join_description = "Run and don't get killed."
    view_description = 'survive ${ARG1} mines'

class Custom_Mine(stdbomb.Bomb):
    """Custom a mine :)"""
    def __init__(self,position,source_player):
        stdbomb.Bomb.__init__(self,position=position,bomb_type='land_mine',source_player=source_player)
        
    def handlemessage(self,msg: Any) -> Any:
        if isinstance(msg, ba.HitMessage):
            return
        else:
            super().handlemessage(msg)

# ba_meta export game
class SnakeGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Snake'
    description = description

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
            ba.IntSetting(
                'Score to Win',
                min_value=40,
                default=80,
                increment=5,
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
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: Optional[int] = None
        self._dingsound = ba.getsound('dingSmall')
        
        self._beep_1_sound = ba.getsound('raceBeep1')
        self._beep_2_sound = ba.getsound('raceBeep2')
        
        self._epic_mode = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(
            settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])
        
        self._started = False
        
        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.TO_THE_DEATH)

    def get_instance_description(self) -> Union[str, Sequence]:
        return join_description

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return view_description, self._score_to_win

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        #self.setup_standard_powerup_drops()

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = (self._kills_to_win_per_player *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()
        
    
        if self.slow_motion:
            t_scale = 0.4
            light_y = 50
        else:
            t_scale = 1.0
            light_y = 150
        lstart = 7.1 * t_scale
        inc = 1.25 * t_scale

        ba.timer(lstart, self._do_light_1)
        ba.timer(lstart + inc, self._do_light_2)
        ba.timer(lstart + 2 * inc, self._do_light_3)
        ba.timer(lstart + 3 * inc, self._start_race)

        self._start_lights = []
        for i in range(4):
            lnub = ba.newnode('image',
                              attrs={
                                  'texture': ba.gettexture('nub'),
                                  'opacity': 1.0,
                                  'absolute_scale': True,
                                  'position': (-75 + i * 50, light_y),
                                  'scale': (50, 50),
                                  'attach': 'center'
                              })
            ba.animate(
                lnub, 'opacity', {
                    4.0 * t_scale: 0,
                    5.0 * t_scale: 1.0,
                    12.0 * t_scale: 1.0,
                    12.5 * t_scale: 0.0
                })
            ba.timer(13.0 * t_scale, lnub.delete)
            self._start_lights.append(lnub)

        self._start_lights[0].color = (0.2, 0, 0)
        self._start_lights[1].color = (0.2, 0, 0)
        self._start_lights[2].color = (0.2, 0.05, 0)
        self._start_lights[3].color = (0.0, 0.3, 0)

    def _do_light_1(self) -> None:
        assert self._start_lights is not None
        self._start_lights[0].color = (1.0, 0, 0)
        ba.playsound(self._beep_1_sound)

    def _do_light_2(self) -> None:
        assert self._start_lights is not None
        self._start_lights[1].color = (1.0, 0, 0)
        ba.playsound(self._beep_1_sound)

    def _do_light_3(self) -> None:
        assert self._start_lights is not None
        self._start_lights[2].color = (1.0, 0.3, 0)
        ba.playsound(self._beep_1_sound)

    def _start_race(self) -> None:
        assert self._start_lights is not None
        self._start_lights[3].color = (0.0, 1.0, 0)
        ba.playsound(self._beep_2_sound)

        self._started = True
        
        for player in self.players:
            self.generate_mines(player)
    
    # overriding the default character spawning..
    def spawn_player(self, player: Player) -> ba.Actor:
        spaz = self.spawn_player_spaz(player)

        # Let's reconnect this player's controls to this
        # spaz but *without* the ability to attack or pick stuff up.
        spaz.connect_controls_to_player(enable_punch=False,
                                        enable_bomb=False,
                                        enable_pickup=False)

        # Also lets have them make some noise when they die.
        spaz.play_big_death_sound = True
        if self._started:
            self.generate_mines(player)
        return spaz
        
    
    def generate_mines(self,player: Player):
        try:
            player.actived = ba.Timer(0.5,ba.Call(self.spawn_mine, player),repeat=True)
        except Exception as e:
         print('Exception -> '+ str(e))
                
    
    
    def spawn_mine(self,player: Player):
        if player.team.score >= self._score_to_win:
            return
        pos = player.actor.node.position
        # mine = stdbomb.Bomb(position=(pos[0], pos[1] + 2.0, pos[2]),
                    # velocity=(0, 0, 0),
                    # bomb_type='land_mine',
                    # #blast_radius=,
                    # source_player=player.actor.source_player,
                    # owner=player.actor.node).autoretain()
        mine = Custom_Mine(position=(pos[0], pos[1] + 2.0, pos[2]),
                            source_player=player.actor.source_player)
        
        def arm():
            mine.arm()
        ba.timer(0.5,arm)
        
        player.mines.append(mine)
        if len(player.mines) > 15:
            for m in player.mines:
                try:
                    m.node.delete()
                except Exception:
                    pass
                player.mines.remove(m)
                break
        
        self.handlemessage(ScoreMessage(player))
    
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)
            
            player.actived = None
            
        elif isinstance(msg, ScoreMessage):
            player = msg.getplayer()
            
            player.team.score += 1
            self._update_scoreboard()
            
            assert self._score_to_win is not None
            if any(team.score >= self._score_to_win for team in self.teams):
                self.end_game() #ba.timer(0.5, self.end_game)
        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
