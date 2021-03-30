# Released under the MIT License. See LICENSE for details.
#
"""Defines Actor(s)."""

from __future__ import annotations
from bastd.gameutils import SharedObjects
import ba,random,admin,json,os,mysettings
from typing import Any, Sequence, Tuple, Optional, Type, Literal
from ba.internal import get_default_powerup_distribution
from bastd.actor import powerupbox
from bastd.actor.powerupbox import _TouchedMessage, PowerupBoxFactory

DEFAULT_POWERUP_INTERVAL = 8.0

tt = ba.TimeType.SIM
tf = ba.TimeFormat.MILLISECONDS


def new_default_powerup_distribution() -> Sequence[Tuple[str, int]]:
    """Standard set of powerups."""
    a = mysettings.powerups
    return (('triple_bombs',3 if a['triple'] else 0),
            ('ice_bombs',3 if a['ice'] else 0),
            ('punch',2 if a['punch'] else 0),
            ('impact_bombs',2 if a['impact'] else 0),
            ('land_mines',2 if a['land'] else 0),
            ('sticky_bombs',3 if a['sticky'] else 0),
            ('shield',1 if a['shield'] else 0),
            ('health',2 if a['health'] else 0),
            ('curse',2 if a['curse'] else 0),
            ('speed',1 if a['speed'] else 0),
            ('cc',5 if a['cc'] else 0))


class NewPowerupBox(ba.Actor):
    """A box that grants a powerup.

    category: Gameplay Classes

    This will deliver a ba.PowerupMessage to anything that touches it
    which has the ba.PowerupBoxFactory.powerup_accept_material applied.

    Attributes:

       poweruptype
          The string powerup type.  This can be 'triple_bombs', 'punch',
          'ice_bombs', 'impact_bombs', 'land_mines', 'sticky_bombs', 'shield',
          'health', or 'curse'.

       node
          The 'prop' ba.Node representing this box.
    """

    def __init__(self,
                 position: Sequence[float] = (0.0, 1.0, 0.0),
                 poweruptype: str = 'triple_bombs',
                 expire: bool = True):
        """Create a powerup-box of the requested type at the given position.

        see ba.Powerup.poweruptype for valid type strings.
        """

        super().__init__()
        shared = SharedObjects.get()
        factory = PowerupBoxFactory.get()
        self.poweruptype = poweruptype
        self._powersgiven = False

        if poweruptype == 'triple_bombs':
            tex = factory.tex_bomb
            prefix = u'\ue00cTriple Bombs\ue00c'
        elif poweruptype == 'punch':
            tex = factory.tex_punch
            prefix = u'\ue00cBoxing Gloves\ue00c'
        elif poweruptype == 'ice_bombs':
            tex = factory.tex_ice_bombs
            prefix = u'\ue00cIce Bombs\ue00c'
        elif poweruptype == 'impact_bombs':
            tex = factory.tex_impact_bombs
            prefix = u'\ue00cImpact Bombs\ue00c'
        elif poweruptype == 'land_mines':
            tex = factory.tex_land_mines
            prefix = u'\ue043Land Mine\ue043'
        elif poweruptype == 'sticky_bombs':
            tex = factory.tex_sticky_bombs
            prefix = u'\ue00cStickey Bombs\ue00c'
        elif poweruptype == 'shield':
            tex = factory.tex_shield
            prefix = u'\ue00cArmor\ue00c'
        elif poweruptype == 'health':
            tex = factory.tex_health
            prefix = u'\ue047MedKit\ue047'
        elif poweruptype == 'curse':
            tex = factory.tex_curse
            prefix = u'\ue046Danger\ue046'

        #MODIFIED POWERUPS
        elif poweruptype == 'speed':   
            tex =  ba.gettexture("powerupSpeed")
            prefix = u'\ue048Speed\ue048'
        elif poweruptype == 'cc':   
            tex = ba.gettexture("achievementEmpty")
            prefix = u'\ue043Character Changer\ue043'
        else:
            raise ValueError('invalid poweruptype: ' + str(poweruptype))

        if len(position) != 3:
            raise ValueError('expected 3 floats for position')

        self.node = ba.newnode(
            'prop',
            delegate=self,
            attrs={
                'body': 'box',
                'position': position,
                'model': factory.model,
                'light_model': factory.model_simple,
                'shadow_size': 0.5,
                'color_texture': tex,
                'reflection': 'powerup',
                'reflection_scale': [1.0],
                'materials': (factory.powerup_material,
                              shared.object_material)
            })  # yapf: disable
        m = ba.newnode('math', owner=self.node, attrs={'input1': (0, 0.7, 0), 'operation': 'add'})
        self.node.connectattr('position', m, 'input2')
        self._Text = None
        self.light = None
        self.shield = None
        def my_text():
            self._Text = ba.newnode('text',
                             owner=self.node,
                             attrs={'text':prefix,
                                'in_world': True,
                                'color': (1,1,1),
                                'shadow': 0.8,
                                'flatness': 0.8,
                                'scale': 0.01,
                                'h_align': 'center',
                             })  # yapf: disable
            #ba.animate(self._Text, 'scale', {0: 0.0, 1000: 0.01}, timetype=tt, timeformat=tf)
            ba.animate_array(self._Text,'color',3,mysettings.multicolor,True, timetype=tt, timeformat=tf)
            m.connectattr('output', self._Text, 'position')
        def my_light():
            self.light = ba.newnode('light', attrs={'position':self.node.position, 'color':(1,1,1), 'volume_intensity_scale':0.4, 'intensity':0.4, 'radius':0.03})
            ba.animate_array(self.light,'color',3,mysettings.multicolor,True, timetype=tt, timeformat=tf)
            self.node.connectattr('position',self.light,'position')
        def del_light():
            light_Deleter = ba.timer(1,self.light.delete)
        def my_shield():
            self.shield = ba.newnode('shield', owner=self.node, attrs={'color':(random.random()*2,random.random()*2,random.random()*2), 'radius':0.9})
            ba.animate_array(self.shield,'color',3,mysettings.multicolor,True, timetype=tt, timeformat=tf)
            self.node.connectattr('position', self.shield, 'position')
        if mysettings.settings['pUpTag']: my_text()
        if mysettings.settings['pUpLight']: my_light()
        if mysettings.settings['pUpShield']: my_shield()

        # Animate in.
        curve = ba.animate(self.node, 'model_scale', {0: 0, 0.14: 1.6, 0.2: 1})
        ba.timer(0.2, curve.delete)

        if expire:
            ba.timer(DEFAULT_POWERUP_INTERVAL - 2.5,
                     ba.WeakCall(self._start_flashing))
            ba.timer(DEFAULT_POWERUP_INTERVAL - 1.0,
                     ba.WeakCall(self.handlemessage, ba.DieMessage()))
            ba.timer(DEFAULT_POWERUP_INTERVAL - 1.0,
                     ba.Call(del_light))

    def _start_flashing(self) -> None:
        if self.node:
            self.node.flashing = True

    def handlemessage(self, msg: Any) -> Any:
        assert not self.expired

        if isinstance(msg, ba.PowerupAcceptMessage):
            factory = PowerupBoxFactory.get()
            assert self.node
            if self.poweruptype == 'health':
                ba.playsound(factory.health_powerup_sound,
                             3,
                             position=self.node.position)
            ba.playsound(factory.powerup_sound, 3, position=self.node.position)
            self._powersgiven = True
            self.handlemessage(ba.DieMessage())

        elif isinstance(msg, _TouchedMessage):
            if not self._powersgiven:
                node = ba.getcollision().opposingnode
                node.handlemessage(
                    ba.PowerupMessage(self.poweruptype, sourcenode=self.node))

        elif isinstance(msg, ba.DieMessage):
            if self.node:
                if msg.immediate:
                    self.node.delete()
                else:
                    ba.animate(self.node, 'model_scale', {0: 1, 0.1: 0})
                    ba.timer(0.1, self.node.delete)

        elif isinstance(msg, ba.OutOfBoundsMessage):
            self.handlemessage(ba.DieMessage())

        elif isinstance(msg, ba.HitMessage):
            # Don't die on punches (that's annoying).
            if msg.hit_type != 'punch':
                self.handlemessage(ba.DieMessage())
        else:
            return super().handlemessage(msg)
        return None

ba.internal.get_default_powerup_distribution = ba._powerup.get_default_powerup_distribution = new_default_powerup_distribution
powerupbox.PowerupBox = NewPowerupBox