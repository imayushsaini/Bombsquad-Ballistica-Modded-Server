# Made by Froshlee14
# ba_meta require api 6

from __future__ import annotations

from typing import TYPE_CHECKING

import ba, _ba, random
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor import spaz

if TYPE_CHECKING:
   from typing import Any, Union, Type, List, Dict, Tuple, Sequence, Optional

class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0

# ba_meta export game
class GetTheTargetGame(ba.TeamGameActivity[Player, Team]):
    name = 'Get the Target'
    description = 'Kill target to get points (dont kill if teammate). If you\'re \nthe Target, survive to get points, \nplayer/team that reached the\n required points, wins.'
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
        ba.IntSetting("Points to Win Per Player", min_value=1, default=5, increment=1),
        ba.IntSetting("Time to Kill", min_value=5, max_value=30, default=10, increment=1),
        ba.IntChoiceSetting("Time Limit", choices=[('None', 0),('1 Minute', 60),('2 Minutes', 120),('5 Minutes', 300),('10 Minutes', 600),('20 Minutes', 1200)],default=0),
        ba.FloatChoiceSetting("Respawn Times",choices=[('Shorter', 0.25),('Short', 0.5),('Normal', 1.0),('Long', 2.0),('Longer', 4.0)],default=1.0),
        ba.IntChoiceSetting("Target Indicator", choices=[('None', 0),('Light', 1),('Text', 2)],default=0),
        ba.BoolSetting("Epic Mode", default=False)
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
        self.settings = settings
        if self.settings['Epic Mode']: self.slow_motion = True
        self._chosed_player = self.chosen_player = None
        self._score_to_win: Optional[int] = None
        self._dingsound = ba.getsound('dingSmall')
        self._chosing_sound = ba.getsound('scoreIncrease')
        self._chosed_sound = ba.getsound('cashRegister2')
        self._error_sound = ba.getsound('error')
        self._tick_sound = ba.getsound('tick')
        self._time_remaining = int(self.settings['Time to Kill'])
        self._time_limit = float(settings['Time Limit'])
        self.ytpe = int(settings["Target Indicator"])
        self._scoreboard = Scoreboard()
        
        self.default_music = (ba.MusicType.EPIC if self.slow_motion else
                              ba.MusicType.TO_THE_DEATH)

    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Kill enemy targets or Survive ${ARG1} times.', self._score_to_win

    def get_instance_scoreboard_display_string(self) -> str:
        return 'Kill target/Survive ' + str(self._score_to_win) + ' times.'

    def on_team_join(self, team: Team) -> None:
        if self.has_begun(): self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()
        self._score_to_win = (int(self.settings["Points to Win Per Player"]) *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()
        ba.timer(3000 * 0.001, self.star_chosing_player)
        
        self._chose_text = ba.newnode('text',
                         attrs={
                         'text':' ',
                         'v_attach':'bottom',
                         'h_attach':'center',
                         'h_align':'center',
                         'v_align':'center',
                         'maxwidth':150,  
                         'shadow':1.0,
                         'flatness':1.0,
                         'color':(1,1,1),
                         'scale':1,
                         'position':(0,155)})
        
    def on_player_leave(self, player: PlayerType) -> None:
        super().on_player_leave(player)
        if len(self.players) in [0,1]: self.end_game()
        if player == self._chosed_player: self.star_chosing_player()

    def print_random_icon(self) -> None:
        get_alive = []
        for spas in self.players:
          if spas.is_alive():
             get_alive.append(spas)

        if not len(get_alive) == 0:
            self._chose_text.text = 'Chosing Player...'
            self.loops += 1
            player = random.choice(get_alive)
            icon = player.get_icon()
            outline_tex = ba.gettexture('characterIconMask')
            texture = icon['texture']
            self._image = ba.NodeActor(ba.newnode('image',
                           attrs={'texture':texture,
                           'tint_texture':icon['tint_texture'],
                           'tint_color':icon['tint_color'],
                           'tint2_color':icon['tint2_color'],
                           'mask_texture':outline_tex,
                           'position':(0,80),
                           'scale':(100,100), 'opacity':1.0,
                           'absolute_scale':True,'attach':'bottomCenter'}))
            self._name = ba.NodeActor(ba.newnode('text',
                             attrs={'v_attach':'bottom', 'h_attach':'center',
                             'text':ba.Lstr(value=player.getname()),
                             'maxwidth':100,  'h_align':'center',
                             'v_align':'center', 'shadow':1.0,
                             'flatness':1.0, 'color':ba.safecolor(icon['tint_color']),
                                 'scale':1,'position':(0,20)}))
            if self.loops >= self.loop_max:
               self.chosen_player = player
               self.stopn_chose_player()
        else:
            self._chose_text.text = 'Waiting for players...'
            texture = ba.gettexture("powerupCurse")
            self._image = ba.NodeActor(ba.newnode('image',
                           attrs={'texture':texture,
                           'position':(0,80),
                           'scale':(100,100), 'opacity':1.0,
                           'absolute_scale':True,'attach':'bottomCenter'}))
            self._name = ba.NodeActor(ba.newnode('text',
                             attrs={'v_attach':'bottom', 'h_attach':'center',
                             'text':" ",
                             'maxwidth':100,  'h_align':'center',
                             'v_align':'center', 'shadow':1.0,
                             'flatness':1.0,
                             'color':(1,1,1),
                             'scale':1,'position':(0,20)}))
            return


    def star_chosing_player(self) -> None:
        if len(self.players) in [0,1]: self.end_game()
        self._sound = ba.NodeActor(ba.newnode('sound',attrs={'sound':self._chosing_sound,'volume':1.0}))
        self.stop_timer()
        self.loops = 0
        self.loop_max = random.randrange(15,30)
        self._chosed_player = None
        self._logo_effect = ba.Timer(80 * 0.001,ba.WeakCall(self.print_random_icon),repeat=True)
        self._chose_text.color =  (1,1,1)
        
    def stopn_chose_player(self) -> None:
        self._sound = None
        self._logo_effect = None
        ba.playsound(self._chosed_sound)
        player = self.chosen_player
        self._chosed_player = player
        self._chose_text.text = 'Kill the Enemy!'
        self._chose_text.color =  (1,1,0)
        
        palyer = player.actor
        if self.ytpe == 1:
            palyer.r = ba.newnode('light',
              attrs={
              'radius':0.2,
              'intensity': 5.0,
              'color': palyer.node.color
             })
            palyer.node.connectattr('position', palyer.r, 'position')
        elif self.ytpe == 2:
            dummy = ba.newnode('math',owner=palyer.node,attrs={'input1': (0, 1.25, 0),'operation': 'add'})
            palyer.node.connectattr('position', dummy, 'input2')
            palyer.r = ba.newnode('text',owner=palyer.node,
                               attrs={'text': 'TARGET!',
                               'in_world': True,
                               'shadow': 1.0,
                               'flatness': 1.5,
                               'scale': 0.014,
                               'h_align': 'center',})
            ba.animate_array(palyer.r,'color',3,{
            0.0:(0.3, 0.3, 1.0),
            0.5:(1, 0.3, 0.3),
            1.0:(0.3, 1 , 0.3),
            2.0:(0.3, 0.3, 1.0)
            }, True)
            dummy.connectattr('output', palyer.r, 'position')
        self.start_timer()

    def start_timer(self) -> None:
        self._time_remaining = self.settings['Time to Kill']
        self._timer_x = ba.Timer(1000*0.001,ba.WeakCall(self.tick),repeat=True)

    def stop_timer(self) -> None:
        self._time = None
        self._timer_x = None

    def tick(self) -> None:
        self.check_for_expire()
        self._time = ba.NodeActor(ba.newnode('text',
                         attrs={'v_attach':'top', 'h_attach':'center',
                         'text':('Kill Time: '+str(self._time_remaining)+'s'), 'opacity': 0.8,
                         'maxwidth':100,  'h_align':'center',
                         'v_align':'center', 'shadow':1.0,
                         'flatness':1.0, 'color':(1,1,1),
                         'scale':2,'position':(0,-100)}))
        self._time_remaining -= 1
        ba.playsound(self._tick_sound)
        
    def check_for_expire(self) -> None:
        if self._time_remaining <= 0:
            self.stop_timer()
            if len(self.players) == 0: pass
            elif self._chosed_player.is_alive():
                player = self._chosed_player 
                player.team.score += 1
                player.actor.r.delete()
                ba.playsound(self._dingsound)
                self._update_scoreboard()
                if any(team.score >= self._score_to_win for team in self.teams):
                    ba.timer(500*0.001,self.end_game)
                self._chose_text.text = 'Survived!'
                self._chose_text.color =  (0,1,0)
            ba.timer(600*0.001,self.star_chosing_player)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            self.respawn_player(player)

            killer = msg.getkillerplayer(Player)
            assert self._score_to_win is not None
            
            if player == self._chosed_player:
                self._chosed_player.actor.r.delete()
                if killer.team is player.team:
                    if isinstance(self.session, ba.FreeForAllSession):
                        player.team.score = max(0,player.team.score-1)
                    else:
                        ba.playsound(self._dingsound)
                        for team in self.teams:
                            if team is not killer.team:
                                team.score += 1
                else:
                    killer.team.score += 1
                    ba.playsound(self._dingsound)
                    try: killer.actor.set_score_text(str(killer.team.score)+'/'+str(self._score_to_win),color=killer.team.color,flash=True)
                    except Exception: pass

                self._update_scoreboard()
                if any(team.score >= self._score_to_win for team in self.teams):
                    ba.timer(500*0.001,self.end_game)
                    
                if killer != self._chosed_player:
                    self._chose_text.text = 'Killed!'
                    self._chose_text.color =  (1,0.5,0)
                else:
                    self._chose_text.text = 'Dead!'
                    self._chose_text.color =  (1.0,0,0)
                    ba.playsound(self._error_sound)
                ba.timer(600*0.001,self.star_chosing_player)

        else: super().handlemessage(msg)

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)