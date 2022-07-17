import ba
from bastd.gameutils import SharedObjects
from bastd.actor import playerspaz as ps
from bastd import maps


from typing import Any, Sequence, Dict, Type, List, Optional, Union

class BasketMap(maps.FootballStadium):
    name = 'BasketBall Stadium'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return []

    def __init__(self) -> None:
        super().__init__()
        
        gnode = ba.getactivity().globalsnode
        gnode.tint = [(0.806, 0.8, 1.0476), (1.3, 1.2, 1.0)][0]
        gnode.ambient_color = (1.3, 1.2, 1.0)
        gnode.vignette_outer = (0.57, 0.57, 0.57)
        gnode.vignette_inner = (0.9, 0.9, 0.9)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5

class BasketMapV2(maps.HockeyStadium):
    name = 'BasketBall Stadium V2'

    def __init__(self) -> None:
        super().__init__()
        
        shared = SharedObjects.get()    
        self.node.materials = [shared.footing_material]
        self.node.collide_model = ba.getcollidemodel('footballStadiumCollide')
        self.node.model = None
        self.stands.model = None
        self.floor.reflection = 'soft'
        self.floor.reflection_scale = [1.6]
        self.floor.color = (1.1, 0.05, 0.8)
        
        self.background = ba.newnode('terrain',
            attrs={'model': ba.getmodel('thePadBG'),
                   'lighting': False,
                   'background': True,
                   'color': (1.0, 0.2, 1.0),
                   'color_texture': ba.gettexture('menuBG')})

        gnode = ba.getactivity().globalsnode
        gnode.floor_reflection = True
        gnode.debris_friction = 0.3
        gnode.debris_kill_height = -0.3
        gnode.tint = [(1.2, 1.3, 1.33), (0.7, 0.9, 1.0)][1]
        gnode.ambient_color = (1.15, 1.25, 1.6)
        gnode.vignette_outer = (0.66, 0.67, 0.73)
        gnode.vignette_inner = (0.93, 0.93, 0.95)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5
        self.is_hockey = False

        ##################
        self.collision = ba.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))
        
        self.regions: List[ba.Node] = [
            ba.newnode('region',
                attrs={'position': (12.676897048950195, 0.2997918128967285, 5.583303928375244),
                       'scale': (1.01, 12, 28),
                       'type': 'box',
                       'materials': [self.collision]}),
                       
            ba.newnode('region',
                attrs={'position': (11.871315956115723, 0.29975247383117676, 5.711406707763672),
                       'scale': (50, 12, 0.9),
                       'type': 'box',
                       'materials': [self.collision]}),
                       
            ba.newnode('region',
                attrs={'position': (-12.776557922363281, 0.30036890506744385, 4.96237850189209),
                       'scale': (1.01, 12, 28),
                       'type': 'box',
                       'materials': [self.collision]}),
            ]

ba._map.register_map(BasketMap)
ba._map.register_map(BasketMapV2)