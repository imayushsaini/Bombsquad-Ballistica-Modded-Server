import random
from typing import TYPE_CHECKING

import ba
import _ba


from typing import Any, Sequence


class PopupText(ba.Actor):
    """Text that pops up above a position to denote something special.
    category: Gameplay Classes
    """

    def __init__(
        self,
        text: str | ba.Lstr,
        position: Sequence[float] = (0.0, 0.0, 0.0),
        color: Sequence[float] = (1.0, 1.0, 1.0, 1.0),
        random_offset: float = 0.5,
        offset: Sequence[float] = (0.0, 0.0, 0.0),
        scale: float = 1.0,
    ):
        """Instantiate with given values.
        random_offset is the amount of random offset from the provided position
        that will be applied. This can help multiple achievements from
        overlapping too much.
        """
        super().__init__()
        if len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)
        pos = (
            position[0] + offset[0] + random_offset * (0.5 - random.random()),
            position[1] + offset[1] + random_offset * (0.5 - random.random()),
            position[2] + offset[2] + random_offset * (0.5 - random.random()),
        )

        self.node = ba.newnode(
            'text',
            attrs={
                'text': text,
                'in_world': True,
                'shadow': 1.0,
                'flatness': 1.0,
                'h_align': 'center',
            },
            delegate=self,
        )

        lifespan = 10.5

        # scale up
        ba.animate(
            self.node,
            'scale',
            {
                0: 0.0,
                lifespan * 0.11: 0.020 * 0.7 * scale,
                lifespan * 0.16: 0.013 * 0.7 * scale,
                lifespan * 0.25: 0.016 * 0.7 * scale,
                lifespan * 0.45: 0.012 * 0.7 * scale,
                lifespan * 0.65: 0.014 * 0.7 * scale,
                lifespan * 0.75: 0.011 * 0.7 * scale,
                lifespan * 0.85: 0.015 * 0.7 * scale,
                lifespan * 0.90: 0.012 * 0.7 * scale,
                lifespan * 0.95: 0.016 * 0.7 * scale,
            },
        )

        # translate upward
        self._tcombine = ba.newnode(
            'combine',
            owner=self.node,
            attrs={'input0': pos[0], 'input2': pos[2], 'size': 3},
        )
        ba.animate(
            self._tcombine, 'input1', {0: pos[1] + 0, lifespan: pos[1] + 8.0}
        )
        self._tcombine.connectattr('output', self.node, 'position')

        # fade our opacity in/out
        self._combine = ba.newnode(
            'combine',
            owner=self.node,
            attrs={
                'input0': color[0],
                'input1': color[1],
                'input2': color[2],
                'size': 4,
            },
        )
        for i in range(4):
            ba.animate(
                self._combine,
                'input' + str(i),
                {
                    0.13 * lifespan: color[i],
                    0.18 * lifespan: 4.0 * color[i],
                    0.22 * lifespan: color[i],
                },
            )
        ba.animate(
            self._combine,
            'input3',
            {
                0: 0,
                0.1 * lifespan: color[3],
                0.7 * lifespan: color[3],
                lifespan: 0,
            },
        )
        self._combine.connectattr('output', self.node, 'color')

        # kill ourself
        self._die_timer = ba.Timer(
            lifespan, ba.WeakCall(self.handlemessage, ba.DieMessage())
        )

    def handlemessage(self, msg: Any) -> Any:
        assert not self.expired
        if isinstance(msg, ba.DieMessage):
            if self.node:
                self.node.delete()
        else:
            super().handlemessage(msg)


def spawn_heart():
    activity = _ba.get_foreground_host_activity()
    if not hasattr(activity, "heart"):
        activity.heart = []
    if hasattr(activity, "map"):
        bounds = activity.map.get_def_bound_box("area_of_interest_bounds")

        for i in range(0, 4):
            position = (random.uniform(bounds[0], bounds[3]), random.uniform(
                bounds[4]*1.15, bounds[4]*1.45)-8, random.uniform(bounds[2], bounds[5]))
            k = PopupText(u"\ue047", position)
            activity.heart.append(k)


def start():
    _ba.timer(random.uniform(7, 8), spawn_heart, repeat=True)
ba._activity.Activity.hearts_generator = start
