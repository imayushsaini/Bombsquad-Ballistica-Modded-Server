# -*- coding: utf-8 -*-
# Released under the MIT License. See LICENSE for details.
#
"""Functionality related to player-controlled Spazzes."""

from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, overload
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
import ba,_ba,bastd,weakref,random,math,time,base64,os,json,setting
import ba.internal
from playersData import pdata
from stats import mystats
PlayerType = TypeVar('PlayerType', bound=ba.Player)
TeamType = TypeVar('TeamType', bound=ba.Team)
from ba._generated.enums import TimeType
tt = ba.TimeType.SIM
tf = ba.TimeFormat.MILLISECONDS

multicolor = {0:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              250:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              500:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              750:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              1000:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              1250:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              1500:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              1750:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              2000:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              2250:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0)),
              2500:((0+random.random()*3.0),(0+random.random()*3.0),(0+random.random()*3.0))}

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
        self.surroundTimer = ba.Timer(30, self.circleMove, repeat=True, timetype=tt, timeformat=tf)

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

class Effect(ba.Actor):
    def __init__(self, spaz, player):
        ba.Actor.__init__(self)
        _settings = setting.get_settings_data()
        custom_tag = pdata.get_custom()['customtag']
        custom_effects = pdata.get_custom()['customeffects']
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

        node_id = self.source_player.node.playerID
        cl_str = None
        clID = None
        for c in ba.internal.get_foreground_host_session().sessionplayers:
            if (c.activityplayer) and (c.activityplayer.node.playerID == node_id):
                profiles = c.inputdevice.get_player_profiles()
                clID = c.inputdevice.client_id
                cl_str = c.get_v1_account_id()

        try:
            if cl_str in custom_effects:
                effect = custom_effects[cl_str]

                if effect == 'ice':

                    self.emitIce()
                    self.snowTimer = ba.Timer(0.5, self.emitIce, repeat=True, timetype=TimeType.SIM)
                    return
                elif effect == 'sweat':
                    self.smokeTimer = ba.Timer(0.6, self.emitSmoke, repeat=True, timetype=TimeType.SIM)
                    return
                elif effect == 'scorch':
                    self.scorchTimer = ba.Timer(500, self.update_Scorch, repeat=True, timetype=tt, timeformat=tf)
                    return
                elif effect == 'glow':
                    self.addLightColor((1, 0.6, 0.4))
                    self.checkDeadTimer = ba.Timer(150, self.checkPlayerifDead, repeat=True, timetype=tt, timeformat=tf)
                    return
                elif effect == 'distortion':
                    self.DistortionTimer = ba.Timer(1000, self.emitDistortion, repeat=True, timetype=tt, timeformat=tf)
                    return
                elif effect == 'slime':
                    self.slimeTimer = ba.Timer(250, self.emitSlime, repeat=True, timetype=tt, timeformat=tf)
                    return
                elif effect == 'metal':
                    self.metalTimer = ba.Timer(500, self.emitMetal, repeat=True, timetype=tt, timeformat=tf)
                    return
                elif effect == 'surrounder':
                    self.surround = SurroundBall(spaz, shape="bones")
                    return
                elif effect == 'spark':
                    self.sparkTimer = ba.Timer(100, self.emitSpark, repeat=True, timetype=tt, timeformat=tf)
                    return
        except:
            pass

        if _settings['enablestats']:
            pats = mystats.get_all_stats()
            if cl_str in pats and _settings['enableTop5effects']:
                rank = pats[cl_str]["rank"]
                if rank < 6:
                    if rank == 1:

                        self.surround = SurroundBall(spaz, shape="bones") #self.neroLightTimer = ba.Timer(500, ba.WeakCall(self.neonLightSwitch,("shine" in self.Decorations),("extra_Highlight" in self.Decorations),("extra_NameColor" in self.Decorations)),repeat = True, timetype=tt, timeformat=tf)
                    elif rank == 2:

                        self.smokeTimer = ba.Timer(40, self.emitSmoke, repeat=True, timetype=tt, timeformat=tf)
                    elif rank == 3:

                        self.addLightColor((1, 0.6, 0.4));self.scorchTimer = ba.Timer(500, self.update_Scorch, repeat=True, timetype=tt, timeformat=tf)
                    elif rank == 4:

                        self.metalTimer = ba.Timer(500, self.emitMetal, repeat=True, timetype=tt, timeformat=tf)
                    else:

                        self.addLightColor((1, 0.6, 0.4));self.checkDeadTimer = ba.Timer(150, self.checkPlayerifDead, repeat=True, timetype=tt, timeformat=tf)

        if "smoke" and "spark" and "snowDrops" and "slimeDrops" and "metalDrops" and "Distortion" and "neroLight" and "scorch" and "HealTimer" and "KamikazeCheck" not in self.Decorations:
            #self.checkDeadTimer = ba.Timer(150, ba.WeakCall(self.checkPlayerifDead), repeat=True, timetype=tt, timeformat=tf)
            if self.source_player.is_alive() and self.source_player.actor.node.exists():
                #print("OK")
                self.source_player.actor.node.addDeathAction(ba.Call(self.handlemessage,ba.DieMessage()))

    def add_multicolor_effect(self):
        if spaz.node: ba.animate_array(spaz.node, 'color', 3, multicolor, True, timetype=tt, timeformat=tf)

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
            if hasattr(self,"scorchNode"):
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
