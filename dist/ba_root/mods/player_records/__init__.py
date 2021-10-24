"""Initialize the system and make plugin"""

# ba_meta require api 6

from __future__ import annotations

from ba import Plugin, SessionPlayer
from ba._activitytypes import ScoreScreenActivity
from ba._session import Session

# pakage imports
import player_records.levelups
from player_records.auto_update import AutoUpdate
from player_records.stats import PlayerStats
from player_records.level import PlayerLevel


# ba_meta export plugin
class PlayerRecord(Plugin):
    """Initialize the system and redefine some internal objects."""

    def on_app_launch(self) -> None:
        AutoUpdate()

        on_begin = ScoreScreenActivity.on_begin
        on_player_request = Session.on_player_request

        def modified_on_begin(self) -> None:
            on_begin(self)
            PlayerStats(self.stats).start()

        def modified_on_player_request(self, player: SessionPlayer) -> bool:
            PlayerLevel(player)
            return on_player_request(self, player)

        ScoreScreenActivity.on_begin = modified_on_begin  # type: ignore
        Session.on_player_request = modified_on_player_request  # type: ignore
