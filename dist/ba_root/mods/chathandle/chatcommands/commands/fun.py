# Released under the MIT License. See LICENSE for details.
"""Fun chat commands."""

import babase
import bascenev1 as bs
from tools import corelib
from .handlers import get_target_actors
from .registry import registry


@registry.register(['speed'], category='Fun', shop_cost=200)
def speed(arguments: list[str], clientid: int, accountid: str) -> None:
    """Set the game simulation speed multiplier.

    Usage: /speed <multiplier>
    Examples:
      /speed 1.0
      /speed 2.0
      /speed 0.5
    """
    if not arguments or arguments == ['']:
        return
    try:
        corelib.set_speed(float(arguments[0]))
    except (ValueError, TypeError):
        pass


@registry.register(['fly'], category='Fun', shop_cost=300)
def fly(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle flight mode allowing target player(s) to float in the air.

    Usage: /fly [all | <player_index>]
    Examples:
      /fly
      /fly all
      /fly 0
    """
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node:
            node.fly = not getattr(node, 'fly', False)


@registry.register(['invisible', 'inv'], category='Fun', shop_cost=250)
def invisible(arguments: list[str], clientid: int, accountid: str) -> None:
    """Make target player(s) character meshes invisible.

    Usage: /invisible [all | <player_index>]
    Examples:
      /invisible
      /invisible all
      /inv 1
    """
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
    """Remove head mesh from target player(s).

    Usage: /headless [all | <player_index>]
    Examples:
      /headless
      /headless all
      /hl 0
    """
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node and node.head_mesh is not None:
            node.head_mesh = None
            node.style = 'cyborg'


@registry.register(['creepy', 'creep'], category='Fun', shop_cost=150)
def creepy(arguments: list[str], clientid: int, accountid: str) -> None:
    """Make target player(s) creepy (remove head, add punch and shield powerups).

    Usage: /creepy [all | <player_index>]
    Examples:
      /creepy
      /creepy all
      /creep 0
    """
    for actor in get_target_actors(arguments, clientid):
        node = actor.node
        if node and node.head_mesh is not None:
            node.head_mesh = None
            actor.handlemessage(bs.PowerupMessage(poweruptype='punch'))
            actor.handlemessage(bs.PowerupMessage(poweruptype='shield'))


@registry.register(['celebrate', 'celeb'], category='Fun', shop_cost=100)
def celebrate(arguments: list[str], clientid: int, accountid: str) -> None:
    """Make target player(s) perform a victory dance animation.

    Usage: /celebrate [all | <player_index>]
    Examples:
      /celebrate
      /celebrate all
      /celeb 0
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.CelebrateMessage())


@registry.register(['spaz'], category='Fun')
def spaz(arguments: list[str], clientid: int, accountid: str) -> None:
    """Spaz command placeholder.

    Usage: /spaz
    Examples:
      /spaz
    """
    return


@registry.register(['floater', 'flo'], category='Fun', shop_cost=200)
def floater(arguments: list[str], clientid: int, accountid: str) -> None:
    """Assign floater controls to yourself or a specific client ID.

    Usage: /floater [<client_id>]
    Examples:
      /floater
      /flo 113
    """
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


@registry.register(['tnt', 'spawntnt', 'spawn'], category='Fun', shop_cost=200)
def spawn_tnt(arguments: list[str], clientid: int, accountid: str) -> None:
    """Spawn a TNT crate at target player position or arena center.

    Usage: /tnt [all | <player_index>]
    Examples:
      /tnt
      /tnt all
      /spawn 0
    """
    from bascenev1lib.actor.bomb import BombFactory
    from bascenev1lib.gameutils import SharedObjects
    try:
        activity = bs.get_foreground_host_activity()
        if activity is not None:
            with activity.context:
                from assetpackage import testasset
                shared = SharedObjects.get()
                factory = BombFactory.get()
                materials = (
                    factory.bomb_material,
                    shared.footing_material,
                    shared.object_material,
                    factory.normal_sound_material,
                )
                bs.NodeActor(bs.newnode(
                    'prop',
                    attrs={
                        'position': (0, 2, 0),
                        'velocity': (0.0, 0.0, 0.0),
                        'mesh': factory.tnt_mesh,
                        'light_mesh': factory.tnt_mesh,
                        'body': 'crate',
                        'body_scale': 1.0,
                        'shadow_size': 0.5,
                        'color_texture': testasset.texture.bnt,
                        'reflection': 'soft',
                        'reflection_scale': [0.23],
                        'materials': materials,
                    },
                )).autoretain()
                target_args = [arg for arg in arguments if arg.lower()
                               not in ('tnt', 'spawn')]
                for actor in get_target_actors(target_args, clientid):
                    if actor.node:
                        pos = actor.node.position
                        bs.NodeActor(bs.newnode(
                            'prop',
                            attrs={
                                'position': pos,
                                'velocity': (0.0, 0.0, 0.0),
                                'mesh': factory.tnt_mesh,
                                'light_mesh': factory.tnt_mesh,
                                'body': 'crate',
                                'body_scale': 1.0,
                                'shadow_size': 0.5,
                                'color_texture': testasset.texture.bnt,
                                'reflection': 'soft',
                                'reflection_scale': [0.23],
                                'materials': materials,
                            },
                        )).autoretain()
                    else:
                        bs.NodeActor(bs.newnode(
                            'prop',
                            attrs={
                                'position': (0, 2, 0),
                                'velocity': (0.0, 0.0, 0.0),
                                'mesh': factory.tnt_mesh,
                                'light_mesh': factory.tnt_mesh,
                                'body': 'crate',
                                'body_scale': 1.0,
                                'shadow_size': 0.5,
                                'color_texture': testasset.texture.bnt,
                                'reflection': 'soft',
                                'reflection_scale': [0.23],
                                'materials': materials,
                            },
                        )).autoretain()
    except Exception as e:
        print(f"Error spawning TNT: {e}")
