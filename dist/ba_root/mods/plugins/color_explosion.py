"""Define a simple example plugin."""

# ba_meta require api 7

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import random
from bastd.actor import bomb
from bastd.actor.bomb import BombFactory
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence, Optional, Callable


def new_blast_init(
    self,
    position: Sequence[float] = (0.0, 1.0, 0.0),
    velocity: Sequence[float] = (0.0, 0.0, 0.0),
    blast_radius: float = 2.0,
    blast_type: str = "normal",
    source_player: ba.Player = None,
    hit_type: str = "explosion",
    hit_subtype: str = "normal",
):
    """Instantiate with given values."""

    # bah; get off my lawn!
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    ba.Actor.__init__(self)  # super method can't be used here

    shared = SharedObjects.get()
    factory = BombFactory.get()

    self.blast_type = blast_type
    self._source_player = source_player
    self.hit_type = hit_type
    self.hit_subtype = hit_subtype
    self.radius = blast_radius

    # Set our position a bit lower so we throw more things upward.
    rmats = (factory.blast_material, shared.attack_material)
    self.node = ba.newnode(
        "region",
        delegate=self,
        attrs={
            "position": (position[0], position[1] - 0.1, position[2]),
            "scale": (self.radius, self.radius, self.radius),
            "type": "sphere",
            "materials": rmats,
        },
    )

    ba.timer(0.05, self.node.delete)

    # Throw in an explosion and flash.
    evel = (velocity[0], max(-1.0, velocity[1]), velocity[2])
    explosion = ba.newnode(
        "explosion",
        attrs={
            "position": position,
            "velocity": evel,
            "radius": self.radius,
            "big": (self.blast_type == "tnt"),
        },
    )
    if self.blast_type == "ice":
        explosion.color = (0, 0.05, 0.4)

    ba.timer(1.0, explosion.delete)

    if self.blast_type != "ice":
        ba.emitfx(
            position=position,
            velocity=velocity,
            count=int(1.0 + random.random() * 4),
            emit_type="tendrils",
            tendril_type="thin_smoke",
        )
    ba.emitfx(
        position=position,
        velocity=velocity,
        count=int(4.0 + random.random() * 4),
        emit_type="tendrils",
        tendril_type="ice" if self.blast_type == "ice" else "smoke",
    )
    ba.emitfx(
        position=position,
        emit_type="distortion",
        spread=1.0 if self.blast_type == "tnt" else 2.0,
    )

    # And emit some shrapnel.
    if self.blast_type == "ice":

        def emit() -> None:
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=30,
                spread=2.0,
                scale=0.4,
                chunk_type="ice",
                emit_type="stickers",
            )

        # It looks better if we delay a bit.
        ba.timer(0.05, emit)

    elif self.blast_type == "sticky":

        def emit() -> None:
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(4.0 + random.random() * 8),
                spread=0.7,
                chunk_type="slime",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(4.0 + random.random() * 8),
                scale=0.5,
                spread=0.7,
                chunk_type="slime",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=15,
                scale=0.6,
                chunk_type="slime",
                emit_type="stickers",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=20,
                scale=0.7,
                chunk_type="spark",
                emit_type="stickers",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(6.0 + random.random() * 12),
                scale=0.8,
                spread=1.5,
                chunk_type="spark",
            )

        # It looks better if we delay a bit.
        ba.timer(0.05, emit)

    elif self.blast_type == "impact":

        def emit() -> None:
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(4.0 + random.random() * 8),
                scale=0.8,
                chunk_type="metal",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(4.0 + random.random() * 8),
                scale=0.4,
                chunk_type="metal",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=20,
                scale=0.7,
                chunk_type="spark",
                emit_type="stickers",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(8.0 + random.random() * 15),
                scale=0.8,
                spread=1.5,
                chunk_type="spark",
            )

        # It looks better if we delay a bit.
        ba.timer(0.05, emit)

    else:  # Regular or land mine bomb shrapnel.

        def emit() -> None:
            if self.blast_type != "tnt":
                ba.emitfx(
                    position=position,
                    velocity=velocity,
                    count=int(4.0 + random.random() * 8),
                    chunk_type="rock",
                )
                ba.emitfx(
                    position=position,
                    velocity=velocity,
                    count=int(4.0 + random.random() * 8),
                    scale=0.5,
                    chunk_type="rock",
                )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=30,
                scale=1.0 if self.blast_type == "tnt" else 0.7,
                chunk_type="spark",
                emit_type="stickers",
            )
            ba.emitfx(
                position=position,
                velocity=velocity,
                count=int(18.0 + random.random() * 20),
                scale=1.0 if self.blast_type == "tnt" else 0.8,
                spread=1.5,
                chunk_type="spark",
            )

            # TNT throws splintery chunks.
            if self.blast_type == "tnt":

                def emit_splinters() -> None:
                    ba.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(20.0 + random.random() * 25),
                        scale=0.8,
                        spread=1.0,
                        chunk_type="splinter",
                    )

                ba.timer(0.01, emit_splinters)

            # Every now and then do a sparky one.
            if self.blast_type == "tnt" or random.random() < 0.1:

                def emit_extra_sparks() -> None:
                    ba.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(10.0 + random.random() * 20),
                        scale=0.8,
                        spread=1.5,
                        chunk_type="spark",
                    )

                ba.timer(0.02, emit_extra_sparks)

        # It looks better if we delay a bit.
        ba.timer(0.05, emit)

    lcolor = (0.6, 0.6, 1.0) if self.blast_type == "ice" else (1, 0.3, 0.1)
    light = ba.newnode(
        "light",
        attrs={"position": position, "volume_intensity_scale": 10.0, "color": lcolor},
    )

    scl = random.uniform(0.6, 0.9)
    scorch_radius = light_radius = self.radius
    if self.blast_type == "tnt":
        light_radius *= 1.4
        scorch_radius *= 1.15
        scl *= 3.0

    iscale = 1.6
    ba.animate(
        light,
        "intensity",
        {
            0: 2.0 * iscale,
            scl * 0.02: 0.1 * iscale,
            scl * 0.025: 0.2 * iscale,
            scl * 0.05: 17.0 * iscale,
            scl * 0.06: 5.0 * iscale,
            scl * 0.08: 4.0 * iscale,
            scl * 0.2: 0.6 * iscale,
            scl * 2.0: 0.00 * iscale,
            scl * 3.0: 0.0,
        },
    )
    ba.animate(
        light,
        "radius",
        {
            0: light_radius * 0.2,
            scl * 0.05: light_radius * 0.55,
            scl * 0.1: light_radius * 0.3,
            scl * 0.3: light_radius * 0.15,
            scl * 1.0: light_radius * 0.05,
        },
    )
    ba.timer(scl * 3.0, light.delete)

    # Make a scorch that fades over time.
    scorch = ba.newnode(
        "scorch",
        attrs={
            "position": position,
            "size": scorch_radius * 0.5,
            "big": (self.blast_type == "tnt"),
        },
    )
    if self.blast_type == "ice":
        scorch.color = (1, 1, 1.5)
    else:
        scorch.color = (random.random(), random.random(), random.random())

    ba.animate(scorch, "presence", {3.000: 1, 13.000: 0})
    ba.timer(13.0, scorch.delete)

    if self.blast_type == "ice":
        ba.playsound(factory.hiss_sound, position=light.position)

    lpos = light.position
    ba.playsound(factory.random_explode_sound(), position=lpos)
    ba.playsound(factory.debris_fall_sound, position=lpos)

    ba.camerashake(intensity=5.0 if self.blast_type == "tnt" else 1.0)

    # TNT is more epic.
    if self.blast_type == "tnt":
        ba.playsound(factory.random_explode_sound(), position=lpos)

        def _extra_boom() -> None:
            ba.playsound(factory.random_explode_sound(), position=lpos)

        ba.timer(0.25, _extra_boom)

        def _extra_debris_sound() -> None:
            ba.playsound(factory.debris_fall_sound, position=lpos)
            ba.playsound(factory.wood_debris_fall_sound, position=lpos)

        ba.timer(0.4, _extra_debris_sound)


def enable() -> None:
    bomb.Blast.__init__ = new_blast_init
