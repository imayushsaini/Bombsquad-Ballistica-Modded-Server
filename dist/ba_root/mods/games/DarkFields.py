#Made by Froshlee14
#Ported by: Freaku / @[Just] Freak#4999






# ba_meta require api 6
from __future__ import annotations
from typing import TYPE_CHECKING
import ba,random
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.bomb import Bomb
from bastd.gameutils import SharedObjects
if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional


class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class DFGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Dark Fields'
    description = 'Get to the other side.'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
            ba.IntSetting(
                'Score to Win',
                min_value=1,
                default=3,
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
            ba.BoolSetting('Epic Mode', default=False)
        ]
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Football Stadium']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._dingsound = ba.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self._score_to_win = int(
            settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else ba.MusicType.TO_THE_DEATH)
        self._scoreRegionMaterial = ba.Material()
        self._scoreRegionMaterial.add_actions(
            conditions=("they_have_material",shared.player_material),
            actions=(("modify_part_collision","collide",True),
                     ("modify_part_collision","physical",False),
                     ("call","at_connect", self._onPlayerScores)))
        self.first_time = True

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Get to the other side ${ARG1} times', self._score_to_win

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'Get to the other side ${ARG1} times', self._score_to_win

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        ba.getactivity().globalsnode.tint = (0.5, 0.5, 0.5)
        a = ba.newnode('locator',attrs={'shape':'box','position':(12,0,.1087926362),'color':(5,5,5),'opacity':1,'draw_beauty':True,'additive':False,'size':[2.0,0.1,11.8]})
        b = ba.newnode('locator',attrs={'shape':'box','position':(-12,0,.1087926362),'color':(5,5,5),'opacity':1,'draw_beauty':True,'additive':False,'size':[2.0,0.1,11.8]})
        self.isUpdatingMines = False
        self._scoreSound = ba.getsound('dingSmall')
        self.setup_standard_time_limit(self._time_limit)

        self._update_scoreboard()
        for p in self.players:
            if p.actor is not None:
                try:p.actor.disconnect_controls_from_player()
                except Exception as e: print ('Can\'t connect to player',e)

        self._scoreRegions = []
        defs = self.map.defs
        self._scoreRegions.append(ba.NodeActor(ba.newnode('region',
                                 attrs={'position':defs.boxes['goal1'][0:3],
                                        'scale':defs.boxes['goal1'][6:9],
                                        'type': 'box',
                                        'materials':[self._scoreRegionMaterial]})))
        self.mines = []
        self.spawnMines()
        ba.timer(2.5,self.start)

    def start(self):
        ba.timer(random.randrange(3,7),self.doRandomLighting)
        ba.animate_array(ba.getactivity().globalsnode,'tint',3,{0:(0.5,0.5,0.5),2:(0.2,0.2,0.2)})

    def doRandomLighting(self):
        ba.timer(random.randrange(3,7),self.doRandomLighting)
        if self.isUpdatingMines: return
        ba.animate_array(ba.getactivity().globalsnode,'tint',3,{0:(0.5,0.5,0.5),0.8:(0.2,0.2,0.2)})

    def spawnMines(self):
        delay = 0
        xs = [10,8,6,4,2,0,-2,-4,-6,-8,-10]
        for x in xs:
            for i in range(3):
                pos = (x,1,random.randrange(-5,6))
                ba.timer(delay,ba.Call(self.doMine,pos))
                delay += 0.075
        ba.timer(2.48,self.stopUpdateMines)

    def stopUpdateMines(self):
        self.isUpdatingMines = False
        self.first_time = False

    def updateMines(self):
        if self.isUpdatingMines: return
        self.isUpdatingMines = True
        for m in self.mines:
            m.node.delete()
        self.mines = []
        self.spawnMines()

    def doMine(self,pos):
        b = Bomb(position=pos,bomb_type='land_mine').autoretain()
        b.arm()
        self.mines.append(b)

    # overriding the default character spawning..
    def spawn_player(self, player: Player):
        if self.first_time: ba.timer(2.5, ba.Call(self.spawn_with_delay, player))
        else: self.spawn_with_delay(player)
    def spawn_with_delay(self, player: Player):
        spaz = self.spawn_player_spaz(player)
        position = (-12.4,1,random.randrange(-5,5))
        spaz.connect_controls_to_player(enable_punch=False,enable_bomb=False)
        spaz.handlemessage(ba.StandMessage(position, random.uniform(0,360)))
        return spaz

    def _onPlayerScores(self):
        try: player = ba.getcollision().opposingnode.getdelegate(PlayerSpaz, True).getplayer(Player, True)
        except Exception: player = None
        if player.exists() and player.is_alive():
            for team in self.teams:
                if team is player.team:
                    team.score += 1
            ba.playsound(self._scoreSound) 
            ba.animate_array(ba.getactivity().globalsnode,'tint',3,{0:(0.5,0.5,0.5),2.8:(0.2,0.2,0.2)})
            self._update_scoreboard()
            player.actor.handlemessage(ba.DieMessage())
            self.updateMines()

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

            self._update_scoreboard()

            # If someone has won, set a timer to end shortly.
            # (allows the dust to clear and draws to occur if deaths are
            # close enough)
            assert self._score_to_win is not None
            if any(team.score >= self._score_to_win for team in self.teams):
                ba.timer(0.5, self.end_game)

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
