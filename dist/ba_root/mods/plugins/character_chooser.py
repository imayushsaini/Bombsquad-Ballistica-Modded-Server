# ba_meta require api 8

'''
Character Chooser by Mr.Smoothy

This plugin will let you choose your character from lobby.

Install this plugin on your Phone/PC  or on Server

If installed on server :- this will also let players choose server specific custom characters . so no more sharing of character file with all players,
just install this plugin on server ...and players can pick character from lobby .

Use:-
> select your profile (focus on color and name)
> press ready (punch)
> now use UP/DOWN buttons to scroll character list
> Press ready again (punch) to join the game
> or press Bomb button to go back to profile choosing menu
> END

Watch   : https://www.youtube.com/watch?v=hNmv2l-NahE
Join    : https://discord.gg/ucyaesh
Contact : discord mr.smoothy#5824


Share this plugin with your server owner /admins  to use it online

 :)

'''

from __future__ import annotations

import _babase
from typing import TYPE_CHECKING

import babase
import bauiv1 as bui
from babase._error import print_error
from babase._language import Lstr

if TYPE_CHECKING:
    from typing import Any, List, Dict, Union, Sequence, Optional
import weakref
from bascenev1._lobby import ChangeMessage, PlayerReadyMessage
from bascenev1 import _lobby
from bascenev1lib.actor.spazappearance import *


def __init__(self, vpos: float, sessionplayer: bs.SessionPlayer,
             lobby: 'Lobby') -> None:
    self._deek_sound = bs.getsound('deek')
    self._click_sound = bs.getsound('click01')
    self._punchsound = bs.getsound('punch01')
    self._swish_sound = bs.getsound('punchSwish')
    self._errorsound = bs.getsound('error')
    self._mask_texture = bs.gettexture('characterIconMask')
    self._vpos = vpos
    self._lobby = weakref.ref(lobby)
    self._sessionplayer = sessionplayer
    self._inited = False
    self._dead = False
    self._text_node: Optional[bs.Node] = None
    self._profilename = ''
    self._profilenames: List[str] = []
    self._ready: bool = False
    self._character_names: List[str] = []
    self._last_change: Sequence[Union[float, int]] = (0, 0)
    self._profiles: Dict[str, Dict[str, Any]] = {}

    app = babase.app

    self.bakwas_chars = ["Lee", "Todd McBurton", "Zola", "Butch", "Witch",
                         "warrior",
                         "Middle-Man", "Alien", "OldLady", "Gladiator",
                         "Wrestler", "Gretel", "Robot"]

    # Load available player profiles either from the local config or
    # from the remote device.
    self.reload_profiles()
    for name in bs.app.classic.spaz_appearances:
        if name not in self._character_names and name not in self.bakwas_chars:
            self._character_names.append(name)
    # Note: this is just our local index out of available teams; *not*
    # the team-id!
    self._selected_team_index: int = self.lobby.next_add_team

    # Store a persistent random character index and colors; we'll use this
    # for the '_random' profile. Let's use their input_device id to seed
    # it. This will give a persistent character for them between games
    # and will distribute characters nicely if everyone is random.
    self._random_color, self._random_highlight = (
        bs.get_player_profile_colors(None))

    # To calc our random character we pick a random one out of our
    # unlocked list and then locate that character's index in the full
    # list.
    char_index_offset = app.classic.lobby_random_char_index_offset
    self._random_character_index = (
        (sessionplayer.inputdevice.id + char_index_offset) %
        len(self._character_names))

    # Attempt to set an initial profile based on what was used previously
    # for this input-device, etc.
    self._profileindex = self._select_initial_profile()
    self._profilename = self._profilenames[self._profileindex]

    self._text_node = bs.newnode('text',
                                 delegate=self,
                                 attrs={
                                     'position': (-100, self._vpos),
                                     'maxwidth': 190,
                                     'shadow': 0.5,
                                     'vr_depth': -20,
                                     'h_align': 'left',
                                     'v_align': 'center',
                                     'v_attach': 'top'
                                 })
    bs.animate(self._text_node, 'scale', {0: 0, 0.1: 1.0})
    self.icon = bs.newnode('image',
                           owner=self._text_node,
                           attrs={
                               'position': (-130, self._vpos + 20),
                               'mask_texture': self._mask_texture,
                               'vr_depth': -10,
                               'attach': 'topCenter'
                           })

    bs.animate_array(self.icon, 'scale', 2, {0: (0, 0), 0.1: (45, 45)})

    # Set our initial name to '<choosing player>' in case anyone asks.
    self._sessionplayer.setname(
        Lstr(resource='choosingPlayerText').evaluate(), real=False)

    # Init these to our rando but they should get switched to the
    # selected profile (if any) right after.
    self._character_index = self._random_character_index
    self._color = self._random_color
    self._highlight = self._random_highlight
    self.characterchooser = False
    self.update_from_profile()
    self.update_position()
    self._inited = True

    self._set_ready(False)


def _set_ready(self, ready: bool) -> None:
    # pylint: disable=cyclic-import
    from bauiv1lib.profile import browser as pbrowser
    from babase._general import Call
    profilename = self._profilenames[self._profileindex]

    # Handle '_edit' as a special case.
    if profilename == '_edit' and ready:
        with _babase.Context('ui'):
            pbrowser.ProfileBrowserWindow(in_main_menu=False)

            # Give their input-device UI ownership too
            # (prevent someone else from snatching it in crowded games)
            _babase.set_ui_input_device(self._sessionplayer.inputdevice)
        return

    if ready == False:
        self._sessionplayer.assigninput(
            babase.InputType.LEFT_PRESS,
            Call(self.handlemessage, ChangeMessage('team', -1)))
        self._sessionplayer.assigninput(
            babase.InputType.RIGHT_PRESS,
            Call(self.handlemessage, ChangeMessage('team', 1)))
        self._sessionplayer.assigninput(
            babase.InputType.BOMB_PRESS,
            Call(self.handlemessage, ChangeMessage('character', 1)))
        self._sessionplayer.assigninput(
            babase.InputType.UP_PRESS,
            Call(self.handlemessage, ChangeMessage('profileindex', -1)))
        self._sessionplayer.assigninput(
            babase.InputType.DOWN_PRESS,
            Call(self.handlemessage, ChangeMessage('profileindex', 1)))
        self._sessionplayer.assigninput(
            (babase.InputType.JUMP_PRESS, babase.InputType.PICK_UP_PRESS,
             babase.InputType.PUNCH_PRESS),
            Call(self.handlemessage, ChangeMessage('ready', 1)))
        self._ready = False
        self._update_text()
        self._sessionplayer.setname('untitled', real=False)
    elif ready == True:
        self.characterchooser = True
        self._sessionplayer.assigninput(
            (babase.InputType.LEFT_PRESS, babase.InputType.RIGHT_PRESS,
             babase.InputType.UP_PRESS, babase.InputType.DOWN_PRESS,
             babase.InputType.JUMP_PRESS, babase.InputType.BOMB_PRESS,
             babase.InputType.PICK_UP_PRESS), self._do_nothing)
        self._sessionplayer.assigninput(
            (babase.InputType.UP_PRESS),
            Call(self.handlemessage, ChangeMessage('characterchooser', -1)))
        self._sessionplayer.assigninput(
            (babase.InputType.DOWN_PRESS),
            Call(self.handlemessage, ChangeMessage('characterchooser', 1)))
        self._sessionplayer.assigninput(
            (babase.InputType.BOMB_PRESS),
            Call(self.handlemessage, ChangeMessage('ready', 0)))

        self._sessionplayer.assigninput(
            (babase.InputType.JUMP_PRESS, babase.InputType.PICK_UP_PRESS,
             babase.InputType.PUNCH_PRESS),
            Call(self.handlemessage, ChangeMessage('ready', 2)))

        # Store the last profile picked by this input for reuse.
        input_device = self._sessionplayer.inputdevice
        name = input_device.name
        unique_id = input_device.unique_identifier
        device_profiles = _babase.app.config.setdefault(
            'Default Player Profiles', {})

        # Make an exception if we have no custom profiles and are set
        # to random; in that case we'll want to start picking up custom
        # profiles if/when one is made so keep our setting cleared.
        special = ('_random', '_edit', '__account__')
        have_custom_profiles = any(p not in special
                                   for p in self._profiles)

        profilekey = name + ' ' + unique_id
        if profilename == '_random' and not have_custom_profiles:
            if profilekey in device_profiles:
                del device_profiles[profilekey]
        else:
            device_profiles[profilekey] = profilename
        _babase.app.config.commit()

        # Set this player's short and full name.
        self._sessionplayer.setname(self._getname(),
                                    self._getname(full=True),
                                    real=True)
        self._ready = True
        self._update_text()
    else:

        # Inform the session that this player is ready.
        bs.getsession().handlemessage(PlayerReadyMessage(self))


def handlemessage(self, msg: Any) -> Any:
    """Standard generic message handler."""

    if isinstance(msg, ChangeMessage):
        self._handle_repeat_message_attack()

        # If we've been removed from the lobby, ignore this stuff.
        if self._dead:
            print_error('chooser got ChangeMessage after dying')
            return

        if not self._text_node:
            print_error('got ChangeMessage after nodes died')
            return
        if msg.what == 'characterchooser':
            self._click_sound.play()
            # update our index in our local list of characters
            self._character_index = ((self._character_index + msg.value) %
                                     len(self._character_names))
            self._update_text()
            self._update_icon()

        if msg.what == 'team':
            sessionteams = self.lobby.sessionteams
            if len(sessionteams) > 1:
                self._swish_sound.play()
            self._selected_team_index = (
                (self._selected_team_index + msg.value) %
                len(sessionteams))
            self._update_text()
            self.update_position()
            self._update_icon()

        elif msg.what == 'profileindex':
            if len(self._profilenames) == 1:

                # This should be pretty hard to hit now with
                # automatic local accounts.
                bui.getsound('error').play()
            else:

                # Pick the next player profile and assign our name
                # and character based on that.
                self._deek_sound.play()
                self._profileindex = ((self._profileindex + msg.value) %
                                      len(self._profilenames))
                self.update_from_profile()

        elif msg.what == 'character':
            self._click_sound.play()
            self.characterchooser = True
            # update our index in our local list of characters
            self._character_index = ((self._character_index + msg.value) %
                                     len(self._character_names))
            self._update_text()
            self._update_icon()

        elif msg.what == 'ready':
            self._handle_ready_msg(msg.value)


def _update_text(self) -> None:
    assert self._text_node is not None
    if self._ready:

        # Once we're ready, we've saved the name, so lets ask the system
        # for it so we get appended numbers and stuff.
        text = Lstr(value=self._sessionplayer.getname(full=True))
        if self.characterchooser:
            text = Lstr(value='${A}\n${B}',
                        subs=[('${A}', text),
                              ('${B}', Lstr(value="" + self._character_names[
                                  self._character_index]))])
            self._text_node.scale = 0.8
        else:
            text = Lstr(value='${A} (${B})',
                        subs=[('${A}', text),
                              ('${B}', Lstr(resource='readyText'))])
    else:
        text = Lstr(value=self._getname(full=True))
        self._text_node.scale = 1.0

    can_switch_teams = len(self.lobby.sessionteams) > 1

    # Flash as we're coming in.
    fin_color = _babase.safecolor(self.get_color()) + (1,)
    if not self._inited:
        bs.animate_array(self._text_node, 'color', 4, {
            0.15: fin_color,
            0.25: (2, 2, 2, 1),
            0.35: fin_color
        })
    else:

        # Blend if we're in teams mode; switch instantly otherwise.
        if can_switch_teams:
            bs.animate_array(self._text_node, 'color', 4, {
                0: self._text_node.color,
                0.1: fin_color
            })
        else:
            self._text_node.color = fin_color

    self._text_node.text = text


# ba_meta export plugin
def enable():
    _lobby.Chooser.__init__ = __init__
    _lobby.Chooser._set_ready = _set_ready

    _lobby.Chooser._update_text = _update_text
    _lobby.Chooser.handlemessage = handlemessage
