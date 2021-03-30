damage_data = {}
#Don't touch the above line
"""
mystats module for BombSquad version 1.5.29
Provides functionality for dumping player stats to disk between rounds.
"""

import threading,json,os,urllib.request,ba,_ba,mysettings
from ba._activity import Activity
from ba._music import setmusic, MusicType
from ba._enums import InputType, UIScale
# False-positive from pylint due to our class-generics-filter.
from ba._player import EmptyPlayer  # pylint: disable=W0611
from ba._team import EmptyTeam  # pylint: disable=W0611
from typing import Any, Dict, Optional
from ba._lobby import JoinInfo
from ba import _activitytypes as ba_actypes
from ba._activitytypes import *

# where our stats file and pretty html output will go
statsfile = mysettings.statsFile
htmlfile = mysettings.htmlFile
table_style = "{width:100%;border: 3px solid black;border-spacing: 5px;border-collapse:collapse;text-align:center;background-color:#fff}"
heading_style = "{border: 3px solid black;text-align:center;}"
html_start = f'''<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Test Server</title>
        <style>table{table_style} th{heading_style}</style>
    </head>
    <body>
        <h3 style="text-align:center">Top 200 Players of {mysettings.server_name}</h3>
        <table border=1>
            <tr>
                <th><b>Rank</b></th>
                <th style="text-align:center"><b>Name</b></th>
                <th><b>Score</b></th>
                <th><b>Kills</b></th>
                <th><b>Deaths</b></th>
                <th><b>Games Played</b></th>
            </tr>
'''
#                <th><b>Total Damage</b></th>  #removed this line as it isn't crt data
def refreshStats():
    # lastly, write a pretty html version.
    # our stats url could point at something like this...
    stats = mysettings.getStats()
    f=open(htmlfile, 'w')       
    f.write(html_start)
    entries = [(a['scores'], a['kills'], a['deaths'], a['games'], a['name_html'], a['aid']) for a in stats.values()]
    # this gives us a list of kills/names sorted high-to-low
    entries.sort(reverse=True)
    rank = 0
    toppers = {}
    pStats = stats
    toppersIDs=[]
    for entry in entries:
        if True:
            rank += 1
            scores = str(entry[0])
            kills = str(entry[1])
            deaths = str(entry[2])
            games = str(entry[3])
            name = str(entry[4])
            aid = str(entry[5])
            if rank < 6: toppersIDs.append(aid)
            #The below kd and avg_score will not be added to website's html document, it will be only added in stats.json
            try:
                kd = str(float(kills) / float(deaths))
                kd_int = kd.split('.')[0]
                kd_dec = kd.split('.')[1]
                p_kd = kd_int + '.' + kd_dec[:3]
            except Exception:
                p_kd = "0"
            try:
                avg_score = str(float(scores) / float(games))
                avg_score_int = avg_score.split('.')[0]
                avg_score_dec = avg_score.split('.')[1]
                p_avg_score = avg_score_int + '.' + avg_score_dec[:3]
            except Exception:
                p_avg_score = "0"
            if damage_data and aid in damage_data:
                dmg = damage_data[aid]
                dmg = str(str(dmg).split('.')[0] + '.' + str(dmg).split('.')[1][:3])
            else: dmg = 0
            pStats[str(aid)]["rank"] = int(rank)
            pStats[str(aid)]["scores"] = int(scores)
            pStats[str(aid)]["total_damage"] = float(dmg) #not working properly
            pStats[str(aid)]["games"] = int(games)
            pStats[str(aid)]["kills"] = int(kills)
            pStats[str(aid)]["deaths"] = int(deaths)
            pStats[str(aid)]["kd"] = float(p_kd)
            pStats[str(aid)]["avg_score"] = float(p_avg_score)

            if rank < 201:
                #<td>{str(dmg)}</td> #removed this line as it isn't crt data
                f.write(f'''
            <tr>
                <td>{str(rank)}</td>
                <td style="text-align:center">{str(name)}</td>
                <td>{str(scores)}</td>
                <td>{str(kills)}</td>
                <td>{str(deaths)}</td>
                <td>{str(games)}</td>
            </tr>''')
    f.write('''
        </table>
    </body>
</html>''')
    f.close()

    f2 = open(mysettings.statsFile, "w")
    f2.write(json.dumps(pStats, indent=4))
    f2.close()
    
    if True:#mysettings.mysettings[enableTop5commands]:
        import roles
        roles.toppersList = toppersIDs
        with open(mysettings.python_path + "/roles.py") as file:
            s = [row for row in file]
            s[7] = 'toppersList = ' + str(roles.toppersList) + '\n'
            f = open(mysettings.python_path + "/roles.py",'w')
            for i in s:
                f.write(i)
            f.close()

def update(score_set):
    """
    Given a Session's ScoreSet, tallies per-account kills
    and passes them to a background thread to process and
    store.
    """ 
    # look at score-set entries to tally per-account kills for this round

    account_kills = {}
    account_deaths = {}
    account_scores = {}

    for p_entry in score_set.get_records().values():
        account_id = p_entry.player.get_account_id()
        if account_id is not None:
            account_kills.setdefault(account_id, 0)  # make sure exists
            account_kills[account_id] += p_entry.accum_kill_count
            account_deaths.setdefault(account_id, 0)  # make sure exists
            account_deaths[account_id] += p_entry.accum_killed_count
            account_scores.setdefault(account_id, 0)  # make sure exists
            account_scores[account_id] += p_entry.accumscore
    # Ok; now we've got a dict of account-ids and kills.
    # Now lets kick off a background thread to load existing scores
    # from disk, do display-string lookups for accounts that need them,
    # and write everything back to disk (along with a pretty html version)
    # We use a background thread so our server doesn't hitch while doing this.
    if account_scores: UpdateThread(account_kills, account_deaths, account_scores).start()

class UpdateThread(threading.Thread):
    def __init__(self, account_kills, account_deaths, account_scores):
        threading.Thread.__init__(self)
        self._account_kills = account_kills
        self.account_deaths = account_deaths
        self.account_scores = account_scores
    def run(self):
        # pull our existing stats from disk
        try:
            if os.path.exists(statsfile):
                with open(statsfile) as f:
                    stats = json.loads(f.read())
        except:
            return

        # now add this batch of kills to our persistant stats
        for account_id, kill_count in self._account_kills.items():
            # add a new entry for any accounts that dont have one
            if account_id not in stats:
                # also lets ask the master-server for their account-display-str.
                # (we only do this when first creating the entry to save time,
                # though it may be smart to refresh it periodically since
                # it may change)
                '''url = 'http://bombsquadgame.com/accountquery?id=' + account_id
                response = json.loads(
                    urllib.request.urlopen(urllib.Request(url)).read())
                print('response variable from mystats.py line 183:')
                print(response)
                name_html = response['name_html']'''
                stats[account_id] = {'rank': 0,
                                     'name_html': str(account_id),
                                     'scores': 0,
                                     'total_damage': 0,
                                     'kills': 0,
                                     'deaths': 0,
                                     'games': 0,
                                     'kd': 0,
                                     'avg_score': 0,
                                     'aid': str(account_id)}
            # now increment their kills whether they were already there or not
            stats[account_id]['kills'] += kill_count
            stats[account_id]['deaths'] += self.account_deaths[account_id]
            stats[account_id]['scores'] += self.account_scores[account_id]
            # also incrementing the games played and adding the id
            stats[account_id]['games'] += 1
            stats[account_id]['aid'] = str(account_id)
        # dump our stats back to disk
        tempppp = None
        from datetime import datetime
        with open(statsfile, 'w') as f:
            f.write(json.dumps(stats))
        # aaand that's it!  There IS no step 27!
        now = datetime.now()
        update_time = now.strftime("%S:%M:%H - %d %b %y")
        print(f"Added {str(len(self._account_kills))} account's stats entries. || {str(update_time)}")
        refreshStats()



class myScoreScreenActivity(Activity[EmptyPlayer, EmptyTeam]):
    """A standard score screen that fades in and shows stuff for a while.

    After a specified delay, player input is assigned to end the activity.
    """

    transition_time = 0.5
    inherits_tint = True
    inherits_vr_camera_offset = True
    use_fixed_vr_overlay = True

    default_music: Optional[MusicType] = MusicType.SCORES

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._birth_time = _ba.time()
        self._min_view_time = 5.0
        self._allow_server_transition = False
        self._background: Optional[ba.Actor] = None
        self._tips_text: Optional[ba.Actor] = None
        self._kicked_off_server_shutdown = False
        self._kicked_off_server_restart = False
        self._default_show_tips = True
        self._custom_continue_message: Optional[ba.Lstr] = None
        self._server_transitioning: Optional[bool] = None

    def on_player_join(self, player: EmptyPlayer) -> None:
        from ba._general import WeakCall
        super().on_player_join(player)
        time_till_assign = max(
            0, self._birth_time + self._min_view_time - _ba.time())

        # If we're still kicking at the end of our assign-delay, assign this
        # guy's input to trigger us.
        _ba.timer(time_till_assign, WeakCall(self._safe_assign, player))

    def on_transition_in(self) -> None:
        from bastd.actor.tipstext import TipsText
        from bastd.actor.background import Background
        super().on_transition_in()
        self._background = Background(fade_time=0.5,
                                      start_faded=False,
                                      show_logo=True)
        if self._default_show_tips:
            self._tips_text = TipsText()
        setmusic(self.default_music)

    def on_begin(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.actor.text import Text
        from ba import _language
        super().on_begin()

        # Pop up a 'press any button to continue' statement after our
        # min-view-time show a 'press any button to continue..'
        # thing after a bit.
        if _ba.app.ui.uiscale is UIScale.LARGE:
            # FIXME: Need a better way to determine whether we've probably
            #  got a keyboard.
            sval = _language.Lstr(resource='pressAnyKeyButtonText')
        else:
            sval = _language.Lstr(resource='pressAnyButtonText')

        Text(self._custom_continue_message
             if self._custom_continue_message is not None else sval,
             v_attach=Text.VAttach.BOTTOM,
             h_align=Text.HAlign.CENTER,
             flash=True,
             vr_depth=50,
             position=(0, 10),
             scale=0.8,
             color=(0.5, 0.7, 0.5, 0.5),
             transition=Text.Transition.IN_BOTTOM_SLOW,
             transition_delay=self._min_view_time).autoretain()
        update(self._stats)

    def _player_press(self) -> None:

        # If this activity is a good 'end point', ask server-mode just once if
        # it wants to do anything special like switch sessions or kill the app.
        if (self._allow_server_transition and _ba.app.server is not None
                and self._server_transitioning is None):
            self._server_transitioning = _ba.app.server.handle_transition()
            assert isinstance(self._server_transitioning, bool)

        # If server-mode is handling this, don't do anything ourself.
        if self._server_transitioning is True:
            return

        # Otherwise end the activity normally.
        self.end()

    def _safe_assign(self, player: EmptyPlayer) -> None:

        # Just to be extra careful, don't assign if we're transitioning out.
        # (though theoretically that should be ok).
        if not self.is_transitioning_out() and player:
            player.assigninput((InputType.JUMP_PRESS, InputType.PUNCH_PRESS,
                                InputType.BOMB_PRESS, InputType.PICK_UP_PRESS),
                               self._player_press)
#ba_actypes.ScoreScreenActivity = myScoreScreenActivity