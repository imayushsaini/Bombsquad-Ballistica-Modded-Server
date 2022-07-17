
import ba,_ba
from bastd.gameutils import SharedObjects

from typing import Any, Sequence, Optional, List, Dict, Type, Type , Union, Any, Literal

a=0.0
class Pointzz:
	points, boxes = {}, {}
	points['ffa_spawn1'] = (-0.08016, 0.02275, -4.37367) + (8.89506, 0.05, 0.44435)
	points['ffa_spawn2'] = (-0.08016, 0.02275, 4.07629) + (8.89506, 0.05, 0.44435)
	points['flag1'] = (-10.72073, 0.06537, 0.14648)
	points['flag2'] = (10.7587, 0.04779, 0.14648)
	points['flag_default'] = (-0.10014, 0.0418, 0.10956)
	points['powerup_spawn1'] = (500000000.41468, 50000.9515, -500000.03791)
	points['powerup_spawn2'] = (-500000.5554, 500000.9515, -500000.03791)
	points['powerup_spawn3'] = (500000.41468, 50000.9515, 5000.14822)
	points['powerup_spawn4'] = (-50000.73727, 50000.9515, 500.14822)
	points['spawn1'] = (-8.03866, 0.02275, 0.0) + (0.5, 0.05, 4.0)
	points['spawn2'] = (8.82311, 0.01092, 0.0) + (0.5, 0.05, 4.0)
	boxes['area_of_interest_bounds'] = (0.0, 1.18575, 0.43262) + (0, 0, 0) + (29.81803, 11.57249, 18.89134)
	boxes['tnt1'] = (-0.10387, 0.41333, 0.42947) + (0, 0, 0) + (22.48296, 1.29024, 8.99025)
	boxes['goal1'] = (10,0.001,8)
	boxes['goal2'] = (10,0.001,8)
	boxes['map_bounds'] = (0.0, 1.185751251, 0.4326226188) + (0.0, 0.0, 0.0) + (
    42.09506485, 22.81173179, 29.76723155)

class PointzzforH:
    points, boxes = {}, {}
    boxes['area_of_interest_bounds'] = (0.0, 0.7956858119, 0.0) + (
    0.0, 0.0, 0.0) + (30.80223883, 0.5961646365, 13.88431707)
    points['ffa_spawn1'] = (-0.001925625146, 0.02305323209,
                        -3.81971842) + (7.828121539, 1.0, 0.1588021252)
    points['ffa_spawn2'] = (-0.001925625146, 0.02305323209,
                        3.560115735) + (7.828121539, 1.0, 0.05859841271)
    points['flag1'] = (-11.21689747, 0.09527878981, -0.07659307272)
    points['flag2'] = (11.08204909, 0.04119542459, -0.07659307272)
    points['flag_default'] = (-0.01690735171, 0.06139940044, -0.07659307272)
    boxes['goal1'] = (10,0.001,8)
    boxes['goal2'] = (10,0.001,8)
    boxes['map_bounds'] = (0.0, 0.7956858119, -0.4689020853) + (0.0, 0.0, 0.0) + (
    35.16182389, 12.18696164, 21.52869693)
    points['powerup_spawn1'] = (-3.654355317, 1.080990833, -4.765886164)
    points['powerup_spawn2'] = (-3.654355317, 1.080990833, 4.599802158)
    points['powerup_spawn3'] = (2.881071011, 1.080990833, -4.765886164)
    points['powerup_spawn4'] = (2.881071011, 1.080990833, 4.599802158)
    points['spawn1'] = (-6.835352227, 0.02305323209, 0.0) + (1.0, 1.0, 3.0)
    points['spawn2'] = (6.857415055, 0.03938567998, 0.0) + (1.0, 1.0, 3.0)
    points['tnt1'] = (-0.05791962398, 1.080990833, -4.765886164)

class VolleyBallMap(ba.Map):
    defs = Pointzz
    name = "Open Field"

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return []

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'footballStadiumPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('footballStadium'),
            'vr_fill_model': ba.getmodel('footballStadiumVRFill'),
            'collide_model': ba.getcollidemodel('footballStadiumCollide'),
            'tex': ba.gettexture('footballStadium')
        }
        return data
        
    def __init__(self):
        super().__init__()
        shared = SharedObjects.get()

    ## Hey Quasi thx for looping these xD ##
        
        
        
        x = -5
        while x<5:
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,0,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,.25,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,.5,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,.75,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,1,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            x = x + 0.5
        
        
        
        
        
        
        
        
        
        y = -1
        while y>-11:
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(y,0.01,4),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(y,0.01,-4),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-y,0.01,4),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-y,0.01,-4),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            y-=1
                    
                    
                    
        z = 0
        while z<5:
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(11,0.01,z),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(11,0.01,-z),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-11,0.01,z),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-11,0.01,-z),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            z+=1
                    
                    
        
        self.node = ba.newnode(
            'terrain',
            delegate=self,
            attrs={
                'model': self.preloaddata['model'],
                'collide_model': self.preloaddata['collide_model'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material]
            })
        ba.newnode('terrain',
                   attrs={
                       'model': self.preloaddata['vr_fill_model'],
                       'lighting': False,
                       'vr_only': True,
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

    def is_point_near_edge(self,
                           point: ba.Vec3,
                           running: bool = False) -> bool:
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5

class VolleyBallMapH(ba.Map):
    """Stadium map used for ice hockey games."""

    defs = PointzzforH
    name = 'Closed Arena'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return []

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'hockeyStadiumPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'models': (ba.getmodel('hockeyStadiumOuter'),
                       ba.getmodel('hockeyStadiumInner')),
            'vr_fill_model': ba.getmodel('footballStadiumVRFill'),
            'collide_model': ba.getcollidemodel('hockeyStadiumCollide'),
            'tex': ba.gettexture('hockeyStadium'),
        }
        mat = ba.Material()
        mat.add_actions(actions=('modify_part_collision', 'friction', 0.01))
        data['ice_material'] = mat
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()

    ## Hey Quasi thx for looping these xD ##
        
        
        x = -5
        while x<5:
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,0,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,.25,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,.5,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,.75,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(0,1,x),
                        'color':(1,1,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            x = x + 0.5
        
        
        
        
        
        
        
        
        
        y = -1
        while y>-11:
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(y,0.01,4),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(y,0.01,-4),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-y,0.01,4),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-y,0.01,-4),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            y-=1
                    
                    
                    
        z = 0
        while z<5:
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(11,0.01,z),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(11,0.01,-z),
                    'color':(1,0,0),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-11,0.01,z),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            self.zone = ba.newnode('locator',attrs={'shape':'circle','position':(-11,0.01,-z),
                    'color':(0,0,1),'opacity':1,'draw_beauty':True,'additive':False,'size':[0.40]})
            z+=1
                    
                    
                    
        self.node = ba.newnode('terrain',
                               delegate=self,
                               attrs={
                                   'model':
                                       None,
                                   'collide_model':
                                       ba.getcollidemodel('footballStadiumCollide'), ## we dont want Goalposts...
                                   'color_texture':
                                       self.preloaddata['tex'],
                                   'materials': [
                                       shared.footing_material]
                               })
        ba.newnode('terrain',
                   attrs={
                       'model': self.preloaddata['vr_fill_model'],
                       'vr_only': True,
                       'lighting': False,
                       'background': True,
                   })
        mats = [shared.footing_material]
        self.floor = ba.newnode('terrain',
                                attrs={
                                    'model': self.preloaddata['models'][1],
                                    'color_texture': self.preloaddata['tex'],
                                    'opacity': 0.92,
                                    'opacity_in_low_or_medium_quality': 1.0,
                                    'materials': mats,
                                    'color': (0.4,0.9,0)
                                })

        self.background = ba.newnode(
            'terrain',
            attrs={
                'model': ba.getmodel('natureBackground'),
                'lighting': False,
                'background': True,
                'color': (0.5,0.30,0.4)
            })

        gnode = ba.getactivity().globalsnode
        gnode.floor_reflection = True
        gnode.debris_friction = 0.3
        gnode.debris_kill_height = -0.3
        gnode.tint = (1.2, 1.3, 1.33)
        gnode.ambient_color = (1.15, 1.25, 1.6)
        gnode.vignette_outer = (0.66, 0.67, 0.73)
        gnode.vignette_inner = (0.93, 0.93, 0.95)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5
        #self.is_hockey = True


## Plugin only for our dirty map UwU ##

ba._map.register_map(VolleyBallMap)
ba._map.register_map(VolleyBallMapH)
