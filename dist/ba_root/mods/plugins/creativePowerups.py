# ba_meta require api 8
from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, Sequence, Any
import babase
import bauiv1 as bui
import bascenev1 as bs
from bascenev1lib.actor import powerupbox as pupbox
from bascenev1lib.actor import bomb
from bascenev1lib.actor.bomb import Bomb, Blast, BombFactory
from bascenev1lib.actor.spaz import Spaz, SpazFactory, POWERUP_WEAR_OFF_TIME
from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    pass

# Keep references to the original methods for chaining
old_pbx_init = None
old_bomb_init = None
old_bomb_handlemessage = None
old_blast_init = None
old_blast_handlemessage = None
old_spaz_handlemessage = None

class BouncyTouchMessage:
    """Message sent when bouncy bomb touches footing."""
    pass

def wear_off_second_chance(spaz: Spaz):
    """Clean up second chance perk when it expires."""
    if spaz.exists() and getattr(spaz, 'second_chance_active', False):
        spaz.second_chance_active = False
        if hasattr(spaz, 'second_chance_halo') and spaz.second_chance_halo:
            spaz.second_chance_halo.delete()
            spaz.second_chance_halo = None
        if spaz.node:
            PopupText(text="Second Chance Expired", scale=1.0, position=spaz.node.position, color=(0.7, 0.7, 0.7)).autoretain()
            bs.getsound('powerdown01').play(position=spaz.node.position)

def apply_slime(spaz: Spaz):
    """Apply a temporary movement slowdown to slimed players."""
    if not spaz.node:
        return
    PopupText(text="SLIMED!", scale=1.2, position=spaz.node.position, color=(0.1, 0.9, 0.1)).autoretain()
    
    # Setup a repeating timer to slow the spaz velocity
    def do_slow(count: int):
        if spaz.node.exists() and not spaz._dead:
            v = spaz.node.velocity
            spaz.node.velocity = (v[0] * 0.7, v[1], v[2] * 0.7)
            # Emit small green sweat particles
            bs.emitfx(position=spaz.node.position, scale=0.6, count=2, spread=0.2, chunk_type='sweat')
            if count > 0:
                bs.timer(0.1, babase.Call(do_slow, count - 1))
    do_slow(30) # 3 seconds duration

def creative_pbx(self, position: Sequence[float] = (0.0, 1.0, 0.0),
                 poweruptype: str = 'triple_bombs',
                 expire: bool = True):
    """Wrapper around PowerupBox.__init__ to support creative powerups."""
    our_custom_types = ['void_bombs', 'teleport_bombs', 'bouncy_bombs', 'second_chance']
    
    if poweruptype in our_custom_types:
        self.creative_poweruptype = poweruptype
        # Initialize as a base powerup 'shield' to prevent game crashes
        base_type = 'shield'
    else:
        self.creative_poweruptype = None
        base_type = poweruptype
        
    old_pbx_init(self, position, base_type, expire)
    
    if self.creative_poweruptype:
        self.poweruptype = self.creative_poweruptype
        factory = CreativePowerupBoxFactory.get()
        
        # Customize visuals and add glowing lights
        if self.creative_poweruptype == 'void_bombs':
            self.node.color_texture = factory.tex_void_bombs
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (0.5, 0.1, 0.9), 'radius': 0.25, 'intensity': 1.2})
            self.node.connectattr('position', self.light, 'position')
            
        elif self.creative_poweruptype == 'teleport_bombs':
            self.node.color_texture = factory.tex_teleport_bombs
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (0.1, 0.8, 0.9), 'radius': 0.25, 'intensity': 1.2})
            self.node.connectattr('position', self.light, 'position')
            
        elif self.creative_poweruptype == 'bouncy_bombs':
            self.node.color_texture = factory.tex_bouncy_bombs
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (0.1, 0.9, 0.1), 'radius': 0.25, 'intensity': 1.2})
            self.node.connectattr('position', self.light, 'position')
            
        elif self.creative_poweruptype == 'second_chance':
            self.node.color_texture = factory.tex_second_chance
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (1.0, 0.8, 0.1), 'radius': 0.25, 'intensity': 1.2})
            self.node.connectattr('position', self.light, 'position')

        # Override name text label
        if hasattr(self, 'texts') and 'Name' in self.texts:
            name_mapping = {
                'void_bombs': 'Void Bombs',
                'teleport_bombs': 'Teleport Bomb',
                'bouncy_bombs': 'Bouncy Bomb',
                'second_chance': 'Second Chance'
            }
            self.texts['Name'].text = name_mapping.get(self.creative_poweruptype, self.creative_poweruptype)

def creative_bomb_init(self,
                       position: Sequence[float] = (0.0, 1.0, 0.0),
                       velocity: Sequence[float] = (0.0, 0.0, 0.0),
                       bomb_type: str = 'normal',
                       blast_radius: float = 2.0,
                       bomb_scale: float = 1.0,
                       source_player: bs.Player = None,
                       owner: bs.Node = None):
    """Wrapper around Bomb.__init__ to support creative bomb types."""
    our_bombs = ['void', 'teleport', 'bouncy']
    
    if bomb_type in our_bombs:
        self.creative_bomb_type = bomb_type
        # Map to standard bomb type bases
        if bomb_type == 'void':
            base_bomb_type = 'normal'
        elif bomb_type == 'teleport':
            base_bomb_type = 'impact'
        elif bomb_type == 'bouncy':
            base_bomb_type = 'normal'
    else:
        self.creative_bomb_type = None
        base_bomb_type = bomb_type
        
    old_bomb_init(self,
                  position=position,
                  velocity=velocity,
                  bomb_type=base_bomb_type,
                  blast_radius=blast_radius,
                  bomb_scale=bomb_scale,
                  source_player=source_player,
                  owner=owner)
                  
    if self.creative_bomb_type:
        self.bomb_type = self.creative_bomb_type
        factory = CreativePowerupBoxFactory.get()
        shared = SharedObjects.get()
        
        if self.creative_bomb_type == 'void':
            self.node.color_texture = factory.tex_void_bombs
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (0.6, 0.1, 1.0), 'radius': 0.3, 'intensity': 1.0})
            self.node.connectattr('position', self.light, 'position')
            self.shield = bs.newnode('shield', owner=self.node, attrs={'color': (0.6, 0.1, 1.0), 'radius': 0.5})
            self.node.connectattr('position', self.shield, 'position')
            
        elif self.creative_bomb_type == 'teleport':
            self.node.color_texture = factory.tex_teleport_bombs
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (0.1, 0.8, 0.9), 'radius': 0.35, 'intensity': 1.2})
            self.node.connectattr('position', self.light, 'position')
            self.shield = bs.newnode('shield', owner=self.node, attrs={'color': (0.1, 0.8, 0.9), 'radius': 0.5})
            self.node.connectattr('position', self.shield, 'position')
            
        elif self.creative_bomb_type == 'bouncy':
            self.node.color_texture = factory.tex_bouncy_bombs
            self.light = bs.newnode('light', owner=self.node, attrs={'color': (0.1, 0.9, 0.1), 'radius': 0.3, 'intensity': 1.0})
            self.node.connectattr('position', self.light, 'position')
            
            # Attach bouncy physics behavior using material callback
            self.bouncy_material = bs.Material()
            self.bouncy_material.add_actions(
                conditions=('they_have_material', shared.footing_material),
                actions=('message', 'our_node', 'at_connect', BouncyTouchMessage())
            )
            self.node.materials = self.node.materials + (self.bouncy_material,)

def creative_bomb_handlemessage(self, msg: Any) -> Any:
    """Wrapper around Bomb.handlemessage to make bouncy bombs bounce."""
    if isinstance(msg, BouncyTouchMessage):
        if self.node.exists():
            vel = self.node.velocity
            if vel[1] < -0.8: # Bounce on downward collisions
                bs.getsound('pop01').play(0.4, position=self.node.position)
                self.node.velocity = (vel[0] * 0.9, -vel[1] * 0.85, vel[2] * 0.9)
                bs.emitfx(position=self.node.position, scale=0.8, count=5, spread=0.1, chunk_type='sweat')
        return None
        
    return old_bomb_handlemessage(self, msg)

def creative_blast_init(self, *args, **kwargs):
    """Wrapper around Blast.__init__ to customize explosion start effects."""
    old_blast_init(self, *args, **kwargs)
    
    pos = self.node.position
    
    if self.blast_type == 'teleport':
        # Teleport throwing player to the explosion site immediately
        source_player = self._source_player
        if source_player and source_player.exists():
            spaz = source_player.actor
            if spaz and spaz.exists() and spaz.node:
                old_pos = spaz.node.position
                
                # Release hold if any
                spaz.node.hold_node = None
                
                # Sparkles and sound at original location
                bs.emitfx(position=old_pos, scale=1.5, count=25, spread=0.5, chunk_type='spark')
                bs.getsound('activate_beep').play(position=old_pos)
                
                # Relocate player
                spaz.node.position = (pos[0], pos[1] + 0.8, pos[2])
                
                # Sparkles and sound at destination location
                bs.emitfx(position=pos, scale=1.5, count=25, spread=0.5, chunk_type='spark')
                bs.getsound('shield_up').play(position=pos)
                
    elif self.blast_type == 'void':
        # Custom visual expanding/contracting gravity sphere
        self.void_halo = bs.newnode('shield', owner=self.node, attrs={'color': (0.8, 0.1, 1.2), 'radius': 0.1})
        self.node.connectattr('position', self.void_halo, 'position')
        bs.animate(self.void_halo, 'radius', {0.0: 0.1, 0.15: self.radius, 0.25: 0.0})
        bs.timer(0.25, self.void_halo.delete)
        bs.getsound('shield_down').play(position=pos)
        
    elif self.blast_type == 'bouncy':
        # Custom slime blast sphere
        self.slime_halo = bs.newnode('shield', owner=self.node, attrs={'color': (0.2, 2.0, 0.2), 'radius': 0.1})
        self.node.connectattr('position', self.slime_halo, 'position')
        bs.animate(self.slime_halo, 'radius', {0.0: 0.1, 0.2: self.radius, 0.3: 0.0})
        bs.timer(0.3, self.slime_halo.delete)
        bs.getsound('splatter').play(position=pos)

def creative_blast_handlemessage(self, msg: Any) -> Any:
    """Wrapper around Blast.handlemessage to customize hit physics/damage."""
    if isinstance(msg, bs.DieMessage):
        if self.node:
            self.node.delete()
        return None

    elif isinstance(msg, bomb.ExplodeHitMessage):
        node = bs.getcollision().opposingnode
        if not self.node or not node:
            return None
            
        blast_pos = self.node.position
        target_pos = node.position
        
        # Calculate vector and distance
        direction = (target_pos[0] - blast_pos[0], target_pos[1] - blast_pos[1], target_pos[2] - blast_pos[2])
        dist = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
        if dist < 0.01:
            dist = 0.01
            
        norm_dir = (direction[0]/dist, direction[1]/dist, direction[2]/dist)
        
        if self.blast_type == 'void':
            # Pull targets towards explosion center
            pull_dir = (-norm_dir[0], -norm_dir[1] + 0.25, -norm_dir[2])
            pull_mag = 1900.0 * (1.0 - (dist / self.radius))
            
            if pull_mag > 0:
                node.handlemessage(
                    bs.HitMessage(
                        pos=blast_pos,
                        velocity=(0, 0, 0),
                        magnitude=pull_mag,
                        hit_type='explosion',
                        hit_subtype='void',
                        radius=self.radius,
                        source_player=babase.existing(self._source_player),
                        force_direction=pull_dir
                    )
                )
            return None
            
        elif self.blast_type == 'teleport':
            # Teleport bomb does no blast push/damage to other players
            return None
            
        elif self.blast_type == 'bouncy':
            # Huge bounce knockback push, slime slowdown applied
            push_mag = 4800.0 * (1.0 - (dist / self.radius))
            if push_mag > 0:
                node.handlemessage(
                    bs.HitMessage(
                        pos=blast_pos,
                        velocity=(norm_dir[0] * 8.0, norm_dir[1] * 8.0, norm_dir[2] * 8.0),
                        magnitude=push_mag,
                        hit_type='explosion',
                        hit_subtype='bouncy',
                        radius=self.radius,
                        source_player=babase.existing(self._source_player),
                        force_direction=norm_dir
                    )
                )
            return None

    return old_blast_handlemessage(self, msg)

def creative_spaz_handlemessage(self, msg: Any) -> Any:
    """Wrapper around Spaz.handlemessage to process new powerups, slime hits, and second chances."""
    # 1. Custom Powerup Collection
    if isinstance(msg, bs.PowerupMessage):
        if self._dead or not self.node:
            return True
            
        if msg.poweruptype in ['void_bombs', 'teleport_bombs', 'bouncy_bombs', 'second_chance']:
            if self.pick_up_powerup_callback is not None:
                self.pick_up_powerup_callback(self)
                
            bs.getsound('powerup01').play(position=self.node.position)
            self.node.handlemessage('flash')
            
            if msg.poweruptype == 'void_bombs':
                self.bomb_type = 'void'
                tex = CreativePowerupBoxFactory.get().tex_void_bombs
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = t_ms + POWERUP_WEAR_OFF_TIME
                    self._bomb_wear_off_flash_timer = bs.Timer(POWERUP_WEAR_OFF_TIME - 2000, bs.WeakCall(self._bomb_wear_off_flash))
                    self._bomb_wear_off_timer = bs.Timer(POWERUP_WEAR_OFF_TIME, bs.WeakCall(self._bomb_wear_off))
                    
            elif msg.poweruptype == 'teleport_bombs':
                self.bomb_type = 'teleport'
                tex = CreativePowerupBoxFactory.get().tex_teleport_bombs
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = t_ms + POWERUP_WEAR_OFF_TIME
                    self._bomb_wear_off_flash_timer = bs.Timer(POWERUP_WEAR_OFF_TIME - 2000, bs.WeakCall(self._bomb_wear_off_flash))
                    self._bomb_wear_off_timer = bs.Timer(POWERUP_WEAR_OFF_TIME, bs.WeakCall(self._bomb_wear_off))
                    
            elif msg.poweruptype == 'bouncy_bombs':
                self.bomb_type = 'bouncy'
                tex = CreativePowerupBoxFactory.get().tex_bouncy_bombs
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = t_ms + POWERUP_WEAR_OFF_TIME
                    self._bomb_wear_off_flash_timer = bs.Timer(POWERUP_WEAR_OFF_TIME - 2000, bs.WeakCall(self._bomb_wear_off_flash))
                    self._bomb_wear_off_timer = bs.Timer(POWERUP_WEAR_OFF_TIME, bs.WeakCall(self._bomb_wear_off))
                    
            elif msg.poweruptype == 'second_chance':
                self.second_chance_active = True
                tex = CreativePowerupBoxFactory.get().tex_second_chance
                self._flash_billboard(tex)
                
                # Visual golden halo around player
                if hasattr(self, 'second_chance_halo') and self.second_chance_halo:
                    self.second_chance_halo.delete()
                self.second_chance_halo = bs.newnode('shield', owner=self.node, attrs={'color': (2.0, 1.6, 0.1), 'radius': 1.0})
                self.node.connectattr('position', self.second_chance_halo, 'position')
                
                # Expiry timer (20 seconds)
                bs.timer(20.0, babase.Call(wear_off_second_chance, self))
                
            if msg.sourcenode:
                msg.sourcenode.handlemessage(bs.PowerupAcceptMessage())
            return True

    # 2. Custom Hit Interactions
    elif isinstance(msg, bs.HitMessage):
        if msg.hit_subtype == 'bouncy':
            # Slime bouncy blast does no damage but applies massive push
            was_invincible = self.node.invincible
            self.node.invincible = True
            res = old_spaz_handlemessage(self, msg)
            self.node.invincible = was_invincible
            apply_slime(self)
            return res
            
        elif msg.hit_subtype == 'void':
            # Gravity pull does a fixed small damage of 40 HP
            was_invincible = self.node.invincible
            self.node.invincible = True
            res = old_spaz_handlemessage(self, msg)
            self.node.invincible = was_invincible
            
            if not self._dead:
                self.hitpoints -= 40
                self.node.hurt = 1.0 - float(self.hitpoints) / self.hitpoints_max
                PopupText(text="-40HP", scale=1.0, position=self.node.position, color=(0.7, 0.1, 0.9)).autoretain()
                if self.hitpoints <= 0:
                    self.node.handlemessage(bs.DieMessage())
            return res

    # 3. Intercept death to execute Second Chance resurrection
    elif isinstance(msg, bs.DieMessage):
        if getattr(self, 'second_chance_active', False) and not self._dead:
            self.second_chance_active = False
            if hasattr(self, 'second_chance_halo') and self.second_chance_halo:
                self.second_chance_halo.delete()
                self.second_chance_halo = None
                
            self.hitpoints = self.hitpoints_max // 2
            if self.node:
                self.node.hurt = 1.0 - float(self.hitpoints) / self.hitpoints_max
                self.equip_shields()
                self.node.handlemessage('flash')
                
                PopupText(text="SECOND CHANCE!", scale=1.5, position=self.node.position, color=(1.0, 0.8, 0.0)).autoretain()
                bs.getsound('shield_up').play(position=self.node.position)
                bs.emitfx(position=self.node.position, scale=2.0, count=40, spread=0.8, chunk_type='spark')
            return True

    return old_spaz_handlemessage(self, msg)

class CreativePowerupBoxFactory(pupbox.PowerupBoxFactory):
    """Dynamic class instantiated inside enable() to wrap the active PowerupBoxFactory class."""
    pass

def enable():
    """Enable the plugin by replacing/wrapping methods from Bomb, Blast, PowerupBox, and Spaz."""
    global old_pbx_init, old_bomb_init, old_bomb_handlemessage, old_blast_init, old_blast_handlemessage, old_spaz_handlemessage
    
    # Wrap PowerupBoxFactory to include new powerups
    current_factory_class = pupbox.PowerupBoxFactory
    
    class FactoryWrapper(current_factory_class):
        def __init__(self) -> None:
            super().__init__()
            self.tex_void_bombs = bs.gettexture('achievementSharingIsCaring')
            self.tex_teleport_bombs = bs.gettexture('achievementDualWielding')
            self.tex_bouncy_bombs = bs.gettexture('ouyaYButton')
            self.tex_second_chance = bs.gettexture('shield')
            
            # Setup distribution frequencies
            our_powerups = {
                'void_bombs': 3,
                'teleport_bombs': 2,
                'bouncy_bombs': 3,
                'second_chance': 2
            }
            for pup, freq in our_powerups.items():
                for _ in range(freq):
                    self._powerupdist.append(pup)
                    
    # Register our wrapped factory class
    pupbox.PowerupBoxFactory = FactoryWrapper
    # Globally bind CreativePowerupBoxFactory to FactoryWrapper so other methods can retrieve it
    globals()['CreativePowerupBoxFactory'] = FactoryWrapper
    
    # Method Wrapping
    old_pbx_init = pupbox.PowerupBox.__init__
    pupbox.PowerupBox.__init__ = creative_pbx
    
    old_bomb_init = Bomb.__init__
    Bomb.__init__ = creative_bomb_init
    
    old_bomb_handlemessage = Bomb.handlemessage
    Bomb.handlemessage = creative_bomb_handlemessage
    
    old_blast_init = Blast.__init__
    Blast.__init__ = creative_blast_init
    
    old_blast_handlemessage = Blast.handlemessage
    Blast.handlemessage = creative_blast_handlemessage
    
    old_spaz_handlemessage = Spaz.handlemessage
    Spaz.handlemessage = creative_spaz_handlemessage

# ba_meta export plugin
class CreativePowerupsPlugin(babase.Plugin):
    """Discovery plugin for the Ballistica engine."""
    def on_activate(self) -> None:
        enable()
