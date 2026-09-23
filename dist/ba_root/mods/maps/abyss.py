
from typing import TYPE_CHECKING

import bascenev1 as bs
from bascenev1._map import register_map

if TYPE_CHECKING:
    from typing import Any


class AbyssMap(bs.Map):
    from bascenev1lib.mapdata import happy_thoughts as defs
    # Add the y-dimension space for players
    defs.boxes['map_bounds'] = (-0.8748348681, 9.212941713, -9.729538885) \
        + (0.0, 0.0, 0.0) \
        + (36.09666006, 26.19950145, 20.89541168)
    name = 'Abyss Unhappy'

    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['abyss']

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'alwaysLandPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('alwaysLandLevel'),
            'bottom_mesh': bs.getmesh('alwaysLandLevelBottom'),
            'bgmesh': bs.getmesh('alwaysLandBG'),
            'collision_mesh': bs.getcollisionmesh('alwaysLandLevelCollide'),
            'tex': bs.gettexture('alwaysLandLevelColor'),
            'bgtex': bs.gettexture('alwaysLandBGColor'),
            'vr_fill_mound_mesh': bs.getmesh('alwaysLandVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound')
        }
        return data

    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        return bs.MusicType.FLYING

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -3.7, 2.5))
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex']
            })
        bs.newnode('terrain',
                   attrs={
                       'mesh': self.preloaddata['vr_fill_mound_mesh'],
                       'lighting': False,
                       'vr_only': True,
                       'color': (0.2, 0.25, 0.2),
                       'background': True,
                       'color_texture': self.preloaddata['vr_fill_mound_tex']
                   })
        gnode = bs.getactivity().globalsnode
        gnode.happy_thoughts_mode = True
        gnode.shadow_offset = (0.0, 8.0, 5.0)
        gnode.tint = (1.3, 1.23, 1.0)
        gnode.ambient_color = (1.3, 1.23, 1.0)
        gnode.vignette_outer = (0.64, 0.59, 0.69)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
        gnode.vr_near_clip = 1.0
        self.is_flying = True

register_map(AbyssMap)