"""A simple levelup rewards functionality."""

from __future__ import annotations
from player_records.level import PlayerLevel, on_levelup
import ba


# pylint: disable=missing-function-docstring


@on_levelup(4)
def add_smoke_effect(player_record: PlayerLevel) -> None:
    player_record.add_item("smoke", False)
    message = '"smoke" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(6)
def add_metal_drop_effect(player_record: PlayerLevel) -> None:
    player_record.add_item("metalDrop", False)
    message = '"metal_drop" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(9)
def add_distortion_effect(player_record: PlayerLevel) -> None:
    player_record.add_item("Distortion", False)
    message = '"distortion" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(11)
def add_death_animation(player_record: PlayerLevel) -> None:
    player_record.add_item("deathAnim", False)
    message = "you unlocked death animation"
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(13)
def add_snow_drop_effect(player_record: PlayerLevel) -> None:
    player_record.add_item("snowDrop", False)
    message = '"snow_drop" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(15)
def add_slime_drop_effect(player_record: PlayerLevel) -> None:
    player_record.add_item("slimeDrop", False)
    message = '"slime_drop" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(19)
def add_spawn_animation(player_record: PlayerLevel) -> None:
    player_record.add_item("spawnAnim", False)
    message = "you unlocked spawn animation"
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(21)
def add_spark_effect(player_record: PlayerLevel) -> None:
    player_record.add_item("spark", False)
    message = '"spark" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(22)
def add_custom_tag(player_record: PlayerLevel) -> None:
    player_record.add_item("customTag", player_record.player.getname())
    message = "you unlocked custom tag"
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )


@on_levelup(25)
def add_trail(player_record: PlayerLevel) -> None:
    player_record.add_item("trail", False)
    message = '"Trail" effect has been added to your inventory'
    ba.screenmessage(
        message=message,
        transient=True,
        clients=[player_record.player.inputdevice.client_id],
    )
