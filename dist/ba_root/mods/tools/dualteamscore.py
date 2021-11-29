# Released under the MIT License. See LICENSE for details.
#
"""Functionality related to the end screen in dual-team mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.activity.multiteamscore import MultiTeamScoreScreenActivity
from bastd.actor.zoomtext import ZoomText
from bastd.actor.text import Text
from bastd.actor.image import Image
if TYPE_CHECKING:
    pass


class TeamVictoryScoreScreenActivity(MultiTeamScoreScreenActivity):
    """Scorescreen between rounds of a dual-team session."""

    def __init__(self, settings: dict):
        super().__init__(settings=settings)
        self._winner: ba.SessionTeam = settings['winner']
        assert isinstance(self._winner, ba.SessionTeam)

    def on_begin(self) -> None:
        ba.set_analytics_screen('Teams Score Screen')
        super().on_begin()

        height = 130
        active_team_count = len(self.teams)
        vval = (height * active_team_count) / 2 - height / 2
        i = 0
        shift_time = 2.5

        # Usually we say 'Best of 7', but if the language prefers we can say
        # 'First to 4'.
        session = self.session
        assert isinstance(session, ba.MultiTeamSession)
        if ba.app.lang.get_resource('bestOfUseFirstToInstead'):
            best_txt = ba.Lstr(resource='firstToSeriesText',
                               subs=[('${COUNT}',
                                      str(session.get_series_length() / 2 + 1))
                                     ])
        else:
            best_txt = ba.Lstr(resource='bestOfSeriesText',
                               subs=[('${COUNT}',
                                      str(session.get_series_length()))])

        # ZoomText(best_txt,
        #          position=(0, 175),
        #          shiftposition=(-250, 175),
        #          shiftdelay=2.5,
        #          flash=False,
        #          trail=False,
        #          h_align='center',
        #          scale=0.25,
        #          color=(0.5, 0.5, 0.5, 1.0),
        #          jitter=3.0).autoretain()
        for team in self.session.sessionteams:
            ba.timer(
                i * 0.15 + 0.15,
                ba.WeakCall(self._show_team_name, vval - i * height, team,
                            i * 0.2, shift_time - (i * 0.150 + 0.150)))
            ba.timer(i * 0.150 + 0.5,
                     ba.Call(ba.playsound, self._score_display_sound_small))
            scored = (team is self._winner)
            delay = 0.2
            if scored:
                delay = 1.2
                ba.timer(
                    i * 0.150 + 0.2,
                    ba.WeakCall(self._show_team_old_score, vval - i * height,
                                team, shift_time - (i * 0.15 + 0.2)))
                ba.timer(i * 0.15 + 1.5,
                         ba.Call(ba.playsound, self._score_display_sound))

            ba.timer(
                i * 0.150 + delay,
                ba.WeakCall(self._show_team_score, vval - i * height, team,
                            scored, i * 0.2 + 0.1,
                            shift_time - (i * 0.15 + delay)))
            i += 1
        self.show_player_scores()

    def _show_team_name(self, pos_v: float, team: ba.SessionTeam,
                        kill_delay: float, shiftdelay: float) -> None:
        del kill_delay  # Unused arg.
        ZoomText(ba.Lstr(value='${A}', subs=[('${A}', team.name)]),
                 position=(-250, 260) if pos_v == 65 else (250,260),
                 shiftposition=(-250, 260) if pos_v == 65 else (250,260),
                 shiftdelay=shiftdelay,
                 flash=False,
                 trail=False,
                 h_align='center',
                 maxwidth=300,
                 scale=0.45,
                 color=team.color,
                 jitter=1.0).autoretain()

    def _show_team_old_score(self, pos_v: float, sessionteam: ba.SessionTeam,
                             shiftdelay: float) -> None:
        ZoomText(str(sessionteam.customdata['score'] - 1),
                 position=(-250, 190) if pos_v == 65 else (250,190),
                 maxwidth=100,
                 color=(0.6, 0.6, 0.7),
                 shiftposition=(-250, 190) if pos_v == 65 else (250,190),
                 shiftdelay=shiftdelay,
                 flash=False,
                 trail=False,
                 lifespan=1.0,
                 scale=0.56,
                 h_align='center',
                 jitter=1.0).autoretain()

    def _show_team_score(self, pos_v: float, sessionteam: ba.SessionTeam,
                         scored: bool, kill_delay: float,
                         shiftdelay: float) -> None:
        del kill_delay  # Unused arg.
        ZoomText(str(sessionteam.customdata['score']),
                 position=(-250, 190) if pos_v == 65 else (250,190),
                 maxwidth=100,
                 color=(1.0, 0.9, 0.5) if scored else (0.6, 0.6, 0.7),
                 shiftposition=(-250, 190) if pos_v == 65 else (250,190),
                 shiftdelay=shiftdelay,
                 flash=scored,
                 trail=scored,
                 scale=0.56,
                 h_align='center',
                 jitter=1.0,
                 trailcolor=(1, 0.8, 0.0, 0)).autoretain()


# ===================================================================================================

#                                 score board
# ====================================================================================================

def show_player_scores(self,
                           delay: float = 2.5,
                           results: Optional[ba.GameResults] = None,
                           scale: float = 1.0,
                           x_offset: float = 0.0,
                           y_offset: float = 0.0) -> None:
        """Show scores for individual players."""
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements

        ts_v_offset = 150.0 + y_offset
        ts_h_offs = 80.0 + x_offset
        tdelay = delay
        spacing = 40


        is_free_for_all = isinstance(self.session, ba.FreeForAllSession)

        is_two_team = True if len(self.session.sessionteams) == 2 else False

        def _get_prec_score(p_rec: ba.PlayerRecord) -> Optional[int]:
            if is_free_for_all and results is not None:
                assert isinstance(results, ba.GameResults)
                assert p_rec.team.activityteam is not None
                val = results.get_sessionteam_score(p_rec.team)
                return val
            return p_rec.accumscore

        def _get_prec_score_str(p_rec: ba.PlayerRecord) -> Union[str, ba.Lstr]:
            if is_free_for_all and results is not None:
                assert isinstance(results, ba.GameResults)
                assert p_rec.team.activityteam is not None
                val = results.get_sessionteam_score_str(p_rec.team)
                assert val is not None
                return val
            return str(p_rec.accumscore)

        # stats.get_records() can return players that are no longer in
        # the game.. if we're using results we have to filter those out
        # (since they're not in results and that's where we pull their
        # scores from)
        if results is not None:
            assert isinstance(results, ba.GameResults)
            player_records = []
            assert self.stats
            valid_players = list(self.stats.get_records().items())

            def _get_player_score_set_entry(
                    player: ba.SessionPlayer) -> Optional[ba.PlayerRecord]:
                for p_rec in valid_players:
                    if p_rec[1].player is player:
                        return p_rec[1]
                return None

            # Results is already sorted; just convert it into a list of
            # score-set-entries.
            for winnergroup in results.winnergroups:
                for team in winnergroup.teams:
                    if len(team.players) == 1:
                        player_entry = _get_player_score_set_entry(
                            team.players[0])
                        if player_entry is not None:
                            player_records.append(player_entry)
        else:
            player_records = []
            player_records_scores = [
                (_get_prec_score(p), name, p)
                for name, p in list(self.stats.get_records().items())
            ]
            player_records_scores.sort(reverse=True)

            # Just want living player entries.
            player_records = [p[2] for p in player_records_scores if p[2]]

        voffs = -140.0 + spacing * 5 * 0.5

        voffs_team0=voffs
        tdelay_team0=tdelay

        def _txt(xoffs: float,
                 yoffs: float,
                 text: ba.Lstr,
                 h_align: Text.HAlign = Text.HAlign.RIGHT,
                 extrascale: float = 1.0,
                 maxwidth: Optional[float] = 120.0) -> None:
            Text(text,
                 color=(0.5, 0.5, 0.6, 0.5),
                 position=(ts_h_offs + xoffs * scale,
                           ts_v_offset + (voffs + yoffs + 4.0) * scale),
                 h_align=h_align,
                 v_align=Text.VAlign.CENTER,
                 scale=0.8 * scale * extrascale,
                 maxwidth=maxwidth,
                 transition=Text.Transition.IN_LEFT,
                 transition_delay=tdelay).autoretain()

        session = self.session
        assert isinstance(session, ba.MultiTeamSession)
        if is_two_team:
            tval =  "Game "+str(session.get_game_number())+" Results"
            _txt(-75,
                 160,
                 tval,
                 h_align=Text.HAlign.CENTER,
                 extrascale=1.4,
                 maxwidth=None)
        _txt(-15, 4, ba.Lstr(resource='playerText'), h_align=Text.HAlign.LEFT)
        _txt(180, 4, ba.Lstr(resource='killsText'))
        _txt(280, 4, ba.Lstr(resource='deathsText'), maxwidth=100)

        score_label = 'Score' if results is None else results.score_label
        translated = ba.Lstr(translate=('scoreNames', score_label))

        _txt(390, 0, translated)

        if is_two_team:
            _txt(-595, 4, ba.Lstr(resource='playerText'), h_align=Text.HAlign.LEFT)
            _txt(-400, 4, ba.Lstr(resource='killsText'))
            _txt(-300, 4, ba.Lstr(resource='deathsText'), maxwidth=100)
            _txt(-190, 0, translated)


        topkillcount = 0
        topkilledcount = 99999
        top_score = 0 if not player_records else _get_prec_score(
            player_records[0])

        for prec in player_records:
            topkillcount = max(topkillcount, prec.accum_kill_count)
            topkilledcount = min(topkilledcount, prec.accum_killed_count)

        def _scoretxt(text: Union[str, ba.Lstr],
                      x_offs: float,
                      highlight: bool,
                      delay2: float,
                      maxwidth: float = 70.0,team_id=1) -> None:
            
            Text(text,
                 position=(ts_h_offs + x_offs * scale,
                           ts_v_offset + (voffs + 15) * scale) if team_id==1 else (ts_h_offs+x_offs*scale,ts_v_offset+(voffs_team0+15)*scale),
                 scale=scale,
                 color=(1.0, 0.9, 0.5, 1.0) if highlight else
                 (0.5, 0.5, 0.6, 0.5),
                 h_align=Text.HAlign.RIGHT,
                 v_align=Text.VAlign.CENTER,
                 maxwidth=maxwidth,
                 transition=Text.Transition.IN_LEFT,
                 transition_delay=(tdelay + delay2) if team_id==1 else (tdelay_team0+delay2) ).autoretain()

        for playerrec in player_records:
            if is_two_team and playerrec.team.id==0:
                tdelay_team0 +=0.05
                voffs_team0 -=spacing
                x_image=617
                x_text=-595
                y=ts_v_offset + (voffs_team0 + 15.0) * scale


                

            else:
                tdelay += 0.05
                voffs -= spacing
                x_image=12
                x_text=10.0
                y=ts_v_offset + (voffs + 15.0) * scale
                

            
            
            Image(playerrec.get_icon(),
                  position=(ts_h_offs - x_image* scale,
                            y),
                  scale=(30.0 * scale, 30.0 * scale),
                  transition=Image.Transition.IN_LEFT,
                  transition_delay=tdelay if playerrec.team.id==1 else tdelay_team0).autoretain()
            Text(ba.Lstr(value=playerrec.getname(full=True)),
                 maxwidth=160,
                 scale=0.75 * scale,
                 position=(ts_h_offs + x_text * scale,
                           y),
                 h_align=Text.HAlign.LEFT,
                 v_align=Text.VAlign.CENTER,
                 color=ba.safecolor(playerrec.team.color + (1, )),
                 transition=Text.Transition.IN_LEFT,
                 transition_delay=tdelay if playerrec.team.id==1 else tdelay_team0).autoretain()

            if is_two_team and playerrec.team.id==0:
                _scoretxt(str(playerrec.accum_kill_count), -400,
                      playerrec.accum_kill_count == topkillcount, 0.1,team_id=0)
                _scoretxt(str(playerrec.accum_killed_count), -300,
                      playerrec.accum_killed_count == topkilledcount, 0.1,team_id=0)
                _scoretxt(_get_prec_score_str(playerrec), -190,
                      _get_prec_score(playerrec) == top_score, 0.2,team_id=0)
            else:
                _scoretxt(str(playerrec.accum_kill_count), 180,
                          playerrec.accum_kill_count == topkillcount, 0.1)
                _scoretxt(str(playerrec.accum_killed_count), 280,
                          playerrec.accum_killed_count == topkilledcount, 0.1)
                _scoretxt(_get_prec_score_str(playerrec), 390,
                          _get_prec_score(playerrec) == top_score, 0.2)


# ======================== draw screen =============
class DrawScoreScreenActivity(MultiTeamScoreScreenActivity):
    """Score screen shown after a draw."""

    default_music = None  # Awkward silence...

    def on_begin(self) -> None:
        ba.set_analytics_screen('Draw Score Screen')
        super().on_begin()
        ZoomText(ba.Lstr(resource='drawText'),
                 position=(0, 200),
                 maxwidth=400,
                 shiftposition=(0, 200),
                 shiftdelay=2.0,
                 flash=False,
                 scale=0.7,
                 trail=False,
                 jitter=1.0).autoretain()
        ba.timer(0.35, ba.Call(ba.playsound, self._score_display_sound))
        self.show_player_scores(results=self.settings_raw.get('results', None))