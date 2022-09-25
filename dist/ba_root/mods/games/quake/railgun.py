"""Quake Game Rocket weapon"""
from __future__ import annotations

from typing import TYPE_CHECKING

import _ba
import ba

from bastd.actor.playerspaz import PlayerSpaz

if TYPE_CHECKING:
    from typing import Optional, Any
    from bastd.actor.spaz import Spaz

STORAGE_ATTR_NAME = f'_shared_{__name__}_factory'


class Railgun:
    """Very dangerous weapon"""

    def __init__(self) -> None:
        self.last_shot: Optional[int, float] = 0

    def give(self, spaz: Spaz) -> None:
        """Give spaz a railgun"""
        spaz.punch_callback = self.shot
        self.last_shot = ba.time()

    # FIXME
    # noinspection PyUnresolvedReferences
    def shot(self, spaz: Spaz) -> None:
        """Release a rocket"""
        time = ba.time()
        if time - self.last_shot > 0.6:
            self.last_shot = time
            center = spaz.node.position_center
            forward = spaz.node.position_forward
            direction = [
                center[0] - forward[0], forward[1] - center[1],
                center[2] - forward[2]
            ]
            direction[1] = 0.0

            RailBullet(position=spaz.node.position,
                       direction=direction,
                       owner=spaz.getplayer(ba.Player),
                       source_player=spaz.getplayer(ba.Player),
                       color=spaz.node.color).autoretain()


class TouchedToSpazMessage:
    """I hit!"""

    def __init__(self, spaz) -> None:
        self.spaz = spaz


class RailBullet(ba.Actor):
    """Railgun bullet"""

    def __init__(self,
                 position=(0, 5, 0),
                 direction=(0, 2, 0),
                 source_player=None,
                 owner=None,
                 color=(1, 1, 1)) -> None:
        super().__init__()
        self._color = color

        self.node = ba.newnode('light',
                               delegate=self,
                               attrs={
                                   'position': position,
                                   'color': self._color
                               })
        ba.animate(self.node, 'radius', {0: 0, 0.1: 0.5, 0.5: 0})

        self.source_player = source_player
        self.owner = owner
        self._life_timer = ba.Timer(
            0.5, ba.WeakCall(self.handlemessage, ba.DieMessage()))

        pos = position
        vel = tuple(i / 5 for i in ba.Vec3(direction).normalized())
        for _ in range(500):  # Optimization :(
            ba.newnode('explosion',
                       owner=self.node,
                       attrs={
                           'position': pos,
                           'radius': 0.2,
                           'color': self._color
                       })
            pos = (pos[0] + vel[0], pos[1] + vel[1], pos[2] + vel[2])

        for node in _ba.getnodes():
            if node and node.getnodetype() == 'spaz':
                # pylint: disable=invalid-name
                m3 = ba.Vec3(position)
                a = ba.Vec3(direction[2], direction[1], direction[0])
                m1 = ba.Vec3(node.position)
                # pylint: enable=invalid-name
                # distance between node and line
                dist = (a * (m1 - m3)).length() / a.length()
                if dist < 0.3:
                    if node and node != self.owner and node.getdelegate(
                            PlayerSpaz, True).getplayer(
                                ba.Player, True).team != self.owner.team:
                        node.handlemessage(ba.FreezeMessage())
                        pos = self.node.position
                        hit_dir = (0, 10, 0)

                        node.handlemessage(
                            ba.HitMessage(pos=pos,
                                          magnitude=50,
                                          velocity_magnitude=50,
                                          radius=0,
                                          srcnode=self.node,
                                          source_player=self.source_player,
                                          force_direction=hit_dir))

    def handlemessage(self, msg: Any) -> Any:
        super().handlemessage(msg)
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ba.OutOfBoundsMessage):
            self.handlemessage(ba.DieMessage())
