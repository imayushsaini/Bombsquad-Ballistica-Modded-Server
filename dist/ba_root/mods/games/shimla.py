# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects
from bastd.game.deathmatch import DeathMatchGame, Player, Team
if TYPE_CHECKING:
    from typing import Any, Sequence

# ba_meta export game


class ShimlaGame(DeathMatchGame):
    name = 'Shimla'

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Creative Thoughts']

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self.lifts = {}
        self._real_wall_material = ba.Material()
        self._real_wall_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))

        self._real_wall_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))
        self._lift_material = ba.Material()
        self._lift_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))
        self._lift_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_connect', self._handle_lift),),
        )
        self._lift_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(('call', 'at_disconnect', self._handle_lift_disconnect),),
        )

    def on_begin(self):
        ba.getactivity().globalsnode.happy_thoughts_mode = False
        super().on_begin()
        
        self.make_map()
        ba.timer(2, self.disable_fly)
    def disable_fly(self):
        activity = _ba.get_foreground_host_activity()

        for players in activity.players:
            players.actor.node.fly = False
    def spawn_player_spaz(
        self,
        player: Player,
        position: Sequence[float] | None = None,
        angle: float | None = None,
    ) -> PlayerSpaz:
        """Intercept new spazzes and add our team material for them."""
        spaz = super().spawn_player_spaz(player, position, angle)
        
        spaz.connect_controls_to_player(enable_punch=True,
                                        enable_bomb=True,
                                        enable_pickup=True,
                                        enable_fly=False,
                                        enable_jump=True)
        spaz.fly = False                              
        return spaz

    def make_map(self):
        shared = SharedObjects.get()
        _ba.get_foreground_host_activity()._map.leftwall.materials = [
            shared.footing_material, self._real_wall_material]

        _ba.get_foreground_host_activity()._map.rightwall.materials = [
            shared.footing_material, self._real_wall_material]

        _ba.get_foreground_host_activity()._map.topwall.materials = [
            shared.footing_material, self._real_wall_material]
        floor = ""
        for i in range(0, 90):
            floor += "_ "
        self.floorwall1 = ba.newnode('region', attrs={'position': (-10, 5, -5.52), 'scale': 
        (15, 0.2, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        self.floorwall2 = ba.newnode('region', attrs={'position': (10, 5, -5.52), 'scale': (
            15, 0.2, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})

        self.wall1 = ba.newnode('region', attrs={'position': (0, 11, -6.90), 'scale': (
            35.4, 20, 1), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        self.wall2 = ba.newnode('region', attrs={'position': (0, 11, -4.14), 'scale': (
            35.4, 20, 1), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})

        ba.newnode('locator', attrs={'shape': 'box', 'position': (-10, 5, -5.52), 'color': (
            0, 0, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (15, 0.2, 2)})

        ba.newnode('locator', attrs={'shape': 'box', 'position': (10, 5, -5.52), 'color': (
            0, 0, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (15, 0.2, 2)})
        self.create_lift(-16.65, 8)

        self.create_lift(16.65, 8)

        self.create_static_step(0, 18.29)
        self.create_static_step(0, 7)

        self.create_static_step(13, 17)
        self.create_static_step(-13, 17)
        self.create_slope(8, 15, True)
        self.create_slope(-8, 15, False)
        self.create_static_step(5, 15)
        self.create_static_step(-5, 15)

        self.create_static_step(13, 12)
        self.create_static_step(-13, 12)
        self.create_slope(8, 10, True)
        self.create_slope(-8, 10, False)
        self.create_static_step(5, 10)
        self.create_static_step(-5, 10)

    def create_static_step(self, x, y):
        floor = ""
        for i in range(0, 7):
            floor += "_ "
        shared = SharedObjects.get()

        ba.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (5.5, 0.1, 6),
                   'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
        ba.newnode('locator', attrs={'shape': 'box', 'position': (x, y,  -5.52), 'color': (
            1, 1, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (5.5, 0.1, 2)})

    def create_lift(self, x, y):
        shared = SharedObjects.get()
        color = (0.7, 0.6, 0.5)

        floor = ba.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (
            1.8, 0.1, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material ,self._lift_material]})

        cleaner = ba.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (
            2, 0.3, 2), 'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})

        lift = ba.newnode('locator', attrs={'shape': 'box', 'position': (
            x, y,  -5.52), 'color': color, 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (1.8, 3.7, 2)})

        _tcombine = ba.newnode('combine',
                               owner=floor,
                               attrs={
                                   'input0': x,
                                   'input2': -5.5,
                                   'size': 3
                               })
        mnode = ba.newnode('math',
                           owner=lift,
                           attrs={
                               'input1': (0, 2, 0),
                               'operation': 'add'
                           })
        _tcombine.connectattr('output', mnode, 'input2')

        _cleaner_combine = ba.newnode('combine',
                               owner=cleaner,
                               attrs={
                                   'input1': 5.6,
                                   'input2': -5.5,
                                   'size': 3
                               })
        _cleaner_combine.connectattr('output', cleaner, 'position')    
        ba.animate(_tcombine, 'input1', {
            0: 5.1,
        })
        ba.animate(_cleaner_combine, 'input0', {
            0: -19 if x < 0 else 19,
        })

        _tcombine.connectattr('output', floor, 'position')
        mnode.connectattr('output', lift, 'position')
        self.lifts[floor] = {"state":"origin","lift":_tcombine,"cleaner":_cleaner_combine,'leftLift': x < 0}

    def _handle_lift(self):
        region = ba.getcollision().sourcenode
        lift = self.lifts[region]
        def clean(lift):
            ba.animate(lift["cleaner"], 'input0', {
                0: -19 if lift["leftLift"] else 19 ,
                2: -16 if lift["leftLift"] else 16,
                4.3: -19 if lift["leftLift"] else 19
            })
        if lift["state"] == "origin":
            lift["state"] = "transition"
            ba.animate(lift["lift"], 'input1', {
                0: 5.1,
                1.3: 5.1,
                6: 5+12,
                9: 5+12,
                15: 5.1
            })
            ba.timer(16, ba.Call(lambda lift: lift.update({'state': 'end'}), lift))
            ba.timer(12, ba.Call(clean, lift))

        
    def _handle_lift_disconnect(self):
        region = ba.getcollision().sourcenode
        lift = self.lifts[region]
        if lift["state"] == 'end':
            lift["state"] = "origin"

    def create_slope(self, x, y, backslash):
        shared = SharedObjects.get()

        for i in range(0, 21):
            ba.newnode('region', attrs={'position': (x, y, -5.52), 'scale': (0.2, 0.1, 6),
                       'type': 'box', 'materials': [shared.footing_material, self._real_wall_material]})
            ba.newnode('locator', attrs={'shape': 'box', 'position': (x, y,  -5.52), 'color': (
                1, 1, 0), 'opacity': 1, 'draw_beauty': True, 'additive': False, 'size': (0.2, 0.1, 2)})
            if backslash:
                x = x+0.1
                y = y+0.1
            else:
                x = x-0.1
                y = y+0.1
