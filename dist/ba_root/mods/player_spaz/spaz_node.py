"""A file redefining Player spaz object and also core of this pakage."""

from __future__ import annotations
from typing import Callable, Sequence, Tuple, List

from bastd.actor import playerspaz
from player_records.file_handle import read
import ba


PlayerSpazFunction = Callable[[ba.Player, ba.Node], None]
player_spaz_events: List[Tuple[str, bool, PlayerSpazFunction]] = []


def on_player_spawn(
    name, all_players: bool = False
) -> Callable[[PlayerSpazFunction], PlayerSpazFunction]:
    """A decorator to listen when player spawns.
    decorated function will get `ba.player` and `ba.node` passed.

    Parameters
    ----------
    name : str, optional
        name of node
    all_players : bool, optional
        to spawn the node for all players, by default False
    """

    def wrapper(function: PlayerSpazFunction) -> PlayerSpazFunction:
        player_spaz_events.append((name, all_players, function))
        return function

    return wrapper


class ModifiedPlayerSpaz(playerspaz.PlayerSpaz):
    """Modified player spaz nodes."""

    def __init__(
        self,
        player: ba.Player,
        color: Sequence[float] = (1.0, 1.0, 1.0),
        highlight: Sequence[float] = (0.5, 0.5, 0.5),
        character: str = "Spaz",
        powerups_expire: bool = True,
    ) -> None:
        super().__init__(
            player=player,
            color=color,
            highlight=highlight,
            character=character,
            powerups_expire=powerups_expire,
        )

        account_id = player.sessionplayer.get_account_id()
        players_data = read(ba.app.config["Player_Data_Path"])

        if players_data is not None and account_id in players_data:
            for node, all_players, callback in player_spaz_events:
                if all_players:
                    callback(player, self.node)
                elif (
                    node in players_data[account_id]["inventory"]
                    and players_data[account_id]["inventory"][node]
                ):
                    callback(player, self.node)


playerspaz.PlayerSpaz = ModifiedPlayerSpaz  # type: ignore
