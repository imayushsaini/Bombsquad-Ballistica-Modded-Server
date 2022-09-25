# This plugin developed fro Bombsquad Server, and I don't know how to make UI
# Just edit Config before starting server
# by: Lirik
# Further edited/Fixed by:Freak
import ba
import random
from random import choice
CONFIGS = {
                "Radius": 2.0,
                "Blinking": False,
                "AdaptivePos": True,
                "IgnoreOnMaps": [],
                "Colors": {
                "Intensity": 0.8,
                "Animate": True,
                "Random": True,
                "LeftSide": (1, 0, 1),
                "RightSide": (0, 0, 1),
                          }
                     }

def get_random_color():
    """Fetches random color every time for our nodes"""

    choices = [0, 1, 2, 3]
    return (choice(choices), choice(choices), choice(choices))


def get_colors():
    """Fucntion for getting colors for our light node based on configs"""

    if CONFIGS["Colors"]["Random"]:
        return get_random_color(), get_random_color()
    return CONFIGS["Colors"]["LeftSide"], CONFIGS["Colors"]["RightSide"]


# Add more perfect positions for all maps
def get_adaptive_pos(name: str) -> tuple:
    """Fuction for getting pecfect positions for the current map

    Args:
        name (str): Name of the map

    Returns:
        [tuple]: tuple containing left and right position respectively
    """
    adaptive = {"Crag Castle": ((-6, 7, -7), (6, 7, -7))}

    if name in adaptive and CONFIGS["AdaptivePos"]:
        return adaptive[name]
    return (-10, 7, -3), (10, 7, -3)


def Map___init__(func):
    """Redefined method for ba.Map"""

    def wrapper(self, vr_overlay_offset=None):
        func(self, vr_overlay_offset)

        name = self.getname()

        if name in CONFIGS["IgnoreOnMaps"]:
            return

        left_color, right_color = get_colors()
        left_pos, right_pos = get_adaptive_pos(name)

        self.left_light = ba.newnode(
            "light",
            attrs={
                "position": left_pos,
                "radius": CONFIGS["Radius"],
                "intensity": CONFIGS["Colors"]["Intensity"],
                "color": left_color,
                "volume_intensity_scale": 10,
            },
        )

        self.right_light = ba.newnode(
            "light",
            attrs={
                "position": right_pos,
                "radius": CONFIGS["Radius"],
                "intensity": CONFIGS["Colors"]["Intensity"],
                "color": right_color,
                "volume_intensity_scale": 10,
            },
        )

        ba.animate(
            self.left_light,
            "radius",
            {0: 0, 1.5: 0.5, 3: CONFIGS["Radius"]},
            loop=True if CONFIGS["Blinking"] else False,
        )
        ba.animate(
            self.right_light,
            "radius",
            {0: 0, 1.5: 0.5, 3: CONFIGS["Radius"]},
            loop=True if CONFIGS["Blinking"] else False,
        )

        if CONFIGS["Colors"]["Animate"]:
            ba.animate_array(
                self.left_light,
                "color",
                3,
                {
                    0: get_random_color(),
                    1: get_random_color(),
                    2: get_random_color(),
                    3: get_random_color(),
                    4: get_random_color(),
                    5: get_random_color(),
                },
                loop=True,
            )

    return wrapper


ba.Map.__init__ = Map___init__(ba.Map.__init__)
