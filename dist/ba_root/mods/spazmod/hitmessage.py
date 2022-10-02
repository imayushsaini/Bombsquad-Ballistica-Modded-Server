# -*- coding: utf-8 -*-
# Released under the MIT License. See LICENSE for details.

import ba, _ba, setting
import ba.internal
from stats.mystats import damage_data
from bastd.actor.popuptext import PopupText

our_settings = setting.get_settings_data()

def handle_hit(msg, hp, dmg, hit_by, msg_pos):
    #Check
    if not msg.hit_type: return

    #Record Out Data
    dmg = dmg / 10
    if hit_by is not None:
        hit_by_id = None
        hit_by_id = hit_by.node.playerID
        if hit_by_id is not None:
            hit_by_account_id = None
            for c in ba.internal.get_foreground_host_session().sessionplayers:
                if (c.activityplayer) and (c.activityplayer.node.playerID == hit_by_id):
                    hit_by_account_id = c.get_v1_account_id()
                    if hit_by_account_id in damage_data: damage_data[hit_by_account_id] += float(dmg)
                    else: damage_data[hit_by_account_id] = float(dmg)
    #Send Screen Texts in enabled
    if our_settings['enableHitTexts']:
        try:
            if hp <= 0: PopupText("Rest In Peace !",color=(1,0.2,0.2),scale=1.6,position=msg_pos).autoretain()
            else:
                if dmg >= 800: PopupText("#PRO !",color=(1,0.2,0.2),scale=1.6,position=msg_pos).autoretain()
                elif dmg >= 600 and dmg < 800: PopupText("GOOD ONE!",color=(1,0.3,0.1),scale=1.6,position=msg_pos).autoretain()
                elif dmg >= 400 and dmg < 600: PopupText("OH! YEAH",color=(1,0.5,0.2),scale=1.6,position=msg_pos).autoretain()
                elif dmg >= 200 and dmg < 400: PopupText("WTF!",color=(0.7,0.4,0.2),scale=1.6,position=msg_pos).autoretain()
                elif dmg > 0 and dmg < 200: PopupText("!!!",color=(1,1,1),scale=1.6,position=msg_pos).autoretain()
        except: pass
    return