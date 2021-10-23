"""A Level object presenting a level of player."""

from __future__ import annotations
from typing import Callable, Dict

from player_records.file_handle import read, write
import ba


LevelupCallback = Callable[[ba.Player], None]
levelup_callbacks: Dict[int, LevelupCallback] = {}


def on_levelup(level: int) -> Callable[[LevelupCallback], LevelupCallback]:
    """A decorator to listen levelp events.
    The function will automatically get player parameter.

    Parameters
    ----------
    level : int
        A level to add listener
    """

    def wrapper(function: LevelupCallback) -> LevelupCallback:
        levelup_callbacks[level] = function
        return function

    return wrapper


class PlayerLevel:
    """player records to get player records store"""

    def __init__(self, player: ba.SessionPlayer):

        self.player = player
        self.players_data_path = ba.app.config["Player_Data_Path"]
        self.players_data = read(self.players_data_path)
        self.account_id = player.get_account_id()
        self.timer = ba.Timer(5, self.add_experience, repeat=True)

    def add_experience(self) -> None:
        """Add experince to the account."""

        if not self.player:
            del self.timer

        if self.players_data is None:
            return

        self.players_data.setdefault("exp", 0)
        self.players_data.setdefault("level", 1)

        self.players_data[self.account_id]["exp"] += 1
        self.check_levelup()

    def check_levelup(self) -> None:
        """Check if account is leveled up."""

        if self.players_data is None:
            return

        exp = self.players_data[self.account_id]["exp"]
        level = self.players_data[self.account_id]["level"]
        required_exp = int(exp ** (1 / 4))

        if level < required_exp:
            self.players_data[self.account_id]["level"] += 1
            self.run_events(level + 1)

        write(self.players_data_path, self.players_data)

    def run_events(self, level: int) -> None:
        """Calls the Level up listeners."""

        callback = levelup_callbacks.get(level)

        if callback is not None:
            callback(self.player)
