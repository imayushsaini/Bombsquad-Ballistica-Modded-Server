# Released under the MIT License. See LICENSE for details.
"""Fun chat commands."""

import babase
import bascenev1 as bs
from tools import corelib
from .handlers import get_target_actors
from .registry import registry


@registry.register(['speed'], category='Fun', shop_cost=200)
def speed(arguments: list[str], clientid: int, accountid: str) -> None:
    """Set the game speed."""
    if not arguments or arguments == ['']:
        return
    try:
        corelib.set_speed(float(arguments[0]))
    except (ValueError, TypeError):
        pass


@registry.register(['fly'], category='Fun', shop_cost=300)
def fly(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle fly mode for target players."""
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node:
            node.fly = not getattr(node, 'fly', False)


@registry.register(['invisible', 'inv'], category='Fun', shop_cost=250)
def invisible(arguments: list[str], clientid: int, accountid: str) -> None:
    """Make target players invisible."""
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node:
            node.head_mesh = None
            node.torso_mesh = None
            node.upper_arm_mesh = None
            node.forearm_mesh = None
            node.pelvis_mesh = None
            node.hand_mesh = None
            node.toes_mesh = None
            node.upper_leg_mesh = None
            node.lower_leg_mesh = None
            node.style = 'cyborg'


@registry.register(['headless', 'hl'], category='Fun', shop_cost=150)
def headless(arguments: list[str], clientid: int, accountid: str) -> None:
    """Remove head mesh from target players."""
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node and node.head_mesh is not None:
            node.head_mesh = None
            node.style = 'cyborg'


@registry.register(['creepy', 'creep'], category='Fun', shop_cost=150)
def creepy(arguments: list[str], clientid: int, accountid: str) -> None:
    """Make target players creepy (remove head, add punch and shield)."""
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node and node.head_mesh is not None:
            node.head_mesh = None
            actor.handlemessage(bs.PowerupMessage(poweruptype='punch'))
            actor.handlemessage(bs.PowerupMessage(poweruptype='shield'))


@registry.register(['celebrate', 'celeb'], category='Fun', shop_cost=100)
def celebrate(arguments: list[str], clientid: int, accountid: str) -> None:
    """Force target players to celebrate."""
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.CelebrateMessage())


@registry.register(['spaz'], category='Fun')
def spaz(arguments: list[str], clientid: int, accountid: str) -> None:
    """Dummy spaz command, does nothing."""
    return


@registry.register(['floater', 'flo'], category='Fun', shop_cost=200)
def floater(arguments: list[str], clientid: int, accountid: str) -> None:
    """Assign floater controls to a client."""
    try:
        from .. import floater as floater_mod
        if not arguments or arguments == ['']:
            floater_mod.assignFloInputs(clientid)
        else:
            val = arguments[0]
            try:
                val = int(val)
            except ValueError:
                pass
            floater_mod.assignFloInputs(val)
    except Exception:
        pass
