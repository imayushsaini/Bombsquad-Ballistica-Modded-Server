
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, List, Dict

class mapdefs:
    points = {}
    # noinspection PyDictCreation
    boxes = {}
    boxes['area_of_interest_bounds'] = (-1.045859963, 12.67722855,
                                        -5.401537075) + (0.0, 0.0, 0.0) + (
                                            42.46156851, 20.94044653, 0.6931564611)
    points['ffa_spawn1'] = (-9.295167711, 8.010664315,
                            -5.44451005) + (1.555840357, 1.453808816, 0.1165648888)
    points['ffa_spawn2'] = (7.484707127, 8.172681752, -5.614479365) + (
        1.553861796, 1.453808816, 0.04419853907)
    points['ffa_spawn3'] = (9.55724115, 11.30789446, -5.614479365) + (
        1.337925849, 1.453808816, 0.04419853907)
    points['ffa_spawn4'] = (-11.55747023, 10.99170684, -5.614479365) + (
        1.337925849, 1.453808816, 0.04419853907)
    points['ffa_spawn5'] = (-1.878892369, 9.46490571, -5.614479365) + (
        1.337925849, 1.453808816, 0.04419853907)
    points['ffa_spawn6'] = (-0.4912812943, 5.077006397, -5.521672101) + (
        1.878332089, 1.453808816, 0.007578097856)
    points['flag1'] = (-11.75152479, 8.057427485, -5.52)
    points['flag2'] = (9.840909039, 8.188634282, -5.52)
    points['flag3'] = (-0.2195258696, 5.010273907, -5.52)
    points['flag4'] = (-0.04605809154, 12.73369108, -5.52)
    points['flag_default'] = (-0.04201942896, 12.72374492, -5.52)
    boxes['map_bounds'] = (-0.8748348681, 9.212941713, -5.729538885) + (
        0.0, 0.0, 0.0) + (42.09666006, 26.19950145, 7.89541168)
    points['powerup_spawn1'] = (1.160232442, 6.745963662, -5.469115985)
    points['powerup_spawn2'] = (-1.899700206, 10.56447241, -5.505721177)
    points['powerup_spawn3'] = (10.56098871, 12.25165669, -5.576232453)
    points['powerup_spawn4'] = (-12.33530337, 12.25165669, -5.576232453)
    points['spawn1'] = (-9.295167711, 8.010664315,
                        -5.44451005) + (1.555840357, 1.453808816, 0.1165648888)
    points['spawn2'] = (7.484707127, 8.172681752,
                        -5.614479365) + (1.553861796, 1.453808816, 0.04419853907)
    points['spawn_by_flag1'] = (-9.295167711, 8.010664315, -5.44451005) + (
        1.555840357, 1.453808816, 0.1165648888)
    points['spawn_by_flag2'] = (7.484707127, 8.172681752, -5.614479365) + (
        1.553861796, 1.453808816, 0.04419853907)
    points['spawn_by_flag3'] = (-1.45994593, 5.038762459, -5.535288724) + (
        0.9516389866, 0.6666414677, 0.08607244075)
    points['spawn_by_flag4'] = (0.4932087091, 12.74493212, -5.598987003) + (
        0.5245740665, 0.5245740665, 0.01941146064)
class CreativeThoughts(ba.Map):
    """Freaking map by smoothy."""

    defs = mapdefs

    name = 'Creative Thoughts'

    @classmethod
    def get_play_types(cls) -> List[str]:
        """Return valid play types for this map."""
        return [
            'melee', 'keep_away', 'team_flag'
        ]

    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'alwaysLandPreview'

    @classmethod
    def on_preload(cls) -> Any:
        data: Dict[str, Any] = {
            'model': ba.getmodel('alwaysLandLevel'),
            'bottom_model': ba.getmodel('alwaysLandLevelBottom'),
            'bgmodel': ba.getmodel('alwaysLandBG'),
            'collide_model': ba.getcollidemodel('alwaysLandLevelCollide'),
            'tex': ba.gettexture('alwaysLandLevelColor'),
            'bgtex': ba.gettexture('alwaysLandBGColor'),
            'vr_fill_mound_model': ba.getmodel('alwaysLandVRFillMound'),
            'vr_fill_mound_tex': ba.gettexture('vrFillMound')
        }
        return data

    @classmethod
    def get_music_type(cls) -> ba.MusicType:
        return ba.MusicType.FLYING

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -3.7, 2.5))
        shared = SharedObjects.get()
        self._fake_wall_material=ba.Material()
        self._real_wall_material=ba.Material()
        self._fake_wall_material.add_actions(
            conditions=(('they_are_younger_than',9000),'and',('they_have_material', shared.player_material)),
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
        self.background = ba.newnode(
            'terrain',
            attrs={
                'model': self.preloaddata['bgmodel'],
                'lighting': False,
                'background': True,
                'color_texture': ba.gettexture("rampageBGColor")
            })

        self.leftwall=ba.newnode('region',attrs={'position': (-17.75152479, 13, -5.52),'scale': (0.1,15.5,2),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        self.rightwall=ba.newnode('region',attrs={'position': (17.75, 13, -5.52),'scale': (0.1,15.5,2),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        self.topwall=ba.newnode('region',attrs={'position': (0, 21.0, -5.52),'scale': (35.4,0.2,2),'type': 'box','materials': [shared.footing_material,self._real_wall_material ]})
        ba.newnode('locator', attrs={'shape':'box', 'position':(-17.75152479, 13, -5.52), 'color':(0,0,0), 'opacity':1,'draw_beauty':True,'additive':False,'size':(0.1,15.5,2)})
        ba.newnode('locator', attrs={'shape':'box', 'position':(17.75, 13, -5.52), 'color':(0,0,0), 'opacity':1,'draw_beauty':True,'additive':False,'size':(0.1,15.5,2)})
        ba.newnode('locator', attrs={'shape':'box', 'position':(0, 21.0, -5.52), 'color':(0,0,0), 'opacity':1,'draw_beauty':True,'additive':False,'size':(35.4,0.2,2)})
        
        # self.node_text_left = ba.newnode('text',
        #                        attrs={
        #                            'text': "|\n|\n|\n|\n|\n\n\n\n|\n|\n|\n|\n End here \n|\n|\n|\n|\n|\n|\n|\n\n\n\n|\n|\n",
        #                            'in_world': True,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'center',
        #                            'position':(-18,20,-5)
        #                        })
        # self.node_text_right = ba.newnode('text',
        #                        attrs={
        #                            'text': "|\n|\n|\n|\n|\n\n\n\n|\n|\n|\n|\n End here \n|\n|\n|\n|\n|\n|\n|\n\n\n\n|\n|\n",
        #                            'in_world': True,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'center',
        #                            'position':(17,20,-5)
        #                        })
        # self.node_text_top = ba.newnode('text',
        #                        attrs={
        #                            'text': "_ _  _ _  _  _ _ _ _         _ _ _    _ _ _ _          _ _ _ _   _ _   _ _ _  _ _      _ _ _",
        #                            'in_world': True,
        #                            'shadow': 1.0,
        #                            'flatness': 1.0,
        #                            'scale':0.019,
        #                            'h_align': 'center',
        #                            'position':(0,21,-5)
        #                        })
        gnode = ba.getactivity().globalsnode
        gnode.happy_thoughts_mode = True
        gnode.shadow_offset = (0.0, 8.0, 5.0)
        gnode.tint = (1.3, 1.23, 1.0)
        gnode.ambient_color = (1.3, 1.23, 1.0)
        gnode.vignette_outer = (0.64, 0.59, 0.69)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
        gnode.vr_near_clip = 1.0
        self.is_flying = True

        # throw out some tips on flying
        txt = ba.newnode('text',
                         attrs={
                             'text': ba.Lstr(resource='pressJumpToFlyText'),
                             'scale': 1.2,
                             'maxwidth': 800,
                             'position': (0, 200),
                             'shadow': 0.5,
                             'flatness': 0.5,
                             'h_align': 'center',
                             'v_attach': 'bottom'
                         })
        cmb = ba.newnode('combine',
                         owner=txt,
                         attrs={
                             'size': 4,
                             'input0': 0.3,
                             'input1': 0.9,
                             'input2': 0.0
                         })
        ba.animate(cmb, 'input3', {3.0: 0, 4.0: 1, 9.0: 1, 10.0: 0})
        cmb.connectattr('output', txt, 'color')
        ba.timer(10.0, txt.delete)



ba._map.register_map(CreativeThoughts)
