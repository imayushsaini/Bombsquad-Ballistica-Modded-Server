import datetime
import json
import os
import shutil
import threading

import _babase
import setting

damage_data = {}

ranks = []
top3Name = []

base_path = os.path.join(_babase.env()['python_directory_user'],
                         "stats" + os.sep)
statsfile = base_path + 'stats.json'
cached_stats = {}
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

seasonStartDate = None


def get_all_stats():
    global seasonStartDate
    our_settings = setting.get_settings_data()
    if os.path.exists(statsfile):
        try:
            with open(statsfile, 'r', encoding='utf8') as f:
                jsonData = json.loads(f.read())
        except Exception:
            try:
                with open(statsfile + ".backup", 'r', encoding='utf-8') as f:
                    jsonData = json.load(f)
            except Exception:
                return {}
        try:
            stats = jsonData["stats"]
            seasonStartDate = datetime.datetime.strptime(
                jsonData["startDate"], "%d-%m-%Y")
            _babase.season_ends_in_days = our_settings["statsResetAfterDays"] - (
                datetime.datetime.now() - seasonStartDate).days
            if (datetime.datetime.now() - seasonStartDate).days >= \
                our_settings["statsResetAfterDays"]:
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
    shutil.copy(statsfile, statsfile.replace(
        ".json", "") + str(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ".json")


def dump_stats(s: dict):
    global seasonStartDate
    if seasonStartDate is None:
        seasonStartDate = datetime.datetime.now()
    s = {"startDate": seasonStartDate.strftime("%d-%m-%Y"), "stats": s}
    if os.path.exists(statsfile):
        shutil.copyfile(statsfile, statsfile + ".backup")
        try:
            with open(statsfile, 'w', encoding='utf8') as f:
                f.write(json.dumps(s, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"Error dumping stats: {e}")
    else:
        print('Stats file not found!')


def get_stats_by_id(account_id: str):
    a = get_cached_stats()
    if account_id in a:
        return a[account_id]
    else:
        return None


def get_cached_stats():
    return cached_stats


def get_sorted_stats(stats):
    entries = [(a.get('scores', 0), a.get('kills', 0), a.get('deaths', 0), a.get('games', 0),
                a.get('name', 'default'), a.get('aid', '')) for a in stats.values()]
    # this gives us a list of kills/names sorted high-to-low
    entries.sort(key=lambda x: x[1] or 0, reverse=True)
    return entries


def refreshStats(stats_dict: dict | None = None):
    global cached_stats, ranks, top3Name

    if stats_dict is None:
        pStats = get_all_stats()
    else:
        pStats = stats_dict

    cached_stats = pStats
    entries = get_sorted_stats(pStats)
    
    # Configure the range for toppers and leaderboard
    our_settings = setting.get_settings_data()
    leaderboard_range = our_settings.get("leaderboard", {}).get("range", 3)
    
    toppersIDs = []
    _ranks = []
    
    for rank, entry in enumerate(entries, start=1):
        scores, kills, deaths, games, name, aid = entry
        aid_str = str(aid)
        _ranks.append(aid_str)
        
        if rank <= leaderboard_range:
            toppersIDs.append(aid_str)
          
        player_stats = pStats.get(aid_str)
        if player_stats:
            player_stats["rank"] = rank
            player_stats["scores"] = int(scores)
            player_stats["games"] = int(games)
            player_stats["kills"] = int(kills)
            player_stats["deaths"] = int(deaths)
            
            try:
                kd = round(float(kills) / float(deaths), 3) if float(deaths) > 0 else float(kills)
            except Exception:
                kd = 0.0
                
            try:
                avg_score = round(float(scores) / float(games), 3) if float(games) > 0 else 0.0
            except Exception:
                avg_score = 0.0
                
            dmg = 0.0
            if damage_data and aid_str in damage_data:
                try:
                    dmg = round(float(damage_data[aid_str]), 3)
                except Exception:
                    pass

            player_stats["total_damage"] = round(player_stats.get("total_damage", 0.0) + dmg, 3)
            player_stats["kd"] = kd
            player_stats["avg_score"] = avg_score

    ranks = _ranks
    
    # Extract top names directly from sorted local entries list without API calls
    top3Name = [entry[4] for entry in entries[:leaderboard_range]]

    dump_stats(pStats)

    from playersdata import pdata
    pdata.update_toppers(toppersIDs)


def update(score_set):
    """
    Given a Session's ScoreSet, tallies per-account kills
    and passes them to a background thread to process and
    store.
    """
    account_kills = {}
    account_deaths = {}
    account_scores = {}
    account_names = {}

    for p_entry in score_set.get_records().values():
        try:
            player = p_entry.player
            if player is None:
                continue
            account_id = player.get_v1_account_id()
            if account_id is None:
                continue
            name = player.getname(True)
        except Exception:
            continue

        account_kills.setdefault(account_id, 0)
        account_kills[account_id] += p_entry.accum_kill_count
        account_deaths.setdefault(account_id, 0)
        account_deaths[account_id] += p_entry.accum_killed_count
        account_scores.setdefault(account_id, 0)
        account_scores[account_id] += p_entry.accumscore
        account_names[account_id] = name

    if account_scores:
        UpdateThread(account_kills, account_deaths, account_scores, account_names).start()


class UpdateThread(threading.Thread):
    def __init__(self, account_kills, account_deaths, account_scores, account_names):
        super().__init__()
        self._account_kills = account_kills
        self.account_deaths = account_deaths
        self.account_scores = account_scores
        self.account_names = account_names

    def run(self):
        try:
            stats = get_all_stats()
        except Exception:
            stats = {}

        now_str = str(datetime.datetime.now())
        for account_id, kill_count in self._account_kills.items():
            if account_id not in stats:
                stats[account_id] = {
                    'rank': 0,
                    'name': "default name",
                    'scores': 0,
                    'total_damage': 0.0,
                    'kills': 0,
                    'deaths': 0,
                    'games': 0,
                    'kd': 0.0,
                    'avg_score': 0.0,
                    'last_seen': now_str,
                    'aid': str(account_id)
                }

            if account_id in self.account_names:
                stats[account_id]['name'] = self.account_names[account_id]

            stats[account_id]['kills'] += kill_count
            stats[account_id]['deaths'] += self.account_deaths.get(account_id, 0)
            stats[account_id]['scores'] += self.account_scores.get(account_id, 0)
            stats[account_id]['last_seen'] = now_str
            stats[account_id]['games'] += 1
            stats[account_id]['aid'] = str(account_id)

            # Award tickets for playing and kills
            try:
                from shop import add_tickets
                tickets_to_award = 10 + kill_count * 2
                add_tickets(account_id, tickets_to_award)
            except Exception as e:
                print(f"Error awarding tickets to {account_id}: {e}")

        refreshStats(stats)


def getRank(acc_id):
    global ranks
    if not ranks:
        refreshStats()
    if acc_id in ranks:
        return ranks.index(acc_id) + 1
    return None
