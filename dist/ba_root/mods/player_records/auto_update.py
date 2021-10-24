"""An automation functionality to update stats without caring updates."""

from __future__ import annotations
from datetime import date
import os

from player_records.file_handle import write

import ba
import _ba


STATS_DIRECTORY = _ba.env().get("python_directory_user") + "/player_data/"
PLAYER_DATA_PATH = (
    _ba.env().get("python_directory_user") + "/player_data/player_data.json"
)


class AutoUpdate:
    """An object to automating file records."""

    def __init__(
        self,
        stats_dir: str = STATS_DIRECTORY,
        player_data_path: str = PLAYER_DATA_PATH,
    ):

        self.stats_directory = stats_dir
        self.player_data_path = player_data_path
        self.today = date.today()
        self.current_month = self.today.strftime("%b-%Y")
        self.stats_file_name = f"Stats({self.season})-{self.current_month}.json"
        self.stats_file_path = self.stats_directory + self.stats_file_name

        if not os.path.exists(self.stats_directory):
            os.mkdir(self.stats_directory)

        if not os.path.exists(self.player_data_path):
            write(self.player_data_path, {})
            ba.app.config["Player_Data_Path"] = self.player_data_path

        if not os.path.exists(self.stats_file_path):
            write(self.stats_file_path, {})

            ba.app.config["Stats_Path"] = self.stats_file_path
            if ba.app.config["Stats-season"] != 1:
                ba.app.config["Stats-season"] += 1
            ba.app.config.apply_and_commit()
            self.update_stats_log()

    @property
    def season(self) -> int:
        """Returns the number of the season."""
        if "Stats-season" not in ba.app.config:
            ba.app.config["Stats-season"] = 1
        return ba.app.config["Stats-season"]

    def update_stats_log(self) -> None:
        """A log of stat file begin created."""
        log_format = (
            f"Created {self.stats_file_name}\n"
            f"On {self.today.strftime('%B %d ,%Y')}\n"
            f"while starting new season {self.season}\n\n"
        )
        with open(self.stats_directory + "/statslog.txt", "a") as log:
            log.write(log_format)
