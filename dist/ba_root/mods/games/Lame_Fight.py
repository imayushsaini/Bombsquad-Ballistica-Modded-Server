
# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import ba
from bastd.actor.spazbot import SpazBotSet, ChargerBot, BrawlerBotProShielded, TriggerBotProShielded, ExplodeyBot, BomberBotProShielded, SpazBotDiedMessage
from bastd.actor.onscreentimer import OnScreenTimer

if TYPE_CHECKING:
    from typing import Any, Type, Dict, List, Optional

def ba_get_api_version():
    return 6

def ba_get_levels():
	return [ba._level.Level(
            'Lame Fight',
			gametype=LameFightGame,
			settings={},
			preview_texture_name='courtyardPreview')]

class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

# ba_meta export game
class LameFightGame(ba.TeamGameActivity[Player, Team]):
    name = "Lame Fight"
    description = "Save World With Super Powers"
    slow_motion = True
    scoreconfig = ba.ScoreConfig(label='Time',
                                 scoretype=ba.ScoreType.MILLISECONDS,
                                 lower_is_better=True)
    default_music = ba.MusicType.TO_THE_DEATH
    
    def __init__(self, settings:dict):
        settings['map'] = "Courtyard"
        super().__init__(settings)
        self._timer: Optional[OnScreenTimer] = None
        self._winsound = ba.getsound('score')
        self._won = False
        self._bots = SpazBotSet()
    
    def on_begin(self) -> None:
        super().on_begin()
        
        self._timer = OnScreenTimer()
        ba.timer(4.0, self._timer.start)
        
        #Bots Hehe
        ba.timer(1.0, lambda: self._bots.spawn_bot(ChargerBot, pos=(3,3,-2),spawn_time = 3.0))
        ba.timer(1.0, lambda: self._bots.spawn_bot(ChargerBot, pos=(-3,3,-2),spawn_time = 3.0))
        ba.timer(1.0, lambda: self._bots.spawn_bot(ChargerBot, pos=(5,3,-2),spawn_time = 3.0))
        ba.timer(1.0, lambda: self._bots.spawn_bot(ChargerBot, pos=(-5,3,-2),spawn_time = 3.0))
        ba.timer(1.0, lambda: self._bots.spawn_bot(ChargerBot, pos=(0,3,1),spawn_time = 3.0))
        ba.timer(1.0, lambda: self._bots.spawn_bot(ChargerBot, pos=(0,3,-5),spawn_time = 3.0))
        ba.timer(9.0, lambda: self._bots.spawn_bot(BomberBotProShielded, pos=(-7,5,-7.5),spawn_time = 3.0))
        ba.timer(9.0, lambda: self._bots.spawn_bot(BomberBotProShielded, pos=(7,5,-7.5),spawn_time = 3.0))
        ba.timer(9.0, lambda: self._bots.spawn_bot(BomberBotProShielded, pos=(7,5,1.5),spawn_time = 3.0))
        ba.timer(9.0, lambda: self._bots.spawn_bot(BomberBotProShielded, pos=(-7,5,1.5),spawn_time = 3.0))
        ba.timer(12.0, lambda: self._bots.spawn_bot(TriggerBotProShielded, pos=(-1,7,-8),spawn_time = 3.0))
        ba.timer(12.0, lambda: self._bots.spawn_bot(TriggerBotProShielded, pos=(1,7,-8),spawn_time = 3.0))
        ba.timer(15.0, lambda: self._bots.spawn_bot(ExplodeyBot, pos=(0,3,-5),spawn_time = 3.0))
        ba.timer(20.0, lambda: self._bots.spawn_bot(ExplodeyBot, pos=(0,3,1),spawn_time = 3.0))
        ba.timer(20.0, lambda: self._bots.spawn_bot(ExplodeyBot, pos=(-5,3,-2),spawn_time = 3.0))
        ba.timer(20.0, lambda: self._bots.spawn_bot(ExplodeyBot, pos=(5,3,-2),spawn_time = 3.0))
        ba.timer(30,self.street)

    def street(self):
        ba.screenmessage("Lame Guys Are Here!",color = (1,0,0))
        for a in range(-1,2):
            for b in range(-3,0):
                self._bots.spawn_bot(BrawlerBotProShielded, pos=(a,3,b),spawn_time = 3.0)
        
    def spawn_player(self, player: Player) -> ba.Actor:
        spawn_center = (0, 3, -2)
        pos = (spawn_center[0] + random.uniform(-1.5, 1.5), spawn_center[1],
               spawn_center[2] + random.uniform(-1.5, 1.5))
        spaz = self.spawn_player_spaz(player,position = pos)
        p = ["Bigger Blast","Stronger Punch","Shield","Speed"]
        Power = random.choice(p)
        spaz.bomb_type = random.choice(["normal","sticky","ice","impact","normal","ice","sticky"])
        ba.screenmessage(f"Now You Have {Power}")
        if Power == p[0]:
            spaz.bomb_count = 3
            spaz.blast_radius = 2.5
        if Power == p[1]:
            spaz._punch_cooldown = 350
            spaz._punch_power_scale = 2.0
        if Power == p[2]:
            spaz.equip_shields()
        if Power == p[3]:
            spaz.node.hockey = True
        return spaz
    def _check_if_won(self) -> None:
        if not self._bots.have_living_bots():
            self._won = True
            self.end_game()
    def handlemessage(self, msg: Any) -> Any:

        # A player has died.
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)  # Augment standard behavior.
            self.respawn_player(msg.getplayer(Player))

        # A spaz-bot has died.
        elif isinstance(msg, SpazBotDiedMessage):
            # Unfortunately the bot-set will always tell us there are living
            # bots if we ask here (the currently-dying bot isn't officially
            # marked dead yet) ..so lets push a call into the event loop to
            # check once this guy has finished dying.
            ba.pushcall(self._check_if_won)

        # Let the base class handle anything we don't.
        else:
            return super().handlemessage(msg)
        return None

    # When this is called, we should fill out results and end the game
    # *regardless* of whether is has been won. (this may be called due
    # to a tournament ending or other external reason).
    def end_game(self) -> None:

        # Stop our on-screen timer so players can see what they got.
        assert self._timer is not None
        self._timer.stop()

        results = ba.GameResults()

        # If we won, set our score to the elapsed time in milliseconds.
        # (there should just be 1 team here since this is co-op).
        # ..if we didn't win, leave scores as default (None) which means
        # we lost.
        if self._won:
            elapsed_time_ms = int((ba.time() - self._timer.starttime) * 1000.0)
            ba.cameraflash()
            ba.playsound(self._winsound)
            for team in self.teams:
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(ba.CelebrateMessage())
                results.set_team_score(team, elapsed_time_ms)

        # Ends the activity.
        self.end(results)
    
    