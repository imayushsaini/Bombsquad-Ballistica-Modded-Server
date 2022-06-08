damage_data = {}
# Don't touch the above line
"""
mystats module for BombSquad version 1.5.29
Provides functionality for dumping player stats to disk between rounds.
"""
ranks = []
top3Name = []
import threading, json, os, urllib.request, ba, _ba, setting
from ba._activity import Activity
from ba._music import setmusic, MusicType
# False-positive from pylint due to our class-generics-filter.
from ba._player import EmptyPlayer  # pylint: disable=W0611
from ba._team import EmptyTeam  # pylint: disable=W0611
from typing import Any, Dict, Optional
from ba._lobby import JoinInfo
from ba import _activitytypes as ba_actypes
from ba._activitytypes import *
import urllib.request
import custom_hooks
import datetime

# variables
our_settings = setting.get_settings_data()
# where our stats file and pretty html output will go
base_path = os.path.join(_ba.env()['python_directory_user'], "stats" + os.sep)
statsfile = base_path + 'stats.json'
htmlfile = base_path + 'stats_page.html'
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
        <h3 style="text-align:center">Top 200 Players </h3>
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
statsDefault = {
    "pb-IF4VAk4a": {
        "rank": 65,
        "name": "pb-IF4VAk4a",
        "scores": 0,
        "total_damage": 0.0,
        "kills": 0,
        "deaths": 0,
        "games": 18,
        "kd": 0.0,
        "avg_score": 0.0,
        "aid": "pb-IF4VAk4a",
        "last_seen": "2022-04-26 17:01:13.715014"
    }
}
#                <th><b>Total Damage</b></th>  #removed this line as it isn't crt data

# useful functions
seasonStartDate = None
import shutil, os


def get_all_stats():
    global seasonStartDate
    if os.path.exists(statsfile):
        renameFile = False
        with open(statsfile, 'r', encoding='utf8') as f:
            try:
                jsonData = json.loads(f.read())
            except:
                f=open(statsfile+".backup",encoding='utf-8')
                jsonData=json.load(f)
            try:
                stats = jsonData["stats"]

                seasonStartDate = datetime.datetime.strptime(jsonData["startDate"], "%d-%m-%Y")
                if (datetime.datetime.now() - seasonStartDate).days >= our_settings["statsResetAfterDays"]:
                    backupStatsFile()
                    seasonStartDate = datetime.datetime.now()
                    return statsDefault
                return stats
            except OSError as e:
                print(e)
                return jsonData
    else:
        return {}


def backupStatsFile():
    shutil.copy(statsfile, statsfile.replace(".json", "") + str(seasonStartDate) + ".json")


def dump_stats(s: dict):
    global seasonStartDate
    if seasonStartDate == None:
        seasonStartDate = datetime.datetime.now()
    s = {"startDate": seasonStartDate.strftime("%d-%m-%Y"), "stats": s}
    if os.path.exists(statsfile):
        shutil.copyfile(statsfile,statsfile+".backup")
        with open(statsfile, 'w', encoding='utf8') as f:
            f.write(json.dumps(s, indent=4, ensure_ascii=False))
            f.close()
    else:
        print('Stats file not found!')


def get_stats_by_id(ID: str):
    a = get_all_stats()
    if ID in a:
        return a[ID]
    else:
        return None


def refreshStats():
    # lastly, write a pretty html version.
    # our stats url could point at something like this...
    pStats = get_all_stats()
    # f=open(htmlfile, 'w')
    # f.write(html_start)

    entries = [(a['scores'], a['kills'], a['deaths'], a['games'], a['name'], a['aid']) for a in pStats.values()]
    # this gives us a list of kills/names sorted high-to-low
    entries.sort(key=lambda x: x[1] or 0, reverse=True)
    rank = 0
    toppers = {}
    toppersIDs = []
    _ranks = []
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
            # The below kd and avg_score will not be added to website's html document, it will be only added in stats.json
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
            else:
                dmg = 0

            _ranks.append(aid)

            pStats[str(aid)]["rank"] = int(rank)
            pStats[str(aid)]["scores"] = int(scores)
            pStats[str(aid)]["total_damage"] += float(dmg)  # not working properly
            pStats[str(aid)]["games"] = int(games)
            pStats[str(aid)]["kills"] = int(kills)
            pStats[str(aid)]["deaths"] = int(deaths)
            pStats[str(aid)]["kd"] = float(p_kd)
            pStats[str(aid)]["avg_score"] = float(p_avg_score)

    #             if rank < 201:
    #                 #<td>{str(dmg)}</td> #removed this line as it isn't crt data
    #                 f.write(f'''
    #             <tr>
    #                 <td>{str(rank)}</td>
    #                 <td style="text-align:center">{str(name)}</td>
    #                 <td>{str(scores)}</td>
    #                 <td>{str(kills)}</td>
    #                 <td>{str(deaths)}</td>
    #                 <td>{str(games)}</td>
    #             </tr>''')
    #     f.write('''
    #         </table>
    #     </body>
    # </html>''')

    # f.close()
    global ranks
    ranks = _ranks

    dump_stats(pStats)
    updateTop3Names(toppersIDs[0:3])

    from playersData import pdata
    pdata.update_toppers(toppersIDs)


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
        account_id = p_entry.player.get_v1_account_id()
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

    if account_scores:
        UpdateThread(account_kills, account_deaths, account_scores).start()


class UpdateThread(threading.Thread):
    def __init__(self, account_kills, account_deaths, account_scores):
        threading.Thread.__init__(self)
        self._account_kills = account_kills
        self.account_deaths = account_deaths
        self.account_scores = account_scores

    def run(self):
        # pull our existing stats from disk
        import datetime
        try:
            stats = get_all_stats()
        except:
            stats = {}

        # now add this batch of kills to our persistant stats
        for account_id, kill_count in self._account_kills.items():
            # add a new entry for any accounts that dont have one
            if account_id not in stats:
                # also lets ask the master-server for their account-display-str.
                # (we only do this when first creating the entry to save time,
                # though it may be smart to refresh it periodically since
                # it may change)

                stats[account_id] = {'rank': 0,
                                     'name': "deafult name",
                                     'scores': 0,
                                     'total_damage': 0,
                                     'kills': 0,
                                     'deaths': 0,
                                     'games': 0,
                                     'kd': 0,
                                     'avg_score': 0,
                                     'last_seen': str(datetime.datetime.now()),
                                     'aid': str(account_id)}

            # Temporary codes to change 'name_html' to 'name'
            # if 'name_html' in stats[account_id]:
            #     stats[account_id].pop('name_html')
            #     stats[account_id]['name'] = 'default'
            url = "http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID=" + account_id
            data = urllib.request.urlopen(url)
            if data is not None:
                try:
                    name = json.loads(data.read())["profileDisplayString"]
                except ValueError:
                    stats[account_id]['name'] = "???"
                else:
                    stats[account_id]['name'] = name

            # now increment their kills whether they were already there or not

            stats[account_id]['kills'] += kill_count
            stats[account_id]['deaths'] += self.account_deaths[account_id]
            stats[account_id]['scores'] += self.account_scores[account_id]
            stats[account_id]['last_seen'] = str(datetime.datetime.now())
            # also incrementing the games played and adding the id
            stats[account_id]['games'] += 1
            stats[account_id]['aid'] = str(account_id)
        # dump our stats back to disk
        tempppp = None
        from datetime import datetime
        dump_stats(stats)
        # aaand that's it!  There IS no step 27!
        now = datetime.now()
        update_time = now.strftime("%S:%M:%H - %d %b %y")
        # print(f"Added {str(len(self._account_kills))} account's stats entries. || {str(update_time)}")
        refreshStats()


def getRank(acc_id):
    global ranks
    if ranks == []:
        refreshStats()
    if acc_id in ranks:
        return ranks.index(acc_id) + 1


def updateTop3Names(ids):
    global top3Name
    names = []
    for id in ids:
        url = "http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID=" + id
        data = urllib.request.urlopen(url)
        if data is not None:
            try:
                name = json.loads(data.read())["profileDisplayString"]
                if (not name):
                    raise ValueError
            except ValueError:
                names.append("???")
                
            else:
                names.append(name)
    top3Name = names

