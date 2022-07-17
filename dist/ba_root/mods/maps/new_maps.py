## DECODED FOR MODIFICATIONS OF MAP POINTS ##
## DON'T SHARE ##


# ba_meta require api 6

#Mod by Froshlee14
#Updated by SEBASTIAN2059
from __future__ import annotations

from typing import TYPE_CHECKING


import ba
import _ba
import random
from bastd.gameutils import SharedObjects
from bastd.actor.powerupbox import PowerupBox, PowerupBoxFactory

if TYPE_CHECKING:
    from typing import Any, List, Dict


class mega_mine_defs:
    boxes = {}
    points = {}
    boxes['area_of_interest_bounds'] = (0, 1, 0) + (0, 0, 0) + (0, 0, 0)
    boxes['map_bounds'] = (0, 0, 0) + (0, 0, 0) + (20, 20, 20)
    points['ffa_spawn1'] = (3,2,-2)
    points['ffa_spawn2'] = (-3,2,-2)
    points['ffa_spawn3'] = (3,2,2)
    points['ffa_Spawn4'] = (-3,2,2)
    points['powerup_spawn1'] = (-2.8,3,0)
    points['powerup_spawn2'] = (2.8,3,0)
    points['powerup_spawn3'] = (0,3,-2.8)
    points['powerup_spawn4'] = (0,3,2.8)
    

class MegaMine(ba.Map):
    """A giant mine!"""

    defs = mega_mine_defs

    name = 'Mega Mine'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'landMine'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('landMine'),
            'tex': ba.gettexture('landMine'),
            'bgtex': ba.gettexture('menuBG'),
            'bgmodel': ba.getmodel('thePadBG'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={'position':(0,1,0),
                                      'velocity':(0,0,0),
                                      'model':self.preloaddata['model'],
                                      'size':[25,13,4],
                                      'model_scale':14.6,
                                      'body_scale':14.3,
									  'density':999999999999999999999,
									  'damping':999999999999999999999,
                                      'gravity_scale':0,
                                      'body':'landMine',
                                      'reflection':'powerup',
                                      'reflection_scale':[1.0],									  
                                      'color_texture':self.preloaddata['tex'],
                                      'materials':[shared.footing_material]})
                                      
        
        self.background = ba.newnode('terrain',
                                    attrs={
                                    'model': self.preloaddata['bgmodel'],
                                    'lighting': False,
                                    'background': True,
                                    'color_texture': self.preloaddata['bgtex']
            })
    
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.2, 1.17, 1.1)
        gnode.ambient_color = (1.2, 1.17, 1.1)
        gnode.vignette_outer = (0.6, 0.6, 0.64)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
        

class powerups_defs:
    boxes = {}
    points = {}
    boxes['area_of_interest_bounds'] = (0, -2, -2) + (0, 0, 0) + (0, 15, 0)
    boxes['map_bounds'] = (0, 1, 0) + (0, -3, 0) + (50, 30, 50)
    points['ffa_spawn1'] = (3,2,-1.5)
    points['ffa_spawn2'] = (-3,2,-1.5)
    points['ffa_spawn3'] = (3,2,1.5)
    points['ffa_spawn4'] = (-3,2,1.5)
    points['powerup_spawn1'] = (-2,3,0)
    points['powerup_spawn2'] = (2,3,0)


class PowerupMap(ba.Map):
    """A Powerups!"""

    defs = powerups_defs

    name = 'Powerups'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'powerupShield'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'bgtex': ba.gettexture('menuBG'),
            'bgmodel': ba.getmodel('thePadBG'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        Box(position=(-3,-2,0),texture='powerupShield')	
        Box(position=(3,-2,0),texture='powerupSpeed')	
        Box(position=(-3,-7,0),texture='powerupHealth')	
        Box(position=(3,-7,0),texture='powerupCurse')
        
        self._new_region_material = ba.Material()
        self._new_region_material.add_actions(
            conditions=('they_have_material', shared.object_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False)))
                      
        self._region = ba.newnode('region',
                                        attrs={
                                            'position': (2,-10.5,0),
                                            'scale': (18, 0, 12),
                                            'type': 'box',
                                            'materials': [self._new_region_material, shared.death_material]
                                        })
        # a = ba.newnode('locator',attrs={'shape':'box','position':(0,-10.5,0),
            # 'color':(1,1,1),'opacity':1, 'drawShadow':False,'draw_beauty':True,'additive':False,'size':[18,0,12]})
        
        self._call_powerups = ba.timer(0.1,ba.Call(self.spawn_powerup),repeat=True)
        
        self.background = ba.newnode('terrain',
                                    attrs={
                                    'model': self.preloaddata['bgmodel'],
                                    'lighting': False,
                                    'background': True,
                                    'color_texture': self.preloaddata['bgtex']
            })
            
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.0,1.0,1.0)
        gnode.ambient_color = (1.1,1.1,1.0)
        gnode.vignette_outer = (0.7,0.65,0.75)
        gnode.vignette_inner = (0.95,0.95,0.93)
        
    def spawn_powerup(self):
        pos = (-15+random.random()*30,-13,-15+random.random()*30)
        if not random.random() > 0.9997:
            p = PowerupBox(position=pos,poweruptype=PowerupBoxFactory().get_random_powerup_type(),expire=False).autoretain()
            p.node.gravity_scale = -0.1
                
    
class Box(ba.Actor):
    def __init__(self,position=(0,0,0),texture=None):
        ba.Actor.__init__(self)
        shared = SharedObjects.get()
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={'position':position,
                                      'velocity':(0,0,0),
                                      'model':ba.getmodel('powerup'),
                                      'model_scale':8.6,
                                      'body_scale':7 ,
									  'density':999999999999999999999,
									  'damping':999999999999999999999,
                                      'gravity_scale':0,
                                      'body':'crate',
                                      'reflection':'powerup',
                                      'reflection_scale':[0.3],									  
                                      'color_texture':ba.gettexture(texture),
                                      'materials':[shared.footing_material]})



class darkness_defs:
    boxes = {}
    points = {}
    boxes['area_of_interest_bounds'] = (0, 1, 0) + (0, 0, 0) + (17, 0, 0)
    boxes['map_bounds'] = (0, 0, 0) + (0, 0, 0) + (10.5, 20, 10.5)
    points['flag_default'] = (0,1,0)
    points['flag1'] = (-4.7,1,0)
    points['spawn1'] = (-4.7,1,0)
    points['flag2'] = (4.7,1,0)
    points['spawn2'] = (4.7,1,0)
    points['ffa_spawn1'] = (0,1,3)
    points['ffa_spawn2'] = (0,1,-3)
    points['ffa_spawn3'] = (3,1,0)
    points['ffa_spawn4'] = (-3,1,0)
    points['powerup_spawn1'] = (-3.5,2,-3.5)
    points['powerup_spawn2'] = (-3.4,2,3.5)
    points['powerup_spawn3'] = (3.5,2,-3.5)
    points['powerup_spawn4'] = (3.5,2,3.5)

class Dark(ba.Map):
    defs = darkness_defs
    name = 'Dark world'
    
    
    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee','king_of_the_hill','keep_away','team_flag']
    
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'bg'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('footballStadium'),
            'collide_model': ba.getcollidemodel('footballStadiumCollide'),
            'tex': ba.gettexture('bg'),
        }
        return data
        
    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = ba.newnode('terrain', delegate=self,
                                attrs={
                                'model':self.preloaddata['model'],
                                'collide_model':self.preloaddata['collide_model'],
                                'color_texture':self.preloaddata['tex'], 
                                'materials':[shared.footing_material]})
                    
        self.zone = ba.newnode('locator',
                                    attrs={'shape':'circleOutline','position':(0,0,0),
                                    'color':(1,1,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[11]})
                    
        gnode = ba.getactivity().globalsnode
        gnode.tint = (0.8,0.8,1)
        gnode.ambient_color = (1.15,1.25,1.6)
        gnode.vignette_outer = (0.66,0.67,0.73)
        gnode.vignette_inner = (0.93,0.93,0.95)
        
        

class SuperTntMap(ba.Map):
    """A giant mine!"""

    defs = powerups_defs

    name = 'Super TNT'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'tnt'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('powerupSimple'),
            'tex': ba.gettexture('tnt'),
            'bgtex': ba.gettexture('menuBG'),
            'bgmodel': ba.getmodel('thePadBG'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={'position':(0,-3.2,0),
                                      'velocity':(0,0,0),
                                      'model':self.preloaddata['model'],
                                      'model_scale':18,
                                      'body_scale':15,
									  'density':999999999999999999999,
									  'damping':999999999999999999999,
                                      'gravity_scale':0,
                                      'body':'crate',								  
                                      'color_texture':self.preloaddata['tex'],
                                      'materials':[shared.footing_material]})
                                      
        
        self.background = ba.newnode('terrain',
                                    attrs={
                                    'model': self.preloaddata['bgmodel'],
                                    'lighting': False,
                                    'background': True,
                                    'color_texture': self.preloaddata['bgtex']
            })
    
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.0, 1.0, 1.0)
        gnode.ambient_color = (1.1, 1.1, 1.0)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)



class GreenScreenMap(ba.Map):
    """A giant mine!"""

    from bastd.mapdata import doom_shroom as defs

    name = 'Green Screen'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return ['melee','keep_away','team_flag']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'eggTex2'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('doomShroomLevel'),
            'collide_model': ba.getcollidemodel('doomShroomLevelCollide'),
            'tex': ba.gettexture('white'),
            'bgtex': ba.gettexture('doomShroomBGColor'),
            'bgmodel': ba.getmodel('doomShroomBG'),
            'stem_model': ba.getmodel('doomShroomStem'),
            'collide_bg': ba.getcollidemodel('doomShroomStemCollide'),
        }
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
                'color':(0,1,0),
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material]
            })
        self.background = ba.newnode(
            'terrain',
            attrs={
                'model': self.preloaddata['bgmodel'],
                'lighting': False,
                'color':(0,1,0),
                'background': True,
                'color_texture': self.preloaddata['tex']
            })
        self.stem = ba.newnode('terrain',
                               attrs={
                                   'model': self.preloaddata['stem_model'],
                                   'lighting': False,
                                   'color':(0,1,0),
                                   'color_texture': self.preloaddata['tex']
                               })
        self.bg_collide = ba.newnode(
            'terrain',
            attrs={
                'collide_model': self.preloaddata['collide_bg'],
                'materials': [shared.footing_material, shared.death_material]
            })
            
        gnode = ba.getactivity().globalsnode
        gnode.tint = (0.82, 1.10, 1.15)
        gnode.ambient_color = (0.9, 1.3, 1.1)
        gnode.shadow_ortho = False
        gnode.vignette_outer = (0.76, 0.76, 0.76)
        gnode.vignette_inner = (0.95, 0.95, 0.99)

##### List containing the maps to be registered #####
MAPS = [MegaMine,PowerupMap,Dark,SuperTntMap,GreenScreenMap]

def register_maps():
    for new_map in MAPS:
        ba._map.register_map(new_map)


register_maps()