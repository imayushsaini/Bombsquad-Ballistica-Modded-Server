import random

import setting

import bascenev1 as bs

setti = setting.get_settings_data()


def showScoreScreenAnnouncement():
    if setti["ScoreScreenAnnouncement"]["enable"]:
        color = ((0 + random.random() * 1.0), (0 + random.random() * 1.0),
                 (0 + random.random() * 1.0))
        msgs = setti["ScoreScreenAnnouncement"]["msg"]
        bs.broadcastmessage(random.choice(msgs), color=color)
