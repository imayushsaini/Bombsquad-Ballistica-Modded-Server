import random

import babase
import bascenev1 as bs
from bascenev1._messages import DeathType, OutOfBoundsMessage
from bascenev1lib.gameutils import SharedObjects

on_begin_original = bs._activity.Activity.on_begin


def fireflies_generator(activity, count, random_color: False):

    if random_color:
        color = (random.uniform(0, 1.2), random.uniform(
            0, 1.2), random.uniform(0, 1.2))
    else:
        color = (0.9, 0.7, 0.0)
    increment = count - len(activity.fireflies)

    if increment > 0:
        spawn_areas = _calculate_spawn_areas()
        if not spawn_areas:
            return
        for _ in range(increment):
            with activity.context:
                firefly = FireFly(random.choice(spawn_areas), color)
            activity.fireflies.append(firefly)
    else:
        for _ in range(abs(increment)):
            firefly = activity.fireflies.pop()
            try:
                firefly.handlemessage(bs.DieMessage())
            except AttributeError:
                pass
            firefly.timer = None


def _calculate_spawn_areas():
    activity = bs.get_foreground_host_activity()
    if not isinstance(activity, bs.GameActivity):
        return
    aoi_bounds = activity.map.get_def_bound_box("area_of_interest_bounds")
    # aoi_bounds = activity.map.get_def_bound_box("map_bounds")
    first_half = list(aoi_bounds)
    second_half = list(aoi_bounds)
    midpoint_x = (aoi_bounds[0] + aoi_bounds[3]) / 2
    first_half[3] = midpoint_x
    second_half[0] = midpoint_x
    spawn_areas = (first_half, second_half)
    return spawn_areas


class FireFly(bs.Actor):
    def __init__(self, area, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.area = area
        self.color = color
        initial_timer = random.uniform(0.5, 6)
        self.timer = bs.Timer(initial_timer, self.on)

    def on(self):
        shared = SharedObjects.get()
        self.mat = bs.Material()
        self.mat.add_actions(
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
            ))
        self.node = bs.newnode('locator',
                               attrs={'shape': 'circle', 'position': (0, .5, 0),
                                      'color': self.color, 'opacity': 0.5,
                                      'draw_beauty': True, 'additive': False,
                                      'size': [0.10]})
        # bs.animate(
        #     self.node,
        #     'scale',
        #     {0:0, 1:0.004, 5:0.006, 10:0.0},
        #     loop=True,
        # )
        bs.animate_array(
            self.node,
            'position',
            3,
            self.generate_keys(self.area),
            loop=True
        )

        self.light = bs.newnode(
            'light',
            owner=self.node,
            attrs={
                'intensity': 0.6,
                'height_attenuated': True,
                'radius': 0.2,
                'color': self.color
            })
        bs.animate(
            self.light,
            'radius',
            {0: 0.0, 20: 0.4, 70: 0.1, 100: 0.3, 150: 0},
            loop=True
        )
        self.node.connectattr('position', self.light, 'position')

    def off(self):
        death_secs = random.uniform(0.5, 3)
        with babase.Context(self._activity()):
            bs.animate(
                self.node,
                'mesh_scale',
                {0: self.node.mesh_scale, death_secs: 0}
            )
            bs.animate(
                self.light,
                'radius',
                {0: self.light.radius, death_secs: 0}
            )
            bs.timer(death_secs, self.node.delete)

    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self.off()
            return None
        elif isinstance(msg, OutOfBoundsMessage):
            return self.handlemessage(
                bs.DieMessage(how=DeathType.OUT_OF_BOUNDS))
        return super().handlemessage(msg)

    def generate_keys(self, m):
        keys = {}
        t = 0
        last_x = random.randrange(int(m[0]), int(m[3]))
        last_y = random.randrange(int(m[1]), int(m[4]))
        if int(m[2]) == int(m[5]):
            last_z = int(m[2])
        else:
            last_z = random.randrange(int(m[2]), int(m[5]))
        for i in range(0, 7):
            x = self.generate_random(int(m[0]), int(m[3]), last_x)
            last_x = x
            y = self.generate_random(int(m[1]), int(m[4]), last_y)
            last_y = y
            z = self.generate_random(int(m[2]), int(m[5]), last_z)
            last_z = z
            keys[t] = (x, abs(y), z)
            t += 30
        return keys

    def generate_random(self, a, b, z):
        if a == b:
            return a
        while True:
            n = random.randrange(a, b)
            if abs(z - n) < 6:
                return n


def on_begin(self, *args, **kwargs) -> None:
    self.fireflies = []
    return on_begin_original(self, *args, **kwargs)


bs._activity.Activity.fireflies_generator = fireflies_generator
bs._activity.Activity.on_begin = on_begin
