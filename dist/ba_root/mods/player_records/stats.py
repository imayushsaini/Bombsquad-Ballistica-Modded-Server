"""Player stats for ranking players."""

from __future__ import annotations
from threading import Thread

from player_records.file_handle import read, write
from ba._stats import Stats
import ba


class PlayerStats(Thread):
    """A Thread updating stats on game result screen."""

    def __init__(self, stats: Stats) -> None:
        super().__init__()

        self.stats = stats
        self.stats_file_path = ba.app.config["Stats_Path"]
        self.stats_data = read(self.stats_file_path)

    def run(self) -> None:

        for player_record in self.stats.get_records().values():
            account_id = player_record.player.get_account_id()

            if self.stats_data is None:
                return

            self.stats_data.setdefault(account_id, {})
            self.stats_data[account_id].setdefault("rank", 0)
            self.stats_data[account_id].setdefault("kills", 0)
            self.stats_data[account_id].setdefault("deaths", 0)
            self.stats_data[account_id].setdefault("score", 0)
            self.stats_data[account_id].setdefault("rounds", 0)

            self.stats_data[account_id]["kills"] += player_record.accum_kill_count
            self.stats_data[account_id]["deaths"] += player_record.accum_killed_count
            self.stats_data[account_id]["score"] += player_record.accumscore
            self.stats_data[account_id]["rounds"] += 1

            self.refresh_ranks()

    def refresh_ranks(self) -> None:
        """Sorts the rank of players."""

        if self.stats_data is None:
            return

        sorted_stats = dict(
            sorted(
                self.stats_data.items(),
                key=lambda x: x[1]["score"],
                reverse=True,
            )
        )

        for rank, player in enumerate(sorted_stats, start=1):
            self.stats_data[player]["rank"] = rank

        write(self.stats_file_path, self.stats_data)
