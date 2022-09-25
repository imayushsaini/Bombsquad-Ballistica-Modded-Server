# Released under the MIT License. See LICENSE for details.
#
"""Defines assault minigame."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba, random
from math import cos, sin
from bastd.actor.popuptext import PopupText
from bastd.actor.powerupbox import PowerupBox, PowerupBoxFactory
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Sequence, Union

class Player(ba.Player['Team']):
    ...

class Team(ba.Team[Player]):
    def __init__(self) -> None:
        self.score = 0
        self.stored_score = 0
        self.role: str = ''
        self.spot: str = ''


# ba_meta export game
class BaseRaidGame(ba.TeamGameActivity[Player, Team]):

    name = 'Tower Rush'
    description = """If "score" is shown on your character,\ngo through inside the enemy team's castle-like structure\nto score. Otherwise if "defend" is shown\nprevent the enemy team from entering."""
    available_settings = [
        ba.IntSetting('Score to Win Per Team', min_value=1, default=10),
        ba.IntChoiceSetting('Time Limit',
            choices=[
                ('None', 0),
                ('1 Minute', 60),
                ('2 Minutes', 120),
                ('5 Minutes', 300),
                ('10 Minutes', 600),
                ('20 Minutes', 1200)], 
            default=300),
        ba.IntSetting('Countdown Time Each Round', min_value = 10, increment=5 ,default = 60),
        ba.FloatChoiceSetting(
            'Respawn Times',
            choices=[
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0)],
            default=1.0),
        ba.BoolSetting('Epic Mode', default=False),
        ba.BoolSetting('Kill player on ground', default=True),
        ba.BoolSetting('Random Spawn Point (Team)', default=False),
        ba.BoolSetting('[On score] Single Teleport', default=True),
        ba.BoolSetting('[On score] Single Celebrate', default=True)]

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Tower D']

    def get_instance_scoreboard_display_string(self) -> ba.Lstr:
        return "Score " + str(self._score_to_win) + " Points"

    def get_instance_description(self) -> Union[str, Sequence]:
        return "if Score, score by reaching through the foe's structure\nif Defend, prevent enemy from scoring."

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.get_s = settings
        self._scoreboard = Scoreboard()
        self._last_score_time = 0.0
        self._score_sound = ba.getsound('score')
        self._epic_mode = bool(settings['Epic Mode'])
        self._score_to_win = int(settings['Score to Win Per Team'])
        self._time_limit = float(settings['Time Limit'])
        self.time = int(settings['Countdown Time Each Round'])
        self.change_spawn_points = bool(settings['Random Spawn Point (Team)'])
        self.ground = bool(settings['Kill player on ground'])
        self.loop_timer = self.knocker = None

        self.disable_controls = bool(True)

        # Base class overrides
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.FORWARD_MARCH)

    def on_team_join(self, team: Team) -> None:
        self._update_scoreboard()

    def on_player_join(self, player: PlayerType) -> None:
        if not self.disable_controls:
           self.spawn_player(player)
        else:
           pass

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_powerup_drops()
        palyer = SharedObjects.get().player_material

        death_material = ba.Material(); box_1 = ba.Material(); box_2 = ba.Material()
        death_material.add_actions(
                 conditions=('they_have_material', palyer),
                 actions=(('modify_part_collision', 'collide', True),
                         ('modify_part_collision', 'physical', False),
                         ('call', 'at_connect', ba.WeakCall(self.handle_region, 'ground'))))
        box_1.add_actions(
                 conditions=('they_have_material', palyer),
                 actions=(('modify_part_collision', 'collide', True),
                         ('modify_part_collision', 'physical', False),
                         ('call', 'at_connect', ba.WeakCall(self.handle_region, 'turret_1'))))
        box_2.add_actions(
                 conditions=('they_have_material', palyer),
                 actions=(('modify_part_collision', 'collide', True),
                         ('modify_part_collision', 'physical', False),
                         ('call', 'at_connect', ba.WeakCall(self.handle_region, 'turret_2'))))

        self.r: List[ba.NodeActor] = []
        self.r.append(ba.NodeActor(ba.newnode('region',
                              attrs={'position': (-8.450964, 4.784977, 0.300695),
                              'scale': (0.2, 3.45, 1.28),
                              'type': 'box',
                              'materials':[box_1]})))
        self.r.append(ba.NodeActor(ba.newnode('region',
                              attrs={'position': (7.470666, 3.429754, 0.328592),
                              'scale': (0.2, 2.47, 1.39),
                              'type': 'box',
                              'materials':[box_2]})))
        if self.ground:
            self.r.append(ba.NodeActor(ba.newnode('region',
                              attrs={'position': (-0.588583, 1.569668, 4.049047),
                              'scale': (18.0, 0.1, 5.0),
                              'type': 'box',
                              'materials':[death_material]})))
            self.r.append(ba.NodeActor(ba.newnode('region',
                              attrs={'position': (-0.128583, 1.569668, -1.670954),
                              'scale': (5.0, 0.1, 7.0),
                              'type': 'box',
                              'materials':[death_material]})))

        self.r_timer = ba.newnode('text',
                       attrs={
                           'v_attach': 'top',
                           'h_attach': 'center',
                           'h_align': 'center',
                           'color': (0.7,0.88,1.0,1.1),
                           'shadow': 1.0,
                           'flatness': 1.0,
                           'position': (0, -120),
                           'scale': 1.7,
                           'text': "..."})
        self.setup_standard_time_limit(self._time_limit)
        ba.timer(4.5, ba.WeakCall(self.selection, first_run = True))
        teams = []
        for t in self.teams:
            teams.append(t)
        roles = ['raid', 'defend']
        if self.change_spawn_points:
            spots = ['spot2','spot1']

            teams[0].spot = spots[random.randint(0,1)]
            spots.remove(teams[0].spot)
            teams[1].spot = spots[0]
        else:
            teams[0].spot = 'spot1'
            teams[1].spot = 'spot2'

        
        teams[0].role = roles[random.randint(0, 1)]
        roles.remove(teams[0].role)
        teams[1].role = roles[0]
        def launch():
            for t in self.teams:
                if t.role == 'raid':
                    ba.screenmessage(t.name.evaluate() + " Team, will be the goaler", color=t.color)
                elif t.role == 'defend':
                    ba.screenmessage(t.name.evaluate() + " Team, will be the defender", color=t.color)
        ba.timer(1.9, launch)

    def knock_players(self) -> None:
        for p in self.players:
            if p.is_alive():
                p.actor.node.handlemessage('knockout', 800.0)

    def decrease(self) -> None:
        if int(self.time) != 0:
            self.time -= 1
            self.r_timer.text = "Round Time: " + str(self.time)
        else:
            self.loop_timer = None
            self.disable_controls = True
            self.r_timer.text = "Round Ended"
            self.knock_players()
            self.knocker = ba.Timer(0.8, ba.Call(self.knock_players), repeat=True)
            ba.timer(1, lambda: self.selection())

    def get_pos(self, player: Player, center: bool = False) -> None:

        ang = random.randint(0, 360)
        rad = random.uniform(0, 2.0) if not center else 0.0
        y = random.uniform(0.9, 1.16)
        if player.team.spot == 'spot1':
           x = cos(ang) * rad
           z = sin(ang) * rad
           pos = (-5.786582 + x, 2.8651068 + y, -0.7751054 + z)
        elif player.team.spot == 'spot2':
           ang = random.randint(0, 360)
           rad = random.uniform(0, 2.0)
           x = cos(ang) * rad
           z = sin(ang) * rad
           pos = (4.37031 + x, 2.51977 + y, -0.1901849 + z)
        return pos        


    def selection(self, first_run: bool = False) -> None:

        def scene():
            self.disable_controls = True
            teams = []
            for team in self.teams:
                teams.append(team)

            spots = ['spot1', 'spot2']

            if self.change_spawn_points:
                teams[0].spot = spots[random.randint(0, 1)]
                spots.remove(teams[0].spot)
                teams[1].spot = spots[0]

            if not first_run:
                temp2 = teams[0].role
                teams[0].role = teams[1].role

                teams[1].role = temp2

            def func():
                for t in self.teams:
                    if not first_run:
                        if t.role == 'raid':
                            ba.screenmessage(
                                      "It's now " + t.name.evaluate() + " Team's turn, to score. ",
                                      color=(0.5, 0.8, 0.8))
                            break
            ba.timer(0.926, func)

        def scene_2():
            for t in self.teams:
                t.stored_score = 0
            for p in self.players:
                if p.actor is None:
                   self.spawn_player(p)
                elif p.is_alive():
                   p.actor.handlemessage(ba.StandMessage(position=self.get_pos(p), angle=random.uniform(0, 360)))

            def delay():
                for get_s in self.players:
                    if get_s.is_alive():
                        if get_s.team.role == 'raid':
                            PopupText(position=get_s.actor.node.position, text="Score!", color=get_s.team.color, scale=1.5).autoretain()
                        else: 
                            PopupText(position=get_s.actor.node.position, text="Defend!", color=get_s.team.color, scale=1.5).autoretain()

            self.r_timer.text = "Round Time: " + str(self.time)
            self.disable_controls = False
            def a(): self.knocker = None
            ba.timer(0.9, a)
            ba.timer(0.488 if first_run else 0.67, delay)

            self.time = self.get_s['Countdown Time Each Round']
            self.loop_timer = ba.Timer(1, ba.Call(self.decrease), repeat=True)

        def text():
            for team in self.teams:
                if not first_run:
                    if team.role == 'raid':
                        ba.screenmessage(
                                  team.name.evaluate() + " Team secured " + str(team.stored_score) + " goals in " + str(self.get_s["Countdown Time Each Round"]) + " seconds.",
                                  color=(0.4, 0.6, 1.0)
                                  )
                        break

        ba.timer(1.033, text)
        ba.timer(2, scene)
        ba.timer(4.858 if not first_run else 3, scene_2)

    def spawn_player(self, player: Player) -> ba.Actor:
        spaz = self.spawn_player_spaz(player, position=self.get_pos(player))
        return spaz

    def teleport(self, player: Player) -> None:
        if self.get_s["[On score] Single Teleport"]:
            for this in player.team.players:
                if this.actor:
                    this.actor.handlemessage(ba.StandMessage(position=self.get_pos(this), angle=random.uniform(0, 360)))
        else:
            if player.actor:
                player.actor.handlemessage(ba.StandMessage(position=self.get_pos(player), angle=random.uniform(0, 360)))

        if self.get_s['[On score] Single Celebrate']:
            for this in player.team.players:
                if this.actor:
                    this.actor.handlemessage(ba.CelebrateMessage(2.0))
        else:
            if player.actor:
                player.actor.handlemessage(ba.CelebrateMessage(2.0))
        self.stats.player_scored(player, 10, big_message=True)

    def handle_region(self, region: str) -> None:
        try:
           player = ba.getcollision().opposingnode.getdelegate(
                PlayerSpaz, True).getplayer(Player, True)
        except: return

        if region == 'ground' and not self.disable_controls:
            def delay():
                player.actor.handlemessage(ba.DieMessage())
            ba.timer(10*0.001, delay)

        elif region == 'turret_2':
            if player.is_alive():
                if player.team.role == 'raid' and player.team.spot != 'spot2':
                   if ba.time() != self._last_score_time:
                      self._last_score_time = ba.time()
                      ba.playsound(self._score_sound)
                      player.team.score += 1
                      player.team.stored_score += 1
                      self._update_scoreboard()
                      self.teleport(player)
                else:
                   return

        elif region == 'turret_1':
            if player.is_alive():
                if player.team.role == 'raid' and player.team.spot != 'spot1':
                   if ba.time() != self._last_score_time:
                      self._last_score_time = ba.time()
                      ba.playsound(self._score_sound)
                      player.team.score += 1
                      player.team.stored_score += 1
                      self._update_scoreboard()
                      self.teleport(player)

    def _standard_drop_powerup(self, index: int, expire: bool = True) -> None:
        self.i = [(6.1527314, 4.9323297, -7.8393626),
                  (-6.8911242, 4.4702456, -7.8909187),
                  (-5.3111238, 3.930246, -6.170918),
                  (3.9788754, 3.8102467, -5.9009175),
                  (-4.926642821, 2.397645612, 2.876782366),
                  (-1.964335546, 2.397645612, 3.751374716),
                  (1.64883201, 2.397645612, 3.751374716),
                  (4.398865293, 2.397645612, 2.877618924)]
        self.i = ([p[:3] for p in self.i])
        PowerupBox(
            position=self.i[index],
            poweruptype=PowerupBoxFactory.get().get_random_powerup_type(),
            expire=expire).autoretain()

    def _standard_drop_powerups(self) -> None:
        for i in range(4 if self.ground else 8):
            ba.timer(i * 0.4, ba.WeakCall(self._standard_drop_powerup, i))

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            self.respawn_player(msg.getplayer(Player))
        else:
            super().handlemessage(msg)
        return None

    def end_game(self) -> None:
        self.loop_timer = self.knocker = None
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)
            if team.score >= self._score_to_win:
               self.end_game()