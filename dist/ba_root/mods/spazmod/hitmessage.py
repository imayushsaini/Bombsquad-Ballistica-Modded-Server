# -*- coding: utf-8 -*-
# Released under the MIT License. See LICENSE for details.

import bascenev1 as bs
import setting
from bascenev1lib.actor.popuptext import PopupText

our_settings = setting.get_settings_data()


def handle_hit(mag, pos):
    if not mag: return
    # Send Screen Texts in enabled
    if our_settings['enableHitTexts']:
        try:
            if mag >= 110:
                PopupText("#PRO !", color=(1, 0.2, 0.2), scale=1.6,
                          position=pos).autoretain()
            elif 93 <= mag < 110:
                PopupText("GOOD ONE!", color=(1, 0.3, 0.1), scale=1.6,
                          position=pos).autoretain()
            elif 63 <= mag < 93:
                PopupText("OH! YEAH", color=(1, 0.5, 0.2), scale=1.6,
                          position=pos).autoretain()
            elif 45 <= mag < 63:
                PopupText("WTF!", color=(0.7, 0.4, 0.2), scale=1.6,
                          position=pos).autoretain()
            elif 30 < mag < 45:
                PopupText("!!!", color=(1, 1, 1), scale=1.6,
                          position=pos).autoretain()
        except:
            pass
    return


class hit_message(bs.HitMessage):
    def __init__(self, *args, **kwargs):
        hit_type = kwargs["hit_type"]
        if hit_type == "punch":
            handle_hit(kwargs['magnitude'], kwargs['pos'])
        super().__init__(*args, **kwargs)


bs.HitMessage = hit_message
