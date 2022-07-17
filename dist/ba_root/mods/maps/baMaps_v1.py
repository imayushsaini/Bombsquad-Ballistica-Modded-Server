# ba_meta require api 6

#  Plugin SEBASTIAN2059 - Zacker Tz
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  - Maps:                                                     - 
#  - Neo Zone         - by Zacker Tz || Zacker#5505            -
#  - Big H map        - by SEBASTIAN2059 || SEBASTIAN2059#5751 -
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from __future__ import annotations

from typing import TYPE_CHECKING

from bastd.maps import *
import ba
import _ba
import base64
from ba import _map
import random

if TYPE_CHECKING:
    from typing import Any, List, Dict

#Map by Zacker Tz 
class neo_defs():
    boxes = {}
    points = {}
    boxes['area_of_interest_bounds'] = (0, 4, 0) + (0, 0, 0) + (50, 10, 20)
    boxes['edge_box'] = (0, 4, 0) + (0.0, 0.0, 0.0) + (40, 2, 10)
    boxes['map_bounds'] = (0, 4, 0) + (0, 0, 0) + (28, 10, 28)
    points['ffa_spawn1'] = (-10,3.17,0) + (1.0,0.1,1.0)
    points['ffa_spawn2'] = (10,3.17,0) + (1.0,0.1,1.0)
    points['ffa_spawn3'] = (-5.25,3.17,-1.75) + (0.5,0.1,0.5) 
    points['ffa_Spawn4'] = (5.25,3.17,-1.75) + (0.5,0.1,0.5) 
    points['spawn1'] = (-11,3.17,0) + (1.0,0.1,1.0)
    points['spawn2'] = (11,3.17,0) + (1.0,0.1,1.0)
    points['flag1'] = (-12.0,3.3,0) + (2.0,0.1,2.0)
    points['flag2'] = (12.0,3.3,0) + (2.0,0.1,2.0)
    points['flag_default'] = (0,3.3,1.75)
    points['powerup_spawn1'] = (-11,4.0,-1.75)
    points['powerup_spawn2'] = (-11,4.0,1.75)
    points['powerup_spawn3'] = (-1.75,4.0,0)
    points['powerup_spawn4'] = (1.75,4.0,0.0)
    points['powerup_spawn5'] = (11,4.0,-1.75)
    points['powerup_spawn6'] = (11,4.0,1.75)
 

class NeoZone(ba.Map):
    """Agent john's former workplace"""

    defs = neo_defs()
    name = 'Neo Zone'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee','king_of_the_hill','keep_away','team_flag']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'rgbStripes'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('landMine'),
            'tex': ba.gettexture('landMine'),
            'bgtex': ba.gettexture('black'),
            'bgmodel': ba.getmodel('thePadBG'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        
        self._collide_with_player=ba.Material()
        self._collide_with_player.add_actions(conditions=('we_are_older_than', 1), actions=(('modify_part_collision', 'collide', True)))
        self.dont_collide=ba.Material()
        self.dont_collide.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', False)))
        
        self._map_model = ba.getmodel('image1x1')
        self._map_model2 = ba.getmodel('tnt')
        self._map_tex = ba.gettexture('powerupIceBombs')
        self._map_tex1 = ba.gettexture('ouyaUButton') 
        
        self.background = ba.newnode('terrain',
                                    attrs={
                                    'model': self.preloaddata['bgmodel'],
                                    'lighting': False,
                                    'background': True,
                                    'color_texture': self.preloaddata['bgtex']
            })

        locations = [(7.0,0.0,0),(5.25,0.0,0),(5.25,0.0,-1.75),
                (3.5,0.0,-1.75),(1.75,0.0,-1.75),(1.75,0.0,0),
                (1.75,0.0,1.75),
                (0,0.0,1.75),
                (-7.0,0.0,0),(-5.25,0.0,0),(-5.25,3.17,-1.75),
                (-3.5,0.0,-1.75),(-1.75,0.0,-1.75),(-1.75,0.0,0),
                (-1.75,0.0,1.75)]
        num = 0
        
        for pos in locations:
            color = (0,1,0) if num in [0,1,5,8,9,13] else (0,0,1) if num in [6,7,14] else (1,0,0) if num in [2,3,4,10,11,12] else (1,1,1)
            self.decor = ba.newnode('prop',
                    attrs={'body': 'puck',
                           'position': (pos[0],3.17,pos[2]),
                           'model': self._map_model,
                           'model_scale': 1.7,
                           'body_scale': 0.1,
                           'shadow_size': 0.0,
                           'gravity_scale':0.0,
                           'color_texture': self._map_tex1,
                           'reflection': 'soft',
                           'reflection_scale': [0.5],
                           'is_area_of_interest': True,
                           'materials': [self.dont_collide]})
            self.region = ba.newnode('region',attrs={
                                        'position': (pos[0],2.3,pos[2]),
                                        'scale': (1.9,1.9,1.9),
                                        'type': 'box',
                                        'materials': (self._collide_with_player, shared.footing_material)})
            self.zone = ba.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(pos[0],2.3,pos[2]),
                                    'color':color,
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[1.75,1.75,1.75]})
            num += 1
        
        #Sides  
        side_locations = [(-10.5,2.3,0),(10.5,2.3,0)]    
        for pos in side_locations:
            self.big_region = ba.newnode('region',attrs={
                                        'position': pos,
                                        'scale': (5.7,1.9,5.7),
                                        'type': 'box',
                                        'materials': (self._collide_with_player, shared.footing_material)})        
            self.big_zone = ba.newnode('locator',
                                        attrs={'shape':'box',
                                        'position':pos,
                                        'color':(0,1,1.5),
                                        'opacity':1,'draw_beauty':True,'additive':False,'size':[5.25,1.75,5.25]})
             
        exec(base64.b64decode("dCA9IGJhLm5ld25vZGUoJ3RleHQnLAogICAgICAgICAgICAgICBhdHRycz17ICd0ZXh0JzoiTWFwYXMgcG9yOiBTRUJBU1RJQU4yMDU5IHkgWmFja2VyIERDIiwgCiAgICAgICAgJ3NjYWxlJzowLjYsCiAgICAgICAgJ3Bvc2l0aW9uJzooMCwwKSwgCiAgICAgICAgJ29wYWNpdHknOiAwLjQsCiAgICAgICAgJ3NoYWRvdyc6MC41LAogICAgICAgICdmbGF0bmVzcyc6MS4yLAogICAgICAgICdjb2xvcic6KDEsIDEsIDEpLAogICAgICAgICdoX2FsaWduJzonY2VudGVyJywKICAgICAgICAndl9hdHRhY2gnOidib3R0b20nfSk=").decode('UTF-8')) #bubalu           
                                    
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.1, 1.05, 1.17)
        gnode.happy_thoughts_mode = False
        gnode.ambient_color = (1.2, 1.17, 1.1)
        gnode.vignette_outer = (0.9, 0.9, 0.96)
        gnode.vignette_inner = (0.95, 0.95, 0.93)

#Map by Sebastian2059
class c_defs():
    boxes = {}
    points = {}
    boxes['area_of_interest_bounds'] = (0, 4, 0) + (0, 0, 0) + (50, 10, 20)
    boxes['edge_box'] = (0, 4, 0) + (0.0, 0.0, 0.0) + (40, 2, 10)
    boxes['map_bounds'] = (0, 4, 0) + (0, 0, 0) + (28, 10, 28)
    points['ffa_spawn1'] = (-9,0.5,-3) + (1.0,0.1,5.0)
    points['ffa_spawn2'] = (9,0.5,-3) + (1.0,0.1,5.0)
    points['ffa_spawn3'] = (-6,0.5,-6.0) + (2.0,0.1,1.0) 
    points['ffa_Spawn4'] = (6,0.5,0.0) + (2.0,0.1,1.0) 
    points['ffa_spawn5'] = (6,0.5,-6.0) + (2.0,0.1,1.0) 
    points['ffa_Spawn6'] = (-6,0.5,0.0) + (2.0,0.1,1.0) 
    points['spawn1'] = (-9,0.5,-3) + (1.0,0.1,1.0)
    points['spawn2'] = (9,0.5,-3) + (1.0,0.1,1.0)
    points['flag1'] = (-10.0,0.8,-3) + (2.0,0.1,2.0)
    points['flag2'] = (10.0,0.8,-3) + (2.0,0.1,2.0)
    points['flag_default'] = (0,0.8,-3.0)
    points['powerup_spawn1'] = (-9,1.0,-8)
    points['powerup_spawn2'] = (-9,1.0,3)
    points['powerup_spawn3'] = (-1.5,1.0,-8.25)
    points['powerup_spawn4'] = (1.5,1.0,-8.25)
    points['powerup_spawn5'] = (-1.5,1.0,2.25)
    points['powerup_spawn6'] = (1.5,1.0,2.25)
    points['powerup_spawn7'] = (9,1.0,-8)
    points['powerup_spawn8'] = (9,1.0,3)
    
    points['race_mine1'] = (-1.5, 0.7, -0.7)
    points['race_mine2'] = (-1.5, 0.7, 0.7)
    points['race_mine3'] = (-4.5, 0.7, 0.0)
    points['race_mine4'] = (4.5, 0.7, 0.0)
    points['race_mine5'] = (4.5, 0.7, -6.0)
    points['race_mine6'] = (-4.5, 0.7, -6.0)
    points['race_mine7'] = (0.0, 0.7, -6.0)
    points['race_mine8'] = (-10.0, 0.7, -4.5)
    points['race_mine9'] = (10.0, 0.7, -4.5)    
    points['race_mine10'] = (10.0, 0.7, -1.5)
    points['race_mine11'] = (-10.0, 0.7, -1.5)
    
    points['race_point1'] = (0.0, 0.5, 0.0) + (0.3, 2.0, 1.5)
    points['race_point2'] = (3.5, 0.5, 0.0) + (0.3, 2.0, 1.5)
    points['race_point3'] = (7.0, 0.5, 0.0) + (0.3, 2.0, 1.5)
    points['race_point4'] = (9.0, 0.5, -2.0) + (1.5, 2.0, 0.3)
    points['race_point5'] = (9.0, 0.5, -4.0) + (1.5, 2.0, 0.3)
    points['race_point6'] = (7.0, 0.5, -6.0) + (0.3, 2.0, 1.5)
    points['race_point7'] = (3.5, 0.5, -6.0) + (0.3, 2.0, 1.5)
    points['race_point8'] = (0.0, 0.5, -6.0) + (0.3, 2.0, 1.5)
    points['race_point9'] = (-3.5, 0.5, -6.0) + (0.3, 2.0, 1.5)
    points['race_point10'] = (-7.0, 0.5, -6.0) + (0.3, 2.0, 1.5)
    points['race_point11'] = (-9.0, 0.5, -2.0) + (1.5, 2.0, 0.3)
    points['race_point12'] = (-9.0, 0.5, -4.0) + (1.5, 2.0, 0.3)
    points['race_point13'] = (-7.0, 0.5, 0.0) + (0.3, 2.0, 1.5)
    points['race_point14'] = (-3.5, 0.5, 0.0) + (0.3, 2.0, 1.5)
 
class CMap(ba.Map):
    """Jack Morgan used to run here"""
    
    defs = c_defs()
    name = 'Big H'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee','king_of_the_hill','keep_away','team_flag','race']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'bigG'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('landMine'),
            'tex': ba.gettexture('landMine'),
            'bgtex': ba.gettexture('black'),
            'bgmodel': ba.getmodel('thePadBG'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        
        self._collide_with_player=ba.Material()
        self._collide_with_player.add_actions(conditions=('we_are_older_than', 1), actions=(('modify_part_collision', 'collide', True)))
        self.dont_collide=ba.Material()
        self.dont_collide.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', False)))
        self.ice_material = ba.Material()
        self.ice_material.add_actions(actions=('modify_part_collision','friction',0.01))
        
        self._map_model = ba.getmodel('image1x1')
        self._map_model2 = ba.getmodel('tnt')
        self._map_tex = ba.gettexture('powerupIceBombs')
        self._map_tex1 = ba.gettexture('circleOutlineNoAlpha') 
        self._map_tex2 = ba.gettexture('black') 
        
        self.background = ba.newnode('terrain',
                                    attrs={
                                    'model': self.preloaddata['bgmodel'],
                                    'lighting': False,
                                    'background': True,
                                    'color_texture': self.preloaddata['bgtex']
            })

        posS = [(0.0,0.05,0)]
        for m_pos in posS:
            self.mv_center = ba.newnode('prop',
                    attrs={'body': 'puck',
                           'position': m_pos,
                           'model': self._map_model,
                           'model_scale': 35,
                           'body_scale': 0.1,
                           'shadow_size': 0.0,
                           'gravity_scale':0.0,
                           'color_texture': self._map_tex2,
                           'reflection': 'soft',
                           'reflection_scale': [0],
                           'is_area_of_interest': True,
                           'materials': [self.dont_collide]})        
        try:
            self._gamemode = ba.getactivity().name
        except Exception:
            print('error')
            pass
        locations = [(-9,0.0,-3.0),(9,0.0,-3.0),(0.0,0.0,0.0),(0.0,0.0,-6.0),(0.0,0.0,-3.0)]
        scales = [[3.0,1.0,14.0],[3.0,1.0,14.0],[15.0,1.0,3.0],[15.0,1.0,3.0],[3.0,1.0,3.0]]
        index = 0
        for pos in locations:
            #
            scale = scales[index]
            ba.newnode('region',attrs={'position': pos,'scale': scale,'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            ba.newnode('locator',attrs={'shape':'box','position':pos,
                'color':(1,1,1),'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':scale})
            index += 1
        
        pos = [-3.0,0.0,-8.25]
        for p in range(10):
            scale = [1.5,1.0,1.5]
            ba.newnode('region',attrs={'position': pos,'scale': scale,'type': 'box','materials': (self._collide_with_player, shared.footing_material)})
            ba.newnode('locator',attrs={'shape':'box','position':pos,
                'color':(1,1,1),'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':scale})
            pos[0] += 1.5
            if p == 4:
                pos[0] = -3.0
                pos[2] = 2.25
        
        if self._gamemode == 'Race':
            ice_locations = [(-8,0.0,0),(8,0.0,0),
                             (-8,0.0,-6),(8,0.0,-6),
                             (-9,0.0,-3),(9,0.0,-3)]

            for pos in ice_locations:
                scale = [3.0,1.025,3.0]
                ba.newnode('region',attrs={'position': pos,'scale': scale,'type': 'box','materials': (self._collide_with_player, shared.footing_material, self.ice_material)})
                ba.newnode('locator',attrs={'shape':'box','position':pos,
                    'color':(0,1,1),'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':scale})
                    
        exec(base64.b64decode("dCA9IGJhLm5ld25vZGUoJ3RleHQnLAogICAgICAgICAgICAgICBhdHRycz17ICd0ZXh0JzoiTWFwYXMgcG9yOiBTRUJBU1RJQU4yMDU5IHkgWmFja2VyIERDIiwgCiAgICAgICAgJ3NjYWxlJzowLjYsCiAgICAgICAgJ3Bvc2l0aW9uJzooMCwwKSwgCiAgICAgICAgJ29wYWNpdHknOiAwLjQsCiAgICAgICAgJ3NoYWRvdyc6MC41LAogICAgICAgICdmbGF0bmVzcyc6MS4yLAogICAgICAgICdjb2xvcic6KDEsIDEsIDEpLAogICAgICAgICdoX2FsaWduJzonY2VudGVyJywKICAgICAgICAndl9hdHRhY2gnOidib3R0b20nfSk=").decode('UTF-8')) #saludo            
                    
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.1, 1.05, 1.17)
        gnode.happy_thoughts_mode = False
        gnode.ambient_color = (1.2, 1.17, 1.1)
        gnode.vignette_outer = (0.9, 0.9, 0.96)
        gnode.vignette_inner = (0.95, 0.95, 0.93)        
        
#List Maps
zk2059 = [NeoZone,CMap]

def register_maps():
    for new_map in zk2059:
        _map.register_map(new_map)
    
# ba_meta export plugin
class Zk2059(ba.Plugin):
    def __init__(self):
        if _ba.env().get("build_number", 0) >= 20258:
            register_maps()
        else:
            print("new_maps.py only runs with BombSquad versions higher than 1.5.29.")
            