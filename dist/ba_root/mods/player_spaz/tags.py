"""Tags functionality for players."""

from __future__ import annotations

from player_spaz.spaz_node import on_player_spawn
from player_records.file_handle import read
import ba


@on_player_spawn(name="rank-level-tag", all_players=True)
def rank_level_node(player: ba.Player, node: ba.Node) -> None:
    """Text node showing rank and level on players head."""

    account_id = player.sessionplayer.get_account_id()
    players_data = read(ba.app.config["Player_Data_Path"])
    stats_data = read(ba.app.config["Stats_Path"])

    if players_data is not None and stats_data is not None:

        if account_id in players_data:
            level = players_data[account_id]["level"]
        else:
            level = "New"

        if account_id in stats_data:
            rank = stats_data[account_id]["rank"]
            text = f"#{rank} | lvl {level}"
        else:
            text = f"new | lvl {level}"

    mnode = ba.newnode(
        "math", owner=node, attrs={"input1": (0, 1.2, 0), "operation": "add"}
    )
    node.connectattr("torso_position", mnode, "input2")

    rank_text = ba.newnode(
        "text",
        owner=node,
        attrs={
            "text": text,
            "in_world": True,
            "shadow": 1.0,
            "flatness": 1.0,
            "color": node.color,
            "scale": 0.01,
            "h_align": "center",
        },
    )
    mnode.connectattr("output", rank_text, "position")


@on_player_spawn(name="customTag")
def tag_node(player: ba.Player, node: ba.Node) -> None:
    """A custom tag for player."""

    account_id = player.sessionplayer.get_account_id()
    players_data = read(ba.app.config["Player_Data_Path"])
    if players_data is not None:
        tag = players_data[account_id]["inventory"]["customTag"]

    mnode = ba.newnode(
        "math", owner=node, attrs={"input1": (0, 1.5, 0), "operation": "add"}
    )
    node.connectattr("torso_position", mnode, "input2")

    tag_text = ba.newnode(
        "text",
        owner=node,
        attrs={
            "text": tag,
            "in_world": True,
            "shadow": 1.0,
            "flatness": 1.0,
            "color": node.color,
            "scale": 0.01,
            "h_align": "center",
        },
    )
    mnode.connectattr("output", tag_text, "position")
