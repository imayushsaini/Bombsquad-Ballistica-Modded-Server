"""Module to update `setting.json`."""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import json
import os

import _babase
from typing import TYPE_CHECKING

from bascenev1lib.actor.spazappearance import Appearance

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
    t.head_mesh = char['head']
    t.torso_mesh = char['torso']
    t.pelvis_mesh = char['pelvis']
    t.upper_arm_mesh = char['upper_arm']
    t.forearm_mesh = char['forearm']
    t.hand_mesh = char['hand']
    t.upper_leg_mesh = char['upper_leg']
    t.lower_leg_mesh = char['lower_leg']
    t.toes_mesh = char['toes_mesh']
    t.jump_sounds = char['jump_sounds']
    t.attack_sounds = char['attack_sounds']
    t.impact_sounds = char['impact_sounds']
    t.death_sounds = char['death_sounds']
    t.pickup_sounds = char['pickup_sounds']
    t.fall_sounds = char['fall_sounds']
    t.style = char['style']


def enable() -> None:
    path = os.path.join(_babase.env()["python_directory_user"],
                        "custom_characters" + os.sep)

    if not os.path.isdir(path):
        os.makedirs(path)

    files = os.listdir(path)

    for file in files:
        if file.endswith(".json"):
            with open(path + file) as json_file:
                character = json.load(json_file)
                register_character(file, character)
