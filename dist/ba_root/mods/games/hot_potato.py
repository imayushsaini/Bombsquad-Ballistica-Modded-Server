"""
    
    Hot Potato by TheMikirog#1984
    
    A random player(s) gets Marked. 
    They will die if they don't pass the mark to other players.
    After they die, another random player gets Marked.
    Last player standing wins!
    
    Heavily commented for easy modding learning!

    No Rights Reserved

"""

# ba_meta require api 7

from __future__ import annotations

from typing import TYPE_CHECKING

# Define only what we need and nothing more
import ba
from bastd.actor.spaz import SpazFactory
from bastd.actor.spaz import PickupMessage
from bastd.actor.spaz import BombDiedMessage
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.bomb import Bomb
from bastd.actor.bomb import Blast
from enum import Enum
import random

if TYPE_CHECKING:
    pass
    
# Let's define stun times for falling.
# First element is stun for the first fall, second element is stun for the second fall and so on.
# If we fall more than the amount of elements on this list, we'll use the last entry.
FALL_PENALTIES = [1.5, 
                  2.5,
                  3.5,
                  5.0, 
                  6.0, 
                  7.0, 
                  8.0, 
                  9.0,
                  10.0]
    
RED_COLOR = (1.0, 0.2, 0.2)
YELLOW_COLOR = (1.0, 1.0, 0.2)
                  
    
# The player in Hot Potato can be in one of these states:
class PlayerState(Enum):
    # REGULAR - the state all players start in.
    REGULAR = 0
    # MARKED - when a player is marked, they'll be eliminated when the timer hits zero.
    # Marked players pass the mark to REGULAR or STUNNED players by harming or grabbing other players.
    # MARKED players respawn instantly if they somehow get knocked off the map.
    MARKED = 1
    # ELIMINATED - a player is eliminated if the timer runs out during the MARKED state or they leave the game.
    # These players can't win and won't respawn.
    ELIMINATED = 2
    # STUNNED - if a REGULAR player falls out of the map, they'll receive the STUNNED state.
    # STUNNED players are incapable of all movement and actions.
    # STUNNED players can still get MARKED, but can't be punched, grabbed or knocked around by REGULAR players.
    # STUNNED players will go back to the REGULAR state after several seconds.
    # The time it takes to go back to the REGULAR state gets more severe the more times the player dies by falling off the map.
    STUNNED = 3

# To make the game easier to parse, I added Elimination style icons to the bottom of the screen.
# Here's the behavior of each icon.
class Icon(ba.Actor):
    """Creates in in-game icon on screen."""

    def __init__(self,
                 player: Player,
                 position: tuple[float, float],
                 scale: float,
                 name_scale: float = 1.0,
                 name_maxwidth: float = 100.0,
                 shadow: float = 1.0):
        super().__init__()

        # Define the player this icon belongs to
        self._player = player
        self._name_scale = name_scale
        
        self._outline_tex = ba.gettexture('characterIconMask')

        # Character portrait
        icon = player.get_icon()
        self.node = ba.newnode('image',
                               delegate=self,
                               attrs={
                                   'texture': icon['texture'],
                                   'tint_texture': icon['tint_texture'],
                                   'tint_color': icon['tint_color'],
                                   'vr_depth': 400,
                                   'tint2_color': icon['tint2_color'],
                                   'mask_texture': self._outline_tex,
                                   'opacity': 1.0,
                                   'absolute_scale': True,
                                   'attach': 'bottomCenter'
                               })
        # Player name
        self._name_text = ba.newnode(
            'text',
            owner=self.node,
            attrs={
                'text': ba.Lstr(value=player.getname()),
                'color': ba.safecolor(player.team.color),
                'h_align': 'center',
                'v_align': 'center',
                'vr_depth': 410,
                'maxwidth': name_maxwidth,
                'shadow': shadow,
                'flatness': 1.0,
                'h_attach': 'center',
                'v_attach': 'bottom'
            })
        # Status text (such as Marked!, Stunned! and You're Out!)
        self._marked_text = ba.newnode(
            'text',
            owner=self.node,
            attrs={
                'text': '',
                'color': (1, 0.1, 0.0),
                'h_align': 'center',
                'v_align': 'center',
                'vr_depth': 430,
                'shadow': 1.0,
                'flatness': 1.0,
                'h_attach': 'center',
                'v_attach': 'bottom'
            })
        # Status icon overlaying the character portrait
        self._marked_icon = ba.newnode(
            'text',
            owner=self.node,
            attrs={
                'text': ba.charstr(ba.SpecialChar.HAL),
                'color': (1, 1, 1),
                'h_align': 'center',
                'v_align': 'center',
                'vr_depth': 430,
                'shadow': 0.0,
                'opacity': 0.0,
                'flatness': 1.0,
                'scale': 2.1,
                'h_attach': 'center',
                'v_attach': 'bottom'
            })
        self.set_marked_icon(player.state)
        self.set_position_and_scale(position, scale)
        
    # Change our icon's appearance depending on the player state.
    def set_marked_icon(self, type: PlayerState) -> None:
        pos = self.node.position
        # Regular players get no icons or status text
        if type is PlayerState.REGULAR:
            self._marked_icon.text = ''
            self._marked_text.text = ''
            self._marked_icon.opacity = 0.0
            self._name_text.flatness = 1.0
            assert self.node
            self.node.color = (1.0, 1.0, 1.0)
        # Marked players get ALL of the attention - red portrait, red text and icon overlaying the portrait
        elif type is PlayerState.MARKED:
            self._marked_icon.text = ba.charstr(ba.SpecialChar.HAL)
            self._marked_icon.position = (pos[0] - 1, pos[1] - 13)
            self._marked_icon.opacity = 1.0
            self._marked_text.text = 'Marked!'
            self._marked_text.color = (1.0, 0.0, 0.0)
            self._name_text.flatness = 0.0
            assert self.node
            self.node.color = (1.0, 0.2, 0.2)
        # Stunned players are just as important - yellow portrait, yellow text and moon icon.
        elif type is PlayerState.STUNNED:
            self._marked_icon.text = ba.charstr(ba.SpecialChar.MOON)
            self._marked_icon.position = (pos[0] - 2, pos[1] - 12)
            self._marked_icon.opacity = 1.0
            self._marked_text.text = 'Stunned!'
            self._marked_text.color = (1.0, 1.0, 0.0)
            assert self.node
            self.node.color = (0.75, 0.75, 0.0)
        # Eliminated players get special treatment.
        # We make the portrait semi-transparent, while adding some visual flair with an fading skull icon and text.
        elif type is PlayerState.ELIMINATED:
            self._marked_icon.text = ba.charstr(ba.SpecialChar.SKULL)
            self._marked_icon.position = (pos[0] - 2, pos[1] - 12)
            self._marked_text.text = 'You\'re Out!'
            self._marked_text.color = (0.5, 0.5, 0.5)
            
            # Animate text and icon
            animation_end_time = 1.5 if bool(self.activity.settings['Epic Mode']) else 3.0
            ba.animate(self._marked_icon,'opacity', {
                0: 1.0,
                animation_end_time: 0.0})
            ba.animate(self._marked_text,'opacity', {
                       0: 1.0,
                       animation_end_time: 0.0})
            
            self._name_text.opacity = 0.2
            assert self.node
            self.node.color = (0.7, 0.3, 0.3)
            self.node.opacity = 0.2
        else:
            # If we beef something up, let the game know we made a mess in the code by providing a non-existant state.
            raise Exception("invalid PlayerState type")

    # Set where our icon is positioned on the screen and how big it is.
    def set_position_and_scale(self, position: tuple[float, float],
                               scale: float) -> None:
        """(Re)position the icon."""
        assert self.node
        self.node.position = position
        self.node.scale = [70.0 * scale]
        self._name_text.position = (position[0], position[1] + scale * 52.0)
        self._name_text.scale = 1.0 * scale * self._name_scale
        self._marked_text.position = (position[0], position[1] - scale * 52.0)
        self._marked_text.scale = 0.8 * scale

# This gamemode heavily relies on edited player behavior.
# We need that amount of control, so we're gonna create our own class and use the original PlayerSpaz as our blueprint.
class PotatoPlayerSpaz(PlayerSpaz):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs) # unchanged Spaz __init__ code goes here
        self.dropped_bombs = [] # we use this to track bombs thrown by the player
        
        # Define a marked light
        self.marked_light = ba.newnode('light',
                               owner=self.node,
                               attrs={'position':self.node.position,
                                      'radius':0.15,
                                      'intensity':0.0,
                                      'height_attenuated':False,
                                      'color': (1.0, 0.0, 0.0)})
        
        # Pulsing red light when the player is Marked
        ba.animate(self.marked_light,'radius',{
            0: 0.1,
            0.3: 0.15,
            0.6: 0.1},
            loop = True)
        self.node.connectattr('position_center',self.marked_light,'position')
        
        # Marked timer. It should be above our head, so we attach the text to the offset that's attached to the player.
        self.marked_timer_offset = ba.newnode('math', owner = self.node, attrs = {
            'input1': (0, 1.2, 0),
            'operation': 'add'})
        self.node.connectattr('torso_position', self.marked_timer_offset, 'input2')
        
        self.marked_timer_text = ba.newnode('text', owner = self.node, attrs = {
                'text': '',
                'in_world': True,
                'shadow': 0.4,
                'color': (RED_COLOR[0], RED_COLOR[1], RED_COLOR[2], 0.0),
                'flatness': 0,
                'scale': 0.02,
                'h_align': 'center'})
        self.marked_timer_offset.connectattr('output', self.marked_timer_text, 'position')
        
    # Modified behavior when dropping bombs
    def drop_bomb(self) -> stdbomb.Bomb | None:
        # The original function returns the Bomb the player created.
        # This is super helpful for us, since all we need is to mark the bombs red 
        # if they belong to the Marked player and nothing else.
        bomb = super().drop_bomb()
        # Let's make sure the player actually created a new bomb
        if bomb:
            # Add our bomb to the list of our tracked bombs
            self.dropped_bombs.append(bomb)
            # Bring a light
            bomb.bomb_marked_light = ba.newnode('light',
                                            owner=bomb.node,
                                            attrs={'position':bomb.node.position,
                                                   'radius':0.04,
                                                   'intensity':0.0,
                                                   'height_attenuated':False,
                                                   'color': (1.0, 0.0, 0.0)})
            # Attach the light to the bomb
            bomb.node.connectattr('position',bomb.bomb_marked_light,'position')
            # Let's adjust all lights for all bombs that we own.
            self.set_bombs_marked()
            # When the bomb physics node dies, call a function.
            bomb.node.add_death_action(
                ba.WeakCall(self.bomb_died, bomb))
                
                
    # Here's the function that gets called when one of the player's bombs dies.
    # We reference the player's dropped_bombs list and remove the bomb that died.
    def bomb_died(self, bomb):
        self.dropped_bombs.remove(bomb)
            
    # Go through all the bombs this player has in the world.
    # Paint them red if the owner is marked, turn off the light otherwise.
    # We need this light to inform the player about bombs YOU DON'T want to get hit by.
    def set_bombs_marked(self):
        for bomb in self.dropped_bombs:
            bomb.bomb_marked_light.intensity = 20.0 if self._player.state == PlayerState.MARKED else 0.0
        
    # Since our gamemode relies heavily on players passing the mark to other players
    # we need to have access to this message. This gets called when the player takes damage for any reason.
    def handlemessage(self, msg):
        if isinstance(msg, ba.HitMessage):
            # This is basically the same HitMessage code as in the original Spaz.
            # The only difference is that there is no health bar and you can't die with punches or bombs.
            # Also some useless or redundant code was removed.
            # I'm still gonna comment all of it since we're here.
            if not self.node:
                return None
                
            # If the attacker is marked, pass that mark to us.
            self.activity.pass_mark(msg._source_player, self._player)
            
            # When stun timer runs out, we explode. Let's make sure our own explosion does throw us around.
            if msg.hit_type == 'stun_blast' and msg._source_player == self.source_player: return True
            # If the attacker is healthy and we're stunned, do a flash and play a sound, then ignore the rest of the code.
            if self.source_player.state == PlayerState.STUNNED and msg._source_player != PlayerState.MARKED:
                self.node.handlemessage('flash')
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True
                
            # Here's all the damage and force calculations unchanged from the source.
            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            # We use them to apply a physical force to the player.
            # Normally this is also used for damage, but we we're not gonna do it.
            # We're still gonna calculate it, because it's still responsible for knockback.
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                velocity_mag, msg.radius, 0, msg.force_direction[0],
                msg.force_direction[1], msg.force_direction[2])
            damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound') # That's how we play spaz node's hurt sound
            
            # Play punch impact sounds based on damage if it was a punch.
            # We don't show damage percentages, because it's irrelevant.
            if msg.hit_type == 'punch':
                self.on_punched(damage)

                if damage >= 500:
                    sounds = SpazFactory.get().punch_sound_strong
                    sound = sounds[random.randrange(len(sounds))]
                elif damage >= 100:
                    sound = SpazFactory.get().punch_sound
                else:
                    sound = SpazFactory.get().punch_sound_weak
                ba.playsound(sound, 1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(damage * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                ba.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(damage * 0.04)),
                          scale=0.9,
                          spread=0.28)

                # Momentary flash. This spawns around where the Spaz's punch would be (we're kind of guessing here).
                hurtiness = damage * 0.003
                punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                            msg.pos[1] + msg.force_direction[1] * 0.02,
                            msg.pos[2] + msg.force_direction[2] * 0.02)
                flash_color = (1.0, 0.8, 0.4)
                light = ba.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color
                    })
                ba.timer(0.06, light.delete)

                flash = ba.newnode('flash',
                                   attrs={
                                       'position': punchpos,
                                       'size': 0.17 + 0.17 * hurtiness,
                                       'color': flash_color
                                   })
                ba.timer(0.06, flash.delete)

            # Physics collision particles.
            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)
                          
            # Briefly flash when hit.
            # We shouldn't do this if we're dead.
            if self.hitpoints > 0:

                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
        # If we get grabbed, this function is called.
        # We want to pass along the mark with grabs too.
        elif isinstance(msg, PickupMessage):
            # Make sure our body exists.
            if not self.node:
                return None
                
            # Let's get all collision data if we can. Otherwise cancel.
            try:
                collision = ba.getcollision()
                opposingnode = collision.opposingnode
            except ba.NotFoundError:
                return True
                
            # Our grabber needs to be a Spaz
            if opposingnode.getnodetype() == 'spaz':
                # Disallow grabbing if a healthy player tries to grab us and we're stunned.
                # If they're marked, continue with our scheduled program.
                # It's the same sound and flashing behavior as hitting a stunned player as a healthy player.
                if (opposingnode.source_player.state == PlayerState.STUNNED and self.source_player.state != PlayerState.MARKED):
                    opposingnode.handlemessage('flash')
                    ba.playsound(SpazFactory.get().block_sound,
                                 1.0,
                                 position=opposingnode.position)
                    return True
                # If they're marked and we're healthy or stunned, pass that mark along to us.
                elif opposingnode.source_player.state in [PlayerState.REGULAR, PlayerState.STUNNED] and self.source_player.state == PlayerState.MARKED:
                    self.activity.pass_mark(self.source_player, opposingnode.source_player)
                
            # Our work is done. Continue with the rest of the grabbing behavior as usual.
            super().handlemessage(msg)
        # Dying is important in this gamemode and as such we need to address this behavior.
        elif isinstance(msg, ba.DieMessage):
            
            # If a player left the game, inform our gamemode logic.
            if msg.how == ba.DeathType.LEFT_GAME:
                self.activity.player_left(self.source_player)
                
            # If a MARKED or STUNNED player dies, hide the text from the previous spaz.
            if self.source_player.state in [PlayerState.MARKED, PlayerState.STUNNED]:
                self.marked_timer_text.color = (self.marked_timer_text.color[0],
                                                self.marked_timer_text.color[1],
                                                self.marked_timer_text.color[2],
                                                0.0)
                ba.animate(self.marked_light,'intensity',{
                        0: self.marked_light.intensity,
                        0.5: 0.0})
            
            # Continue with the rest of the behavior.
            super().handlemessage(msg)
        # If a message is something we haven't modified yet, let's pass it along to the original.
        else: super().handlemessage(msg)
    
# A concept of a player is very useful to reference if we don't have a player character present (maybe they died).
class Player(ba.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        # Most of these are self explanatory.
        self.icon: Icon = None
        self.fall_times: int = 0
        self.state: PlayerState = PlayerState.REGULAR
        self.stunned_time_remaining = None
        # These are references to timers responsible for handling stunned behavior.
        self.stunned_timer = None
        self.stunned_update_timer = None
        
    # If we're stunned, a timer calls this every 0.1 seconds.
    def stunned_timer_tick(self) -> None:
        # Decrease our time remaining then change the text displayed above the Spaz's head 
        self.stunned_time_remaining -= 0.1
        self.stunned_time_remaining = max(0.0, self.stunned_time_remaining)
        self.actor.marked_timer_text.text = str(round(self.stunned_time_remaining, 2))
        
    # When stun time is up, call this function.
    def stun_remove(self) -> None:
        # Let's proceed only if we're stunned
        if self.state != PlayerState.STUNNED: return
        # Do an explosion where we're standing. Normally it would throw us around, but we dealt 
        # with this issue in PlayerSpaz's edited HitMessage in line 312.
        Blast(position=self.actor.node.position,
              velocity=self.actor.node.velocity,
              blast_radius=2.5,
              hit_type='stun_blast', # This hit type allows us to ignore our own stun blast explosions.
              source_player=self).autoretain()
        # Let's switch our state back to healthy.
        self.set_state(PlayerState.REGULAR)
        
    # States are a key part of this gamemode and a lot of logic has to be done to acknowledge these state changes.
    def set_state(self, state: PlayerState) -> None:
        # Let's remember our old state before we change it.
        old_state = self.state
        
        # If we just became stunned, do all of this:
        if old_state != PlayerState.STUNNED and state == PlayerState.STUNNED:
            self.actor.disconnect_controls_from_player() # Disallow all movement and actions
            # Let's set our stun time based on the amount of times we fell out of the map.
            if self.fall_times < len(FALL_PENALTIES):
                stun_time = FALL_PENALTIES[self.fall_times]
            else:
                stun_time = FALL_PENALTIES[len(FALL_PENALTIES) - 1]
                
            self.stunned_time_remaining = stun_time # Set our stun time remaining
            self.stunned_timer = ba.Timer(stun_time + 0.1, ba.Call(self.stun_remove)) # Remove our stun once the time is up
            self.stunned_update_timer = ba.Timer(0.1, ba.Call(self.stunned_timer_tick), repeat = True) # Call a function every 0.1 seconds
            self.fall_times += 1 # Increase the amount of times we fell by one
            self.actor.marked_timer_text.text = str(stun_time) # Change the text above the Spaz's head to total stun time
            
        # If we were stunned, but now we're not, let's reconnect our controls.
        # CODING CHALLENGE: to punch or bomb immediately after the stun ends, you need to 
        # time the button press frame-perfectly in order for it to work.
        # What if we could press the button shortly before stun ends to do the action as soon as possible?
        # If you're feeling up to the challenge, feel free to implement that!
        if old_state == PlayerState.STUNNED and state != PlayerState.STUNNED:
            self.actor.connect_controls_to_player()
            
        # When setting a state that is not STUNNED, clear all timers.
        if state != PlayerState.STUNNED:
            self.stunned_timer = None
            self.stunned_update_timer = None
            
        # Here's all the light and text colors that we set depending on the state.
        if state == PlayerState.MARKED:
            self.actor.marked_light.intensity = 1.5
            self.actor.marked_light.color = (1.0, 0.0, 0.0)
            self.actor.marked_timer_text.color = (RED_COLOR[0],
                                                  RED_COLOR[1],
                                                  RED_COLOR[2],
                                                  1.0)
        elif state == PlayerState.STUNNED:
            self.actor.marked_light.intensity = 0.5
            self.actor.marked_light.color = (1.0, 1.0, 0.0)
            self.actor.marked_timer_text.color = (YELLOW_COLOR[0],
                                                  YELLOW_COLOR[1],
                                                  YELLOW_COLOR[2],
                                                  1.0)
        else:
            self.actor.marked_light.intensity = 0.0
            self.actor.marked_timer_text.text = ''
        
        self.state = state
        self.actor.set_bombs_marked() # Light our bombs red if we're Marked, removes the light otherwise
        self.icon.set_marked_icon(state) # Update our icon
        

# ba_meta export game
class HotPotato(ba.TeamGameActivity[Player, ba.Team]):

    # Let's define the basics like the name of the game, description and some tips that should appear at the start of a match.
    name = 'Hot Potato'
    description = ('A random player gets marked.\n'
                   'Pass the mark to other players.\n'
                   'Marked player gets eliminated when time runs out.\n'
                   'Last one standing wins!')
    tips = [
        'You can pass the mark not only with punches and grabs, but bombs as well.',
        'If you\'re not marked, DON\'T fall off the map!\nEach fall will be punished with immobility.',
        'Falling can be a good escape strategy, but don\'t over rely on it.\nYou\'ll be defenseless if you respawn!',
        'Stunned players are immune to healthy players, but not to Marked players!',
        'Each fall when not Marked increases your time spent stunned.',
        'Try throwing healthy players off the map to make their timers\nlonger the next time they get stunned.',
        'Marked players don\'t get stunned when falling off the map.',
        'For total disrespect, try throwing the Marked player off the map\nwithout getting marked yourself!',
        'Feeling evil? Throw healthy players towards the Marked player!',
        'Red bombs belong to the Marked player!\nWatch out for those!',
        'Stunned players explode when their stun timer runs out.\nIf that time is close to zero, keep your distance!'
    ]
    
    # We're gonna distribute end of match session scores based on who dies first and who survives.
    # First place gets most points, then second, then third.
    scoreconfig = ba.ScoreConfig(label='Place',
                                 scoretype=ba.ScoreType.POINTS,
                                 lower_is_better=True)
    
    # These variables are self explanatory too.
    show_kill_points = False
    allow_mid_activity_joins = False
    
    # Let's define some settings the user can mess around with to fit their needs.
    available_settings = [
        ba.IntSetting('Elimination Timer',
            min_value=5,
            default=15,
            increment=1,
        ),
        ba.BoolSetting('Marked Players use Impact Bombs', default=False),
        ba.BoolSetting('Epic Mode', default=False),
    ]
    
    # Hot Potato is strictly a Free-For-All gamemode, so only picking the gamemode in FFA playlists.
    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.FreeForAllSession)

    # Most maps should work in Hot Potato. Generally maps marked as 'melee' are the most versatile map types of them all.
    # As the name implies, fisticuffs are common forms of engagement.
    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ba.getmaps('melee')
        
    # Here we define everything the gamemode needs, like sounds and settings.
    def __init__(self, settings: dict):
        super().__init__(settings)
        self.settings = settings
        
        # Let's define all of the sounds we need.
        self._tick_sound = ba.getsound('tick')
        self._player_eliminated_sound = ba.getsound('playerDeath')
        # These next sounds are arrays instead of single sounds.
        # We'll use that fact later.
        self._danger_tick_sounds = [ba.getsound('orchestraHit'),
                                    ba.getsound('orchestraHit2'),
                                    ba.getsound('orchestraHit3')]
        self._marked_sounds = [ba.getsound('powerdown01'),
                               ba.getsound('activateBeep'),
                               ba.getsound('hiss')]
        
        # Normally play KOTH music, but switch to Epic music if we're in slow motion.
        self._epic_mode = bool(settings['Epic Mode'])
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.SCARY)
                  
    # This description appears below the title card after it comes crashing when the game begins.
    def get_instance_description(self) -> str | Sequence:
        return 'Pass the mark to someone else before you explode!'

    # This is the tiny text that is displayed in the corner during the game as a quick reminder of the objective.
    def get_instance_description_short(self) -> str | Sequence:
        return 'pass the mark'
        
    # Set up our player every time they join.
    # Because you can't join mid-match, this will always be called at the beginning of the game.
    def on_player_join(self, player: Player) -> None:
    
        player.state = PlayerState.REGULAR
        player.fall_times = 0

        # Create our icon and spawn.
        if not self.has_begun():
            player.icon = Icon(player, position=(0, 50), scale=0.8)
        self.spawn_player(player)
            
    # Returns every single marked player.
    # This piece of info is used excensively in this gamemode, so it's advantageous to have a function to cut on
    # work and make the gamemode easier to maintain
    def get_marked_players(self) -> Sequence[ba.Player]:
        marked_players = []
        for p in self.players:
            if p.state == PlayerState.MARKED:
                marked_players.append(p)
        return marked_players
            
    # Marks a player. This sets their state, spawns some particles and sets the timer text above their heads.
    def mark(self, target: Player) -> None:
        target.set_state(PlayerState.MARKED)
                                                
        ba.emitfx(position=target.actor.node.position,
                  velocity=target.actor.node.velocity,
                  chunk_type='spark',
                  count=int(20.0+random.random()*20),
                  scale=1.0,
                  spread=1.0);
        if bool(self.settings['Marked Players use Impact Bombs']):
            target.actor.bomb_type = 'impact'
        target.actor.marked_timer_text.text = str(self.elimination_timer_display)
        
    # Removes the mark from the player. This restores the player to its initial state.
    def remove_mark(self, target: Player) -> None:
        if target.state != PlayerState.MARKED: 
            return
            
        target.actor.bomb_type = 'normal'
        
        target.set_state(PlayerState.REGULAR)
        target.actor.marked_timer_text.text = ''
        
    # Pass the mark from one player to another.
    # This is more desirable than calling mark and remove_mark functions constantly and gives us
    # more control over the mark spreading mechanic.
    def pass_mark(self, marked_player: Player, hit_player: Player) -> None:
        # Make sure both players meet the requirements
        if not marked_player or not hit_player: return
        if marked_player.state == PlayerState.MARKED and hit_player.state != PlayerState.MARKED:
            self.mark(hit_player)
            self.remove_mark(marked_player)
        
    # This function is called every second a marked player exists.
    def _eliminate_tick(self) -> None:
        marked_players = self.get_marked_players()
        marked_player_amount = len(marked_players)
        
        # If there is no marked players, raise an exception.
        # This is used for debugging purposes, which lets us know we messed up somewhere else in the code.
        if len(self.get_marked_players()) == 0:
            raise Exception("no marked players!")
            
        if self.elimination_timer_display > 1:
            self.elimination_timer_display -= 1 # Decrease our timer by one second.
            sound_volume = 1.0 / marked_player_amount
            
            for target in marked_players:
                ba.playsound(self._tick_sound, sound_volume, target.actor.node.position)
                target.actor.marked_timer_text.text = str(self.elimination_timer_display)
                
            # When counting down 3, 2, 1 play some dramatic sounds
            if self.elimination_timer_display <= 3:
                # We store our dramatic sounds in an array, so we target a specific element on the array
                # depending on time remaining. Arrays start at index 0, so we need to decrease 
                # our variable by 1 to get the element index.
                ba.playsound(self._danger_tick_sounds[self.elimination_timer_display - 1], 1.5)
        else:
            # Elimination timer is up! Let's eliminate all marked players.
            self.elimination_timer_display -= 1 # Decrease our timer by one second.
            self._eliminate_marked_players()
        
    # This function explodes all marked players
    def _eliminate_marked_players(self) -> None:
        self.marked_tick_timer = None
        for target in self.get_marked_players():
            target.set_state(PlayerState.ELIMINATED)
            target.actor.marked_timer_text.text = ''
            
            Blast(position=target.actor.node.position,
                  velocity=target.actor.node.velocity,
                  blast_radius=3.0,
                  source_player=target).autoretain()
            ba.emitfx(position=target.actor.node.position,
                      velocity=target.actor.node.velocity,
                      count=int(16.0+random.random()*60),
                      scale=1.5,
                      spread=2,
                      chunk_type='spark')
            target.actor.handlemessage(ba.DieMessage(how='marked_elimination'))
            target.actor.shatter(extreme=True)
            
            self.match_placement.append(target.team)
            
        ba.playsound(self._player_eliminated_sound, 1.0)
        
        # Let the gamemode know a Marked 
        self.marked_players_died()
        
    # This function should be called when a Marked player dies, like when timer runs out or they leave the game.
    def marked_players_died(self) -> bool:
        alive_players = self.get_alive_players()
        # Is there only one player remaining? Or none at all? Let's end the gamemode
        if len(alive_players) < 2:
            if len(alive_players) == 1:
                self.match_placement.append(alive_players[0].team) # Let's add our lone survivor to the match placement list.
            # Wait a while to let this sink in before we announce our victor.
            self._end_game_timer = ba.Timer(1.25, ba.Call(self.end_game))
        else:
            # There's still players remaining, so let's wait a while before marking a new player.
            self.new_mark_timer = ba.Timer(2.0 if self.slow_motion else 4.0, ba.Call(self.new_mark))
        
    # Another extensively used function that returns all alive players.
    def get_alive_players(self) -> Sequence[ba.Player]:
        alive_players = []
        for player in self.players:
            if player.state == PlayerState.ELIMINATED: continue # Ignore players who have been eliminated
            if player.is_alive():
                alive_players.append(player)
        return alive_players
        
    # This function is called every time we want to start a new "round" by marking a random player.
    def new_mark(self) -> None:
    
        # Don't mark a new player if we've already announced a victor.
        if self.has_ended():
            return
            
        possible_targets = self.get_alive_players()
        all_victims = []
        # Let's mark TWO players at once if there's 6 or more players. Helps with the pacing.
        multi_choice = len(possible_targets) > 5
            
        if multi_choice:
            # Pick our first victim at random.
            first_victim = random.choice(possible_targets)
            all_victims.append(first_victim)
            possible_targets.remove(first_victim)
            # Let's pick our second victim, but this time excluding the player we picked earlier.
            all_victims.append(random.choice(possible_targets))
        else:
            # Pick one victim at random.
            all_victims = [random.choice(possible_targets)]
        
        self.elimination_timer_display = self.settings['Elimination Timer'] # Set time until marked players explode
        self.marked_tick_timer = ba.Timer(1.0, ba.Call(self._eliminate_tick), repeat=True) # Set a timer that calls _eliminate_tick every second
        # Mark all chosen victims and play a sound
        for new_victim in all_victims:
            # _marked_sounds is an array.
            # To make a nice marked sound effect, I play multiple sounds at once
            # All of them are contained in the array.
            for sound in self._marked_sounds:
                ba.playsound(sound, 1.0, new_victim.actor.node.position)
            self.mark(new_victim)
        
    # This function is called when the gamemode first loads.
    def on_begin(self) -> None:
        super().on_begin() # Do standard gamemode on_begin behavior
        
        self.elimination_timer_display = 0
        self.match_placement = []
        
        # End the game if there's only one player
        if len(self.players) < 2:
            self.match_placement.append(self.players[0].team)
            self._round_end_timer = ba.Timer(0.5, self.end_game)
        else:
            # Pick random player(s) to get marked
            self.new_mark_timer = ba.Timer(2.0 if self.slow_motion else 5.2, ba.Call(self.new_mark))
        
        self._update_icons() # Create player state icons
        
    # This function creates and positions player state icons
    def _update_icons(self):
        count = len(self.teams)
        x_offs = 100
        xval = x_offs * (count - 1) * -0.5
        # FUN FACT: In FFA games, every player belongs to a one-player team.
        for team in self.teams:
            if len(team.players) == 1:
                player = team.players[0]
                player.icon.set_position_and_scale((xval, 50), 0.8)
                xval += x_offs
                
    # Hot Potato can be a bit much, so I opted to show gameplay tips at the start of the match.
    # However because I put player state icons, the tips overlay the icons.
    # I'm gonna modify this function to move the tip text above the icons.
    def _show_tip(self) -> None:
    
        from ba._gameutils import animate, GameTip
        from ba._generated.enums import SpecialChar
        from ba._language import Lstr

        # If there's any tips left on the list, display one.
        if self.tips:
            tip = self.tips.pop(random.randrange(len(self.tips)))
            tip_title = Lstr(value='${A}:',
                             subs=[('${A}', Lstr(resource='tipText'))])
            icon: ba.Texture | None = None
            sound: ba.Sound | None = None
            if isinstance(tip, GameTip):
                icon = tip.icon
                sound = tip.sound
                tip = tip.text
                assert isinstance(tip, str)

            # Do a few replacements.
            tip_lstr = Lstr(translate=('tips', tip),
                            subs=[('${PICKUP}',
                                   ba.charstr(SpecialChar.TOP_BUTTON))])
            base_position = (75, 50)
            tip_scale = 0.8
            tip_title_scale = 1.2
            vrmode = ba.app.vr_mode

            t_offs = -350.0
            height_offs = 100.0
            tnode = ba.newnode('text',
                                attrs={
                                    'text': tip_lstr,
                                    'scale': tip_scale,
                                    'maxwidth': 900,
                                    'position': (base_position[0] + t_offs,
                                                 base_position[1] + height_offs),
                                    'h_align': 'left',
                                    'vr_depth': 300,
                                    'shadow': 1.0 if vrmode else 0.5,
                                    'flatness': 1.0 if vrmode else 0.5,
                                    'v_align': 'center',
                                    'v_attach': 'bottom'
                                })
            t2pos = (base_position[0] + t_offs - (20 if icon is None else 82),
                     base_position[1] + 2 + height_offs)
            t2node = ba.newnode('text',
                                 owner=tnode,
                                 attrs={
                                     'text': tip_title,
                                     'scale': tip_title_scale,
                                     'position': t2pos,
                                     'h_align': 'right',
                                     'vr_depth': 300,
                                     'shadow': 1.0 if vrmode else 0.5,
                                     'flatness': 1.0 if vrmode else 0.5,
                                     'maxwidth': 140,
                                     'v_align': 'center',
                                     'v_attach': 'bottom'
                                 })
            if icon is not None:
                ipos = (base_position[0] + t_offs - 40, base_position[1] + 1 + height_offs)
                img = ba.newnode('image',
                                  attrs={
                                      'texture': icon,
                                      'position': ipos,
                                      'scale': (50, 50),
                                      'opacity': 1.0,
                                      'vr_depth': 315,
                                      'color': (1, 1, 1),
                                      'absolute_scale': True,
                                      'attach': 'bottomCenter'
                                  })
                animate(img, 'opacity', {0: 0, 1.0: 1, 4.0: 1, 5.0: 0})
                ba.timer(5.0, img.delete)
            if sound is not None:
                ba.playsound(sound)

            combine = ba.newnode('combine',
                                  owner=tnode,
                                  attrs={
                                      'input0': 1.0,
                                      'input1': 0.8,
                                      'input2': 1.0,
                                      'size': 4
                                  })
            combine.connectattr('output', tnode, 'color')
            combine.connectattr('output', t2node, 'color')
            animate(combine, 'input3', {0: 0, 1.0: 1, 4.0: 1, 5.0: 0})
            ba.timer(5.0, tnode.delete)

    # This function is called when a player leaves the game.
    # This is only called when the player already joined with a character.
    def player_left(self, player: Player) -> None:
        # If the leaving player is marked, remove the mark
        if player.state == PlayerState.MARKED:
            self.remove_mark(player)
        
        # If the leaving player is stunned, remove all stun timers
        elif player.state == PlayerState.STUNNED:
            player.stunned_timer = None
            player.stunned_update_timer = None
        
        if len(self.get_marked_players()) == len(self.get_alive_players()):
            for i in self.get_marked_players():
                self.remove_mark(i)
                
        if len(self.get_marked_players()) == 0:
            self.marked_tick_timer = None
            self.marked_players_died()
            
        player.set_state(PlayerState.ELIMINATED)
                
    # This function is called every time a player spawns
    def spawn_player(self, player: Player) -> ba.Actor:
        position = self.map.get_ffa_start_position(self.players)
        position = (position[0],
                    position[1] - 0.3, # Move the spawn a bit lower
                    position[2])
        
        name = player.getname()
        
        light_color = ba.normalized_color(player.color)
        display_color = ba.safecolor(player.color, target_intensity=0.75)
        
        # Here we actually crate the player character
        spaz = PotatoPlayerSpaz(color=player.color,
                                highlight=player.highlight,
                                character=player.character,
                                player=player)
        spaz.node.invincible = False # Immediately turn off invincibility
        player.actor = spaz # Assign player character to the owner
        
        spaz.node.name = name
        spaz.node.name_color = display_color
        spaz.connect_controls_to_player()
        
        # Move to the stand position and add a flash of light
        spaz.handlemessage(ba.StandMessage(position, random.uniform(0, 360)))
        t = ba.time(ba.TimeType.BASE)
        ba.playsound(self._spawn_sound, 1.0, position=spaz.node.position)
        light = ba.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        ba.animate(light, 'intensity', {0: 0, 
                                        0.25: 1, 
                                        0.5: 0})
        ba.timer(0.5, light.delete)
        
    # Game reacts to various events
    def handlemessage(self, msg: Any) -> Any:
        # This is called if the player dies.
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg) # 
            player = msg.getplayer(Player)
            
            # If a player gets eliminated, don't respawn
            if msg.how == 'marked_elimination': return
            
            self.spawn_player(player) # Spawn a new player character
            
            # If a REGULAR player dies, they respawn STUNNED.
            # If a STUNNED player dies, reapply all visual effects.
            if player.state in [PlayerState.REGULAR, PlayerState.STUNNED]:
                player.set_state(PlayerState.STUNNED)
            
            # If a MARKED player falls off the map, apply the MARKED effects on the new spaz that respawns.
            if player.state == PlayerState.MARKED:
                self.mark(player)
    
    # This is called when we want to end the game and announce a victor
    def end_game(self) -> None:
        # Proceed only if the game hasn't ended yet.
        if self.has_ended():
            return
        results = ba.GameResults()
        # By this point our match placement list should be filled with all players.
        # Players that died/left earliest should be the first entries.
        # We're gonna use array indexes to decide match placements.
        # Because of that, we're gonna flip the order of our array, so the last entries are first.
        self.match_placement.reverse()
        for team in self.teams:
            # Use each player's index in the array for our scoring
            # 0 is the first index, so we add 1 to the score.
            results.set_team_score(team, self.match_placement.index(team) + 1)
        self.end(results=results) # Standard game ending behavior
