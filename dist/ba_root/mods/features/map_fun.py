import _ba
import random

def decorate_map():
    try:
        activity = _ba.get_foreground_host_activity()
        activity.fireflies_generator(20,True)
        activity.map.node.reflection = "powerup"
        activity.map.node.reflection_scale = [4]
        activity.globalsnode.tint = (0.5,0.7,1)
        # activity.map.node.color = random.choices([(0.8,0.3,0.3),(0.6,0.5,0.7),(0.3,0.8,0.5)])[0]
        m = 5
        s = 5000
        ba.animate_array(activity.globalsnode, 'ambient_color', 3, {0: (1*m,0,0), s: (0,1*m,0),s*2:(0,0,1*m),s*3:(1*m,0,0)},True)
        activity.map.background.reflection = "soft"
    except:
        pass
