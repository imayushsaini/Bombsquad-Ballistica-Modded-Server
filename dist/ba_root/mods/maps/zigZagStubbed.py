
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, List, Dict

class ZigZagStubbed(ba.Map):
    """A very long zig-zaggy map"""

    from bastd.mapdata import zig_zag as defs

    name = 'Zigzag Stubbed'

    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return [
            'melee', 'keep_away', 'team_flag', 'conquest', 'king_of_the_hill'
        ]

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'zigzagPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'model': ba.getmodel('zigZagLevel'),
            'model_bottom': ba.getmodel('zigZagLevelBottom'),
            'model_bg': ba.getmodel('natureBackground'),
            'bg_vr_fill_model': ba.getmodel('natureBackgroundVRFill'),
            'collide_model': ba.getcollidemodel('zigZagLevelCollide'),
            'tex': ba.gettexture('zigZagLevelColor'),
            'model_bg_tex': ba.gettexture('natureBackgroundColor'),
            'collide_bg': ba.getcollidemodel('natureBackgroundCollide'),
            'railing_collide_model': ba.getcollidemodel('zigZagLevelBumper'),
            'bg_material': ba.Material()
        }
        data['bg_material'].add_actions(actions=('modify_part_collision',
                                                 'friction', 10.0))
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = ba.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collide_model': self.preloaddata['collide_model'],
                'model': self.preloaddata['model'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material]
            })
        self.background = ba.newnode(
            'terrain',
            attrs={
                'model': self.preloaddata['model_bg'],
                'lighting': False,
                'color_texture': self.preloaddata['model_bg_tex']
            })
        self.bottom = ba.newnode('terrain',
                                 attrs={
                                     'model': self.preloaddata['model_bottom'],
                                     'lighting': False,
                                     'color_texture': self.preloaddata['tex']
                                 })
        ba.newnode('terrain',
                   attrs={
                       'model': self.preloaddata['bg_vr_fill_model'],
                       'lighting': False,
                       'vr_only': True,
                       'background': True,
                       'color_texture': self.preloaddata['model_bg_tex']
                   })
        self.bg_collide = ba.newnode('terrain',
                                     attrs={
                                         'collide_model':
                                             self.preloaddata['collide_bg'],
                                         'materials': [
                                             shared.footing_material,
                                             self.preloaddata['bg_material'],
                                             shared.death_material
                                         ]
                                     })
        
        self._real_wall_material=ba.Material()

        self._real_wall_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)

            ))
        self._prop_material=ba.Material()

        self._prop_material.add_actions(

            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)

            ))
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.0, 1.15, 1.15)
        gnode.ambient_color = (1.0, 1.15, 1.15)
        gnode.vignette_outer = (0.57, 0.59, 0.63)
        gnode.vignette_inner = (0.97, 0.95, 0.93)
        gnode.vr_camera_offset = (-1.5, 0, 0)
        
        self.create_ramp(-4.5,-2.4)
        self.create_ramp(-4.5,0)

        self.create_ramp(-1.4,-4.7)
        self.create_ramp(-1.4,-2.3)

        self.create_ramp(1.5,-2.4)
        self.create_ramp(1.5,0)

    def create_ramp(self,x,z):
        shared = SharedObjects.get()
        self.ud_1_r=ba.newnode('region',attrs={'position': (x,2.45,z),'scale': (2,1,2.5),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})

        self.floor = ba.newnode('prop',
                                    owner=self.ud_1_r,
                                    attrs={
                                    'model':ba.getmodel('image1x1'),
                                    'light_model':ba.getmodel('powerupSimple'),
                                    'position':(2,7,2),
                                    'body':'puck',
                                    'shadow_size':0.0,
                                    'velocity':(0,0,0),
                                    'color_texture':ba.gettexture('tnt'),
                                    'model_scale':2.45,
                                    'reflection_scale':[.5],
                                    'materials':[ self._prop_material],

                                    'density':9000000000
                                    })
        mnode = ba.newnode('math',
                               owner=self.ud_1_r,
                               attrs={
                                   'input1': (0, 0.6, 0),
                                   'operation': 'add'
                               })



        self.ud_1_r.connectattr('position', mnode, 'input2')
        mnode.connectattr('output', self.floor, 'position')
ba._map.register_map(ZigZagStubbed)