# ba_meta require api 6
from __future__ import annotations
from typing import TYPE_CHECKING
import _ba,ba,random,math
from bastd.gameutils import SharedObjects
from bastd.actor.bomb import Bomb
from ba._generated.enums import InputType
if TYPE_CHECKING:
    from typing import Optional


class Floater(ba.Actor):
    def __init__(self, bounds):
        super().__init__()
        shared = SharedObjects.get()
        self.controlled = False
        self.source_player = None
        self.floaterMaterial = ba.Material()
        self.floaterMaterial.add_actions(
            conditions=('they_have_material',
                        shared.player_material),
            actions=(('modify_node_collision', 'collide', True),
                     ('modify_part_collision', 'physical', True)))
        self.floaterMaterial.add_actions(
            conditions=(('they_have_material',
                         shared.object_material), 'or',
                        ('they_have_material',
                         shared.footing_material), 'or',
                        ('they_have_material',
                        self.floaterMaterial)),
            actions=('modify_part_collision', 'physical', False))

        self.pos = bounds
        self.px = "random.uniform(self.pos[0],self.pos[3])"
        self.py = "random.uniform(self.pos[1],self.pos[4])"
        self.pz = "random.uniform(self.pos[2],self.pos[5])"

        self.node = ba.newnode(
            'prop',
            delegate=self,
            owner=None,
            attrs={
                'position': (eval(self.px), eval(self.py), eval(self.pz)),
                'model':
                ba.getmodel('landMine'),
                'light_model':
                ba.getmodel('landMine'),
                'body':
                'landMine',
                'body_scale':
                3,
                'model_scale':
                3.1,
                'shadow_size':
                0.25,
                'density':
                999999,
                'gravity_scale':
                0.0,
                'color_texture':
                ba.gettexture('achievementFlawlessVictory'),
                'reflection':
                'soft',
                'reflection_scale': [0.25],
                'materials':
                [shared.footing_material, self.floaterMaterial]
            })
        self.node2 = ba.newnode(
            'prop',
            owner=self.node,
            attrs={
                'position': (0, 0, 0),
                'body':
                'sphere',
                'model':
                None,
                'color_texture':
                None,
                'body_scale':
                1.0,
                'reflection':
                'powerup',
                'density':
                999999,
                'reflection_scale': [1.0],
                'model_scale':
                1.0,
                'gravity_scale':
                0,
                'shadow_size':
                0.1,
                'is_area_of_interest':
                True,
                'materials':
                [shared.object_material, self.floaterMaterial]
            })
        self.node.connectattr('position', self.node2, 'position')

    def checkCanControl(self):
        if not self.node.exists():
            return False
        if not self.source_player.is_alive():
            self.dis()
            return False
        return True

    def con(self):
        self.controlled = True
        self.checkPlayerDie()

    def up(self):
        if not self.checkCanControl():
            return
        v = self.node.velocity
        self.node.velocity = (v[0], 5, v[2])

    def upR(self):
        if not self.checkCanControl():
            return
        v = self.node.velocity
        self.node.velocity = (v[0], 0, v[2])

    def down(self):
        if not self.checkCanControl():
            return
        v = self.node.velocity
        self.node.velocity = (v[0], -5, v[2])

    def downR(self):
        if not self.checkCanControl():
            return
        v = self.node.velocity
        self.node.velocity = (v[0], 0, v[2])

    def leftright(self, value):
        if not self.checkCanControl():
            return
        v = self.node.velocity
        self.node.velocity = (5 * value, v[1], v[2])

    def updown(self, value):
        if not self.checkCanControl():
            return
        v = self.node.velocity
        self.node.velocity = (v[0], v[1], -5 * value)

    def dis(self):
        if self.node.exists():
            self.controlled = False
            self.node.velocity = (0, 0, 0)
            self.move()

    def checkPlayerDie(self):
        if not self.controlled:
            return
        if self.source_player is None:
            return
        if self.source_player.is_alive():
            ba.timer(1, self.checkPlayerDie)
            return
        else:
            self.dis()

    def distance(self, x1, y1, z1, x2, y2, z2):
        d = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2))
        return d

    def drop(self):
        try:
            np = self.node.position
        except:
            np = (0, 0, 0)
        self.b = Bomb(bomb_type=random.choice(['normal', 'ice', 'sticky', 'impact', 'land_mine', 'tnt']), source_player=self.source_player, position=(np[0], np[1] - 1, np[2]), velocity=(0, -1, 0)).autoretain()
        if self.b.bomb_type in ['impact', 'land_mine']:
            self.b.arm()

    def move(self):
        px = eval(self.px)
        py = eval(self.py)
        pz = eval(self.pz)
        if self.node.exists() and not self.controlled:
            pn = self.node.position
            dist = self.distance(pn[0], pn[1], pn[2], px, py, pz)
            self.node.velocity = ((px - pn[0]) / dist, (py - pn[1]) / dist, (pz - pn[2]) / dist)
            ba.timer(dist-1, ba.WeakCall(self.move), suppress_format_warning=True)

    def handlemessage(self, msg):
        if isinstance(msg, ba.DieMessage):
            self.node.delete()
            self.node2.delete()
            self.controlled = False
        elif isinstance(msg, ba.OutOfBoundsMessage):
            self.handlemessage(ba.DieMessage())
        else:
            super().handlemessage(msg)






def assignFloInputs(clientID: int):
    with ba.Context(_ba.get_foreground_host_activity()):
        activity = ba.getactivity()
        if not hasattr(activity, 'flo') or not activity.flo.node.exists():
            try: activity.flo = Floater(activity.map.get_def_bound_box('map_bounds'))
            except: return #Perhaps using in main-menu/score-screen
        floater = activity.flo
        if floater.controlled:
            ba.screenmessage('Floater is already being controlled', color=(1, 0, 0), transient=True, clients=[clientID])
            return
        ba.screenmessage('You Gained Control Over The Floater!\n Press Bomb to Throw Bombs and Punch to leave!', clients=[clientID], transient=True, color=(0, 1, 1))

        for i in _ba.get_foreground_host_activity().players:
            if i.sessionplayer.inputdevice.client_id == clientID:
                def dis(i, floater):
                    i.actor.node.invincible = False
                    i.resetinput()
                    i.actor.connect_controls_to_player()
                    floater.dis()
                ps = i.actor.node.position
                i.actor.node.invincible = True
                floater.node.position = (ps[0], ps[1] + 1.0, ps[2])
                i.actor.node.hold_node = ba.Node(None)
                i.actor.node.hold_node = floater.node2
                i.actor.connect_controls_to_player()
                i.actor.disconnect_controls_from_player()
                i.resetinput()
                floater.source_player = i
                floater.con()
                i.assigninput(InputType.PICK_UP_PRESS, floater.up)
                i.assigninput(InputType.PICK_UP_RELEASE, floater.upR)
                i.assigninput(InputType.JUMP_PRESS, floater.down)
                i.assigninput(InputType.BOMB_PRESS, floater.drop)
                i.assigninput(InputType.PUNCH_PRESS, ba.Call(dis, i, floater))
                i.assigninput(InputType.UP_DOWN, floater.updown)
                i.assigninput(InputType.LEFT_RIGHT, floater.leftright)
