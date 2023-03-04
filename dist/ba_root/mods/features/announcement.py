import ba
import ba.internal

import setting
import random
setti=setting.get_settings_data()

def showScoreScreenAnnouncement():
    if setti["ScoreScreenAnnouncement"]["enable"]:
        color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0))
        msgs = setti["ScoreScreenAnnouncement"]["msg"]
        ba.screenmessage(random.choice(msgs), color = color)
