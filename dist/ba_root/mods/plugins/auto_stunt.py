# ba_meta require api 7
# AutoStunt mod by - Mr.Smoothy x Rikko
# https://discord.gg/ucyaesh
# https://bombsquad.ga
# Dont modify redistribute this plugin , if want to use features of this plugin in your mod write logic in seprate file
# and import this as module.
# If want to contribute in this original module, raise PR on github https://github.com/bombsquad-community/plugin-manager

import ba
import _ba
import bastd
from bastd.actor.text import Text
from bastd.actor.image import Image
from bastd.actor import spaz
from bastd.actor import playerspaz
from bastd.gameutils import SharedObjects
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.actor.spazfactory import SpazFactory
from bastd.game.elimination import EliminationGame
import math
import json
import os

from typing import Optional

CONTROLS_CENTER = (0, 0)
CONTROLS_SCALE = 1

BASE_STUNTS_DIRECTORY = os.path.join(_ba.env()["python_directory_user"], "CustomStunts")
PLAYERS_STUNT_INFO = {}

STUNT_CACHE = {}
original_on_begin = ba._activity.Activity.on_begin
original_chatmessage = _ba.chatmessage


class ControlsUI:

    def on_jump_press(activity):
        activity._jump_image.node.color = list(
            channel * 2 for channel in activity._jump_image.node.color[:3]) + [1]

    def on_jump_release(activity):
        activity._jump_image.node.color = list(
            channel * 0.5 for channel in activity._jump_image.node.color[:3]) + [1]

    def on_pickup_press(activity):
        activity._pickup_image.node.color = list(
            channel * 2 for channel in activity._pickup_image.node.color[:3]) + [1]

    def on_pickup_release(activity):
        activity._pickup_image.node.color = list(
            channel * 0.5 for channel in activity._pickup_image.node.color[:3]) + [1]

    def on_punch_press(activity):
        activity._punch_image.node.color = list(
            channel * 2 for channel in activity._punch_image.node.color[:3]) + [1]

    def on_punch_release(activity):
        activity._punch_image.node.color = list(
            channel * 0.5 for channel in activity._punch_image.node.color[:3]) + [1]

    def on_bomb_press(activity):
        activity._bomb_image.node.color = list(
            channel * 2 for channel in activity._bomb_image.node.color[:3]) + [1]

    def on_bomb_release(activity):
        activity._bomb_image.node.color = list(
            channel * 0.5 for channel in activity._bomb_image.node.color[:3]) + [1]

    def on_move_ud(activity, value):
        activity.set_stick_image_position(activity, x=activity.stick_image_position_x, y=value)

    def on_move_lr(activity, value):
        activity.set_stick_image_position(activity, x=value, y=activity.stick_image_position_y)

    def display(activity):
        activity._jump_image.node.color = list(activity._jump_image.node.color[:3]) + [1]
        activity._pickup_image.node.color = list(activity._pickup_image.node.color[:3]) + [1]
        activity._punch_image.node.color = list(activity._punch_image.node.color[:3]) + [1]
        activity._bomb_image.node.color = list(activity._bomb_image.node.color[:3]) + [1]
        activity._stick_base_image.opacity = 1.0
        activity._stick_nub_image.opacity = 1.0

    def hide(activity):
        activity._jump_image.node.color = list(activity._jump_image.node.color[:3]) + [0]
        activity._pickup_image.node.color = list(activity._pickup_image.node.color[:3]) + [0]
        activity._punch_image.node.color = list(activity._punch_image.node.color[:3]) + [0]
        activity._bomb_image.node.color = list(activity._bomb_image.node.color[:3]) + [0]
        activity._stick_base_image.opacity = 0.0
        activity._stick_nub_image.opacity = 0.0


CONTROLS_UI_MAP = {
    "JUMP_PRESS": ControlsUI.on_jump_press,
    "JUMP_RELEASE": ControlsUI.on_jump_release,
    "PICKUP_PRESS": ControlsUI.on_pickup_press,
    "PICKUP_RELEASE": ControlsUI.on_pickup_release,
    "PUNCH_PRESS": ControlsUI.on_punch_press,
    "PUNCH_RELEASE": ControlsUI.on_punch_release,
    "BOMB_PRESS": ControlsUI.on_bomb_press,
    "BOMB_RELEASE": ControlsUI.on_bomb_release,
    "UP_DOWN": ControlsUI.on_move_ud,
    "LEFT_RIGHT": ControlsUI.on_move_lr
}


class NewSpaz(bastd.actor.spaz.Spaz):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.move_map = {
            "UP_DOWN": self.on_move_up_down,
            "LEFT_RIGHT": self.on_move_left_right,
            "HOLD_POSITION": self.on_hold_position_press,
            "HOLD_RELEASE": self.on_hold_position_release,
            "JUMP_PRESS": self.on_jump_press,
            "JUMP_RELEASE": self.on_jump_release,
            "PICKUP_PRESS": self.on_pickup_press,
            "PICKUP_RELEASE": self.on_pickup_release,
            "PUNCH_PRESS": self.on_punch_press,
            "PUNCH_RELEASE": self.on_punch_release,
            "BOMB_PRESS": self.on_bomb_press,
            "BOMB_RELEASE": self.on_bomb_release,
            "RUN": self.on_run,
        }


class NewPlayerSpaz(bastd.actor.playerspaz.PlayerSpaz):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.move_map = {
            "UP_DOWN": self.on_move_up_down,
            "LEFT_RIGHT": self.on_move_left_right,
            "HOLD_POSITION": self.on_hold_position_press,
            "HOLD_RELEASE": self.on_hold_position_release,
            "JUMP_PRESS": self.on_jump_press,
            "JUMP_RELEASE": self.on_jump_release,
            "PICKUP_PRESS": self.on_pickup_press,
            "PICKUP_RELEASE": self.on_pickup_release,
            "PUNCH_PRESS": self.on_punch_press,
            "PUNCH_RELEASE": self.on_punch_release,
            "BOMB_PRESS": self.on_bomb_press,
            "BOMB_RELEASE": self.on_bomb_release,
            "RUN": self.on_run,
        }
        self.mirror_spaz = []
        self.source_player.in_replay = False
        self.source_player.mirror_mode = False

    def _handle_action(self, action, value: Optional[float] = None) -> None:
        if self.source_player.sessionplayer in PLAYERS_STUNT_INFO:
            PLAYERS_STUNT_INFO[self.source_player.sessionplayer].append({
                "time": ba.time() - self.source_player.recording_start_time,
                "move": {
                    "action": action,
                    "value": value,
                }
            })
        elif self.source_player.in_replay:
            ui_activation = CONTROLS_UI_MAP.get(action)
            if ui_activation:
                if action in ["UP_DOWN", "LEFT_RIGHT"]:
                    ui_activation(self.source_player.actor._activity(), value)
                else:
                    ui_activation(self.source_player.actor._activity())
        elif self.source_player.mirror_mode:
            for mspaz in self.mirror_spaz:
                if mspaz and mspaz.node.exists():
                    if action in ["UP_DOWN", "LEFT_RIGHT", "RUN"]:
                        mspaz.move_map[action](value)
                    else:
                        mspaz.move_map[action]()

    def on_move_up_down(self, value: float, *args, **kwargs) -> None:
        self._handle_action("UP_DOWN", value)
        super().on_move_up_down(value, *args, **kwargs)

    def on_move_left_right(self, value: float, *args, **kwargs) -> None:
        self._handle_action("LEFT_RIGHT", value)
        super().on_move_left_right(value, *args, **kwargs)

    def on_hold_position_press(self, *args, **kwargs) -> None:
        self._handle_action("HOLD_POSITION")
        super().on_hold_position_press(*args, **kwargs)

    def on_hold_position_release(self, *args, **kwargs) -> None:
        self._handle_action("HOLD_RELEASE")
        super().on_hold_position_release(*args, **kwargs)

    def on_jump_press(self, *args, **kwargs) -> None:
        self._handle_action("JUMP_PRESS")
        super().on_jump_press(*args, **kwargs)

    def on_jump_release(self, *args, **kwargs) -> None:
        self._handle_action("JUMP_RELEASE")
        super().on_jump_release(*args, **kwargs)

    def on_pickup_press(self, *args, **kwargs) -> None:
        self._handle_action("PICKUP_PRESS")
        super().on_pickup_press(*args, **kwargs)

    def on_pickup_release(self, *args, **kwargs) -> None:
        self._handle_action("PICKUP_RELEASE")
        super().on_pickup_release(*args, **kwargs)

    def on_punch_press(self, *args, **kwargs) -> None:
        self._handle_action("PUNCH_PRESS")
        super().on_punch_press(*args, **kwargs)

    def on_punch_release(self, *args, **kwargs) -> None:
        self._handle_action("PUNCH_RELEASE")
        super().on_punch_release(*args, **kwargs)

    def on_bomb_press(self, *args, **kwargs) -> None:
        self._handle_action("BOMB_PRESS")
        super().on_bomb_press(*args, **kwargs)

    def on_bomb_release(self, *args, **kwargs) -> None:
        self._handle_action("BOMB_RELEASE")
        super().on_bomb_release(*args, **kwargs)

    def on_run(self, value: float, *args, **kwargs) -> None:
        self._handle_action("RUN", value)
        super().on_run(value, *args, **kwargs)


def handle_player_replay_end(player):
    player.in_replay = False
    ControlsUI.hide(player.actor._activity())


def get_player_from_client_id(client_id, activity=None):
    activity = activity or _ba.get_foreground_host_activity()
    for player in activity.players:
        if player.sessionplayer.inputdevice.client_id == client_id:
            return player
    raise ba.SessionPlayerNotFound()


def mirror(clieid):
    player = get_player_from_client_id(clieid)
    spawn_mirror_spaz(player)


def capture(player):
    with ba.Context(player.actor._activity()):
        player.recording_start_time = ba.time()
    PLAYERS_STUNT_INFO[player.sessionplayer] = []


def save(player, stunt_name):
    stunt_path = f"{os.path.join(BASE_STUNTS_DIRECTORY, stunt_name)}.json"
    os.makedirs(BASE_STUNTS_DIRECTORY, exist_ok=True)
    with open(stunt_path, "w") as fout:
        json.dump(PLAYERS_STUNT_INFO[player.sessionplayer], fout, indent=2)
    del PLAYERS_STUNT_INFO[player.sessionplayer]


def replay(player, stunt_name):
    stunt_path = f"{os.path.join(BASE_STUNTS_DIRECTORY, stunt_name)}.json"
    if stunt_name in STUNT_CACHE:
        stunt = STUNT_CACHE[stunt_name]
    else:
        try:
            with open(stunt_path, "r") as fin:
                stunt = json.load(fin)
                STUNT_CACHE[stunt_name] = stunt
        except:
            ba.screenmessage(f"{stunt_name} doesn't exists")
            return
    player.in_replay = True
    with ba.Context(player.actor._activity()):
        ControlsUI.display(player.actor._activity())
        for move in stunt:
            value = move["move"]["value"]
            if value is None:
                ba.timer(
                    move["time"],
                    ba.Call(player.actor.move_map[move["move"]["action"]])
                )
            else:
                ba.timer(
                    move["time"],
                    ba.Call(player.actor.move_map[move["move"]["action"]], move["move"]["value"])
                )
        last_move_time = move["time"]
        time_to_hide_controls = last_move_time + 1
        ba.timer(time_to_hide_controls, ba.Call(handle_player_replay_end, player))


def spawn_mirror_spaz(player):
    player.mirror_mode = True
    with ba.Context(player.actor._activity()):
        bot = spaz.Spaz(player.color, player.highlight, character=player.character).autoretain()
        bot.handlemessage(ba.StandMessage(
            (player.actor.node.position[0], player.actor.node.position[1], player.actor.node.position[2]+1), 93))
        bot.node.name = player.actor.node.name
        bot.node.name_color = player.actor.node.name_color
        player.actor.mirror_spaz.append(bot)


def ghost(player, stunt_name):
    stunt_path = f"{os.path.join(BASE_STUNTS_DIRECTORY, stunt_name)}.json"
    if stunt_name in STUNT_CACHE:
        stunt = STUNT_CACHE[stunt_name]
    else:
        try:
            with open(stunt_path, "r") as fin:
                stunt = json.load(fin)
                STUNT_CACHE[stunt_name] = stunt
        except:
            ba.screenmessage(f"{stunt_name} doesn't exists")
            return
    player.in_replay = True

    with ba.Context(player.actor._activity()):
        bot = spaz.Spaz((1, 0, 0), character="Spaz").autoretain()
        bot.handlemessage(ba.StandMessage(player.actor.node.position, 93))
        give_ghost_power(bot)
        ControlsUI.display(player.actor._activity())
        for move in stunt:
            value = move["move"]["value"]
            if value is None:
                ba.timer(
                    move["time"],
                    ba.Call(bot.move_map[move["move"]["action"]])
                )
                ui_activation = CONTROLS_UI_MAP.get(move["move"]["action"])
                if ui_activation:
                    ba.timer(
                        move["time"],
                        ba.Call(ui_activation, player.actor._activity())
                    )
            else:
                ba.timer(
                    move["time"],
                    ba.Call(bot.move_map[move["move"]["action"]], move["move"]["value"])
                )
                ui_activation = CONTROLS_UI_MAP.get(move["move"]["action"])

                if ui_activation:
                    ba.timer(
                        move["time"],
                        ba.Call(ui_activation, player.actor._activity(), move["move"]["value"])
                    )
        last_move_time = move["time"]
        time_to_hide_controls = last_move_time + 1
        ba.timer(time_to_hide_controls, ba.Call(handle_player_replay_end, player))
        ba.timer(time_to_hide_controls, ba.Call(bot.node.delete))


def give_ghost_power(spaz):
    spaz.node.invincible = True
    shared = SharedObjects.get()
    factory = SpazFactory.get()
    ghost = ba.Material()
    # smoothy hecks
    ghost.add_actions(
        conditions=(('they_have_material', factory.spaz_material), 'or',
                    ('they_have_material', shared.player_material), 'or',
                    ('they_have_material', shared.attack_material), 'or',
                    ('they_have_material', shared.pickup_material), 'or',
                    ('they_have_material',  PowerupBoxFactory.get().powerup_accept_material)),
        actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)
        ))
    mats = list(spaz.node.materials)
    roller = list(spaz.node.roller_materials)
    ext = list(spaz.node.extras_material)
    pick = list(spaz.node.pickup_materials)
    punch = list(spaz.node.punch_materials)

    mats.append(ghost)
    roller.append(ghost)
    ext.append(ghost)
    pick.append(ghost)
    punch.append(ghost)

    spaz.node.materials = tuple(mats)
    spaz.node.roller_materials = tuple(roller)
    spaz.node.extras_material = tuple(ext)
    spaz.node.pickup_materials = tuple(pick)
    spaz.node.punch_materials = tuple(pick)


def new_chatmessage(msg):
    if not msg.startswith("*"):
        return original_chatmessage(msg)

    stripped_msg = msg[1:]
    msg_splits = stripped_msg.split(maxsplit=3)
    command = msg_splits[0]

    client_id = -1
    player = get_player_from_client_id(client_id)

    if command == "start":
        capture(player)
        _ba.chatmessage("Recording started for {}.".format(
            player.getname(),
        ))
        return original_chatmessage(msg)

    stunt_name = " ".join(msg_splits[1:])

    if command == "save":
        if len(msg_splits) < 2:
            ba.screenmessage("Enter name of stunt eg : *save bombjump")
            return original_chatmessage(msg)
        save(player, stunt_name)
        _ba.chatmessage('Recording "{}" by {} saved.'.format(
            stunt_name,
            player.getname(),
        ))
    elif command == "stunt":
        if len(msg_splits) < 2:
            ba.screenmessage("Enter name of stunt eg : *stunt bombjump")
            return original_chatmessage(msg)
        replay(player, stunt_name)
        _ba.chatmessage('Replaying "{}" on {}.'.format(
            stunt_name,
            player.getname(),
        ))
    elif command == "learn":
        if len(msg_splits) < 2:
            ba.screenmessage("Enter name of stunt eg : *learn bombjump")
            return original_chatmessage(msg)
        ghost(player, stunt_name)
        _ba.chatmessage('Replaying "{}" on {}.'.format(
            stunt_name,
            player.getname(),
        ))
    elif command == "mirror":
        spawn_mirror_spaz(player)
    return original_chatmessage(msg)


def set_stick_image_position(self, x: float, y: float) -> None:

    # Clamp this to a circle.
    len_squared = x * x + y * y
    if len_squared > 1.0:
        length = math.sqrt(len_squared)
        mult = 1.0 / length
        x *= mult
        y *= mult

    self.stick_image_position_x = x
    self.stick_image_position_y = y
    offs = 50.0
    assert self._scale is not None
    p = [
        self._stick_nub_position[0] + x * offs * 0.6,
        self._stick_nub_position[1] + y * offs * 0.6
    ]
    c = list(self._stick_nub_image_color)
    if abs(x) > 0.1 or abs(y) > 0.1:
        c[0] *= 2.0
        c[1] *= 4.0
        c[2] *= 2.0
    assert self._stick_nub_image is not None
    self._stick_nub_image.position = p
    self._stick_nub_image.color = c
    c = list(self._stick_base_image_color)
    if abs(x) > 0.1 or abs(y) > 0.1:
        c[0] *= 1.5
        c[1] *= 1.5
        c[2] *= 1.5
    assert self._stick_base_image is not None
    self._stick_base_image.color = c


def on_begin(self, *args, **kwargs) -> None:
    self._jump_image = Image(
        ba.gettexture('buttonJump'),
        position=(385, 160),
        scale=(50, 50),
        color=[0.1, 0.45, 0.1, 0]
    )
    self._pickup_image = Image(
        ba.gettexture('buttonPickUp'),
        position=(385, 240),
        scale=(50, 50),
        color=[0, 0.35, 0, 0]
    )
    self._punch_image = Image(
        ba.gettexture('buttonPunch'),
        position=(345, 200),
        scale=(50, 50),
        color=[0.45, 0.45, 0, 0]
    )
    self._bomb_image = Image(
        ba.gettexture('buttonBomb'),
        position=(425, 200),
        scale=(50, 50),
        color=[0.45, 0.1, 0.1, 0]
    )
    self.stick_image_position_x = self.stick_image_position_y = 0.0
    self._stick_base_position = p = (-328, 200)
    self._stick_base_image_color = c2 = (0.25, 0.25, 0.25, 1.0)
    self._stick_base_image = ba.newnode(
        'image',
        attrs={
            'texture': ba.gettexture('nub'),
            'absolute_scale': True,
            'vr_depth': -40,
            'position': p,
            'scale': (220.0*0.6,  220.0*0.6),
            'color': c2
        })
    self._stick_nub_position = p = (-328, 200)
    self._stick_nub_image_color = c3 = (0.4, 0.4, 0.4, 1.0)
    self._stick_nub_image = ba.newnode('image',
                                       attrs={
                                           'texture': ba.gettexture('nub'),
                                           'absolute_scale': True,
                                           'position': p,
                                           'scale': (110*0.6, 110*0.66),
                                           'color': c3
                                       })
    self._stick_base_image.opacity = 0.0
    self._stick_nub_image.opacity = 0.0
    self.set_stick_image_position = set_stick_image_position
    return original_on_begin(self, *args, **kwargs)




ba._activity.Activity.on_begin = on_begin
        # _ba.chatmessage = new_chatmessage
bastd.actor.playerspaz.PlayerSpaz = NewPlayerSpaz
bastd.actor.spaz.Spaz = NewSpaz


#  lets define a sample elimination game that can use super power of this plugin
