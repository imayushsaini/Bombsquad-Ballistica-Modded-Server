"""Aditional effects for player."""

from __future__ import annotations
import random

from player_spaz.spaz_node import on_player_spawn
from bastd.actor.popuptext import PopupText
import ba


@on_player_spawn(name="smoke")
def smoke_effect(player: ba.Player, node: ba.Node) -> None:
    """Smoke emit effect."""

    def smoke_emitfx():
        if not player.is_alive() or not node.exists():
            return

        ba.emitfx(position=node.position, emit_type="distortion", spread=1.0)
        ba.emitfx(
            position=node.position,
            velocity=node.velocity,
            count=random.randint(1, 5),
            emit_type="tendrils",
            tendril_type="smoke",
        )

    ba.timer(0.6, smoke_emitfx, repeat=True)


@on_player_spawn(name="metalDrop")
def metal_drop_effect(player: ba.Player, node: ba.Node) -> None:
    """Metal drop emit effect.append()"""

    def metal_drop_emitfx():
        if not player.is_alive() or not node.exists():
            return

        ba.emitfx(
            position=node.position,
            velocity=node.velocity,
            count=random.randint(2, 8),
            scale=0.4,
            spread=0.2,
            chunk_type="metal",
        )

    ba.timer(0.7, metal_drop_emitfx, repeat=True)


@on_player_spawn(name="Distortion")
def distortion_effect(player: ba.Player, node: ba.Node) -> None:
    """distortion emit effect"""

    def distortion_emitfx():
        if not player.is_alive() or not node.exists():
            return

        ba.emitfx(position=node.position, emit_type="distortion", spread=1.0)
        ba.emitfx(
            position=node.position,
            velocity=node.velocity,
            count=random.randint(1, 5),
            emit_type="tendrils",
            tendril_type="smoke",
        )

    ba.timer(1, distortion_emitfx, repeat=True)


@on_player_spawn(name="snowDrop")
def snow_drop_effect(player: ba.Player, node: ba.Node) -> None:
    """snow drop emit effect"""

    def snow_drop_emitfx():
        if not player.is_alive() or not node.exists():
            return

        ba.emitfx(
            position=node.position,
            velocity=node.velocity,
            count=random.randint(2, 4),
            scale=0.4,
            spread=0.2,
            chunk_type="ice",
        )

    ba.timer(0.7, snow_drop_emitfx, repeat=True)


@on_player_spawn(name="slimeDrop")
def slime_drop_effect(player: ba.Player, node: ba.Node) -> None:
    """slime drop emit effect"""

    def slime_drop_emitfx():
        if not player.is_alive() or not node.exists():
            return

        ba.emitfx(
            position=node.position,
            velocity=node.velocity,
            count=random.randint(1, 10),
            scale=0.4,
            spread=0.2,
            chunk_type="slime",
        )

    ba.timer(0.25, slime_drop_emitfx, repeat=True)


@on_player_spawn(name="spark")
def spark_effect(player: ba.Player, node: ba.Node) -> None:
    """spark emit effect"""

    def spark_emitfx():
        if not player.is_alive() or not node.exists():
            return

        ba.emitfx(
            position=node.position,
            velocity=node.velocity,
            count=random.randint(1, 10),
            scale=2,
            spread=0.2,
            chunk_type="spark",
        )

    ba.timer(0.5, spark_emitfx, repeat=True)


@on_player_spawn(name="trail")
def trail_node(player: ba.Player, node: ba.Node) -> None:
    """trail floating around player"""
    trails = ["You\nNoobs", "π", "¶", "×", "@", "#", "Get\nRekt", "I Am\n#Pro"]

    def node_text() -> None:
        PopupText(
            random.choice(trails),
            scale=1.25,
            color=random.choice([(1, 0, 0), (0, 1, 0), (0, 0, 1)]),
            position=(
                player.node.position[0],
                player.node.position[1] - 1.5,
                player.node.position[2],
            ),
        ).autoretain()

    ba.timer(2, node_text, repeat=True)
