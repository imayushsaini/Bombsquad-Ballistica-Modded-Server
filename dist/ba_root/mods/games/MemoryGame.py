from __future__ import annotations

## Minigame Fall Guys ##
## Created by: byANG3L ##
## Ported to 1.6 by: Freaku / @[Just] Freak#4999 ##

## From: BSWorld Modpack (https://youtu.be/1TN56NLlShE) ##


# Used in-game boxes and textures instead of external
# So it will run on server and randoms can play init ._.
# (& some improvements)






# incase someone is wondering how is map floating. Check out
# def spawnAllMap(self)



# ba_meta require api 6
from typing import TYPE_CHECKING, overload
import _ba,ba,random
from bastd.gameutils import SharedObjects
if TYPE_CHECKING:
    from typing import Any, Sequence, Optional, List, Dict, Type, Type , Union, Any, Literal


## MoreMinigames.py support ##
def ba_get_api_version():
    return 6

def ba_get_levels():
    return [ba._level.Level('Memory Game',gametype=MGgame, settings={}, preview_texture_name = 'achievementOffYouGo')]
## MoreMinigames.py support ##


class OnTimer(ba.Actor):
    """Timer which counts but doesn't show on-screen"""
    def __init__(self) -> None:
        super().__init__()
        self._starttime_ms: Optional[int] = None
        self.node = ba.newnode('text', attrs={ 'v_attach': 'top', 'h_attach': 'center', 'h_align': 'center', 'color': (1, 1, 0.5, 1), 'flatness': 0.5, 'shadow': 0.5, 'position': (0, -70), 'scale': 0, 'text': ''})
        self.inputnode = ba.newnode('timedisplay',  attrs={      'timemin': 0,      'showsubseconds': True  })
        self.inputnode.connectattr('output', self.node, 'text')
    def start(self) -> None:
        tval = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        assert isinstance(tval, int)
        self._starttime_ms = tval
        self.inputnode.time1 = self._starttime_ms
        ba.getactivity().globalsnode.connectattr('time', self.inputnode, 'time2')
    def has_started(self) -> bool:
        return self._starttime_ms is not None
    def stop(self,
             endtime: Union[int, float] = None,
             timeformat: ba.TimeFormat = ba.TimeFormat.SECONDS) -> None:
        if endtime is None:
            endtime = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
            timeformat = ba.TimeFormat.MILLISECONDS
        if self._starttime_ms is None:
            print('Warning: OnTimer.stop() called without start() first')
        else:
            endtime_ms: int
            if timeformat is ba.TimeFormat.SECONDS:
                endtime_ms = int(endtime * 1000)
            elif timeformat is ba.TimeFormat.MILLISECONDS:
                assert isinstance(endtime, int)
                endtime_ms = endtime
            else:
                raise ValueError(f'invalid timeformat: {timeformat}')

            self.inputnode.timemax = endtime_ms - self._starttime_ms
    # Overloads so type checker knows our exact return type based in args.
    @overload
    def getstarttime(self, timeformat: Literal[ba.TimeFormat.SECONDS] = ba.TimeFormat.SECONDS) -> float:
        ...
    @overload
    def getstarttime(self,
                     timeformat: Literal[ba.TimeFormat.MILLISECONDS]) -> int:
        ...
    def getstarttime(
        self,
        timeformat: ba.TimeFormat = ba.TimeFormat.SECONDS
    ) -> Union[int, float]:
        """Return the sim-time when start() was called.

        Time will be returned in seconds if timeformat is SECONDS or
        milliseconds if it is MILLISECONDS.
        """
        val_ms: Any
        if self._starttime_ms is None:
            print('WARNING: getstarttime() called on un-started timer')
            val_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        else:
            val_ms = self._starttime_ms
        assert isinstance(val_ms, int)
        if timeformat is ba.TimeFormat.SECONDS:
            return 0.001 * val_ms
        if timeformat is ba.TimeFormat.MILLISECONDS:
            return val_ms
        raise ValueError(f'invalid timeformat: {timeformat}')

    @property
    def starttime(self) -> float:
        """Shortcut for start time in seconds."""
        return self.getstarttime()

    def handlemessage(self, msg: Any) -> Any:
        # if we're asked to die, just kill our node/timer
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()




class Player(ba.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        super().__init__()
        self.death_time: Optional[float] = None


class Team(ba.Team[Player]):
    """Our team type for this game."""


# ba_meta export game
class MGgame(ba.TeamGameActivity[Player, Team]):

    name = 'Memory Game'
    description = 'Memories tiles and survive till the end!'
    available_settings = [ba.BoolSetting('Epic Mode', default=False), ba.BoolSetting('Enable Bottom Credits', True)]
    scoreconfig = ba.ScoreConfig(label='Survived', scoretype=ba.ScoreType.MILLISECONDS, version='B')

    # Print messages when players die (since its meaningful in this game).
    announce_player_deaths = True

    # we're currently hard-coded for one map..
    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Sky Tiles']

    # We support teams, free-for-all, and co-op sessions.
    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession)
                or issubclass(sessiontype, ba.CoopSession))

    def __init__(self, settings: dict):
        super().__init__(settings)

        self._epic_mode = settings.get('Epic Mode', False)
        self._last_player_death_time: Optional[float] = None
        self._timer: Optional[OnTimer] = None
        self.credit_text = bool(settings['Enable Bottom Credits'])

        # Some base class overrides:
        self.default_music = (ba.MusicType.EPIC
                              if self._epic_mode else ba.MusicType.SURVIVAL)
        if self._epic_mode:
            self.slow_motion = True
        shared = SharedObjects.get()
        self._collide_with_player=ba.Material()
        self._collide_with_player.add_actions(conditions=('we_are_older_than', 1), actions=(('modify_part_collision', 'collide', True)))
        self.dont_collide=ba.Material()
        self.dont_collide.add_actions(conditions=('we_are_older_than', 1), actions=(('modify_part_collision', 'collide', False)))
        self._levelStage = 0

        self.announcePlayerDeaths = True
        self._lastPlayerDeathTime = None
        self._spawnCenter = (-3.17358, 2.75764, -2.99124)

        self._mapFGPModel = ba.getmodel('buttonSquareOpaque')
        self._mapFGPDefaultTex = ba.gettexture('achievementOffYouGo')

        self._mapFGCurseTex = ba.gettexture('powerupCurse')
        self._mapFGHealthTex = ba.gettexture('powerupHealth')
        self._mapFGIceTex = ba.gettexture('powerupIceBombs')
        self._mapFGImpactTex = ba.gettexture('powerupImpactBombs')
        self._mapFGMinesTex = ba.gettexture('powerupLandMines')
        self._mapFGPunchTex = ba.gettexture('powerupPunch')
        self._mapFGShieldTex = ba.gettexture('powerupShield')
        self._mapFGStickyTex = ba.gettexture('powerupStickyBombs')

        self._mapFGSpaz = ba.gettexture('neoSpazIcon')
        self._mapFGZoe = ba.gettexture('zoeIcon')
        self._mapFGSnake = ba.gettexture('ninjaIcon')
        self._mapFGKronk= ba.gettexture('kronkIcon')
        self._mapFGMel = ba.gettexture('melIcon')
        self._mapFGJack = ba.gettexture('jackIcon')
        self._mapFGSanta = ba.gettexture('santaIcon')
        self._mapFGFrosty = ba.gettexture('frostyIcon')
        self._mapFGBones = ba.gettexture('bonesIcon')
        self._mapFGBernard = ba.gettexture('bearIcon')
        self._mapFGPascal = ba.gettexture('penguinIcon')
        self._mapFGAli = ba.gettexture('aliIcon')
        self._mapFGRobot = ba.gettexture('cyborgIcon')
        self._mapFGAgent = ba.gettexture('agentIcon')
        self._mapFGGrumbledorf = ba.gettexture('wizardIcon')
        self._mapFGPixel = ba.gettexture('pixieIcon')

        self._imageTextDefault = ba.gettexture('bg')
        self._circleTex = ba.gettexture('circleShadow')

        self._image = ba.newnode('image',
                       attrs={'texture': self._imageTextDefault,
                       'position':(0,-100),
                       'scale':(100,100),
                       'opacity': 0.0,
                       'attach':'topCenter'})

        self._textCounter = ba.newnode('text',
                       attrs={'text': '10',
                       'position': (0, -100),
                       'scale': 2.3,
                       'shadow': 1.0,
                       'flatness': 1.0,
                       'opacity': 0.0,
                       'v_attach': 'top',
                       'h_attach': 'center',
                       'h_align': 'center',
                       'v_align': 'center'})

        self._textLevel = ba.newnode('text',
                       attrs={'text': 'Level ' + str(self._levelStage),
                       'position': (0, -28),
                       'scale': 1.3,
                       'shadow': 1.0,
                       'flatness': 1.0,
                       'color': (1.0, 0.0, 1.0),
                       'opacity': 0.0,
                       'v_attach': 'top',
                       'h_attach': 'center',
                       'h_align': 'center',
                       'v_align': 'center'})

        self._imageCircle = ba.newnode('image',
                       attrs={'texture': self._circleTex,
                       'position': (75, -75),
                       'scale': (20,20),
                       'color': (0.2, 0.2, 0.2),
                       'opacity': 0.0,
                       'attach': 'topCenter'})
        self._imageCircle2 = ba.newnode('image',
                       attrs={'texture': self._circleTex,
                       'position': (75, -100),
                       'scale': (20,20),
                       'color': (0.2, 0.2, 0.2),
                       'opacity': 0.0,
                       'attach': 'topCenter'})
        self._imageCircle3 = ba.newnode('image',
                       attrs={'texture': self._circleTex,
                       'position': (75, -125),
                       'scale': (20,20),
                       'color': (0.2, 0.2, 0.2),
                       'opacity': 0.0,
                       'attach': 'topCenter'})


    def on_transition_in(self) -> None:
        super().on_transition_in()
        self._bellLow = ba.getsound('bellLow')
        self._bellMed = ba.getsound('bellMed')
        self._bellHigh = ba.getsound('bellHigh')
        self._tickSound = ba.getsound('tick')
        self._tickFinal = ba.getsound('powerup01')
        self._scoreSound = ba.getsound('score')

        self._image.opacity = 1
        self._textCounter.opacity = 1
        self._textLevel.opacity = 1
        self._imageCircle.opacity = 0.7
        self._imageCircle2.opacity = 0.7
        self._imageCircle3.opacity = 0.7

        self._levelStage += 1

        self._textLevel.text = 'Level ' + str(self._levelStage)

        self._image.texture = self._imageTextDefault

        if self._levelStage == 1:
            timeStart = 6
        ba.timer(timeStart, self._randomPlatform)
        ba.timer(timeStart, self.startCounter)

    def on_begin(self) -> None:
        super().on_begin()

        self._timer = OnTimer()
        self._timer.start()

        self.coldel = True
        self.coldel2 = True
        self.coldel3 = True
        self.coldel4 = True
        self.coldel5 = True
        self.coldel6 = True
        self.coldel7 = True
        self.coldel8 = True
        self.coldel9 = True
        self.coldel10 = True
        self.coldel11 = True
        self.coldel12 = True
        self.coldel13 = True
        self.coldel14 = True
        self.coldel15 = True
        self.coldel16 = True
        import base64
        exec(base64.b64decode("aWYgc2VsZi5jcmVkaXRfdGV4dDoKICAgICMjIFBlb3BsZSBzdGVhbGVkIGNyZWRpdHMgc28gdGhhdHMgd2h5IEkgZW5jb2RlZCB0aGlzLi4uCiAgICAjIyBFdmVuIHRobyB0aGVyZSBpcyBhIG9wdGlvbiwgdGhleSBjaGFuZ2VkIGNyZWF0ZWQgYnkKICAgICMjIGxpa2Ugd3RmIGlzIHRoaWVyIHByb2JsZW0/PwoKICAgICMjIEFueXdheXMgaGF2ZSBhIGdvb2QgZGF5IQogICAgdCA9IGJhLm5ld25vZGUoJ3RleHQnLAogICAgICAgICAgICAgICBhdHRycz17ICd0ZXh0JzoiUG9ydGVkIGJ5IO6BiEZyZWFrdVxuTWFkZSBmb3IgMS40IGJ5IGJ5QU5HM0wiLCAjIyBEaXNhYmxlICdFbmFibGUgQm90dG9tIENyZWRpdHMnIHdoZW4gbWFraW5nIHBsYXlsaXN0LCBObyBuZWVkIHRvIGVkaXQgdGhpcyBsb3ZlbHkuLi4KICAgICAgICAnc2NhbGUnOjAuNywKICAgICAgICAncG9zaXRpb24nOigwLDApLAogICAgICAgICdzaGFkb3cnOjAuNSwKICAgICAgICAnZmxhdG5lc3MnOjEuMiwKICAgICAgICAnY29sb3InOigxLCAxLCAxKSwKICAgICAgICAnaF9hbGlnbic6J2NlbnRlcicsCiAgICAgICAgJ3ZfYXR0YWNoJzonYm90dG9tJ30p").decode('UTF-8'))
        self.spawnAllMap()
        self.flashHide()

        # Check for immediate end (if we've only got 1 player, etc).
        ba.timer(5, self._check_end_game)
        self._dingSound = ba.getsound('dingSmall')
        self._dingSoundHigh = ba.getsound('dingSmallHigh')

    def startCounter(self):
        self._textCounter.text = '10'
        def count9():
            def count8():
                def count7():
                    def count6():
                        def count5():
                            def count4():
                                def count3():
                                    def count2():
                                        def count1():
                                            def countFinal():
                                                self._textCounter.text = ''
                                                ba.playsound(self._tickFinal)
                                                self._stop()
                                            self._textCounter.text = '1'
                                            ba.playsound(self._tickSound)
                                            ba.timer(1, countFinal)
                                        self._textCounter.text = '2'
                                        ba.playsound(self._tickSound)
                                        ba.timer(1, count1)
                                    self._textCounter.text = '3'
                                    ba.playsound(self._tickSound)
                                    ba.timer(1, count2)
                                self._textCounter.text = '4'
                                ba.playsound(self._tickSound)
                                ba.timer(1, count3)
                            self._textCounter.text = '5'
                            ba.playsound(self._tickSound)
                            ba.timer(1, count4)
                        self._textCounter.text = '6'
                        ba.playsound(self._tickSound)
                        ba.timer(1, count5)
                    self._textCounter.text = '7'
                    ba.playsound(self._tickSound)
                    ba.timer(1, count6)
                self._textCounter.text = '8'
                ba.playsound(self._tickSound)
                ba.timer(1, count7)
            self._textCounter.text = '9'
            ba.playsound(self._tickSound)
            ba.timer(1, count8)
        ba.timer(1, count9)

    def on_player_join(self, player: Player) -> None:
        # Don't allow joining after we start
        # (would enable leave/rejoin tomfoolery).
        if self.has_begun():
            ba.screenmessage(
                ba.Lstr(resource='playerDelayedJoinText',
                        subs=[('${PLAYER}', player.getname(full=True))]),
                color=(0, 1, 0))#,transient=True,clients=[player.inputdevice.client_id])
            # For score purposes, mark them as having died right as the
            # game started.
            assert self._timer is not None
            player.death_time = self._timer.getstarttime()
            return
        self.spawn_player(player)

    def on_player_leave(self, player: Player) -> None:
        # Augment default behavior.
        super().on_player_leave(player)

        # A departing player may trigger game-over.
        self._check_end_game()

    # overriding the default character spawning..
    def spawn_player(self, player: Player) -> ba.Actor:
        spaz = self.spawn_player_spaz(player)
        pos = (self._spawnCenter[0] + random.uniform(-1.5, 2.5), self._spawnCenter[1], self._spawnCenter[2] + random.uniform(-2.5, 1.5))
        spaz.connect_controls_to_player(enable_punch=False, enable_bomb=False, enable_pickup=False)
        spaz.handlemessage(ba.StandMessage(pos))
        return spaz

    def _randomSelect(self):
        if self._levelStage == 1:
            self._textureSelected = random.choice([self._mapFGMinesTex,
                                     self._mapFGStickyTex])
            self._image.texture = self._textureSelected
        elif self._levelStage == 2:
            self._textureSelected = random.choice([self._mapFGIceTex,
                                     self._mapFGShieldTex])
            self._image.texture = self._textureSelected
        elif self._levelStage in [3,4,5]:
            self._textureSelected = random.choice([self._mapFGStickyTex,
                                     self._mapFGIceTex,
                                     self._mapFGImpactTex,
                                     self._mapFGMinesTex])
            self._image.texture = self._textureSelected
        elif self._levelStage in [6,7,8,9]:
            self._textureSelected = random.choice([self._mapFGCurseTex,
                                     self._mapFGHealthTex,
                                     self._mapFGIceTex,
                                     self._mapFGImpactTex,
                                     self._mapFGMinesTex,
                                     self._mapFGPunchTex,
                                     self._mapFGShieldTex])
            self._image.texture = self._textureSelected
        elif self._levelStage >= 10:
            self._textureSelected = random.choice([self._mapFGSpaz,
                                     self._mapFGZoe,
                                     self._mapFGSnake,
                                     self._mapFGKronk,
                                     self._mapFGMel,
                                     self._mapFGJack,
                                     self._mapFGSanta,
                                     self._mapFGFrosty,
                                     self._mapFGBones,
                                     self._mapFGBernard,
                                     self._mapFGPascal,
                                     self._mapFGAli,
                                     self._mapFGRobot,
                                     self._mapFGAgent,
                                     self._mapFGGrumbledorf,
                                     self._mapFGPixel])
            self._image.texture = self._textureSelected
        return self._textureSelected

    def _stop(self):
        self._textureSelected = self._randomSelect()
        def circle():
            def circle2():
                def circle3():
                    self._imageCircle3.color = (0.0, 1.0, 0.0)
                    self._imageCircle3.opacity = 1.0
                    ba.playsound(self._bellHigh)
                    ba.timer(0.2, self._doDelete)
                self._imageCircle2.color = (1.0, 1.0, 0.0)
                self._imageCircle2.opacity = 1.0
                ba.playsound(self._bellMed)
                ba.timer(1, circle3)
            self._imageCircle.color = (1.0, 0.0, 0.0)
            self._imageCircle.opacity = 1.0
            ba.playsound(self._bellLow)
            ba.timer(1, circle2)
        ba.timer(1, circle)

    def _randomPlatform(self):
        if self._levelStage == 1:
            randomTexture=[self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex]
        elif self._levelStage == 2:
            randomTexture=[self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex]
        elif self._levelStage in [3,4,5]:
            randomTexture=[self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGStickyTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGImpactTex,
                           self._mapFGImpactTex,
                           self._mapFGImpactTex,
                           self._mapFGImpactTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex]
        elif self._levelStage in [6,7,8,9]:
            randomTexture=[self._mapFGHealthTex,
                           self._mapFGShieldTex,
                           self._mapFGCurseTex,
                           self._mapFGCurseTex,
                           self._mapFGHealthTex,
                           self._mapFGHealthTex,
                           self._mapFGIceTex,
                           self._mapFGIceTex,
                           self._mapFGImpactTex,
                           self._mapFGImpactTex,
                           self._mapFGMinesTex,
                           self._mapFGMinesTex,
                           self._mapFGPunchTex,
                           self._mapFGPunchTex,
                           self._mapFGShieldTex,
                           self._mapFGShieldTex]
        elif self._levelStage >= 10:
            randomTexture=[self._mapFGSpaz,
                           self._mapFGZoe,
                           self._mapFGSnake,
                           self._mapFGKronk,
                           self._mapFGMel,
                           self._mapFGJack,
                           self._mapFGSanta,
                           self._mapFGFrosty,
                           self._mapFGBones,
                           self._mapFGBernard,
                           self._mapFGPascal,
                           self._mapFGAli,
                           self._mapFGRobot,
                           self._mapFGAgent,
                           self._mapFGGrumbledorf,
                           self._mapFGPixel]

        (self.mapFGPTex, self.mapFGP2Tex,
            self.mapFGP3Tex, self.mapFGP4Tex,
                self.mapFGP5Tex, self.mapFGP6Tex,
                    self.mapFGP7Tex, self.mapFGP8Tex,
                        self.mapFGP9Tex,self.mapFGP10Tex,
                            self.mapFGP11Tex, self.mapFGP12Tex,
                                self.mapFGP13Tex, self.mapFGP14Tex,
                                    self.mapFGP15Tex, self.mapFGP16Tex) = (
                                        random.sample(randomTexture, 16))
        self._mixPlatform()

    def _mixPlatform(self):
        ba.timer(1, self.flashShow)
        ba.timer(3, self.flashHide)
        ba.timer(4, self.flashShow)
        ba.timer(6, self.flashHide)
        ba.timer(7, self.flashShow)
        ba.timer(9, self.flashHide)
        ba.timer(13.2, self.flashShow)

    def flashHide(self):
        self.mapFGP.color_texture = self._mapFGPDefaultTex
        self.mapFGP2.color_texture = self._mapFGPDefaultTex
        self.mapFGP3.color_texture = self._mapFGPDefaultTex
        self.mapFGP4.color_texture = self._mapFGPDefaultTex
        self.mapFGP5.color_texture = self._mapFGPDefaultTex
        self.mapFGP6.color_texture = self._mapFGPDefaultTex
        self.mapFGP7.color_texture = self._mapFGPDefaultTex
        self.mapFGP8.color_texture = self._mapFGPDefaultTex
        self.mapFGP9.color_texture = self._mapFGPDefaultTex
        self.mapFGP10.color_texture = self._mapFGPDefaultTex
        self.mapFGP11.color_texture = self._mapFGPDefaultTex
        self.mapFGP12.color_texture = self._mapFGPDefaultTex
        self.mapFGP13.color_texture = self._mapFGPDefaultTex
        self.mapFGP14.color_texture = self._mapFGPDefaultTex
        self.mapFGP15.color_texture = self._mapFGPDefaultTex
        self.mapFGP16.color_texture = self._mapFGPDefaultTex

    def flashShow(self):
        self.mapFGP.color_texture = self.mapFGPTex
        self.mapFGP2.color_texture = self.mapFGP2Tex
        self.mapFGP3.color_texture = self.mapFGP3Tex
        self.mapFGP4.color_texture = self.mapFGP4Tex
        self.mapFGP5.color_texture = self.mapFGP5Tex
        self.mapFGP6.color_texture = self.mapFGP6Tex
        self.mapFGP7.color_texture = self.mapFGP7Tex
        self.mapFGP8.color_texture = self.mapFGP8Tex
        self.mapFGP9.color_texture = self.mapFGP9Tex
        self.mapFGP10.color_texture = self.mapFGP10Tex
        self.mapFGP11.color_texture = self.mapFGP11Tex
        self.mapFGP12.color_texture = self.mapFGP12Tex
        self.mapFGP13.color_texture = self.mapFGP13Tex
        self.mapFGP14.color_texture = self.mapFGP14Tex
        self.mapFGP15.color_texture = self.mapFGP15Tex
        self.mapFGP16.color_texture = self.mapFGP16Tex

    def _doDelete(self):
        if not self.mapFGPTex == self._textureSelected:
            self.mapFGP.delete()
            self.mapFGPcol.delete()
            self.coldel = True
        if not self.mapFGP2Tex == self._textureSelected:
            self.mapFGP2.delete()
            self.mapFGP2col.delete()
            self.coldel2 = True
        if not self.mapFGP3Tex == self._textureSelected:
            self.mapFGP3.delete()
            self.mapFGP3col.delete()
            self.coldel3 = True
        if not self.mapFGP4Tex == self._textureSelected:
            self.mapFGP4.delete()
            self.mapFGP4col.delete()
            self.coldel4 = True
        if not self.mapFGP5Tex == self._textureSelected:
            self.mapFGP5.delete()
            self.mapFGP5col.delete()
            self.coldel5 = True
        if not self.mapFGP6Tex == self._textureSelected:
            self.mapFGP6.delete()
            self.mapFGP6col.delete()
            self.coldel6 = True
        if not self.mapFGP7Tex == self._textureSelected:
            self.mapFGP7.delete()
            self.mapFGP7col.delete()
            self.coldel7 = True
        if not self.mapFGP8Tex == self._textureSelected:
            self.mapFGP8.delete()
            self.mapFGP8col.delete()
            self.coldel8 = True
        if not self.mapFGP9Tex == self._textureSelected:
            self.mapFGP9.delete()
            self.mapFGP9col.delete()
            self.coldel9 = True
        if not self.mapFGP10Tex == self._textureSelected:
            self.mapFGP10.delete()
            self.mapFGP10col.delete()
            self.coldel10 = True
        if not self.mapFGP11Tex == self._textureSelected:
            self.mapFGP11.delete()
            self.mapFGP11col.delete()
            self.coldel11 = True
        if not self.mapFGP12Tex == self._textureSelected:
            self.mapFGP12.delete()
            self.mapFGP12col.delete()
            self.coldel12 = True
        if not self.mapFGP13Tex == self._textureSelected:
            self.mapFGP13.delete()
            self.mapFGP13col.delete()
            self.coldel13 = True
        if not self.mapFGP14Tex == self._textureSelected:
            self.mapFGP14.delete()
            self.mapFGP14col.delete()
            self.coldel14 = True
        if not self.mapFGP15Tex == self._textureSelected:
            self.mapFGP15.delete()
            self.mapFGP15col.delete()
            self.coldel15 = True
        if not self.mapFGP16Tex == self._textureSelected:
            self.mapFGP16.delete()
            self.mapFGP16col.delete()
            self.coldel16 = True

        ba.timer(3.3, self._platformTexDefault)

    def spawnAllMap(self):
        """
        # Here's how it works:
        # First, create prop with a gravity scale of 0
        # Then use a in-game model which will suit it (For this one I didn't chose box, since it will look kinda weird) Right?
        # Instead I used a 2d model (which is nothing but a button in menu)
        # This prop SHOULD NOT collide with anything, since it has gravity_scale of 0 if it'll get weight it will fall down :((
        # These are where we change those color-textures and is seen in-game

        # Now lets talk about the actual node on which we stand (sadly no-one realises it exists)
        # A moment of silence for this node...

        # Alright, so this is a region node (the one used in hockey/football for scoring)
        # Thanksfully these are just thicc boxes positioned on the map (so they are not moved neither they have gravity_scale)
        # So we create this region node and place it to the same position of our prop node
        # and give it collide_with_player and footing materials
        # Thats it, now you have your own floating platforms :D
        """
        shared = SharedObjects.get()
        if self.coldel:
            self.mapFGP = ba.newnode('prop',
                attrs={'body': 'puck', 'position': (3,1,-9), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGPTex = None
            self.mapFGPcol = ba.newnode('region',attrs={'position': (3,1,-9),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel = False

        if self.coldel2:
            self.mapFGP2 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (3,1,-6), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP2Tex = None
            self.mapFGP2col = ba.newnode('region',attrs={'position': (3,1,-6),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel2 = False

        if self.coldel3:
            self.mapFGP3 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (3,1,-3), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP3Tex = None
            self.mapFGP3col = ba.newnode('region',attrs={'position': (3,1,-3),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel3 = False

        if self.coldel4:
            self.mapFGP4 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (3,1,0), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP4Tex = None
            self.mapFGP4col = ba.newnode('region',attrs={'position': (3,1,0),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel4 = False

        if self.coldel5:
            self.mapFGP5 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (0,1,-9), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP5Tex = None
            self.mapFGP5col = ba.newnode('region',attrs={'position': (0,1,-9),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel5 = False

        if self.coldel6:
            self.mapFGP6 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (0,1,-6), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP6Tex = None
            self.mapFGP6col = ba.newnode('region',attrs={'position': (0,1,-6),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel6 = False

        if self.coldel7:
            self.mapFGP7 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (0,1,-3), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP7Tex = None
            self.mapFGP7col = ba.newnode('region',attrs={'position': (0,1,-3),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel7 = False

        if self.coldel8:
            self.mapFGP8 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (0,1,0), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP8Tex = None
            self.mapFGP8col = ba.newnode('region',attrs={'position': (0,1,0),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel8 = False

        if self.coldel9:
            self.mapFGP9 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-3,1,-9), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP9Tex = None
            self.mapFGP9col = ba.newnode('region',attrs={'position': (-3,1,-9),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel9 = False

        if self.coldel10:
            self.mapFGP10 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-3,1,-6), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP10Tex = None
            self.mapFGP10col = ba.newnode('region',attrs={'position': (-3,1,-6),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel10 = False

        if self.coldel11:
            self.mapFGP11 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-3,1,-3), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP11Tex = None
            self.mapFGP11col = ba.newnode('region',attrs={'position': (-3,1,-3),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel11 = False

        if self.coldel12:
            self.mapFGP12 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-3,1,0), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP12Tex = None
            self.mapFGP12col = ba.newnode('region',attrs={'position': (-3,1,0),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel12 = False

        if self.coldel13:
            self.mapFGP13 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-6,1,-9), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP13Tex = None
            self.mapFGP13col = ba.newnode('region',attrs={'position': (-6,1,-9),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel13 = False

        if self.coldel14:
            self.mapFGP14 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-6,1,-6), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP14Tex = None
            self.mapFGP14col = ba.newnode('region',attrs={'position': (-6,1,-6),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel14 = False

        if self.coldel15:
            self.mapFGP15 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-6,1,-3), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP15Tex = None
            self.mapFGP15col = ba.newnode('region',attrs={'position': (-6,1,-3),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel15 = False

        if self.coldel16:
            self.mapFGP16 = ba.newnode('prop', 
                attrs={'body': 'puck', 'position': (-6,1,0), 'model': self._mapFGPModel, 'model_scale': 3.8, 'body_scale': 3.8, 'shadow_size': 0.5, 'gravity_scale':0.0, 'color_texture': self._mapFGPDefaultTex, 'reflection': 'soft', 'reflection_scale': [1.0], 'is_area_of_interest': True, 'materials': [self.dont_collide]})
            self.mapFGP16Tex = None
            self.mapFGP16col = ba.newnode('region',attrs={'position': (-6,1,0),'scale': (3.5,0.1,3.5),'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            self.coldel16 = False

    def _platformTexDefault(self):
        self._textureSelected = None

        self._imageCircle.color = (0.2, 0.2, 0.2)
        self._imageCircle.opacity = 0.7
        self._imageCircle2.color = (0.2, 0.2, 0.2)
        self._imageCircle2.opacity = 0.7
        self._imageCircle3.color = (0.2, 0.2, 0.2)
        self._imageCircle3.opacity = 0.7

        self._levelStage += 1

        self._textLevel.text = 'Level ' + str(self._levelStage)

        self._image.texture = self._imageTextDefault

        if self._levelStage == 1:
            timeStart = 6
        else:
            timeStart = 2
            ba.playsound(self._scoreSound)
            activity = _ba.get_foreground_host_activity()
            for i in activity.players:
                try:
                    i.actor.node.handlemessage(ba.CelebrateMessage(2.0))
                except:
                    pass
        ba.timer(timeStart, self._randomPlatform)
        ba.timer(timeStart, self.startCounter)

        self.spawnAllMap()
        self.flashHide()

    # Various high-level game events come through this method.
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            curtime = ba.time()

            # Record the player's moment of death.
            # assert isinstance(msg.spaz.player
            msg.getplayer(Player).death_time = curtime

            # In co-op mode, end the game the instant everyone dies
            # (more accurate looking).
            # In teams/ffa, allow a one-second fudge-factor so we can
            # get more draws if players die basically at the same time.
            if isinstance(self.session, ba.CoopSession):
                # Teams will still show up if we check now.. check in
                # the next cycle.
                ba.pushcall(self._check_end_game)

                # Also record this for a final setting of the clock.
                self._last_player_death_time = curtime
            else:
                ba.timer(1.0, self._check_end_game)
        else:
            # Default handler:
            return super().handlemessage(msg)
        return None

    def _check_end_game(self) -> None:
        living_team_count = 0
        for team in self.teams:
            for player in team.players:
                if player.is_alive():
                    living_team_count += 1
                    break

        # In co-op, we go till everyone is dead.. otherwise we go
        # until one team remains.
        if isinstance(self.session, ba.CoopSession):
            if living_team_count <= 0:
                self.end_game()
        else:
            if living_team_count <= 1:
                self.end_game()


    def end_game(self) -> None:
        cur_time = ba.time()
        assert self._timer is not None
        start_time = self._timer.getstarttime()

        # Mark death-time as now for any still-living players
        # and award players points for how long they lasted.
        # (these per-player scores are only meaningful in team-games)
        for team in self.teams:
            for player in team.players:
                survived = False

                # Throw an extra fudge factor in so teams that
                # didn't die come out ahead of teams that did.
                if player.death_time is None:
                    survived = True
                    player.death_time = cur_time + 1

                # Award a per-player score depending on how many seconds
                # they lasted (per-player scores only affect teams mode;
                # everywhere else just looks at the per-team score).
                score = int(player.death_time - self._timer.getstarttime())
                if survived:
                    score += 50  # A bit extra for survivors.
                self.stats.player_scored(player, score, screenmessage=False)

        # Stop updating our time text, and set the final time to match
        # exactly when our last guy died.
        self._timer.stop(endtime=self._last_player_death_time)

        # Ok now calc game results: set a score for each team and then tell
        # the game to end.
        results = ba.GameResults()

        # Remember that 'free-for-all' mode is simply a special form
        # of 'teams' mode where each player gets their own team, so we can
        # just always deal in teams and have all cases covered.
        for team in self.teams:

            # Set the team score to the max time survived by any player on
            # that team.
            longest_life = 0.0
            for player in team.players:
                assert player.death_time is not None
                longest_life = max(longest_life, player.death_time - start_time)

            # Submit the score value in milliseconds.
            results.set_team_score(team, int(1000.0 * longest_life))

        self.end(results=results)



