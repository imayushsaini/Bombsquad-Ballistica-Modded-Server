from __future__ import annotations
from typing import TYPE_CHECKING

import ba,_ba
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, List, Dict

class mapdefs:
    points = {}
    # noinspection PyDictCreation
    boxes = {}
    boxes['area_of_interest_bounds'] = (0.0, 1.185751251, 0.4326226188) + (
        0.0, 0.0, 0.0) + (45.8180273, 11.57249038, 22.89134176)
    boxes['edge_box'] = (-0.103873591, 0.4133341891, 0.4294651013) + (
        0.0, 0.0, 0.0) + (22.48295719, 1.290242794, 8.990252454)
    points['ffa_spawn1'] = (-0.08015551329, 0.02275111462,
                            -4.373674593) + (8.895057015, 1.0, 0.444350722)
    points['ffa_spawn2'] = (-0.08015551329, 0.02275111462,
                            4.076288941) + (8.895057015, 1.0, 0.444350722)
    points['flag1'] = (-10.99027878, 0.05744967453, 0.1095578275)
    points['flag2'] = (11.01486398, 0.03986567039, 0.1095578275)
    points['flag_default'] = (-0.1001374046, 0.04180340146, 0.1095578275)
    boxes['goal1'] = (16.22454533, 1.0,
                    -1.6087926362) + (0.0, 0.0, 0.0) + (1.6, 4.0, 6.17466313)
    boxes['goal2'] = (-16.25961605, 1.0,
                    -1.6097860203) + (0.0, 0.0, 0.0) + (1.6, 4.0, 6.11856424)
    boxes['map_bounds'] = (0.0, 1.185751251, 0.4326226188) + (0.0, 0.0, 0.0) + (
        42.09506485, 22.81173179, 29.76723155)
    points['powerup_spawn1'] = (8.414681236, 0.9515026107, -5.037912441)
    points['powerup_spawn2'] = (-8.555402285, 0.9515026107, -5.037912441)
    points['powerup_spawn3'] = (5.414681236, 0.9515026107, 5.148223181)
    points['powerup_spawn4'] = (-5.737266365, 0.9515026107, 5.148223181)
    points['spawn1'] = (-10.03866341, 0.02275111462, 0.0) + (0.5, 1.0, 4.0)
    points['spawn2'] = (9.823107149, 0.01092306765, 0.0) + (0.5, 1.0, 4.0)
    points['tnt1'] = (-0.08421587483, 0.9515026107, -0.7762602271)
class SoccerStadiumPro(ba.Map):
    """Stadium map for football games."""
    defs = mapdefs

    name = 'Soccer Stadium Pro'

    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'football', 'team_flag', 'keep_away']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'footballStadiumPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'model': ba.getmodel('footballStadium'),
            'vr_fill_model': ba.getmodel('footballStadiumVRFill'),
            'collide_model': ba.getcollidemodel('footballStadiumCollide'),
            'tex': ba.gettexture('footballStadium')
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()

        # self.node = ba.newnode(
        #     'terrain',
        #     delegate=self,
        #     attrs={
        #         'model': self.preloaddata['model'],
        #         'collide_model': self.preloaddata['collide_model'],
        #         'color_texture': self.preloaddata['tex'],
        #         'materials': [shared.footing_material]
        #     })
        ba.newnode('terrain',
                   attrs={
                       'model': self.preloaddata['vr_fill_model'],
                       'lighting': False,
                       'background': True,
                       'color_texture': self.preloaddata['tex']
                   })

        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.3, 1.2, 1.0)
        gnode.ambient_color = (1.3, 1.2, 1.0)
        gnode.vignette_outer = (0.57, 0.57, 0.57)

        gnode.vignette_inner = (0.9, 0.9, 0.9)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5
        # gnode.area_of_interest_bounds=(-20,-2,-10,54,2,3)
        self.extend()

    def is_point_near_edge(self,
                           point: ba.Vec3,
                           running: bool = False) -> bool:
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5

    def extend(self):

        shared = SharedObjects.get()
        self.mat = ba.Material()
        self._real_wall_material=ba.Material()

        self._real_wall_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))
        self.mat.add_actions(

            actions=( ('modify_part_collision','physical',False),
                      ('modify_part_collision','collide',False))
            )
        fakemat=ba.Material()
        fakemat.add_actions(

            actions=( ('modify_part_collision','physical',False),
                      ('modify_part_collision','collide',False))
            )
        # map
        pos=(0,0.1,-2)
        self.main_ground=ba.newnode('region',attrs={'position': pos,'scale': (54,0.001,28),'type': 'box','materials': [self._real_wall_material,shared.footing_material]})
        self.node_map = ba.newnode('prop',
                                    owner=self.main_ground,
                                    attrs={
                                    'model':self.preloaddata['model'],
                                    'light_model':ba.getmodel('powerupSimple'),
                                    'position':(0,7,0),
                                    'body':'puck',
                                    'shadow_size':0.0,
                                    'velocity':(0,0,0),
                                    'color_texture':self.preloaddata['tex'],

                                    'reflection_scale':[1.5],
                                    'materials':[self.mat,shared.footing_material],
                                    'model_scale':1.6,
                                    'body_scale':1.7,

                                    'density':9000000000
                                    })
        mnode = ba.newnode('math',
                               owner=self.main_ground,
                               attrs={
                                   'input1': (0, 0.1, 0),
                                   'operation': 'add'
                               })
        self.node_map.changerotation(0,0,0)
        self.main_ground.connectattr('position', mnode, 'input2')
        mnode.connectattr('output', self.node_map, 'position')
        self.main_wall_top=ba.newnode('region',attrs={'position': (-4.30,0.1,-10.8),'scale': (54,20,0.1),'type': 'box','materials': [self._real_wall_material,shared.footing_material]})
        self.main_wall_left=ba.newnode('region',attrs={'position': (-21.30,0.1,-4.8),'scale': (1,20,34),'type': 'box','materials': [self._real_wall_material,shared.footing_material]})
        self.main_wall_right=ba.newnode('region',attrs={'position': (21.30,0.1,-4.8),'scale': (1,20,34),'type': 'box','materials': [self._real_wall_material,shared.footing_material]})
        self.main_wall_bottom=ba.newnode('region',attrs={'position': (-4.30,0.1,6.8),'scale': (54,20,0.1),'type': 'box','materials': [self._real_wall_material,shared.footing_material]})

        # goal posts
        pos=(0.0, 3.504164695739746, -1.6)
        self.ud_1_r=ba.newnode('region',attrs={'position': pos,'scale': (2,1,2),'type': 'box','materials': [fakemat ]})

        self.node = ba.newnode('prop',
                                    owner=self.ud_1_r,
                                    attrs={
                                    'model':ba.getmodel('hockeyStadiumOuter'),
                                    'light_model':ba.getmodel('powerupSimple'),
                                    'position':(2,7,2),
                                    'body':'puck',
                                    'shadow_size':0.0,
                                    'velocity':(0,0,0),
                                    'color_texture':ba.gettexture('hockeyStadium'),

                                    'reflection_scale':[1.5],
                                    'materials':[self.mat,shared.footing_material],
                                    'model_scale':1.9,
                                    'body_scale':1.9,

                                    'density':9000000000
                                    })
        mnode = ba.newnode('math',
                               owner=self.ud_1_r,
                               attrs={
                                   'input1': (0, -3.4, 0),
                                   'operation': 'add'
                               })
        self.node.changerotation(0,0,0)
        self.ud_1_r.connectattr('position', mnode, 'input2')
        mnode.connectattr('output', self.node, 'position')

        # # // goal post collide model
        pos=(16.88630542755127, 0.3009839951992035, -5.2)
        self.gp_upper_r=ba.newnode('region',attrs={'position': pos,'scale': (3.5,6.5,0.4),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        pos= (16.88630542755127, 0.4209839951992035, 1.83331298828125)
        self.gp_lower_r=ba.newnode('region',attrs={'position': pos,'scale': (3.5,6.5,0.4),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        # roof
        pos=(16.88630542755127, 3.6009839951992035, -1.63331298828125)
        self.gp_roof_r=ba.newnode('region',attrs={'position': pos,'scale': (3.2,0.1,7.2),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})

        # back side
        pos=(18.4630542755127, 0.5009839951992035, -2.0)
        self.gp_back_r=ba.newnode('region',attrs={'position': pos,'scale': (0.2,6,6.7),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})

        # Left =============================================================================
        pos=(-16.85874137878418, 0.3002381920814514, -5.2)
        self.gp_upper_l=ba.newnode('region',attrs={'position': pos,'scale': (3.5,6.5,0.4),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        pos=(-16.8830542755127, 0.4209839951992035, 1.83331298828125)
        self.gp_lower_l=ba.newnode('region',attrs={'position': pos,'scale': (3.5,6.5,0.4),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})

        # roof
        pos=(-16.88630542755127, 3.6009839951992035, -1.63331298828125)
        self.gp_roof_l=ba.newnode('region',attrs={'position': pos,'scale': (3.2,0.1,7.2),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})

        # back side
        pos=(-18.4630542755127, 0.5009839951992035, -2.0)
        self.gp_back_l=ba.newnode('region',attrs={'position': pos,'scale': (0.2,6,6.7),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})

ba._map.register_map(SoccerStadiumPro)
