import babase
import bauiv1 as bui
import bascenev1 as bs
import babase.internal

import setting
import random
setti=setting.get_settings_data()

def showScoreScreenAnnouncement():
    if setti["ScoreScreenAnnouncement"]["enable"]:
        color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0))
        msgs = setti["ScoreScreenAnnouncement"]["msg"]
        bs.broadcastmessage(random.choice(msgs), color = color)
