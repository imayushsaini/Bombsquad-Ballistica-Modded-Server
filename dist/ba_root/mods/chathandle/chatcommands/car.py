# ba_meta require api 6
from __future__ import annotations

import random
from typing import TYPE_CHECKING

import _babase
import babase
from babase import InputType
import bascenev1 as bs
from bascenev1 import _classicassets
from bascenev1lib.actor.bomb import Bomb
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Sequence, Any


class Car(bs.Actor):
    """A drivable hockey-puck car controlled by a player."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        self.controlled = False
        self.source_player = None
        self.move_x = 0.0
        self.move_z = 0.0

        try:
            puck_mesh = _classicassets.meshes.puck.get()
            puck_tex = _classicassets.textures.puck_color.get()
            puck_sound = _classicassets.audio.metal_hit.get()
        except Exception:
            puck_mesh = bs.getmesh('puck')
            puck_tex = bs.gettexture('puckColor')
            puck_sound = bs.getsound('metalHit')

        self.puck_material = bs.Material()
        self.puck_material.add_actions(
            actions=('modify_part_collision', 'friction', 0.5)
        )
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=('modify_part_collision', 'collide', False),
        )
        self.puck_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.footing_material),
            actions=('impact_sound', puck_sound, 0.2, 5),
        )

        pmats = [shared.object_material, self.puck_material]

        self.node = bs.newnode(
            'prop',
            delegate=self,
            owner=None,
            attrs={
                'mesh': puck_mesh,
                'color_texture': puck_tex,
                'body': 'landMine',
                'reflection': 'soft',
                'reflection_scale': [0.2],
                'shadow_size': 1.0,
                'is_area_of_interest': True,
                'position': position,
                'materials': pmats,
            },
        )
        bs.animate(self.node, 'mesh_scale', {0: 0, 0.2: 1.3, 0.26: 1})

    def checkCanControl(self) -> bool:
        if not self.node or not self.node.exists():
            return False
        if self.source_player is None or not self.source_player.is_alive():
            self.dis()
            return False
        return True

    def con(self):
        self.controlled = True
        self.move_x = 0.0
        self.move_z = 0.0
        self.checkPlayerDie()

    def _wake_body(self, dir_x: float, dir_z: float):
        """Send an impulse message on input event to wake up ODE physics body if sleeping."""
        if not self.node or not self.node.exists():
            return
        try:
            pos = self.node.position
        except Exception:
            return

        dist = (dir_x ** 2 + dir_z ** 2) ** 0.5
        if dist > 0.001:
            fx = dir_x / dist
            fz = dir_z / dist
        else:
            fx = 0.0
            fz = 0.0

        # Sending 'impulse' triggers C++ dBodyEnable(body_) on ODE body
        self.node.handlemessage(
            'impulse',
            pos[0], pos[1], pos[2],
            0.0, 0.0, 0.0,
            3.0,  # magnitude
            0.0,  # velocity_magnitude
            0.0,  # radius
            0,    # calc_only
            fx, 0.0, fz
        )

    def _update_movement(self):
        if not self.node or not self.node.exists():
            return

        if self.move_x != 0.0 or self.move_z != 0.0:
            # Wake up ODE sleeping body via impulse message directly on input event
            self._wake_body(self.move_x, -self.move_z)

            accel_scale = 35.0
            target_accel_x = self.move_x * accel_scale
            target_accel_z = -self.move_z * accel_scale
            self.node.extra_acceleration = (
                target_accel_x, 0.0, target_accel_z)

            v = self.node.velocity
            target_vel_x = self.move_x * 9.0
            target_vel_z = -self.move_z * 9.0
            self.node.velocity = (
                target_vel_x if abs(self.move_x) > 0.01 else v[0],
                v[1],
                target_vel_z if abs(self.move_z) > 0.01 else v[2],
            )
        else:
            self.node.extra_acceleration = (0.0, 0.0, 0.0)

    def leftright(self, value: float):
        if not self.checkCanControl():
            return
        self.move_x = value
        self._update_movement()

    def updown(self, value: float):
        if not self.checkCanControl():
            return
        self.move_z = value
        self._update_movement()

    def dis(self):
        if self.node and self.node.exists():
            self.controlled = False
            self.move_x = 0.0
            self.move_z = 0.0
            self.node.extra_acceleration = (0.0, 0.0, 0.0)
            self.node.velocity = (0, 0, 0)
            self.source_player = None

    def checkPlayerDie(self):
        if not self.controlled:
            return
        if self.source_player is None:
            return
        if self.source_player.is_alive():
            bs.timer(1.0, self.checkPlayerDie)
        else:
            self.dis()

    def drop(self):
        if not self.checkCanControl():
            return
        try:
            np = self.node.position
        except Exception:
            np = (0, 0, 0)
        b = Bomb(
            bomb_type=random.choice(
                ['normal', 'ice', 'sticky', 'impact', 'land_mine', 'tnt']
            ),
            source_player=self.source_player,
            position=(np[0], np[1] + 0.5, np[2]),
            velocity=(0, 1, 0),
        ).autoretain()
        if b.bomb_type in ['impact', 'land_mine']:
            b.arm()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()
                self.controlled = False
                self.source_player = None
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        elif isinstance(msg, bs.HitMessage):
            if self.node:
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse',
                    msg.pos[0],
                    msg.pos[1],
                    msg.pos[2],
                    msg.velocity[0],
                    msg.velocity[1],
                    msg.velocity[2],
                    1.0 * msg.magnitude,
                    1.0 * msg.velocity_magnitude,
                    msg.radius,
                    0,
                    msg.force_direction[0],
                    msg.force_direction[1],
                    msg.force_direction[2],
                )
        else:
            super().handlemessage(msg)


def assignCarInputs(clientID: int):
    activity = bs.get_foreground_host_activity()
    if activity is None:
        return
    with activity.context:
        for i in activity.players:
            if str(i.sessionplayer.inputdevice.client_id) == str(clientID):
                if not i.actor or not i.actor.exists() or not i.is_alive():
                    return

                ps = i.actor.node.position

                if not hasattr(activity, 'car') or activity.car is None or not activity.car.node.exists():
                    try:
                        activity.car = Car(
                            position=(ps[0] + 1.0, ps[1] + 0.5, ps[2]))
                    except Exception as e:
                        print(f"Error creating Car: {e}")
                        return

                car = activity.car
                if car.controlled:
                    bs.broadcastmessage(
                        'Car is already being controlled',
                        color=(1, 0, 0),
                        transient=True,
                        clients=[clientID],
                    )
                    return

                bs.broadcastmessage(
                    'You Gained Control Over The Car!\n Press Bomb to Throw Bombs and Punch to leave!',
                    clients=[clientID],
                    transient=True,
                    color=(0, 1, 1),
                )

                def dis(player, car_obj):
                    if player and player.actor and player.actor.exists() and player.actor.node:
                        player.actor.node.invincible = False
                        player.resetinput()
                        player.actor.connect_controls_to_player()
                    car_obj.dis()

                player_actor = i.actor
                player_actor.node.invincible = True
                car.node.position = (ps[0] + 1.0, ps[1] + 0.5, ps[2])
                car.node.velocity = (0, 0.5, 0)
                player_actor.connect_controls_to_player()
                player_actor.disconnect_controls_from_player()
                i.resetinput()
                car.source_player = i
                car.con()
                i.assigninput(InputType.BOMB_PRESS, car.drop)
                i.assigninput(InputType.PUNCH_PRESS, babase.Call(dis, i, car))
                i.assigninput(InputType.UP_DOWN, car.updown)
                i.assigninput(InputType.LEFT_RIGHT, car.leftright)
                break
