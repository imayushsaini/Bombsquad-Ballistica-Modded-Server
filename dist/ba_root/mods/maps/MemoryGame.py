import ba
from bastd.gameutils import SharedObjects

from typing import Any, Sequence, Optional, List, Dict, Type, Type , Union, Any, Literal

class MGdefs():
    points = {}
    boxes = {}
    points['flag_default'] = (0.17358, 3.75764, 1.99124)
    boxes['area_of_interest_bounds'] = (0.3544110667, 4.493562578, -2.518391331) + (0.0, 0.0, 0.0) + (16.64754831, 8.06138989, 18.5029888)
    boxes['map_bounds'] = (0.2608783669, 4.899663734, -3.543675157) + (0.0, 0.0, 0.0) + (29.23565494, 14.19991443, 29.92689344)

class MGmap(ba.Map):
    defs = MGdefs()
    name = 'Sky Tiles'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return []

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'achievementOffYouGo'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'bgtex': ba.gettexture('menuBG'),
            'bgmodel': ba.getmodel('thePadBG')
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = ba.newnode(
            'terrain',
            attrs={
                'model': self.preloaddata['bgmodel'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex']
            })
        gnode = ba.getactivity().globalsnode
        gnode.tint = (1.3, 1.2, 1.0)
        gnode.ambient_color = (1.3, 1.2, 1.0)
        gnode.vignette_outer = (0.57, 0.57, 0.57)
        gnode.vignette_inner = (0.9, 0.9, 0.9)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5




ba._map.register_map(MGmap)