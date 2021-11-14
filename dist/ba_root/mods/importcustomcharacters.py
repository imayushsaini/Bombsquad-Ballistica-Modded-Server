# ba_meta require api 6


from __future__ import annotations

from typing import TYPE_CHECKING

import ba,_ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional

import os,json
from bastd.actor.spazappearance import *




def registercharacter(name,char):
        t = Appearance(name.split(".")[0])
        t.color_texture = char['color_texture']
        t.color_mask_texture = char['color_mask']
        t.default_color = (0.6, 0.6, 0.6)
        t.default_highlight = (0, 1, 0)
        t.icon_texture = char['icon_texture']
        t.icon_mask_texture = char['icon_mask_texture']
        t.head_model = char['head']
        t.torso_model = char['torso']
        t.pelvis_model = char['pelvis']
        t.upper_arm_model = char['upper_arm']
        t.forearm_model = char['forearm']
        t.hand_model = char['hand']
        t.upper_leg_model = char['upper_leg']
        t.lower_leg_model = char['lower_leg']
        t.toes_model = char['toes_model']
        t.jump_sounds = char['jump_sounds']
        t.attack_sounds = char['attack_sounds']
        t.impact_sounds = char['impact_sounds']
        t.death_sounds = char['death_sounds']
        t.pickup_sounds = char['pickup_sounds']
        t.fall_sounds = char['fall_sounds']
        t.style = char['style']


# ba_meta export plugin
class HeySmoothy(ba.Plugin):
    
    def __init__(self):
        
        
        path=os.path.join(_ba.env()["python_directory_user"],"CustomCharacters" + os.sep)
        if not os.path.isdir(path):
            os.makedirs(path)
        files=os.listdir(path)
        for file in files:
            with open(path+file, 'r') as f:
                character = json.load(f)
                registercharacter(file,character)