"""Module to update `setting.json`."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING
import os

import ba
import _ba

from bastd.actor.spazappearance import Appearance
from tools.file_handle import OpenJson

if TYPE_CHECKING:
    pass


def register_character(name: str, char: dict) -> None:
    """Registers the character in the game."""
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

def enable() -> None:
    path=os.path.join(_ba.env()["python_directory_user"],"custom_characters" + os.sep)

    if not os.path.isdir(path):
        os.makedirs(path)

    files=os.listdir(path)

    for file in files:
        if file.endswith(".json"):
            with OpenJson(path + file) as json_file:
                character = json_file.load()
                register_character(file,character)
