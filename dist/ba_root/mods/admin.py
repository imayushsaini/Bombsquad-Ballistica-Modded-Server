# -*- coding: utf-8 -*-
# Released under the MIT License. See LICENSE for details.
#
"""Functionality related to player-controlled Spazzes."""

from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, overload
import ba,_ba,weakref,random,math,time,base64,os,json,roles,bastd,mysettings
from bastd.actor.spaz import *
from bastd.gameutils import SharedObjects
from typing import Any, Sequence, Optional, Dict, List, Union, Callable, Tuple, Set, Type, Literal
from bastd.actor import playerspaz
from bastd.actor.playerspaz import *
from bastd.actor.spazfactory import SpazFactory
from bastd.actor.popuptext import PopupText
from bastd.actor import spaz,spazappearance
from bastd.actor import bomb as stdbomb
from bastd.actor.powerupbox import PowerupBoxFactory

PlayerType = TypeVar('PlayerType', bound=ba.Player)
TeamType = TypeVar('TeamType', bound=ba.Team)
tt = ba.TimeType.SIM
tf = ba.TimeFormat.MILLISECONDS
cList = ['neoSpaz','mel','ninja','kronk','jack','frosty','santa','bones','bear','penguin','ali','cyborg','agent','wizard','pixie','bunny']
nList = {'neoSpaz':'Spaz','zoe':'Zoe','ninja':'Snake Shadow','kronk':'Kronk','mel':'Mel','jack':'Jack Morgan','santa':'Santa Claus','frosty':'Frosty','bones':'Bones','bear':'Bernard','penguin':'Pascal','ali':'Taobao Mascot','cyborg':'B-9000','agent':'Agent Johnson','wizard':'Grumbledorf','pixie':'Pixel','bunny':'Easter Bunny'}
mymedia = {}
def add_mychar_media():
    global mymedia
    for k,v in nList.items():
        v_media = SpazFactory.get().get_media(v)
        mymedia[v] = v_media

#
class PermissionEffect(object):
    def __init__(self, position=(1,0, 0), owner=None, prefix='ADMIN', prefixColor=(1, 1, 1), prefixAnim=None, prefixAnimate=True,type = 1):
        if prefixAnim is None: prefixAnim = mysettings.multicolor
        self.position = position
        self.owner = owner
        if type == 1: m = ba.newnode('math', owner=self.owner, attrs={'input1': (0, 1.80, 0), 'operation': 'add'})
        else: m = ba.newnode('math', owner=self.owner, attrs={'input1': (0, 1.40, 0), 'operation': 'add'})
        self.owner.connectattr('position', m, 'input2')
        self._Text = ba.newnode('text', owner=self.owner, attrs={'text': prefix.encode('utf-8').decode('unicode-escape'), 'in_world': True, 'shadow': 1.2, 'flatness': 1.0, 'color': prefixColor, 'scale': 0.0, 'h_align': 'center'})
        m.connectattr('output', self._Text, 'position')
        ba.animate(self._Text, 'scale', {0: 0.0, 1000: 0.01}, timetype=tt, timeformat=tf)
        if prefixAnimate: ba.animate_array(self._Text, 'color', 3, prefixAnim, True, timetype=tt, timeformat=tf)

class showHitPoint(object):
    def __init__(self,position = (0,1.5,0),owner = None,prefix = 'ADMIN',shad = 1.2):
        self.position = position
        self.owner = owner
        m = ba.newnode('math', owner=self.owner, attrs={'input1': self.position, 'operation': 'add'})
        self.owner.connectattr('position', m, 'input2')
        prefix = int(prefix) / 10
        preFix = u"\ue047" + str(prefix) + u"\ue047"
        self._Text = ba.newnode('text',owner=self.owner,attrs={'text':preFix,'in_world':True,'shadow':shad,'flatness':1.0,'color':(1,1,1) if int(prefix) >= 20 else (1.0,0.2,0.2),'scale':0.01,'h_align':'center'})
        m.connectattr('output', self._Text, 'position')
        def a():
            self._Text.delete()
            m.delete()
        self.timer = ba.Timer(10, ba.Call(a), timetype=tt, timeformat=tf)

class SurroundBallFactory(object):
    def __init__(self):
        self.bonesTex = ba.gettexture("powerupCurse")
        self.bonesModel = ba.getmodel("bonesHead")
        self.bearTex = ba.gettexture("bearColor")
        self.bearModel = ba.getmodel("bearHead")
        self.aliTex = ba.gettexture("aliColor")
        self.aliModel = ba.getmodel("aliHead")
        self.b9000Tex = ba.gettexture("cyborgColor")
        self.b9000Model = ba.getmodel("cyborgHead")
        self.frostyTex = ba.gettexture("frostyColor")
        self.frostyModel = ba.getmodel("frostyHead")
        self.cubeTex = ba.gettexture("crossOutMask")
        self.cubeModel = ba.getmodel("powerup")
        try:
            self.mikuModel = ba.getmodel("operaSingerHead")
            self.mikuTex = ba.gettexture("operaSingerColor")
        except:ba.print_exception()
        self.ballMaterial = ba.Material()
        self.impactSound = ba.getsound("impactMedium")
        self.ballMaterial.add_actions(actions=("modify_node_collision", "collide", False))

class SurroundBall(ba.Actor):
    def __init__(self, spaz, shape="bones"):
        if spaz is None or not spaz.is_alive(): return
        ba.Actor.__init__(self)
        self.spazRef = weakref.ref(spaz)
        factory = self.getFactory()
        s_model, s_texture = {
            "bones": (factory.bonesModel, factory.bonesTex),
            "bear": (factory.bearModel, factory.bearTex),
            "ali": (factory.aliModel, factory.aliTex),
            "b9000": (factory.b9000Model, factory.b9000Tex),
            "miku": (factory.mikuModel, factory.mikuTex),
            "frosty": (factory.frostyModel, factory.frostyTex),
            "RedCube": (factory.cubeModel, factory.cubeTex)
        }.get(shape, (factory.bonesModel, factory.bonesTex))
        self.node = ba.newnode("prop", attrs={"model": s_model, "body": "sphere", "color_texture": s_texture, "reflection": "soft", "model_scale": 0.5, "body_scale": 0.1, "density": 0.1, "reflection_scale": [0.15], "shadow_size": 0.6, "position": spaz.node.position, "velocity": (0, 0, 0), "materials": [SharedObjects.get().object_material, factory.ballMaterial] }, delegate=self)
        self.surroundTimer = None
        self.surroundRadius = 1.0
        self.angleDelta = math.pi / 12.0
        self.curAngle = random.random() * math.pi * 2.0
        self.curHeight = 0.0
        self.curHeightDir = 1
        self.heightDelta = 0.2
        self.heightMax = 1.0
        self.heightMin = 0.1
        self.initTimer(spaz.node.position)

    def getTargetPosition(self, spazPos):
        p = spazPos
        pt = (p[0] + self.surroundRadius * math.cos(self.curAngle), p[1] + self.curHeight, p[2] + self.surroundRadius * math.sin(self.curAngle))
        self.curAngle += self.angleDelta
        self.curHeight += self.heightDelta * self.curHeightDir
        if (self.curHeight > self.heightMax) or (self.curHeight < self.heightMin): self.curHeightDir = -self.curHeightDir
        return pt

    def initTimer(self, p):
        self.node.position = self.getTargetPosition(p)
        self.surroundTimer = ba.Timer(30, ba.WeakCall(self.circleMove), repeat=True, timetype=tt, timeformat=tf)

    def circleMove(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        p = spaz.node.position
        pt = self.getTargetPosition(p)
        pn = self.node.position
        d = [pt[0] - pn[0], pt[1] - pn[1], pt[2] - pn[2]]
        speed = self.getMaxSpeedByDir(d)
        self.node.velocity = speed

    @staticmethod
    def getMaxSpeedByDir(direction):
        k = 7.0 / max((abs(x) for x in direction))
        return tuple(x * k for x in direction)

    def handlemessage(self, m):
        ba.Actor.handlemessage(self, m)
        if isinstance(m, ba.DieMessage):
            if self.surroundTimer is not None: self.surroundTimer = None
            self.node.delete()
        elif isinstance(m, ba.OutOfBoundsMessage):
            self.handlemessage(ba.DieMessage())

    def getFactory(cls):
        activity = ba.getactivity()
        if activity is None: raise Exception("no current activity")
        try:
            return activity._sharedSurroundBallFactory
        except Exception:
            f = activity._sharedSurroundBallFactory = SurroundBallFactory()
            return f

class Enhancement(ba.Actor):
    def __init__(self, spaz, player):
        ba.Actor.__init__(self)
        self.source_player = player
        self.spazRef = weakref.ref(spaz)
        self.spazNormalColor = spaz.node.color
        self.Decorations = []
        self.Enhancements = []
        self._powerScale = 1.0
        self._armorScale = 1.0
        self._lifeDrainScale = None
        self._damageBounceScale = None
        self._remoteMagicDamge = False
        self._MulitPunch = None
        self._AntiFreeze = 1.0
        self.fallWings = 0
        self.checkDeadTimer = None
        self._hasDead = False
        self.light = None
        flag = 0
        profiles = []
        node_id = self.source_player.node.playerID
        cl_str = None
        clID = None
        self.hptimer = None
        for c in _ba.get_foreground_host_session().sessionplayers:
            if (c.activityplayer) and (c.activityplayer.node.playerID == node_id):
                profiles = c.inputdevice.get_player_profiles()
                clID = c.inputdevice.client_id
                cl_str = c.get_account_id()
        for client in _ba.get_foreground_host_activity().players:
            if client.node.playerID == node_id:
                def showHP():
                    if spaz.node.exists(): showHitPoint(owner=spaz.node,prefix=str(int(spaz.hitpoints)),position=(0,0.75,0),shad = 1.4)
                if (mysettings.settings['showHP']) and (str(_ba.get_foreground_host_activity().getname()) != 'Super Smash'):
                    self.hptimer = ba.Timer(10,ba.Call(showHP),repeat = True, timetype=tt, timeformat=tf)
        if profiles == []: profiles = []
        if profiles == {}: profiles = {}

        def getTag(*args):
            #if alreadyHasTag: return True
            for p in profiles:
                if p.startswith('/tag'):
                    try:
                        tag = p.split(' ')[1]
                        for k,v in mysettings.uni.items():
                            if k in tag: tag = tag.replace(k,v)	
                        return tag
                    except:
                        pass   
            return '0'

        if True: #try:
            if cl_str in roles.effectCustomers:
                effect = roles.effectCustomers[cl_str]["effect"]
                if effect == 'ice': self.snowTimer = ba.Timer(500, ba.WeakCall(self.emitIce), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'sweat': self.smokeTimer = ba.Timer(40, ba.WeakCall(self.emitSmoke), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'scorch': self.scorchTimer = ba.Timer(500, ba.WeakCall(self.update_Scorch), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'glow': self.addLightColor((1, 0.6, 0.4));self.checkDeadTimer = ba.Timer(150, ba.WeakCall(self.checkPlayerifDead), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'distortion': self.DistortionTimer = ba.Timer(1000, ba.WeakCall(self.emitDistortion), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'slime': self.slimeTimer = ba.Timer(250, ba.WeakCall(self.emitSlime), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'metal': self.metalTimer = ba.Timer(500, ba.WeakCall(self.emitMetal), repeat=True, timetype=tt, timeformat=tf)
                elif effect == 'surrounder': self.surround = SurroundBall(spaz, shape="bones")
            elif cl_str in roles.surroundingObjectEffect:
                self.surround = SurroundBall(spaz, shape="bones")
                flag = 1
            elif cl_str in roles.sparkEffect:
                self.sparkTimer = ba.Timer(100, ba.WeakCall(self.emitSpark), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.smokeEffect:
                self.smokeTimer = ba.Timer(40, ba.WeakCall(self.emitSmoke), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.scorchEffect:
                self.scorchTimer = ba.Timer(500, ba.WeakCall(self.update_Scorch), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.distortionEffect:
                self.DistortionTimer = ba.Timer(1000, ba.WeakCall(self.emitDistortion), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.glowEffect:
                self.addLightColor((1, 0.6, 0.4));self.checkDeadTimer = ba.Timer(150, ba.WeakCall(self.checkPlayerifDead), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.iceEffect:
                self.snowTimer = ba.Timer(500, ba.WeakCall(self.emitIce), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.slimeEffect:
                self.slimeTimer = ba.Timer(250, ba.WeakCall(self.emitSlime), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
            elif cl_str in roles.metalEffect:
                self.metalTimer = ba.Timer(500, ba.WeakCall(self.emitMetal), repeat=True, timetype=tt, timeformat=tf)
                flag = 1
	
            if cl_str in roles.customTag:
                PermissionEffect(owner = spaz.node,prefix =roles.customTag[cl_str],prefixAnim = {0: (1,0,0), 250: (0,1,0),250*2:(0,0,1),250*3:(1,0,0)})
            elif cl_str in roles.customList or cl_str in roles.toppersList:
                tag = getTag(1)
                if tag == '0': tag = u'\ue046Tag Not Found\ue046'
                PermissionEffect(owner = spaz.node,prefix = tag,prefixAnim = {0: (1,0,0), 250: (0,1,0),250*2:(0,0,1),250*3:(1,0,0)})
            elif cl_str in roles.owners:
                tag = getTag(1)
                if tag == '0': tag = u'\ue043O.W.N.E.R\ue043'
                PermissionEffect(owner = spaz.node,prefix = tag,prefixAnim = {0: (1,0,0), 250: (0,1,0),250*2:(0,0,1),250*3:(1,0,0)})
            elif cl_str in roles.admins:
                tag = getTag(1)
                if tag == '0': tag = u'\ue048A.D.M.I.N\ue048'
                PermissionEffect(owner = spaz.node,prefix = tag,prefixAnim = {0: (1,0,0), 250: (0,1,0),250*2:(0,0,1),250*3:(1,0,0)})
            elif cl_str in roles.vips:	
                tag = getTag(1)
                if tag == '0': tag = u'\ue046VIP\ue046'
                PermissionEffect(owner = spaz.node,prefix = tag,prefixAnim = {0: (1,0,0), 250: (0,1,0),250*2:(0,0,1),250*3:(1,0,0)})
        '''except:
            pass'''

        if mysettings.enableStats:
            if os.path.exists(mysettings.statsFile):
                f = open(mysettings.statsFile, "r")
                aid = str(cl_str)
                pats = {}
                try:
                    pats = json.loads(f.read())	
                except Exception:
                    pass #ba.print_exception()
                if aid in pats:
                    rank = pats[aid]["rank"]
                    if int(rank) < 6:
                        icon = '\\ue043'
                        #dragon='' crown= fireball=	ninja= skull=	
                        if rank == '1':
                            if flag == 0 and mysettings.settings['enableTop5effects']: self.add_multicolor_effect() #self.neroLightTimer = ba.Timer(500, ba.WeakCall(self.neonLightSwitch,("shine" in self.Decorations),("extra_Highlight" in self.Decorations),("extra_NameColor" in self.Decorations)),repeat = True, timetype=tt, timeformat=tf)
                        elif rank == '2': 
                            if flag == 0 and mysettings.settings['enableTop5effects']: self.smokeTimer = ba.Timer(40, ba.WeakCall(self.emitSmoke), repeat=True, timetype=tt, timeformat=tf)
                        elif rank == '3': 
                            if flag == 0 and mysettings.settings['enableTop5effects']: self.addLightColor((1, 0.6, 0.4));self.scorchTimer = ba.Timer(500, ba.WeakCall(self.update_Scorch), repeat=True, timetype=tt, timeformat=tf)
                        elif rank == '4': 
                            if flag == 0 and mysettings.settings['enableTop5effects']: self.metalTimer = ba.Timer(500, ba.WeakCall(self.emitMetal), repeat=True, timetype=tt, timeformat=tf)
                        else:   
                            if flag == 0 and mysettings.settings['enableTop5effects']: self.addLightColor((1, 0.6, 0.4));self.checkDeadTimer = ba.Timer(150, ba.WeakCall(self.checkPlayerifDead), repeat=True, timetype=tt, timeformat=tf)
                        display = icon + '#' + str(rank) + icon
                        PermissionEffect(owner = spaz.node,prefix = display,prefixAnim = {0: (1,1,1)},type = 2)
                    else:
                        display = '#' + str(rank)
                        PermissionEffect(owner=spaz.node, prefix=display, prefixAnim={0: (1,1,1)},type=2)

        if "smoke" and "spark" and "snowDrops" and "slimeDrops" and "metalDrops" and "Distortion" and "neroLight" and "scorch" and "HealTimer" and "KamikazeCheck" not in self.Decorations:
            #self.checkDeadTimer = ba.Timer(150, ba.WeakCall(self.checkPlayerifDead), repeat=True, timetype=tt, timeformat=tf)
            if self.source_player.is_alive() and self.source_player.actor.node.exists():
                #print("OK")
                self.source_player.actor.node.addDeathAction(ba.Call(self.handlemessage,ba.DieMessage()))

    def add_multicolor_effect(self):
        if spaz.node: ba.animate_array(spaz.node, 'color', 3, mysettings.multicolor, True, timetype=tt, timeformat=tf)

    def checkPlayerifDead(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.checkDeadTimer = None
            self.handlemessage(ba.DieMessage())
            return

    def update_Scorch(self):
        spaz = self.spazRef()
        if spaz is not None and spaz.is_alive() and spaz.node.exists():
            color = (random.random(),random.random(),random.random())
            if not hasattr(self,"scorchNode") or self.scorchNode == None:
                self.scorchNode = None
                self.scorchNode = ba.newnode("scorch",attrs={"position":(spaz.node.position),"size":1.17,"big":True})
                spaz.node.connectattr("position",self.scorchNode,"position")
            ba.animate_array(self.scorchNode,"color",3,{0:self.scorchNode.color,500:color}, timetype=tt, timeformat=tf)
        else:
            self.scorchTimer = None
            self.scorchNode.delete()
            self.handlemessage(ba.DieMessage())

    def neonLightSwitch(self,shine,Highlight,NameColor):
        spaz = self.spazRef()
        if spaz is not None and spaz.is_alive() and spaz.node.exists():
            color = (random.random(),random.random(),random.random())
            if NameColor: ba.animate_array(spaz.node,"nameColor",3,{0:spaz.node.nameColor,500:ba.safecolor(color)}, timetype=tt, timeformat=tf)
            if shine:color = tuple([min(10., 10 * x) for x in color])
            ba.animate_array(spaz.node,"color",3,{0:spaz.node.color,500:color}, timetype=tt, timeformat=tf)
            if Highlight:
                #print spaz.node.highlight
                color = (random.random(),random.random(),random.random())
                if shine:color = tuple([min(10., 10 * x) for x in color])
                ba.animate_array(spaz.node,"highlight",3,{0:spaz.node.highlight,500:color}, timetype=tt, timeformat=tf)
        else:
            self.neroLightTimer = None
            self.handlemessage(ba.DieMessage())

    def addLightColor(self, color):
        self.light = ba.newnode("light", attrs={"color": color, "height_attenuated": False, "radius": 0.4})
        self.spazRef().node.connectattr("position", self.light, "position")
        ba.animate(self.light, "intensity", {0: 0.1, 250: 0.3, 500: 0.1}, loop=True, timetype=tt, timeformat=tf)

    def emitDistortion(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        ba.emitfx(position=spaz.node.position,emit_type="distortion",spread=1.0)
        ba.emitfx(position=spaz.node.position, velocity=spaz.node.velocity,count=random.randint(1,5),emit_type="tendrils",tendril_type="smoke")

    def emitSpark(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        ba.emitfx(position=spaz.node.position, velocity=spaz.node.velocity, count=random.randint(1,10), scale=2, spread=0.2, chunk_type="spark")

    def emitIce(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        ba.emitfx(position=spaz.node.position , velocity=spaz.node.velocity, count=random.randint(2,8), scale=0.4, spread=0.2, chunk_type="ice")

    def emitSmoke(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        ba.emitfx(position=spaz.node.position, velocity=spaz.node.velocity, count=random.randint(1,10), scale=2, spread=0.2, chunk_type="sweat")

    def emitSlime(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        ba.emitfx(position=spaz.node.position , velocity=spaz.node.velocity, count=random.randint(1,10), scale=0.4, spread=0.2, chunk_type="slime")

    def emitMetal(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.is_alive() or not spaz.node.exists():
            self.handlemessage(ba.DieMessage())
            return
        ba.emitfx(position=spaz.node.position, velocity=spaz.node.velocity, count=random.randint(2,8), scale=0.4, spread=0.2, chunk_type="metal")

    def handlemessage(self, m):
        #self._handlemessageSanityCheck()
        if isinstance(m, ba.OutOfBoundsMessage): self.handlemessage(ba.DieMessage())
        elif isinstance(m, ba.DieMessage):
            if hasattr(self,"light") and self.light is not None:self.light.delete()
            if hasattr(self,"smokeTimer"):self.smokeTimer = None
            if hasattr(self,"surround"):self.surround = None
            if hasattr(self,"sparkTimer"):self.sparkTimer = None
            if hasattr(self,"snowTimer"):self.snowTimer = None
            if hasattr(self,"metalTimer"):self.metalTimer = None
            if hasattr(self,"DistortionTimer"):self.DistortionTimer = None
            if hasattr(self,"slimeTimer"):self.slimeTimer = None
            if hasattr(self,"KamikazeCheck"):self.KamikazeCheck = None
            if hasattr(self,"neroLightTimer"):self.neroLightTimer = None
            if hasattr(self,"checkDeadTimer"):self.checkDeadTimer = None
            if hasattr(self,"HealTimer"):self.HealTimer = None
            if hasattr(self,"scorchTimer"):self.scorchTimer = None
            if hasattr(self,"scorchNode"):self.scorchNode = None
            if not self._hasDead:
                spaz = self.spazRef()
                #print str(spaz) + "Spaz"
                if spaz is not None and spaz.is_alive() and spaz.node.exists(): spaz.node.color = self.spazNormalColor
                killer = spaz.last_player_attacked_by if spaz is not None else None
                try:
                    if killer in (None,ba.Player(None)) or killer.actor is None or not killer.actor.exists() or killer.actor.hitPoints <= 0:killer = None
                except:
                    killer = None
                    #if hasattr(self,"hasDead") and not self.hasDead:
                self._hasDead = True

        ba.Actor.handlemessage(self, m)

############################# REPLACEMENT #############################
class PlayerSpazHurtMessage:
    """A message saying a ba.PlayerSpaz was hurt.

    category: Message Classes

    Attributes:

       spaz
          The ba.PlayerSpaz that was hurt
    """

    def __init__(self, spaz: PlayerSpaz):
        """Instantiate with the given ba.Spaz value."""
        self.spaz = spaz


class ModifiedPlayerSpaz(Spaz):
    """A ba.Spaz subclass meant to be controlled by a ba.Player.

    category: Gameplay Classes

    When a PlayerSpaz dies, it delivers a ba.PlayerDiedMessage
    to the current ba.Activity. (unless the death was the result of the
    player leaving the game, in which case no message is sent)

    When a PlayerSpaz is hurt, it delivers a ba.PlayerSpazHurtMessage
    to the current ba.Activity.
    """

    def __init__(self,
                 player: ba.Player,
                 color: Sequence[float] = (1.0, 1.0, 1.0),
                 highlight: Sequence[float] = (0.5, 0.5, 0.5),
                 character: str = 'Spaz',
                 powerups_expire: bool = True):
        """Create a spaz for the provided ba.Player.

        Note: this does not wire up any controls;
        you must call connect_controls_to_player() to do so.
        """

        super().__init__(color=color,
                         highlight=highlight,
                         character=character,
                         source_player=player,
                         start_invincible=True,
                         powerups_expire=powerups_expire)
        self.last_player_attacked_by: Optional[ba.Player] = None
        self.last_attacked_time = 0.0
        self.last_attacked_type: Optional[Tuple[str, str]] = None
        self.held_count = 0
        self.last_player_held_by: Optional[ba.Player] = None
        self._player = player
        self._drive_player_position()
        self.admin_enhancment = Enhancement(self, self._player).autoretain()
        if ba.do_once():
            add_mychar_media()

    # Overloads to tell the type system our return type based on doraise val.

    @overload
    def getplayer(self,
                  playertype: Type[PlayerType],
                  doraise: Literal[False] = False) -> Optional[PlayerType]:
        ...

    @overload
    def getplayer(self, playertype: Type[PlayerType],
                  doraise: Literal[True]) -> PlayerType:
        ...

    def getplayer(self,
                  playertype: Type[PlayerType],
                  doraise: bool = False) -> Optional[PlayerType]:
        """Get the ba.Player associated with this Spaz.

        By default this will return None if the Player no longer exists.
        If you are logically certain that the Player still exists, pass
        doraise=False to get a non-optional return type.
        """
        player: Any = self._player
        assert isinstance(player, playertype)
        if not player.exists() and doraise:
            raise ba.PlayerNotFoundError()
        return player if player.exists() else None

    def connect_controls_to_player(self,
                                   enable_jump: bool = True,
                                   enable_punch: bool = True,
                                   enable_pickup: bool = True,
                                   enable_bomb: bool = True,
                                   enable_run: bool = True,
                                   enable_fly: bool = True) -> None:
        """Wire this spaz up to the provided ba.Player.

        Full control of the character is given by default
        but can be selectively limited by passing False
        to specific arguments.
        """
        player = self.getplayer(ba.Player)
        assert player

        # Reset any currently connected player and/or the player we're
        # wiring up.
        if self._connected_to_player:
            if player != self._connected_to_player:
                player.resetinput()
            self.disconnect_controls_from_player()
        else:
            player.resetinput()

        player.assigninput(ba.InputType.UP_DOWN, self.on_move_up_down)
        player.assigninput(ba.InputType.LEFT_RIGHT, self.on_move_left_right)
        player.assigninput(ba.InputType.HOLD_POSITION_PRESS,
                           self.on_hold_position_press)
        player.assigninput(ba.InputType.HOLD_POSITION_RELEASE,
                           self.on_hold_position_release)
        intp = ba.InputType
        if enable_jump:
            player.assigninput(intp.JUMP_PRESS, self.on_jump_press)
            player.assigninput(intp.JUMP_RELEASE, self.on_jump_release)
        if enable_pickup:
            player.assigninput(intp.PICK_UP_PRESS, self.on_pickup_press)
            player.assigninput(intp.PICK_UP_RELEASE, self.on_pickup_release)
        if enable_punch:
            player.assigninput(intp.PUNCH_PRESS, self.on_punch_press)
            player.assigninput(intp.PUNCH_RELEASE, self.on_punch_release)
        if enable_bomb:
            player.assigninput(intp.BOMB_PRESS, self.on_bomb_press)
            player.assigninput(intp.BOMB_RELEASE, self.on_bomb_release)
        if enable_run:
            player.assigninput(intp.RUN, self.on_run)
        if enable_fly:
            player.assigninput(intp.FLY_PRESS, self.on_fly_press)
            player.assigninput(intp.FLY_RELEASE, self.on_fly_release)

        self._connected_to_player = player

    def disconnect_controls_from_player(self) -> None:
        """
        Completely sever any previously connected
        ba.Player from control of this spaz.
        """
        if self._connected_to_player:
            self._connected_to_player.resetinput()
            self._connected_to_player = None

            # Send releases for anything in case its held.
            self.on_move_up_down(0)
            self.on_move_left_right(0)
            self.on_hold_position_release()
            self.on_jump_release()
            self.on_pickup_release()
            self.on_punch_release()
            self.on_bomb_release()
            self.on_run(0.0)
            self.on_fly_release()
        else:
            print('WARNING: disconnect_controls_from_player() called for'
                  ' non-connected player')

    def handlemessage(self, msg: Any) -> Any:
        # FIXME: Tidy this up.
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-nested-blocks
        assert not self.expired

        # Keep track of if we're being held and by who most recently.
        if isinstance(msg, ba.PickedUpMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            self.held_count += 1
            picked_up_by = msg.node.source_player
            if picked_up_by:
                self.last_player_held_by = picked_up_by
        elif isinstance(msg, ba.DroppedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            self.held_count -= 1
            if self.held_count < 0:
                print('ERROR: spaz held_count < 0')

            # Let's count someone dropping us as an attack.
            picked_up_by = msg.node.source_player
            if picked_up_by:
                self.last_player_attacked_by = picked_up_by
                self.last_attacked_time = ba.time()
                self.last_attacked_type = ('picked_up', 'default')
        elif isinstance(msg, ba.StandMessage):
            super().handlemessage(msg)  # Augment standard behavior.

            # Our Spaz was just moved somewhere. Explicitly update
            # our associated player's position in case it is being used
            # for logic (otherwise it will be out of date until next step)
            self._drive_player_position()

        elif isinstance(msg, ba.DieMessage):

            # Report player deaths to the game.
            if not self._dead:

                # Immediate-mode or left-game deaths don't count as 'kills'.
                killed = (not msg.immediate
                          and msg.how is not ba.DeathType.LEFT_GAME)

                activity = self._activity()

                player = self.getplayer(ba.Player, False)
                if not killed:
                    killerplayer = None
                else:
                    # If this player was being held at the time of death,
                    # the holder is the killer.
                    if self.held_count > 0 and self.last_player_held_by:
                        killerplayer = self.last_player_held_by
                    else:
                        # Otherwise, if they were attacked by someone in the
                        # last few seconds, that person is the killer.
                        # Otherwise it was a suicide.
                        # FIXME: Currently disabling suicides in Co-Op since
                        #  all bot kills would register as suicides; need to
                        #  change this from last_player_attacked_by to
                        #  something like last_actor_attacked_by to fix that.
                        if (self.last_player_attacked_by
                                and ba.time() - self.last_attacked_time < 4.0):
                            killerplayer = self.last_player_attacked_by
                        else:
                            # ok, call it a suicide unless we're in co-op
                            if (activity is not None and not isinstance(
                                    activity.session, ba.CoopSession)):
                                killerplayer = player
                            else:
                                killerplayer = None

                # We should never wind up with a dead-reference here;
                # we want to use None in that case.
                assert killerplayer is None or killerplayer

                # Only report if both the player and the activity still exist.
                if killed and activity is not None and player:
                    activity.handlemessage(
                        ba.PlayerDiedMessage(player, killed, killerplayer,
                                             msg.how))

            super().handlemessage(msg)  # Augment standard behavior.

        #POWERUPS
        elif isinstance(msg, ba.PowerupMessage):
            if self._dead or not self.node:
                return True
            if self.pick_up_powerup_callback is not None:
                self.pick_up_powerup_callback(self)
            if msg.poweruptype == 'triple_bombs':
                tex = PowerupBoxFactory.get().tex_bomb
                self._flash_billboard(tex)
                self.set_bomb_count(3)
                PopupText("Now 3x Bombing !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
                if self.powerups_expire:
                    self.node.mini_billboard_1_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_1_start_time = t_ms
                    self.node.mini_billboard_1_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME)
                    self._multi_bomb_wear_off_timer = (ba.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000),
                        ba.WeakCall(self._multi_bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._multi_bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._multi_bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'land_mines':
                self.set_land_mine_count(min(self.land_mine_count + 3, 3))
                PopupText("Its Mining Time !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
            elif msg.poweruptype == 'impact_bombs':
                self.bomb_type = 'impact'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                PopupText("War has come !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME)
                    self._bomb_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'sticky_bombs':
                self.bomb_type = 'sticky'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                PopupText("Lets stick ppls !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME)
                    self._bomb_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'punch':
                self._has_boxing_gloves = True
                tex = PowerupBoxFactory.get().tex_punch
                self._flash_billboard(tex)
                self.equip_boxing_gloves()
                PopupText("Its Boxing Time !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
                if self.powerups_expire:
                    self.node.boxing_gloves_flashing = False
                    self.node.mini_billboard_3_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_3_start_time = t_ms
                    self.node.mini_billboard_3_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME)
                    self._boxing_gloves_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._gloves_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._boxing_gloves_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._gloves_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'shield':
                factory = SpazFactory.get()

                # Let's allow powerup-equipped shields to lose hp over time.
                self.equip_shields(decay=factory.shield_decay_rate > 0)
                PopupText("Geared Up !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
            elif msg.poweruptype == 'curse':
                self.curse()
                PopupText("Waaadu !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
            elif msg.poweruptype == 'ice_bombs':
                self.bomb_type = 'ice'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                PopupText("Its Winter wars !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME)
                    self._bomb_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'health':
                if self._cursed:
                    self._cursed = False

                    # Remove cursed material.
                    factory = SpazFactory.get()
                    for attr in ['materials', 'roller_materials']:
                        materials = getattr(self.node, attr)
                        if factory.curse_material in materials:
                            setattr(
                                self.node, attr,
                                tuple(m for m in materials
                                      if m != factory.curse_material))
                    self.node.curse_death_time = 0
                self.hitpoints = self.hitpoints_max
                self._flash_billboard(PowerupBoxFactory.get().tex_health)
                self.node.hurt = 0
                self._last_hit_time = None
                self._num_times_hit = 0
                PopupText("God is there !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
            elif msg.poweruptype == 'cc':
                if self.node.exists():
                    c = random.choice(cList)
                    s = c + 'Head'
                    if self.node.head_model == s:
                        cList.remove(c)
                        n = random.choice(cList)
                    else: n = c
                    name = nList[n]
                    cMedia = mymedia[name]
                    a = self.node
                    a.jump_sounds = cMedia['jump_sounds'] #Errors
                    a.attack_sounds = cMedia['attack_sounds']
                    a.impact_sounds = cMedia['impact_sounds']
                    a.death_sounds = cMedia['death_sounds']
                    a.pickup_sounds = cMedia['pickup_sounds']
                    a.fall_sounds = cMedia['fall_sounds']
                    a.color_texture = cMedia['color_texture']
                    a.color_mask_texture = cMedia['color_mask_texture']
                    a.head_model = cMedia['head_model']
                    a.torso_model = cMedia['torso_model']
                    a.pelvis_model = cMedia['pelvis_model']
                    a.upper_arm_model = cMedia['upper_arm_model']
                    a.forearm_model = cMedia['forearm_model']
                    a.hand_model = cMedia['hand_model']
                    a.upper_leg_model = cMedia['upper_leg_model']
                    a.lower_leg_model = cMedia['lower_leg_model']
                    a.toes_model = cMedia['toes_model']
                    a.style = SpazFactory.get().get_style(name)
                    PopupText(f"Now i am {name} !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
            elif msg.poweruptype == 'Speed':
                tex = ba.gettexture("powerupSpeed")
                self._flash_billboard(tex)
                if self.node.exists():
                    PopupText("GOD SPEED !",color=((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),scale=1.6,position=self.node.position).autoretain()
                    self.node.hockey = True
                if self.powerups_expire:
                    self.node.mini_billboard_1_texture = tex
                    t = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    self.node.mini_billboard_1_start_time = t
                    self.node.mini_billboard_1_end_time = t + POWERUP_WEAR_OFF_TIME
                    self._speed_wear_off_flash_timer = ba.Timer(POWERUP_WEAR_OFF_TIME-2000,ba.WeakCall(self._speed_wear_off_flash), timeformat=ba.TimeFormat.MILLISECONDS)
                    self._speed_wear_off_timer = ba.Timer(POWERUP_WEAR_OFF_TIME,ba.WeakCall(self._speed_wear_off), timeformat=ba.TimeFormat.MILLISECONDS)

            self.node.handlemessage('flash')
            if msg.sourcenode:
                msg.sourcenode.handlemessage(ba.PowerupAcceptMessage())
            return True

        elif isinstance(msg, ba.HitMessage):
            source_player = msg.get_source_player(type(self._player))
            if source_player:
                self.last_player_attacked_by = source_player
                self.last_attacked_time = ba.time()
                self.last_attacked_type = (msg.hit_type, msg.hit_subtype)
            activity = self._activity()
            if activity is not None and self._player.exists():
                activity.handlemessage(PlayerSpazHurtMessage(self))
            if not self.node:
                return None
            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

            # If we were recently hit, don't count this as another.
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
            assert isinstance(local_time, int)
            if (self._last_hit_time is None
                    or local_time - self._last_hit_time > 1000):
                self._num_times_hit += 1
                self._last_hit_time = local_time

            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            # If they've got a shield, deliver it to that instead.
            if self.shield:
                if msg.flat_damage:
                    damage = msg.flat_damage * self.impact_scale
                else:
                    # Hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse.
                    assert msg.force_direction is not None
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 1, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])
                    damage = damage_scale * self.node.damage

                assert self.shield_hitpoints is not None
                self.shield_hitpoints -= int(damage)
                self.shield.hurt = (
                    1.0 -
                    float(self.shield_hitpoints) / self.shield_hitpoints_max)

                # Its a cleaner event if a hit just kills the shield
                # without damaging the player.
                # However, massive damage events should still be able to
                # damage the player. This hopefully gives us a happy medium.
                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:

                    # FIXME: Transition out perhaps?
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,
                                 1.0,
                                 position=self.node.position)

                    # Emit some cool looking sparks when the shield dies.
                    npos = self.node.position
                    ba.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                              velocity=self.node.velocity,
                              count=random.randrange(20, 30),
                              scale=1.0,
                              spread=0.6,
                              chunk_type='spark')

                else:
                    ba.playsound(SpazFactory.get().shield_hit_sound,
                                 0.5,
                                 position=self.node.position)

                # Emit some cool looking sparks on shield hit.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                # If they passed our spillover threshold,
                # pass damage along to spaz.
                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    # Scale down the magnitudes applied to spaz accordingly.
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True  # Good job shield!
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                # Hit it with an impulse and get the resulting damage.
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                    msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                    velocity_mag, msg.radius, 0, msg.force_direction[0],
                    msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                self.on_punched(damage)

                #HIT MESSAGE
                if mysettings.settings['hitTexts']:
                    if damage >= 800: PopupText("#PRO !",color=(1,0.2,0.2),scale=1.6,position=self.node.position).autoretain()
                    elif damage >= 600 and damage < 800: PopupText("GOOD ONE!",color=(1,0.3,0.1),scale=1.6,position=self.node.position).autoretain()
                    elif damage >= 400 and damage < 600: PopupText("OH! YEAH",color=(1,0.5,0.2),scale=1.6,position=self.node.position).autoretain()
                    elif damage >= 200 and damage < 400: PopupText("WTF!",color=(0.7,0.4,0.2),scale=1.6,position=self.node.position).autoretain()
                    elif damage > 0 and damage < 200: PopupText("!!!",color=(1,1,1),scale=1.6,position=self.node.position).autoretain()
                if self.hitpoints <= 0: PopupText("Rest In Peace !",color=(1,0.2,0.2),scale=1.6,position=self.node.position).autoretain()

                # If damage was significant, lets show it.
                if damage > 350:
                    assert msg.force_direction is not None
                    ba.show_damage_count('-' + str(int(damage / 10)) + '%',
                                         msg.pos, msg.force_direction)

                # Let's always add in a super-punch sound with boxing
                # gloves just to differentiate them.
                if msg.hit_subtype == 'super_punch':
                    ba.playsound(SpazFactory.get().punch_sound_stronger,
                                 1.0,
                                 position=self.node.position)
                if damage > 500:
                    sounds = SpazFactory.get().punch_sound_strong
                    sound = sounds[random.randrange(len(sounds))]
                else:
                    sound = SpazFactory.get().punch_sound
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

                # Momentary flash.
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

            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)
            if self.hitpoints > 0:

                # It's kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount *if* it'll keep us alive
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    # Drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                # If we're cursed, *any* damage blows us up.
                if self._cursed and damage > 0:
                    ba.timer(
                        0.05,
                        ba.WeakCall(self.curse_explode,
                                    msg.get_source_player(ba.Player)))

                # If we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        ba.DieMessage(how=ba.DeathType.IMPACT))

            # If we're dead, take a look at the smoothed damage value
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough.
            if self.hitpoints <= 0:
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()

            #Record the damage
            if True: #try:
                if self.last_player_attacked_by is not None:
                    hit_by = self.last_player_attacked_by.node.playerID
                    if hit_by:
                        from mystats import damage_data
                        hit_by_account_id = None
                        for c in _ba.get_foreground_host_session().sessionplayers:
                            if (c.activityplayer) and (c.activityplayer.node.playerID == hit_by):
                                hit_by_account_id = c.get_account_id()
                        our_dmg = damage / 10
                        if hit_by_account_id in damage_data: damage_data[hit_by_account_id] += float(our_dmg)
                        else: damage_data[hit_by_account_id] = float(our_dmg)
            #except: pass
        else:
            return super().handlemessage(msg)
        return None

    def _drive_player_position(self) -> None:
        """Drive our ba.Player's official position

        If our position is changed explicitly, this should be called again
        to instantly update the player position (otherwise it would be out
        of date until the next sim step)
        """
        player = self._player
        if player:
            assert self.node
            assert player.node
            self.node.connectattr('torso_position', player.node, 'position')

    def _speed_wear_off_flash(self) -> None:
        if self.node.exists():
            self.node.billboard_texture = ba.gettexture("powerupSpeed")
            self.node.billboard_opacity = 1.0
            self.node.billboard_cross_out = True

    def _speed_wear_off(self) -> None:
        if self.node.exists():
            self.node.hockey = False
            ba.playsound(PowerupBoxFactory.get().powerdown_sound,
                         position=self.node.position)
            self.node.billboard_opacity = 0.0

playerspaz.PlayerSpaz = ModifiedPlayerSpaz