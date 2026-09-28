# Released under the MIT License. See LICENSE for details.
"""Cheat chat commands."""

import bascenev1 as bs
from .handlers import get_target_actors
from .registry import registry


@registry.register(['kill', 'die'], category='Cheats')
def kill(arguments: list[str], clientid: int, accountid: str) -> None:
    """Kill target player(s) immediately in game.

    Usage: /kill [all | <player_index>]
    Examples:
      /kill
      /kill all
      /kill 0
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.DieMessage())


@registry.register(['heal', 'heath'], category='Cheats')
def heal(arguments: list[str], clientid: int, accountid: str) -> None:
    """Heal target player(s) to full health.

    Usage: /heal [all | <player_index>]
    Examples:
      /heal
      /heal all
      /heal 1
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.PowerupMessage(poweruptype='health'))


@registry.register(['curse', 'cur'], category='Cheats')
def curse(arguments: list[str], clientid: int, accountid: str) -> None:
    """Curse target player(s) causing them to explode after a short delay.

    Usage: /curse [all | <player_index>]
    Examples:
      /curse
      /curse all
      /curse 0
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.PowerupMessage(poweruptype='curse'))


@registry.register(['sleep'], category='Cheats')
def sleep(arguments: list[str], clientid: int, accountid: str) -> None:
    """Knockout target player(s) for 8 seconds.

    Usage: /sleep [all | <player_index>]
    Examples:
      /sleep
      /sleep all
      /sleep 2
    """
    for actor in get_target_actors(arguments, clientid):
        if actor.node:
            actor.node.handlemessage('knockout', 8000)


@registry.register(['superpunch', 'sp'], category='Cheats')
def super_punch(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle super punch (15x damage and 0 cooldown) for target player(s).

    Usage: /superpunch [all | <player_index>]
    Examples:
      /superpunch
      /superpunch all
      /sp 0
    """
    for actor in get_target_actors(arguments, clientid):
        if getattr(actor, '_punch_power_scale', 1.2) != 15:
            actor._punch_power_scale = 15
            actor._punch_cooldown = 0
        else:
            actor._punch_power_scale = 1.2
            actor._punch_cooldown = 400


@registry.register(['gloves', 'punch'], category='Cheats')
def gloves(arguments: list[str], clientid: int, accountid: str) -> None:
    """Give boxing gloves powerup to target player(s).

    Usage: /gloves [all | <player_index>]
    Examples:
      /gloves
      /gloves all
      /punch 0
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.PowerupMessage(poweruptype='punch'))


@registry.register(['shield', 'protect'], category='Cheats')
def shield(arguments: list[str], clientid: int, accountid: str) -> None:
    """Give energy shield powerup to target player(s).

    Usage: /shield [all | <player_index>]
    Examples:
      /shield
      /shield all
      /protect 1
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.PowerupMessage(poweruptype='shield'))


@registry.register(['freeze', 'ice'], category='Cheats')
def freeze(arguments: list[str], clientid: int, accountid: str) -> None:
    """Freeze target player(s) in ice.

    Usage: /freeze [all | <player_index>]
    Examples:
      /freeze
      /freeze all
      /ice 0
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.FreezeMessage())


@registry.register(['unfreeze', 'thaw'], category='Cheats')
def un_freeze(arguments: list[str], clientid: int, accountid: str) -> None:
    """Unfreeze target player(s) from ice.

    Usage: /unfreeze [all | <player_index>]
    Examples:
      /unfreeze
      /unfreeze all
      /thaw 0
    """
    for actor in get_target_actors(arguments, clientid):
        actor.handlemessage(bs.ThawMessage())


@registry.register(['godmode', 'gm'], category='Cheats')
def god_mode(arguments: list[str], clientid: int, accountid: str) -> None:
    """Toggle invincibility and god mode for target player(s).

    Usage: /godmode [all | <player_index>]
    Examples:
      /godmode
      /godmode all
      /gm 0
    """
    for actor in get_target_actors(arguments, clientid):
        if actor.node:
            if getattr(actor, '_punch_power_scale', 1.2) != 7:
                actor._punch_power_scale = 7
                actor.node.hockey = True
                actor.node.invincible = True
            else:
                actor._punch_power_scale = 1.2
                actor.node.hockey = False
                actor.node.invincible = False
