# ba_meta require api 7
from __future__ import annotations
from typing import TYPE_CHECKING
_sp_ = ('\n')

import ba,_ba,random,time,datetime,weakref,json
import ba.internal
from bastd.ui.profile import browser
from bastd.actor import bomb
from bastd.actor import powerupbox  as pupbox
from bastd.actor.spazbot import SpazBot
from bastd.actor.bomb import (Bomb,Blast)
from bastd.ui.popup import (PopupWindow,PopupMenuWindow,PopupMenu)
from bastd.actor.spaz import (Spaz,SpazFactory,PickupMessage, PunchHitMessage,
                              CurseExplodeMessage, BombDiedMessage)
from bastd.mainmenu import (MainMenuActivity,MainMenuSession)
from bastd.gameutils import SharedObjects
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.actor.popuptext import PopupText
from bastd.ui.confirm import ConfirmWindow
from bastd.actor.spaz import *

if TYPE_CHECKING:
    pass

# === Mod made by @Patron_Modz ===

def getlanguage(text, subs: str = None, almacen: list = []):
    if almacen == []: almacen = list(range(1000))
    lang = _ba.app.lang.language
    translate = {"Reset":
                      {"Spanish": "Reiniciar",
                       "English": "Reset",
                       "Portuguese": "Reiniciar"},
                 "Nothing":
                      {"Spanish": "Sin potenciadores",
                       "English": "No powerups",
                       "Portuguese": "Sem powerups"},
                 "Action 1":
                      {"Spanish": "Potenciadores",
                       "English": "Powerups",
                       "Portuguese": "Powerups"},
                 "Action 2":
                      {"Spanish": "ConfiguraciÃ³n",
                       "English": "Settings",
                       "Portuguese": "DefiniÃ§Ãµes"},
                 "Action 3":
                      {"Spanish": "Extras",
                       "English": "Extras",
                       "Portuguese": "Extras"},
                 "Action 4":
                      {"Spanish": "Tienda",
                       "English": "Store",
                       "Portuguese": "Loja"},
                 "Action 5":
                      {"Spanish": "Canjear cÃ³digo",
                       "English": "Enter Code",
                       "Portuguese": "CÃ³digo promocional"},
                 "Custom":
                      {"Spanish": "",
                       "English": "Customize",
                       "Portuguese": "Customizar"},
                 "Impairment Bombs":
                      {"Spanish": "Bombas menoscabo",
                       "English": "Hyperactive bombs",
                       "Portuguese": "Bombas hiperativas"},
                 "Speed":
                      {"Spanish": "Velocidad",
                       "English": "Speed",
                       "Portuguese": "Velocidade"},
                 "Fire Bombs":
                      {"Spanish": "Bombas de fuego",
                       "English": "Fire Bombs",
                       "Portuguese": "Bombas de fogo"},
                 "Ice Man":
                      {"Spanish": "Hombre de hielo",
                       "English": "Ice man",
                       "Portuguese": "Homem de gelo"},
                 "Fly Bombs":
                      {"Spanish": "Bombas expansivas",
                       "English": "Expansive bombs",
                       "Portuguese": "Bombas expansivas"},
                 "Goodbye":
                      {"Spanish": "Â¡Hasta luego!",
                       "English": "Goodbye!",
                       "Portuguese": "Adeus!"},
                 "Healing Damage":
                      {"Spanish": "Auto-curaciÃ³n",
                       "English": "Healing Damage",
                       "Portuguese": "Auto-cura"},
                 "Tank Shield":
                      {"Spanish": "SÃºper blindaje",
                       "English": "Reinforced shield",
                       "Portuguese": "Escudo reforÃ§ado"},
                 "Tank Shield PTG":
                      {"Spanish": "Porcentaje de disminuciÃ³n",
                       "English": "Percentage decreased",
                       "Portuguese": "Percentual reduzido"},
                 "Healing Damage PTG":
                      {"Spanish": "Porcentaje de recuperaciÃ³n de salud",
                       "English": "Percentage of health recovered",
                       "Portuguese": "Porcentagem de recuperaÃ§Ã£o de saÃºde"},
                 "SY: BALL":
                      {"Spanish": "Esfera",
                       "English": "Sphere",
                       "Portuguese": "Esfera"},
                 "SY: Impact":
                      {"Spanish": "Especial",
                       "English": "Special",
                       "Portuguese": "Especial"},
                 "SY: Egg":
                      {"Spanish": "Huevito",
                       "English": "Egg shape",
                       "Portuguese": "Ovo"},
                 "Powerup Scale":
                      {"Spanish": "TamaÃ±o del potenciador",
                       "English": "Powerups size",
                       "Portuguese": "Tamanho de powerups"},
                 "Powerup With Shield":
                      {"Spanish": "Potenciadores con escudo",
                       "English": "Powerups with shield",
                       "Portuguese": "Powerups com escudo"},
                 "Powerup Time":
                      {"Spanish": "Mostrar Temporizador",
                       "English": "Show end time",
                       "Portuguese": "Mostrar cronÃ´metro"},
                 "Powerup Style":
                      {"Spanish": "Forma de los potenciadores",
                       "English": "Shape of powerup",
                       "Portuguese": "Forma de powerup"},
                 "Powerup Name":
                      {"Spanish": "Mostrar nombre en los potenciadores",
                       "English": "Show name on powerups",
                       "Portuguese": "Mostrar nome em powerups"},
                 "Percentage":
                      {"Spanish": "Probabilidad",
                       "English": "Show percentage",
                       "Portuguese": "Mostrar porcentagem"},
                 "Only Items":
                      {"Spanish": "SÃ³lo Accesorios",
                       "English": "Only utensils",
                       "Portuguese": "Apenas utensilios"},
                 "New":
                      {"Spanish": "Nuevo",
                       "English": "New",
                       "Portuguese": "Novo"},
                 "Only Bombs":
                      {"Spanish": "SÃ³lo Bombas",
                       "English": "Only bombs",
                       "Portuguese": "Apenas bombas"},
                 "Coins 0":
                      {"Spanish": "Monedas Insuficientes",
                       "English": "Insufficient coins",
                       "Portuguese": "Moedas insuficientes"},
                 "Purchase":
                      {"Spanish": "Compra realizada correctamente",
                       "English": "Successful purchase",
                       "Portuguese": "Compra Bem Sucedida"},
                 "Double Product":
                      {"Spanish": "Ya has comprado este artÃ­culo",
                       "English": "You've already bought this",
                       "Portuguese": "Voce ja comprou isto"},
                 "Bought":
                      {"Spanish": "Comprado",
                       "English": "Bought",
                       "Portuguese": "Comprou"},
                 "Confirm Purchase":
                      {"Spanish": f'Tienes {subs} monedas. {_sp_} Â¿Deseas comprar esto?',
                       "English": f'You have {subs} coins. {_sp_} Do you want to buy this?',
                       "Portuguese": f'VocÃª tem {subs} moedas. {_sp_} Deseja comprar isto?'},
                 "FireBombs Store":
                      {"Spanish": 'Bombas de fuego',
                       "English": 'Fire bombs',
                       "Portuguese": 'Bombas de incÃªndio'},
                 "Timer Store":
                      {"Spanish": 'Temporizador',
                       "English": 'Timer',
                       "Portuguese": 'Timer'},
                 "Percentages Store":
                      {"Spanish": 'Extras',
                       "English": 'Extras',
                       "Portuguese": 'Extras'},
                 "Block Option Store":
                      {"Spanish": f"Uuups..{_sp_}Esta opciÃ³n estÃ¡ bloqueada.{_sp_} Para acceder a ella puedes {_sp_} comprarla en la tienda.{_sp_} Gracias...",
                       "English": f"Oooops...{_sp_}This option is blocked. {_sp_} To access it you can buy {_sp_} it in the store.{_sp_} Thank you...",
                       "Portuguese": f"Ooops...{_sp_}Esta opÃ§Ã£o estÃ¡ bloqueada. {_sp_} Para acessÃ¡-lo, vocÃª pode {_sp_} comprÃ¡-lo na loja.{_sp_} Obrigado..."},
                 "True Code":
                      {"Spanish": "Â¡CÃ³digo canjeado!",
                       "English": "Successful code!",
                       "Portuguese": "Â¡CÃ³digo vÃ¡lido!"},
                 "False Code":
                      {"Spanish": "CÃ³digo ya canjeado",
                       "English": "Expired code",
                       "Portuguese": "CÃ³digo expirado"},
                 "Invalid Code":
                      {"Spanish": "CÃ³digo invÃ¡lido",
                       "English": "Invalid code",
                       "Portuguese": "CÃ³digo invÃ¡lido"},
                 "Reward Code":
                      {"Spanish": f"Â¡Felicitaciones! Â¡Ganaste {subs} monedas!",
                       "English": f"Congratulations! You've {subs} coins",
                       "Portuguese": f"ParabÃ©ns! VocÃª tem {subs} moedas"},
                 "Creator":
                      {"Spanish": "Mod creado por @PatrÃ³nModz",
                       "English": "Mod created by @PatrÃ³nModz",
                       "Portuguese": "Mod creado by @PatrÃ³nModz"},
                 "Mod Info":
                      {"Spanish": f"Un mod genial que te permite gestionar {_sp_} los potenciadores a tu antojo. {_sp_} tambiÃ©n incluye 8 potenciadores extra{_sp_} dejando 17 en total... Â¡Guay!",
                       "English": f"A cool mod that allows you to manage {_sp_} powerups at your whims. {_sp_} also includes 8 extra powerups{_sp_} leaving 17 in total... Wow!",
                       "Portuguese": f"Um mod legal que permite que vocÃª gerencie os{_sp_} powerups de de acordo com seus caprichos. {_sp_} tambÃ©m inclui 8 powerups extras,{_sp_} deixando 17 no total... Uau!"},
                 "Coins Message":
                      {"Spanish": f"Recompensa: {subs} Monedas",
                       "English": f"Reward: {subs} Coins",
                       "Portuguese": f"Recompensa: {subs} Moedas"},
                 "Coins Limit Message":
                      {"Spanish": f"Ganaste {almacen[0]} Monedas.{_sp_} Pero has superado el lÃ­mite de {almacen[1]}",
                       "English": f"You won {almacen[0]} Coins. {_sp_} But you have exceeded the limit of {almacen[1]}",
                       "Portuguese": f"VocÃª ganhou {almacen[0]} Moedas. {_sp_} Mas vocÃª excedeu o limite de {almacen[1]}"},
                 }
    languages = ['Spanish','Portuguese','English']
    if lang not in languages: lang = 'English'

    if text not in translate:
        return text
    
    return translate[text][lang]

import setting
settings=setting.get_settings_data()

def settings_distribution():
    return settings["elPatronPowerups"]["settings"]



apg = ba.app.config

apg['PPM Settings'] = settings_distribution()


config = apg['PPM Settings']

def default_powerups():
    return settings["elPatronPowerups"]["Quantity"]


config['Powerups'] = default_powerups()


powerups = config['Powerups']

# === EXTRAS ===

GLOBAL = {"Tab": 'Action 1',
          "Cls Powerup": 0,
          "Coins Message": []}

# === STORE ===
def promo_codes():
    return {"G-Am54igO42Os": [True,1100],
            "P-tRo8nM8dZ": [True,2800],
            "Y-tU2B3S": [True,500],
            "B-0mB3RYT2z": [True,910],
            "B-Asd14mON9G0D": [True,910],
            "D-rAcK0cJ23": [True,910],
            "E-a27ZO6f3Y": [True,600],
            "E-Am54igO42Os": [True,600],
            "E-M4uN3K34XB": [True,840],
            "PM-731ClcAF": [True,50000]}
            
def store_items():
    return {"Buy Firebombs": False,
            "Buy Option": False,
            "Buy Percentage": False}

if apg.get('Bear Coin') is None:
    apg['Bear Coin'] = 0
    apg.apply_and_commit()
    
if apg.get('Bear Coin') is not None:
    if apg['Bear Coin'] <= 0:
        apg['Bear Coin'] = 0
    apg['Bear Coin'] = int(apg['Bear Coin'])

if apg.get('Bear Store') is None:
    apg['Bear Store'] = {}
    
for i,j in store_items().items():
    store  = apg['Bear Store']
    if i not in store:
        if store.get(i) is None:
            store[i] = j
    apg.apply_and_commit()

STORE = apg['Bear Store']

if STORE.get('Promo Code') is None:
    STORE['Promo Code'] = promo_codes()

for i,x in promo_codes().items():
    pmcode = STORE['Promo Code']
    if i not in pmcode:
        if pmcode.get(i) is None:
            pmcode[i] = x

apg.apply_and_commit()

class BearStore:
    def __init__(self,
                 price: int = 1000,
                 value: str = '',
                 callback: call = None):
                     
        self.price = price
        self.value = value
        self.store = STORE[value]
        self.coins = apg['Bear Coin']
        self.callback = callback
                 
    def buy(self):
        if not self.store:
            if self.coins >= (self.price):
                def confirm():
                    STORE[self.value] = True
                    apg['Bear Coin'] -= int(self.price)
                    ba.screenmessage(getlanguage('Purchase'),(0,1,0))
                    ba.playsound(ba.getsound('cashRegister'))
                    apg.apply_and_commit()
                    self.callback()
                ConfirmWindow(getlanguage('Confirm Purchase',subs=self.coins),
                      width=400, height=120, action=confirm, ok_text=ba.Lstr(resource='okText'))
            else:
                ba.screenmessage(getlanguage('Coins 0'),(1,0,0))
                ba.playsound(ba.getsound('error'))
        else:
            ba.screenmessage(getlanguage('Double Product'),(1,0,0))
            ba.playsound(ba.getsound('error'))

    def __del__(self):
        apg['Bear Coin'] = int(apg['Bear Coin'])
        apg.apply_and_commit()

class PromoCode:
    def __init__(self, code: str = ''):
        self.code = code
        self.codes_store = STORE['Promo Code']
        if self.code in self.codes_store:
            self.code_type = STORE['Promo Code'][code]
            self.promo_code_expire = self.code_type[0]
            self.promo_code_amount = self.code_type[1]

    def __del__(self):
        apg['Bear Coin'] = int(apg['Bear Coin'])
        apg.apply_and_commit()

    def code_confirmation(self):
        if self.code != "":
            ba.screenmessage(
                ba.Lstr(resource='submittingPromoCodeText'),(0,1,0))
            ba.timer(2,ba.Call(self.validate_code))

    def validate_code(self):
        if self.code in self.codes_store:
            if self.promo_code_expire:
                ba.timer(1.5,ba.Call(self.successful_code))
                ba.screenmessage(getlanguage('True Code'),(0,1,0))
                ba.playsound(ba.getsound('cheer'))
                self.code_type[0] = False
            else:
                ba.screenmessage(getlanguage('False Code'),(1,0,0))
                ba.playsound(ba.getsound('error'))
        else:
            ba.screenmessage(getlanguage('Invalid Code'),(1,0,0))
            ba.playsound(ba.getsound('error'))

    def successful_code(self):
        apg['Bear Coin'] += self.promo_code_amount
        ba.screenmessage(getlanguage('Reward Code',
            subs=self.promo_code_amount),(0,1,0))
        ba.playsound(ba.getsound('cashRegister2'))

MainMenuActivity.super_transition_in = MainMenuActivity.on_transition_in
def new_on_transition_in(self):
    self.super_transition_in()
    limit = 8400
    bear_coin = apg['Bear Coin']
    coins_message = GLOBAL['Coins Message']
    try:
        if not (STORE['Buy Firebombs'] and
                STORE['Buy Option'] and
                STORE['Buy Percentage']):
                    
            if coins_message != []:
                result = 0
                for i in coins_message:
                    result += i

                if not bear_coin >= (limit-1):
                    ba.screenmessage(getlanguage('Coins Message',subs=result),(0,1,0))
                    ba.playsound(ba.getsound('cashRegister'))
                else:
                    ba.screenmessage(getlanguage('Coins Limit Message',
                        almacen=[result,limit]),(1,0,0))
                    ba.playsound(ba.getsound('error'))
                self.bear_coin_message = True
                GLOBAL['Coins Message'] = []
    except: pass

SpazBot.super_handlemessage = SpazBot.handlemessage
def bot_handlemessage(self, msg: Any):
    self.super_handlemessage(msg)
    if isinstance(msg, ba.DieMessage):
        if not self.die:
            self.die = True
            self.limit = 8400
            self.free_coins = random.randint(1,25)
            self.bear_coins = apg['Bear Coin']
            
            if not self.bear_coins >= (self.limit):
                self.bear_coins += self.free_coins
                GLOBAL['Coins Message'].append(self.free_coins)

                if self.bear_coins >= (self.limit):
                    self.bear_coins = self.limit
                    
                apg['Bear Coin'] = int(self.bear_coins)
                apg.apply_and_commit()
                
            else: GLOBAL['Coins Message'].append(self.free_coins)

def cls_pow_color():
    return [(1,0.1,0.1),(0.1,0.5,0.9),(0.1,0.9,0.9),
            (0.1,0.9,0.1),(0.1,1,0.5),(1,1,0.2),(2,0.5,0.5),(1,0,6)]

def random_color():
    a = random.random()*3
    b = random.random()*3
    c = random.random()*3
    return (a,b,c)

def powerup_dist():
    return (('triple_bombs', powerups['Triple']),
            ('ice_bombs', powerups['Ice Bombs']),
            ('punch', powerups['Punch']),
            ('impact_bombs', powerups['Impact Bombs']),
            ('land_mines', powerups['Mine Bombs']),
            ('sticky_bombs', powerups['Sticky Bombs']),
            ('shield', powerups['Shield']),
            ('health', powerups['Health']),
            ('curse', powerups['Curse']),
            ('speed',powerups['Speed']),
            ('health_damage', powerups['Healing Damage']),
            ('goodbye',powerups['Goodbye']),
            ('ice_man',powerups['Ice Man']),
            ('tank_shield',powerups['Tank Shield']),
            ('impairment_bombs',powerups['Impairment Bombs']),
            ('fire_bombs',powerups['Fire Bombs']),
            ('fly_bombs',powerups['Fly Bombs']))

def percentage_tank_shield():
    percentage = config['Tank Shield PTG']
    percentage_text = ('0.') + str(percentage)
    return float(percentage_text)
    
def percentage_health_damage():
    percentage = config['Healing Damage PTG']
    percentage_text = ('0.') + str(percentage)
    return float(percentage_text)

# === Modify class ===

class NewProfileBrowserWindow(browser.ProfileBrowserWindow):
    def __init__(self,
                 transition: str = 'in_right',
                 in_main_menu: bool = True,
                 selected_profile: str = None,
                 origin_widget: ba.Widget = None):
        super().__init__(transition,in_main_menu,selected_profile,origin_widget)
       
        self.session = ba.internal.get_foreground_host_session()
        uiscale = ba.app.ui.uiscale
        width = (100 if uiscale is
                 ba.UIScale.SMALL else -14)
        size = 50
        position = (width*1.65,300)
 
        if isinstance(self.session,MainMenuSession):
            self.button = ba.buttonwidget(parent=self._root_widget,
                          autoselect=True,position=position,
                          size=(size,size),button_type='square',
                          label='',on_activate_call=ba.Call(self.powerupmanager_window))
            
            size = size*0.60
            self.image = ba.imagewidget(parent=self._root_widget,
                          size=(size,size),draw_controller=self.button,
                          position=(position[0]+10.5,position[1]+17),
                          texture=ba.gettexture('powerupSpeed'))
    
            self.text = ba.textwidget(parent=self._root_widget,
                          position=(position[0]+25,position[1]+10),
                          size=(0, 0),scale=0.45,color=(0.7,0.9,0.7,1.0),
                          draw_controller=self.button,maxwidth=60,
                          text=(f"Ultimate Powerup {_sp_}Manager"),h_align='center',v_align='center')

    def powerupmanager_window(self):
        ba.containerwidget(edit=self._root_widget,transition='out_left')
        PowerupManagerWindow()

class NewPowerupBoxFactory(pupbox.PowerupBoxFactory):
    def __init__(self) -> None:
        super().__init__()
        self.tex_speed = ba.gettexture('powerupSpeed')
        self.tex_health_damage = ba.gettexture('heart')
        self.tex_goodbye = ba.gettexture('achievementOnslaught')
        self.tex_ice_man = ba.gettexture('ouyaUButton')
        self.tex_tank_shield = ba.gettexture('achievementSuperPunch')
        self.tex_impairment_bombs = ba.gettexture('levelIcon')
        self.tex_fire_bombs = ba.gettexture('ouyaOButton')
        self.tex_fly_bombs = ba.gettexture('star')
        
        self._powerupdist = []
        for powerup, freq in powerup_dist():
            for _i in range(int(freq)):
                self._powerupdist.append(powerup)

    def get_random_powerup_type(self,forcetype = None, excludetypes = None):
        
        try: self.mapa = ba.getactivity()._map.getname()
        except: self.mapa = None
      
        speed_banned_maps = ['Hockey Stadium','Lake Frigid','Happy Thoughts']
      
        if self.mapa in speed_banned_maps:
            powerup_disable = ['speed']
        else: powerup_disable = []
      
        if excludetypes is None:
            excludetypes = []
        if forcetype:
            ptype = forcetype
        else:
            if self._lastpoweruptype == 'curse':
                ptype = 'health'
            else:
                while True:
                    ptype = self._powerupdist[random.randint(
                        0,
                        len(self._powerupdist) - 1)]
                    if ptype not in excludetypes and ptype not in powerup_disable: break
        self._lastpoweruptype = ptype
        return ptype

def fire_effect(self):
    if self.node.exists():
        ba.emitfx(position=self.node.position,
        scale=3,count=50*2,spread=0.3,
        chunk_type='sweat')
    else: self.fire_effect_time = None

###########BOMBS
Bomb._pm_old_bomb = Bomb.__init__
def _bomb_init(self,
               position: Sequence[float] = (0.0, 1.0, 0.0),
               velocity: Sequence[float] = (0.0, 0.0, 0.0),
               bomb_type: str = 'normal',
               blast_radius: float = 2.0,
               bomb_scale: float = 1.0,
               source_player: ba.Player = None,
               owner: ba.Node = None):

    self.bm_type = bomb_type
    new_bomb_type = bomb_type
    bombs = ['ice_bubble','impairment','fire','fly']
    
    if bomb_type in bombs:
        new_bomb_type = 'ice'
                   
    self._pm_old_bomb(position,velocity,new_bomb_type,blast_radius,
                      bomb_scale,source_player,owner)
    
    tex = self.node.color_texture
    
    if self.bm_type == 'ice_bubble':
        self.bomb_type = self.bm_type
        self.node.model = None
        self.shield_ice = ba.newnode('shield',owner=self.node,
            attrs={'color': (0.5, 1.0, 7.0),'radius': 0.6})
        self.node.connectattr('position', self.shield_ice, 'position')
    elif self.bm_type == 'fire':
        self.bomb_type = self.bm_type
        self.node.model = None
        self.shield_fire = ba.newnode('shield',owner=self.node,
            attrs={'color': (6.5, 6.5, 2.0),'radius': 0.6})
        self.node.connectattr('position', self.shield_fire, 'position')
        self.fire_effect_time = ba.Timer(0.1,ba.Call(fire_effect,self),repeat=True)
    elif self.bm_type == 'impairment':
        self.bomb_type = self.bm_type
        tex = ba.gettexture('eggTex3')
    elif self.bm_type == 'fly':
        self.bomb_type = self.bm_type
        tex = ba.gettexture('eggTex1')

    self.node.color_texture = tex
    self.hit_subtype = self.bomb_type

    if self.bomb_type == 'ice_bubble':
        self.blast_radius *= 1.2
    elif self.bomb_type == 'fly':
        self.blast_radius *= 2.2

def bomb_handlemessage(self, msg: Any) -> Any:
    assert not self.expired

    if isinstance(msg, ba.DieMessage):
        if self.node:
            self.node.delete()

    elif isinstance(msg, bomb.ExplodeHitMessage):
        node = ba.getcollision().opposingnode
        assert self.node
        nodepos = self.node.position
        mag = 2000.0
        if self.blast_type in ('ice','ice_bubble'):
            mag *= 0.5
        elif self.blast_type == 'land_mine':
            mag *= 2.5
        elif self.blast_type == 'tnt':
            mag *= 2.0
        elif self.blast_type == 'fire':
            mag *= 0.6
        elif self.blast_type == 'fly':
            mag *= 5.5

        node.handlemessage(
            ba.HitMessage(pos=nodepos,
                          velocity=(0, 0, 0),
                          magnitude=mag,
                          hit_type=self.hit_type,
                          hit_subtype=self.hit_subtype,
                          radius=self.radius,
                          source_player=ba.existing(self._source_player)))
        if self.blast_type in ('ice','ice_bubble'):
            ba.playsound(bomb.BombFactory.get().freeze_sound,
                         10,
                         position=nodepos)
            node.handlemessage(ba.FreezeMessage())

    return None

def powerup_translated(self, type: str):
    powerups_names = {'triple_bombs': ba.Lstr(resource='helpWindow.'+'powerupBombNameText'),
                'ice_bombs': ba.Lstr(resource='helpWindow.'+'powerupIceBombsNameText'),
                'punch': ba.Lstr(resource='helpWindow.'+'powerupPunchNameText'),
                'impact_bombs': ba.Lstr(resource='helpWindow.'+'powerupImpactBombsNameText'),
                'land_mines': ba.Lstr(resource='helpWindow.'+'powerupLandMinesNameText'),
                'sticky_bombs': ba.Lstr(resource='helpWindow.'+'powerupStickyBombsNameText'),
                'shield': ba.Lstr(resource='helpWindow.'+'powerupShieldNameText'),
                'health': ba.Lstr(resource='helpWindow.'+'powerupHealthNameText'),
                'curse': ba.Lstr(resource='helpWindow.'+'powerupCurseNameText'),
                'speed': getlanguage('Speed'),
                'health_damage': getlanguage('Healing Damage'),
                'goodbye': getlanguage('Goodbye'),
                'ice_man': getlanguage('Ice Man'),
                'tank_shield': getlanguage('Tank Shield'),
                'impairment_bombs': getlanguage('Impairment Bombs'),
                'fire_bombs': getlanguage('Fire Bombs'),
                'fly_bombs': getlanguage('Fly Bombs')}
    self.texts['Name'].text = powerups_names[type]
                
###########POWERUP
pupbox.PowerupBox._old_pbx_ = pupbox.PowerupBox.__init__
def _pbx_(self, position: Sequence[float] = (0.0, 1.0, 0.0),
          poweruptype: str = 'triple_bombs',
          expire: bool = True):
    
    self.news: list = []
    for x,i in powerup_dist(): self.news.append(x)
    
    self.box: list = []
    self.texts = {}
    self.news = self.news[9:]
    self.box.append(poweruptype)
    self.npowerup = self.box[0]
    factory = NewPowerupBoxFactory.get()
    
    if self.npowerup in self.news: new_poweruptype = 'shield'
    else: new_poweruptype = poweruptype
    self._old_pbx_(position,new_poweruptype,expire)
    
    type = new_poweruptype
    tex = self.node.color_texture
    model = self.node.model
    
    if self.npowerup == 'speed':
        type = self.npowerup
        tex = factory.tex_speed
    elif self.npowerup == 'health_damage':
        type = self.npowerup
        tex = factory.tex_health_damage
    elif self.npowerup == 'goodbye':
        type = self.npowerup
        tex = factory.tex_goodbye
    elif self.npowerup == 'ice_man':
        type = self.npowerup
        tex = factory.tex_ice_man
    elif self.npowerup == 'tank_shield':
        type = self.npowerup
        tex = factory.tex_tank_shield
    elif self.npowerup == 'impairment_bombs':
        type = self.npowerup
        tex = factory.tex_impairment_bombs
    elif self.npowerup == 'fire_bombs':
        type = self.npowerup
        tex = factory.tex_fire_bombs
    elif self.npowerup == 'fly_bombs':
        type = self.npowerup
        tex = factory.tex_fly_bombs

    self.poweruptype = type
    self.node.model = model
    self.node.color_texture = tex
    n_scale = config['Powerup Scale']
    style = config['Powerup Style']

    curve = ba.animate(self.node, 'model_scale', {0: 0, 0.14: 1.6, 0.2: n_scale})
    ba.timer(0.2, curve.delete)
        
    def util_text(type: str, text: str, scale: float = 1, color: list = [1,1,1],
                  position: list = [0, 0.7, 0], colors_name: bool = False):
        m = ba.newnode('math',owner=self.node,attrs={'input1':
            (position[0], position[1], position[2]),'operation': 'add'})
        self.node.connectattr('position', m, 'input2')
        self.texts[type] = ba.newnode('text',owner=self.node,
                attrs={'text': str(text),
                      'in_world': True,
                      'scale': 0.02,
                      'shadow': 0.5,
                      'flatness': 1.0,
                      'color': (color[0],color[1],color[2]),
                      'h_align': 'center'}) 
        m.connectattr('output', self.texts[type], 'position')
        ba.animate(self.texts[type], 'scale', {0: 0.017,0.4: 0.017, 0.5: 0.01*scale})
    
        if colors_name:
            ba.animate_array(self.texts[type], 'color', 3,
                {0:(1,0,0),
                 0.2:(1,0.5,0),
                 0.4:(1,1,0),
                 0.6:(0,1,0),
                 0.8:(0,1,1),
                 1.0:(1,0,1),
                 1.2:(1,0,0)},True)
    
    def update_time(time):
        if self.texts['Time'].exists():
            self.texts['Time'].text = str(time)
        
    if config['Powerup Time']:
        interval = int(pupbox.DEFAULT_POWERUP_INTERVAL)
        time2 = (interval-1)
        time = 1
        
        util_text('Time', time2, scale=1.5,color=(2,2,2),
                  position=[0,0.9,0], colors_name=False)
        
        while(interval+3):
            ba.timer(time-1,ba.Call(update_time,f'{time2}s'))
    
            if time2 == 0:
                break
    
            time += 1
            time2 -= 1
    
    if config['Powerup With Shield']:
        scale = config['Powerup Scale']
        self.shield = ba.newnode('shield',owner=self.node,attrs={'color': (1,1,0),'radius': 1.3*scale})
        self.node.connectattr('position', self.shield, 'position')
        ba.animate_array(self.shield,'color',3,{0: (2,0,0), 0.5: (0,2,0), 1: (0,1,6), 1.5: (2,0,0)},True)
    
    if config['Powerup Name']:    
        util_text('Name',self.poweruptype,scale=1.2,
                  position=[0,0.4,0],colors_name=True)
        powerup_translated(self,self.poweruptype)
        
    if style == 'SY: BALL':
        self.node.model = ba.getmodel('frostyPelvis')
    elif style == 'SY: Impact':
        self.node.model = ba.getmodel('impactBomb')
    elif style == 'SY: Egg':
        self.node.model = ba.getmodel('egg')
        
###########SPAZ
def _speed_off_flash(self):
    if self.node:
        factory = NewPowerupBoxFactory.get()
        self.node.billboard_texture = factory.tex_speed
        self.node.billboard_opacity = 1.0
        self.node.billboard_cross_out = True
        
def _speed_wear_off(self):
    if self.node:
        self.node.hockey = False
        self.node.billboard_opacity = 0.0
        ba.playsound(ba.getsound('powerdown01'))
        
def _ice_man_off_flash(self):
    if self.node:
        factory = NewPowerupBoxFactory.get()
        self.node.billboard_texture = factory.tex_ice_man
        self.node.billboard_opacity = 1.0
        self.node.billboard_cross_out = True
        
def _ice_man_wear_off(self):
    if self.node:
        f = self.color[0]
        i = (0,1,4)
        
        bomb = self.bmb_color[0]        
        if bomb != 'ice_bubble': self.bomb_type = bomb
        else: self.bomb_type = 'normal'
        
        self.freeze_punch = False
        self.node.billboard_opacity = 0.0
        ba.animate_array(self.node,'color',3,{0: f, 0.3: i, 0.6: f})
        ba.playsound(ba.getsound('powerdown01'))
        
Spaz._pm2_spz_old = Spaz.__init__
def _init_spaz_(self,*args, **kwargs):
    self._pm2_spz_old(*args, **kwargs)
    self.edg_eff = False
    self.kill_eff = False
    self.freeze_punch = False
    self.die = False
    self.color: list = []
    self.color.append(self.node.color)
    
    self.tankshield = {"Tank": False,
                       "Reduction": False,
                       "Shield": None}

Spaz._super_on_punch_press = Spaz.on_punch_press
def spaz_on_punch_press(self) -> None:
    self._super_on_punch_press()

    if self.tankshield['Tank']:
        try:
            self.tankshield['Reduction'] = True
            
            shield = ba.newnode('shield',owner=self.node,
                attrs={'color': (4,1,4),'radius': 1.3})
            self.node.connectattr('position_center', shield, 'position')
            
            self.tankshield['Shield'] = shield
        except: pass

Spaz._super_on_punch_release = Spaz.on_punch_release
def spaz_on_punch_release(self) -> None:
    self._super_on_punch_release()
    try:
        self.tankshield['Shield'].delete()
        self.tankshield['Reduction'] = False
    except: pass

def new_get_bomb_type_tex(self) -> ba.Texture:
        factory = NewPowerupBoxFactory.get()
        if self.bomb_type == 'sticky':
            return factory.tex_sticky_bombs
        if self.bomb_type == 'ice':
            return factory.tex_ice_bombs
        if self.bomb_type == 'impact':
            return factory.tex_impact_bombs
        if self.bomb_type == 'impairment':
            return factory.tex_impairment_bombs
        if self.bomb_type == 'fire':
            return factory.tex_fire_bombs
        if self.bomb_type == 'fly':
            return factory.tex_fly_bombs
        return factory.tex_impact_bombs
        # raise ValueError('invalid bomb type')

def new_handlemessage(self, msg: Any) -> Any:
    assert not self.expired
    
    if isinstance(msg, ba.PickedUpMessage):
        if self.node:
            self.node.handlemessage('hurt_sound')
            self.node.handlemessage('picked_up')

        self._num_times_hit += 1

    elif isinstance(msg, ba.ShouldShatterMessage):
        ba.timer(0.001, ba.Call(self.shatter))

    elif isinstance(msg, ba.ImpactDamageMessage):
        ba.timer(0.001, ba.Call(self._hit_self, msg.intensity))

    elif isinstance(msg, ba.PowerupMessage):
        factory = NewPowerupBoxFactory.get()
        if self._dead or not self.node:
            return True
        if self.pick_up_powerup_callback is not None:
            self.pick_up_powerup_callback(self)
        if msg.poweruptype == 'triple_bombs':
            tex = PowerupBoxFactory.get().tex_bomb
            self._flash_billboard(tex)
            self.set_bomb_count(3)
            if self.powerups_expire:
                self.node.mini_billboard_1_texture = tex
                t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_1_start_time = t_ms
                self.node.mini_billboard_1_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._multi_bomb_wear_off_timer = (ba.Timer(
                    (POWERUP_WEAR_OFF_TIME - 2000),
                    ba.Call(self._multi_bomb_wear_off_flash),
                    timeformat=ba.TimeFormat.MILLISECONDS))
                self._multi_bomb_wear_off_timer = (ba.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    ba.Call(self._multi_bomb_wear_off),
                    timeformat=ba.TimeFormat.MILLISECONDS))
        elif msg.poweruptype == 'land_mines':
            self.set_land_mine_count(min(self.land_mine_count + 3, 3))
        elif msg.poweruptype == 'impact_bombs':
            self.bomb_type = 'impact'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
            if self.powerups_expire:
                self.node.mini_billboard_2_texture = tex
                t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (ba.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    ba.Call(self._bomb_wear_off_flash),
                    timeformat=ba.TimeFormat.MILLISECONDS))
                self._bomb_wear_off_timer = (ba.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    ba.Call(self._bomb_wear_off),
                    timeformat=ba.TimeFormat.MILLISECONDS))
        elif msg.poweruptype == 'sticky_bombs':
            self.bomb_type = 'sticky'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
            if self.powerups_expire:
                self.node.mini_billboard_2_texture = tex
                t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (ba.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    ba.Call(self._bomb_wear_off_flash),
                    timeformat=ba.TimeFormat.MILLISECONDS))
                self._bomb_wear_off_timer = (ba.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    ba.Call(self._bomb_wear_off),
                    timeformat=ba.TimeFormat.MILLISECONDS))
        elif msg.poweruptype == 'punch':
            self._has_boxing_gloves = True
            tex = PowerupBoxFactory.get().tex_punch
            self._flash_billboard(tex)
            self.equip_boxing_gloves()
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
            self.equip_shields(decay=factory.shield_decay_rate > 0)
        elif msg.poweruptype == 'curse':
            self.curse()
        elif msg.poweruptype == 'ice_bombs':
            self.bomb_type = 'ice'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
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
            if self.edg_eff:
                f = self.color[0]
                r = (2,0,0)
                g = (0,2,0)
                ba.animate_array(self.node,'color',3,{0: r, 0.6: g, 1.0: f})
                self.edg_eff = False
            if self._cursed:
                self._cursed = False
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

        elif msg.poweruptype == 'tank_shield':
            self.tankshield['Tank'] = True
            self.edg_eff = False
            tex = factory.tex_tank_shield
            self._flash_billboard(tex)

        elif msg.poweruptype == 'health_damage':
            tex = factory.tex_health_damage
            self.edg_eff = True
            f = self.color[0]
            i = (2,0.5,2)
            ba.animate_array(self.node,'color',3,{0: i, 0.5: i, 0.6: f})
            self._flash_billboard(tex)
            self.tankshield['Tank'] = False
            self.freeze_punch = False

        elif msg.poweruptype == 'goodbye':
            tex = factory.tex_goodbye
            self._flash_billboard(tex)
            self.kill_eff = True

        elif msg.poweruptype == 'fly_bombs':
            self.bomb_type = 'fly'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
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

        elif msg.poweruptype == 'fire_bombs':
            self.bomb_type = 'fire'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
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

        elif msg.poweruptype == 'impairment_bombs':
            self.bomb_type = 'impairment'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
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

        elif msg.poweruptype == 'ice_man':
            tex = factory.tex_ice_man
            self.bomb_type = 'ice_bubble'
            self.freeze_punch = True
            self.edg_eff = False
            self.node.color = (0,1,4)
            self._flash_billboard(tex)
            
            if self.powerups_expire:
                ice_man_time = 17000
                self.node.mini_billboard_2_texture = tex
                t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (t_ms + ice_man_time)
                
                self.ice_man_flash_timer = (ba.Timer(
                    ice_man_time - 2000,
                    ba.Call(_ice_man_off_flash,self),
                    timeformat=ba.TimeFormat.MILLISECONDS))
                    
                self.ice_man_timer = (ba.Timer(ice_man_time,
                    ba.Call(_ice_man_wear_off,self),
                    timeformat=ba.TimeFormat.MILLISECONDS))

        elif msg.poweruptype == 'speed':
            self.node.hockey = True
            tex = factory.tex_speed
            self._flash_billboard(tex)
            if self.powerups_expire:
                
                speed_time = 15000
                self.node.mini_billboard_2_texture = tex
                t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (t_ms + speed_time)
                
                self.speed_flash_timer = (ba.Timer(
                    speed_time - 2000,
                    ba.Call(_speed_off_flash,self),
                    timeformat=ba.TimeFormat.MILLISECONDS))
                    
                self.speed_timer = (ba.Timer(speed_time,
                    ba.Call(_speed_wear_off,self),
                    timeformat=ba.TimeFormat.MILLISECONDS))
        
        self.bmb_color: list = []    
        self.bmb_color.append(self.bomb_type)

        self.node.handlemessage('flash')
        if msg.sourcenode:
            msg.sourcenode.handlemessage(ba.PowerupAcceptMessage())
        return True

    elif isinstance(msg, ba.FreezeMessage):
        if not self.node:
            return None
        if self.node.invincible:
            ba.playsound(SpazFactory.get().block_sound,
                         1.0,
                         position=self.node.position)
            return None
        if self.shield:
            return None
        if not self.frozen:
            self.frozen = True
            self.node.frozen = True
            ba.timer(5.0, ba.Call(self.handlemessage,
                                      ba.ThawMessage()))
            if self.hitpoints <= 0:
                self.shatter()
        if self.freeze_punch:
            self.handlemessage(ba.ThawMessage())

    elif isinstance(msg, ba.ThawMessage):
        if self.frozen and not self.shattered and self.node:
            self.frozen = False
            self.node.frozen = False

    elif isinstance(msg, ba.HitMessage):
        if not self.node:
            return None
        if self.node.invincible:
            ba.playsound(SpazFactory.get().block_sound,
                         1.0,
                         position=self.node.position)
            return True

        local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
        assert isinstance(local_time, int)
        if (self._last_hit_time is None
                or local_time - self._last_hit_time > 1000):
            self._num_times_hit += 1
            self._last_hit_time = local_time

        mag = msg.magnitude * self.impact_scale
        velocity_mag = msg.velocity_magnitude * self.impact_scale       
        damage_scale = 0.22
        
        def fire_effect():
            if not self.shield:
                if self.node.exists():
                    ba.emitfx(position=self.node.position,
                    scale=3,count=50*2,spread=0.3,
                    chunk_type='sweat')
                    self.node.handlemessage('celebrate', 560)
                else: self._fire_time = None
            else: self._fire_time = None
        
        def fire(time, damage):
            if not self.shield and not self._dead:
                self.hitpoints -= damage
                ba.show_damage_count(f'-{damage}HP',
                    self.node.position, msg.force_direction)
                ba.playsound(ba.getsound('fuse01'))
            
            if duration != time:
                self._fire_time = ba.Timer(0.1,ba.Call(fire_effect),repeat=True)
            else: self._fire_time = None
            
            if self.hitpoints < 0:
                self.node.handlemessage(ba.DieMessage())
        
        if msg.hit_subtype == 'fly':
            damage_scale = 0.0
            
            if self.shield:
                self.shield_hitpoints -= 300
                
                if self.shield_hitpoints < 0:
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,1.0,position=self.node.position)
        elif msg.hit_subtype == 'fire':
            index = 1
            duration = 5
            damage = 103
            if not self.shield:
                for firex in range(duration):
                    ba.timer(index,ba.Call(fire,index,damage))
                    self._fire_time = ba.Timer(0.1,ba.Call(fire_effect),repeat=True)
                    index += 1
            else:
                self.shield_hitpoints -= 80
                if self.shield_hitpoints < 1:
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,1.0,position=self.node.position)
        elif msg.hit_subtype == 'impairment':
            damage_scale = 0
            
            if self.shield:
                self.shield.delete()
                self.shield = None
                ba.playsound(SpazFactory.get().shield_down_sound,1.0,position=self.node.position)
            else:
                hitpoints = int(self.hitpoints*0.80)
                self.hitpoints -= int(hitpoints)
                ba.show_damage_count((f'-{int(hitpoints/10)}%'),
                    self.node.position, msg.force_direction)
                
                if self.hitpoints < 0 or hitpoints < 95:
                    self.node.handlemessage(ba.DieMessage())

        if self.shield:
            if msg.flat_damage:
                damage = msg.flat_damage * self.impact_scale
            else:
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

            max_spillover = SpazFactory.get().max_shield_spillover_damage
            if self.shield_hitpoints <= 0:

                self.shield.delete()
                self.shield = None
                ba.playsound(SpazFactory.get().shield_down_sound,
                             1.0,
                             position=self.node.position)

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

            assert msg.force_direction is not None
            ba.emitfx(position=msg.pos,
                      velocity=(msg.force_direction[0] * 1.0,
                                msg.force_direction[1] * 1.0,
                                msg.force_direction[2] * 1.0),
                      count=min(30, 5 + int(damage * 0.005)),
                      scale=0.5,
                      spread=0.3,
                      chunk_type='spark')

            if self.shield_hitpoints <= -max_spillover:
                leftover_damage = -max_spillover - self.shield_hitpoints
                shield_leftover_ratio = leftover_damage / damage

                mag *= shield_leftover_ratio
                velocity_mag *= shield_leftover_ratio
            else:
                return True
        else:
            shield_leftover_ratio = 1.0

        if msg.flat_damage:
            damage = int(msg.flat_damage * self.impact_scale *
                         shield_leftover_ratio)
        else:
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                velocity_mag, msg.radius, 0, msg.force_direction[0],
                msg.force_direction[1], msg.force_direction[2])

            damage = int(damage_scale * self.node.damage)
            
        if self.tankshield['Reduction']:
            porcentaje = percentage_tank_shield()
            dism = int(damage*porcentaje)
            damage = int(damage-dism)
            
            ba.show_damage_count('-' + str(int(damage / 10)) + '%',
                msg.pos, msg.force_direction)

        self.node.handlemessage('hurt_sound')

        if self.edg_eff:
            porcentaje = percentage_health_damage()
            dmg_dism = int(damage*porcentaje)
            self.hitpoints += dmg_dism

            PopupText(text=f'+{int(dmg_dism/10)}%',scale=1.5,
                     position=self.node.position,color=(0,1,0)).autoretain()
            ba.animate_array(self.node,'color',3,{0: (0,1,0), 0.39: (0,2,0), 0.4: self.color[0]})
            ba.playsound(ba.getsound('healthPowerup'))

        if msg.hit_type == 'punch':
            self.on_punched(damage)

            try:
                if msg.get_source_player(ba.Player).actor.freeze_punch:
                    self.node.color = (0,1,4)
                    ba.playsound(ba.getsound('freeze'))
                    self.node.handlemessage(ba.FreezeMessage())
            except: pass

            if damage > 350:
                assert msg.force_direction is not None
                ba.show_damage_count('-' + str(int(damage / 10)) + '%',
                                     msg.pos, msg.force_direction)

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
            if msg.hit_type == 'impact' and damage > self.hitpoints:
                newdamage = max(damage - 200, self.hitpoints - 10)
                damage = newdamage
            self.node.handlemessage('flash')

            if damage > 0.0 and self.node.hold_node:
                self.node.hold_node = None
            self.hitpoints -= damage
            self.node.hurt = 1.0 - float(
                self.hitpoints) / self.hitpoints_max

            if self._cursed and damage > 0:
                ba.timer(
                    0.05,
                    ba.Call(self.curse_explode,
                                msg.get_source_player(ba.Player)))

            if self.frozen and (damage > 200 or self.hitpoints <= 0):
                self.shatter()
            elif self.hitpoints <= 0:
                self.node.handlemessage(
                    ba.DieMessage(how=ba.DeathType.IMPACT))

        if self.hitpoints <= 0:
            damage_avg = self.node.damage_smoothed * damage_scale
            if damage_avg > 1000:
                self.shatter()

    elif isinstance(msg, BombDiedMessage):
        self.bomb_count += 1

    elif isinstance(msg, ba.DieMessage):
        def drop_bomb():
            for xbomb in range(3):
                p = self.node.position
                pos = (p[0]+xbomb,p[1]+5,p[2]-xbomb)
                ball = bomb.Bomb(position=pos,bomb_type='impact').autoretain()
                ball.node.model_scale = 0.6
                ball.node.model = ba.getmodel('egg')
                ball.node.gravity_scale = 2

        if self.edg_eff:
            self.edg_eff = False

        wasdead = self._dead
        self._dead = True
        self.hitpoints = 0
        if msg.immediate:
            if self.node:
                self.node.delete()
        elif self.node:
            self.node.hurt = 1.0
            if self.play_big_death_sound and not wasdead:
                ba.playsound(SpazFactory.get().single_player_death_sound)
            self.node.dead = True
            ba.timer(2.0, self.node.delete)

            t = 0
            if self.kill_eff:
                for bombs in range(3):
                    ba.timer(t,ba.Call(drop_bomb))
                    t += 0.15
                self.kill_eff = False

    elif isinstance(msg, ba.OutOfBoundsMessage):
        self.handlemessage(ba.DieMessage(how=ba.DeathType.FALL))

    elif isinstance(msg, ba.StandMessage):
        self._last_stand_pos = (msg.position[0], msg.position[1],
                                msg.position[2])
        if self.node:
            self.node.handlemessage('stand', msg.position[0],
                                    msg.position[1], msg.position[2],
                                    msg.angle)

    elif isinstance(msg, CurseExplodeMessage):
        self.curse_explode()

    elif isinstance(msg, PunchHitMessage):
        if not self.node:
            return None
        node = ba.getcollision().opposingnode

        if node and (node not in self._punched_nodes):

            punch_momentum_angular = (self.node.punch_momentum_angular *
                                      self._punch_power_scale)
            punch_power = self.node.punch_power * self._punch_power_scale

            if node.getnodetype() != 'spaz':
                sounds = SpazFactory.get().impact_sounds_medium
                sound = sounds[random.randrange(len(sounds))]
                ba.playsound(sound, 1.0, position=self.node.position)

            ppos = self.node.punch_position
            punchdir = self.node.punch_velocity
            vel = self.node.punch_momentum_linear

            self._punched_nodes.add(node)
            node.handlemessage(
                ba.HitMessage(
                    pos=ppos,
                    velocity=vel,
                    magnitude=punch_power * punch_momentum_angular * 110.0,
                    velocity_magnitude=punch_power * 40,
                    radius=0,
                    srcnode=self.node,
                    source_player=self.source_player,
                    force_direction=punchdir,
                    hit_type='punch',
                    hit_subtype=('super_punch' if self._has_boxing_gloves
                                 else 'default')))

            mag = -400.0
            if self._hockey:
                mag *= 0.5
            if len(self._punched_nodes) == 1:
                self.node.handlemessage('kick_back', ppos[0], ppos[1],
                                        ppos[2], punchdir[0], punchdir[1],
                                        punchdir[2], mag)
    elif isinstance(msg, PickupMessage):
        if not self.node:
            return None

        try:
            collision = ba.getcollision()
            opposingnode = collision.opposingnode
            opposingbody = collision.opposingbody
        except ba.NotFoundError:
            return True

        try:
            if opposingnode.invincible:
                return True
        except Exception:
            pass

        if (opposingnode.getnodetype() == 'spaz'
                and not opposingnode.shattered and opposingbody == 4):
            opposingbody = 1

        held = self.node.hold_node
        if held and held.getnodetype() == 'flag':
            return True

        self.node.hold_body = opposingbody
        self.node.hold_node = opposingnode
    elif isinstance(msg, ba.CelebrateMessage):
        if self.node:
            self.node.handlemessage('celebrate', int(msg.duration * 1000))

    return None
        
class PowerupManagerWindow(PopupWindow):
    def __init__(self, transition= 'in_right'):
        columns = 2
        self._width = width = 800
        self._height = height = 500
        self._sub_height = 200
        self._scroll_width = self._width*0.90
        self._scroll_height = self._height - 180
        self._sub_width = self._scroll_width*0.95;
        self.tab_buttons: set = {}
        self.list_cls_power: list = []
        self.default_powerups = default_powerups()
        self.default_power_list = list(self.default_powerups)
        self.coins = apg['Bear Coin']
        self.popup_cls_power = None

        if not STORE['Buy Firebombs']:
            powerups['Fire Bombs'] = 0
            self.default_power_list.remove('Fire Bombs')

        self.charstr = [ba.charstr(ba.SpecialChar.LEFT_ARROW),
                        ba.charstr(ba.SpecialChar.RIGHT_ARROW),
                        ba.charstr(ba.SpecialChar.UP_ARROW),
                        ba.charstr(ba.SpecialChar.DOWN_ARROW)]

        self.tabdefs = {"Action 1": ['powerupIceBombs',(1,1,1)],
                        "Action 2": ['settingsIcon',(0,1,0)],
                        "Action 3": ['inventoryIcon',(1,1,1)],
                        "Action 4": ['storeIcon',(1,1,1)],
                        "Action 5": ['advancedIcon',(1,1,1)],
                        "About": ['heart',(1.5,0.3,0.3)]}
                        
        if (STORE['Buy Firebombs'] and
            STORE['Buy Option'] and
            STORE['Buy Percentage']):
            self.tabdefs = {"Action 1": ['powerupIceBombs',(1,1,1)],
                            "Action 2": ['settingsIcon',(0,1,0)],
                            "Action 3": ['inventoryIcon',(1,1,1)],
                            "About": ['heart',(1.5,0.3,0.3)]}
                        
        self.listdef = list(self.tabdefs)
        
        self.count = len(self.tabdefs)
                        
        self._current_tab = GLOBAL['Tab']

        app = ba.app.ui
        uiscale = app.uiscale

        self._root_widget = ba.containerwidget(size=(width+90,height+80),transition=transition,
                           scale=1.5 if uiscale is ba.UIScale.SMALL else 1.0,
                           stack_offset=(0,-30) if uiscale is ba.UIScale.SMALL else  (0,0))
        
        self._backButton = b = ba.buttonwidget(parent=self._root_widget,autoselect=True,
                       position=(60,self._height-15),size=(130,60),
                       scale=0.8,text_scale=1.2,label=ba.Lstr(resource='backText'),
                       button_type='back',on_activate_call=ba.Call(self._back))
        ba.buttonwidget(edit=self._backButton, button_type='backSmall',size=(60, 60),label=ba.charstr(ba.SpecialChar.BACK))
        ba.containerwidget(edit=self._root_widget,cancel_button=b)

        self.titletext = ba.textwidget(parent=self._root_widget,position=(0, height-15),size=(width,50),
                          h_align="center",color=ba.app.ui.title_color, v_align="center",maxwidth=width*1.3)
        
        index = 0
        for tab in range(self.count):
            for tab2 in range(columns):
                
                tag = self.listdef[index]
                
                position = (620+(tab2*120),self._height-50*2.5-(tab*120))
                
                if tag == 'About':
                    text = ba.Lstr(resource='gatherWindow.aboutText')
                elif tab == 'Action 4':
                    text = ba.Lstr(resource='storeText')
                else: text = getlanguage(tag)
                
                self.tab_buttons[tag] = ba.buttonwidget(parent=self._root_widget,autoselect=True,
                                        position=position,size=(110,110),
                                        scale=1,label='',enable_sound=False,
                                        button_type='square',on_activate_call=ba.Call(self._set_tab,tag,sound=True))
                                       
                self.text = ba.textwidget(parent=self._root_widget,
                            position=(position[0]+55,position[1]+30),
                            size=(0, 0),scale=1,color=ba.app.ui.title_color,
                            draw_controller=self.tab_buttons[tag],maxwidth=100,
                            text=text,h_align='center',v_align='center')
                                       
                self.image = ba.imagewidget(parent=self._root_widget,
                             size=(60,60),color=self.tabdefs[tag][1],
                             draw_controller=self.tab_buttons[tag],
                             position=(position[0]+25,position[1]+40),
                             texture=ba.gettexture(self.tabdefs[tag][0]))

                index += 1
        
                if self.count == index:
                    break
       
            if self.count == index:
                break
        
        self._scrollwidget = None
        self._tab_container = None
        self._set_tab(self._current_tab)

    def __del__(self):
        apg.apply_and_commit()

    def _set_tab(self, tab, sound: bool = False):
        self.sound = sound
        GLOBAL['Tab'] = tab
        apg.apply_and_commit()
        
        if self._tab_container is not None and self._tab_container.exists():
            self._tab_container.delete()

        if self.sound:
            ba.playsound(ba.getsound('click01'))

        if self._scrollwidget:
            self._scrollwidget.delete()

        self._scrollwidget = ba.scrollwidget(parent=self._root_widget,
            position=(self._width*0.08,51*1.8),size=(self._sub_width -140,self._scroll_height +60*1.2))

        if tab == 'Action 4':
            if self._scrollwidget:
                self._scrollwidget.delete()
            self._scrollwidget = ba.hscrollwidget(parent=self._root_widget,
                position=(self._width*0.08,51*1.8),size=(self._sub_width -140,self._scroll_height +60*1.2),
                capture_arrows=True,claims_left_right=True)
            ba.textwidget(edit=self.titletext,text=ba.Lstr(resource='storeText'))
        elif tab == 'About':
            ba.textwidget(edit=self.titletext,text=ba.Lstr(resource='gatherWindow.aboutText'))
        else: ba.textwidget(edit=self.titletext,text=getlanguage(tab))

        choices = ['Reset','Only Bombs','Only Items','New','Nothing']
        c_display = []
        
        for display in choices:
            choices_display = ba.Lstr(translate=("",getlanguage(display)))
            c_display.append(choices_display)
    
        if tab == 'Action 1':
            self.popup_cls_power = PopupMenu(
                  parent=self._root_widget,
                  position=(130,self._width*0.61),
                  button_size=(150,50),scale=2.5,
                  choices=choices,width=150,
                  choices_display=c_display,
                  current_choice=GLOBAL['Cls Powerup'],
                  on_value_change_call=self._set_concept)
            self.list_cls_power.append(self.popup_cls_power._button)
            
            self.button_cls_power = ba.buttonwidget(parent=self._root_widget,
                    position=(500,self._width*0.61),size=(50,50),autoselect=True,
                    scale=1,label=('%'),text_scale=1,button_type='square',
                    on_activate_call=self._percentage_window) 
            self.list_cls_power.append(self.button_cls_power)
            
            rewindow = [self.popup_cls_power._button,self.button_cls_power]
            
            for cls in self.list_cls_power: # this is very important so that pupups don't accumulate
                if cls not in rewindow:
                    cls.delete()
            
        elif tab == 'Action 4':
            self.button_coin = ba.buttonwidget(parent=self._root_widget,icon=ba.gettexture('coin'),
                    position=(550,self._width*0.614),size=(160,40),textcolor=(0,1,0),color=(0,1,6),
                    scale=1,label=str(apg['Bear Coin']),text_scale=1,autoselect=True,
                    on_activate_call=None) #self._percentage_window)
            self.list_cls_power.append(self.button_coin)
            
            try: rewindow.append(self.button_coin)
            except: rewindow = [self.button_coin]
            for cls in self.list_cls_power: # this is very important so that pupups don't accumulate
                if cls not in rewindow:
                    cls.delete()
            
        else:
            try:
                for cls in self.list_cls_power:
                    cls.delete()
            except: pass

        if tab == 'Action 1':
            sub_height = len(self.default_power_list) * 90
            v = sub_height - 55
            width = 300
            posi = 0
            id_power = list(self.default_powerups)
            new_powerups = id_power[9:]
            self.listpower = {}
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(self._sub_width,sub_height),
                background=False,selection_loops_to_parent=True)

            for power in self.default_power_list:
                if power == id_power[0]:
                    text = 'helpWindow.powerupShieldNameText'
                    tex = ba.gettexture('powerupShield')
                elif power == id_power[1]:
                    text = 'helpWindow.powerupPunchNameText'
                    tex = ba.gettexture('powerupPunch')
                elif power == id_power[2]:
                    text = 'helpWindow.powerupLandMinesNameText'
                    tex = ba.gettexture('powerupLandMines')
                elif power == id_power[3]:
                    text = 'helpWindow.powerupImpactBombsNameText'
                    tex = ba.gettexture('powerupImpactBombs')
                elif power == id_power[4]:
                    text = 'helpWindow.powerupIceBombsNameText'
                    tex = ba.gettexture('powerupIceBombs')
                elif power == id_power[5]:
                    text = 'helpWindow.powerupBombNameText'
                    tex = ba.gettexture('powerupBomb')
                elif power == id_power[6]:
                    text = 'helpWindow.powerupStickyBombsNameText'
                    tex = ba.gettexture('powerupStickyBombs')
                elif power == id_power[7]:
                    text = 'helpWindow.powerupCurseNameText'
                    tex = ba.gettexture('powerupCurse')
                elif power == id_power[8]:
                    text = 'helpWindow.powerupHealthNameText'
                    tex = ba.gettexture('powerupHealth')
                elif power == id_power[9]:
                    text = power
                    tex = ba.gettexture('powerupSpeed')
                elif power == id_power[10]:
                    text = power
                    tex = ba.gettexture('heart')
                elif power == id_power[11]:
                    text = "Goodbye!"
                    tex = ba.gettexture('achievementOnslaught')
                elif power == id_power[12]:
                    text = power
                    tex = ba.gettexture('ouyaUButton')
                elif power == id_power[13]:
                    text = power
                    tex = ba.gettexture('achievementSuperPunch')
                elif power == id_power[14]:
                    text = power
                    tex = ba.gettexture('levelIcon')
                elif power == id_power[15]:
                    text = power
                    tex = ba.gettexture('ouyaOButton')
                elif power == id_power[16]:
                    text = power
                    tex = ba.gettexture('star')
                    
                if power in new_powerups: label = getlanguage(power)
                else: label = ba.Lstr(resource=text)

                apperance = powerups[power]
                position = (90,v-posi)

                t = ba.textwidget(parent=c,position=(position[0]-30,position[1]-15),size=(width,50),
                          h_align="center",color=(ba.app.ui.title_color), text=label, v_align="center",maxwidth=width*1.3)
                        
                self.powprev = ba.imagewidget(parent=c,
                    position=(position[0]-70,position[1]-10),
                    size=(50,50),texture=tex)
                        
                dipos = 0
                for direc in ['-','+']:
                    ba.buttonwidget(parent=c,autoselect=True,
                                position=(position[0]+270+dipos,position[1]-10),size=(100,100),
                                scale=0.4,label=direc,button_type='square',text_scale=4,
                                on_activate_call=ba.Call(self.apperance_powerups,power,direc))
                    dipos += 100
                        
                textwidget = ba.textwidget(parent=c,position=(position[0]+190,position[1]-15),size=(width,50),
                          h_align="center",color=cls_pow_color()[apperance],text=str(apperance),
                          v_align="center",maxwidth=width*1.3)
                self.listpower[power] = textwidget
                        
                posi += 90
                        
        elif tab == 'Action 2':
            sub_height = 370 if not STORE['Buy Option'] else 450
            v = sub_height - 55
            width = 300
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(self._sub_width,sub_height),
                background=False,selection_loops_to_parent=True)
               
            position = (40,v-20)
               
            c_display = []
            choices = ['Auto','SY: BALL','SY: Impact','SY: Egg']
            for display in choices:
                choices_display = ba.Lstr(translate=("",getlanguage(display)))
                c_display.append(choices_display)
                
            popup = PopupMenu(parent=c,
                  position=(position[0]+300,position[1]),
                  button_size=(150,50),scale=2.5,
                  choices=choices,width=150,
                  choices_display=c_display,
                  current_choice=config['Powerup Style'],
                  on_value_change_call=ba.Call(self._all_popup,'Powerup Style'))
                  
            text = getlanguage('Powerup Style')
            wt = (len(text)*0.80)
            t = ba.textwidget(parent=c,position=(position[0]-60+wt,position[1]),size=(width,50),maxwidth=width*0.9,
                scale=1.1,h_align="center",color=ba.app.ui.title_color,text=getlanguage('Powerup Style'),v_align="center")
                
            dipos = 0
            for direc in ['-','+']:
                ba.buttonwidget(parent=c,autoselect=True,
                            position=(position[0]+310+dipos,position[1]-100),size=(100,100),
                            repeat=True,scale=0.4,label=direc,button_type='square',text_scale=4,
                            on_activate_call=ba.Call(self._powerups_scale,direc))
                dipos += 100

            txt_scale = config['Powerup Scale']
            self.txt_scale = ba.textwidget(parent=c,position=(position[0]+230,position[1]-105),size=(width,50),
                          scale=1.1,h_align="center",color=(0,1,0),text=str(txt_scale),v_align="center",maxwidth=width*1.3)
             
            text = getlanguage('Powerup Scale')
            wt = (len(text)*0.80)
            t = ba.textwidget(parent=c,position=(position[0]-60+wt,position[1]-100),size=(width,50),maxwidth=width*0.9,
                scale=1.1,h_align="center",color=ba.app.ui.title_color,text=text,v_align="center")
             
            position = (position[0]-20,position[1]+40)
                
            self.check = ba.checkboxwidget(parent=c,position=(position[0]+30,position[1]-230),value=config['Powerup Name'],
                             on_value_change_call=ba.Call(self._switches,'Powerup Name'),maxwidth=self._scroll_width*0.9,
                             text=getlanguage('Powerup Name'),autoselect=True)
                             
            self.check = ba.checkboxwidget(parent=c,position=(position[0]+30,position[1]-230*1.3),value=config['Powerup With Shield'],
                             on_value_change_call=ba.Call(self._switches,'Powerup With Shield'),maxwidth=self._scroll_width*0.9,
                             text=getlanguage('Powerup With Shield'),autoselect=True)
                             
            if STORE['Buy Option']:
                self.check = ba.checkboxwidget(parent=c,position=(position[0]+30,position[1]-230*1.6),value=config['Powerup Time'],
                                 on_value_change_call=ba.Call(self._switches,'Powerup Time'),maxwidth=self._scroll_width*0.9,
                                 text=getlanguage('Powerup Time'),autoselect=True)
                
        elif tab == 'Action 3':
            sub_height = 300
            v = sub_height - 55
            width = 300
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(self._sub_width,sub_height),
                background=False,selection_loops_to_parent=True)

            v -= 20
            position = (110,v-45*1.72)
            
            if not STORE['Buy Percentage']:
                t = ba.textwidget(parent=c,position=(90,v-100),size=(30+width,50),
                    h_align="center",text=getlanguage('Block Option Store'),
                    color=ba.app.ui.title_color,v_align="center",maxwidth=width*1.5,scale=1.5)
                    
                i = ba.imagewidget(parent=c,
                    position=(position[0]+100,position[1]-205),
                    size=(80,80),texture=ba.gettexture('lock'))
            else:
                t = ba.textwidget(parent=c,position=(position[0]-14,position[1]+70),size=(30+width,50),
                    h_align="center",text=f"{getlanguage('Tank Shield PTG')} ({getlanguage('Tank Shield')})",
                    color=ba.app.ui.title_color,v_align="center",maxwidth=width*1.5,scale=1.5)
                
                b = ba.buttonwidget(parent=c,autoselect=True,position=position,size=(100,100),repeat=True,
                                    scale=0.6,label=self.charstr[3],button_type='square',text_scale=2,
                                    on_activate_call=ba.Call(self.tank_shield_percentage,'Decrement'))
    
                b = ba.buttonwidget(parent=c,autoselect=True,repeat=True,text_scale=2,
                                    position=(position[0]*3.2,position[1]),size=(100,100),
                                    scale=0.6,label=self.charstr[2],button_type='square',
                                    on_activate_call=ba.Call(self.tank_shield_percentage,'Increment'))
    
                porcentaje = config['Tank Shield PTG']
                if porcentaje > 59: color = (0,1,0)
                elif porcentaje < 40: color = (1,1,0)
                else: color = (0,1,0.8)
                
                self.tank_text = ba.textwidget(parent=c,position=(position[0]-14,position[1]+5),
                    size=(30+width,50),h_align="center",
                    text=str(porcentaje)+'%',color=color,
                    v_align="center",maxwidth=width*1.3,scale=2)
    
                # ----->
    
                position = (110,v-160*1.6)         
                t = ba.textwidget(parent=c,position=(position[0]-14,position[1]+70),size=(30+width,50),
                    h_align="center",text=f"{getlanguage('Healing Damage PTG')}{_sp_}({getlanguage('Healing Damage')})",
                    color=ba.app.ui.title_color,v_align="center",maxwidth=width*1.3,scale=1.4)
                
                b = ba.buttonwidget(parent=c,autoselect=True,position=position,size=(100,100),repeat=True,
                                    scale=0.6,label=self.charstr[3],button_type='square',text_scale=2,
                                    on_activate_call=ba.Call(self.health_damage_percentage,'Decrement'))
    
                b = ba.buttonwidget(parent=c,autoselect=True,repeat=True,text_scale=2,
                                    position=(position[0]*3.2,position[1]),size=(100,100),
                                    scale=0.6,label=self.charstr[2],button_type='square',
                                    on_activate_call=ba.Call(self.health_damage_percentage,'Increment'))
    
                porcentaje = config['Healing Damage PTG']
                if porcentaje > 59: color = (0,1,0)
                elif porcentaje < 40: color = (1,1,0)
                else: color = (0,1,0.8)
                
                self.hlg_text = ba.textwidget(parent=c,position=(position[0]-14,position[1]+5),
                    size=(30+width,50),h_align="center",
                    text=str(porcentaje)+'%',color=color,
                    v_align="center",maxwidth=width*1.3,scale=2)

        elif tab == 'Percentage':
            sub_height = len(self.default_power_list) * 90
            v = sub_height - 55
            width = 300
            posi = 0
            id_power = list(self.default_powerups)
            new_powerups = id_power[9:]
            self.listpower = {}
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(self._sub_width,sub_height),
                background=False,selection_loops_to_parent=True)
 
            for power in self.default_power_list:
                if power == id_power[0]:
                    text = 'helpWindow.powerupShieldNameText'
                    tex = ba.gettexture('powerupShield')
                elif power == id_power[1]:
                    text = 'helpWindow.powerupPunchNameText'
                    tex = ba.gettexture('powerupPunch')
                elif power == id_power[2]:
                    text = 'helpWindow.powerupLandMinesNameText'
                    tex = ba.gettexture('powerupLandMines')
                elif power == id_power[3]:
                    text = 'helpWindow.powerupImpactBombsNameText'
                    tex = ba.gettexture('powerupImpactBombs')
                elif power == id_power[4]:
                    text = 'helpWindow.powerupIceBombsNameText'
                    tex = ba.gettexture('powerupIceBombs')
                elif power == id_power[5]:
                    text = 'helpWindow.powerupBombNameText'
                    tex = ba.gettexture('powerupBomb')
                elif power == id_power[6]:
                    text = 'helpWindow.powerupStickyBombsNameText'
                    tex = ba.gettexture('powerupStickyBombs')
                elif power == id_power[7]:
                    text = 'helpWindow.powerupCurseNameText'
                    tex = ba.gettexture('powerupCurse')
                elif power == id_power[8]:
                    text = 'helpWindow.powerupHealthNameText'
                    tex = ba.gettexture('powerupHealth')
                elif power == id_power[9]:
                    text = power
                    tex = ba.gettexture('powerupSpeed')
                elif power == id_power[10]:
                    text = power
                    tex = ba.gettexture('heart')
                elif power == id_power[11]:
                    text = "Goodbye!"
                    tex = ba.gettexture('achievementOnslaught')
                elif power == id_power[12]:
                    text = power
                    tex = ba.gettexture('ouyaUButton')
                elif power == id_power[13]:
                    text = power
                    tex = ba.gettexture('achievementSuperPunch')
                elif power == id_power[14]:
                    text = power
                    tex = ba.gettexture('levelIcon')
                elif power == id_power[15]:
                    text = power
                    tex = ba.gettexture('ouyaOButton')
                elif power == id_power[16]:
                    text = power
                    tex = ba.gettexture('star')
                    
                if power in new_powerups: label = getlanguage(power)
                else: label = ba.Lstr(resource=text)

                apperance = powerups[power]
                position = (90,v-posi)
                
                t = ba.textwidget(parent=c,position=(position[0]-30,position[1]-15),size=(width,50),
                          h_align="center",color=(ba.app.ui.title_color), text=label, v_align="center",maxwidth=width*1.3)
                        
                self.powprev = ba.imagewidget(parent=c,
                    position=(position[0]-70,position[1]-10),
                    size=(50,50),texture=tex)
                        
                ptg = str(self.total_percentage(power))
                t = ba.textwidget(parent=c,position=(position[0]+170,position[1]-10),size=(width,50),
                    h_align="center",color=(0,1,0),text=(f'{ptg}%'),v_align="center",maxwidth=width*1.3)
         
                posi += 90
                
        elif tab == 'Action 4':
            sub_height = 370
            width = 300
            v = sub_height - 55
            u = width - 60
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(width+500,sub_height),
                background=False,selection_loops_to_parent=True)
               
            position = (u+150,v-250)
            n_pos = 0
            prices = [7560, 5150, 3360]
            str_name = ["FireBombs Store","Timer Store","Percentages Store"]
            images = ["ouyaOButton","settingsIcon","inventoryIcon"]
            
            index = 0
            for store in store_items():
                p = prices[index]
                txt = str_name[index]
                label = getlanguage(txt)
                tx_pos = len(label)*1.8
                lb_scale = len(label)*0.20
                preview = images[index]
                
                if STORE[store]:
                    text = getlanguage('Bought')
                    icon = ba.gettexture('graphicsIcon')
                    color = (0.52,0.48,0.63)
                    txt_scale = 1.5
                else:
                    text = str(p)
                    icon = ba.gettexture('coin')
                    color = (0.5,0.4,0.93)
                    txt_scale = 2
                
                b = ba.buttonwidget(parent=c,autoselect=True,position=(position[0]+210-n_pos,position[1]),
                        size=(250,80),scale=0.7,label=text,text_scale=txt_scale,icon=icon,color=color,
                        iconscale=1.7,on_activate_call=ba.Call(self._buy_object,store,p))

                s = 180
                b = ba.buttonwidget(parent=c,autoselect=True,position=(position[0]+210-n_pos,position[1]+55),
                        size=(s,s+30),scale=1,label='',color=color,button_type='square',
                        on_activate_call=ba.Call(self._buy_object,store,p))
    
                s -= 80
                i = ba.imagewidget(parent=c,draw_controller=b,
                    position=(position[0]+250-n_pos,position[1]+140),
                    size=(s,s),texture=ba.gettexture(preview))
    
                t = ba.textwidget(parent=c,position=(position[0]+270-n_pos,position[1]+101),
                    h_align="center",color=(ba.app.ui.title_color),text=label,v_align="center",maxwidth=130)
    
                n_pos += 280
                index += 1
    
        elif tab == 'Action 5':
            sub_height = 370
            v = sub_height - 55
            width = 300
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(self._sub_width,sub_height),background=False,
                selection_loops_to_parent=True)
               
            position = (0,v-30)
    
            t = ba.textwidget(parent=c,position=(position[0]+80,position[1]-30),size=(width+60,50),scale=1,
                h_align="center",color=(ba.app.ui.title_color),text=ba.Lstr(
                resource='settingsWindowAdvanced.enterPromoCodeText'),v_align="center",maxwidth=width*1.3)
    
            self.promocode_text = ba.textwidget(parent=c,position=(position[0]+80,position[1]-100),size=(width+60,50),scale=1,
                editable=True,h_align="center",color=(ba.app.ui.title_color),text='', v_align="center",maxwidth=width*1.3,
                max_chars=30,description=ba.Lstr(resource='settingsWindowAdvanced.enterPromoCodeText'))
                
            self.promocode_button = ba.buttonwidget(
                parent=c,position=(position[0]+160,position[1]-170),
                size=(200, 60),scale=1.0,label=ba.Lstr(resource='submitText'),
                on_activate_call=self._promocode)
    
        else:
            sub_height = 0
            v = sub_height - 55
            width = 300
            
            self._tab_container = c = ba.containerwidget(parent=self._scrollwidget,
                size=(self._sub_width,sub_height),
                background=False,selection_loops_to_parent=True)

            t = ba.textwidget(parent=c,position=(110, v-20),size=(width,50),
                      scale=1.4,color=(0.2,1.2,0.2),h_align="center",v_align="center",
                      text=("Ultimate Powerup Manager v1.7"),maxwidth=width*30)

            t = ba.textwidget(parent=c,position=(110, v-90),size=(width,50),
                      scale=1,color=(1.3,0.5,1.0),h_align="center",v_align="center",
                      text=getlanguage('Creator'),maxwidth=width*30)

            t = ba.textwidget(parent=c,position=(110, v-220),size=(width,50),
                      scale=1,color=(1.0,1.2,0.3),h_align="center",v_align="center",
                      text=getlanguage('Mod Info'),maxwidth=width*30)
    
        for select_tab,button_tab in self.tab_buttons.items():
            if select_tab == tab:
                ba.buttonwidget(edit=button_tab,color=(0.5,0.4,1.5))
            else: ba.buttonwidget(edit=button_tab,color=(0.52,0.48,0.63))

    def _all_popup(self, tag: str, popup: str) -> None:
        config[tag] = popup
        apg.apply_and_commit()

    def _set_concept(self, concept: str) -> None:
        GLOBAL['Cls Powerup'] = concept

        if concept == 'Reset':
            for power, deflt in default_powerups().items():
                powerups[power] = deflt
        elif concept == 'Nothing':
            for power in default_powerups():
                powerups[power] = 0
        elif concept == 'Only Bombs':
            for power, deflt in default_powerups().items():
                if 'Bombs' not in power:
                    powerups[power] = 0
                else: powerups[power] = 3
        elif concept == 'Only Items':
            for power, deflt in default_powerups().items():
                if 'Bombs' in power:
                    powerups[power] = 0
                else: powerups[power] = deflt
        elif concept == 'New':
            default_power = default_powerups()
            new_powerups = list(default_power)[9:]
            for power, deflt in default_power.items():
                if power not in new_powerups:
                    powerups[power] = 0
                else: powerups[power] = deflt

        if not STORE['Buy Firebombs']:
            powerups['Fire Bombs'] = 0
            
        self._set_tab('Action 1')

    def tank_shield_percentage(self, tag):
        max = 96
        min = 40
        if tag == 'Increment':
            config['Tank Shield PTG'] += 1
            if config['Tank Shield PTG'] > max:
                config['Tank Shield PTG'] = min
        elif tag == 'Decrement':
            config['Tank Shield PTG'] -= 1
            if config['Tank Shield PTG'] < min:
                config['Tank Shield PTG'] = max
                
        porcentaje = config['Tank Shield PTG']
        if porcentaje > 59: color = (0,1,0)
        elif porcentaje < 40: color = (1,1,0)
        else: color = (0,1,0.8)
        ba.textwidget(edit=self.tank_text,
            text=str(porcentaje)+'%',color=color)

    def health_damage_percentage(self, tag):
        max = 80
        min = 35
        if tag == 'Increment':
            config['Healing Damage PTG'] += 1
            if config['Healing Damage PTG'] > max:
                config['Healing Damage PTG'] = min
        elif tag == 'Decrement':
            config['Healing Damage PTG'] -= 1
            if config['Healing Damage PTG'] < min:
                config['Healing Damage PTG'] = max
                
        porcentaje = config['Healing Damage PTG']
        if porcentaje > 59: color = (0,1,0)
        elif porcentaje < 40: color = (1,1,0)
        else: color = (0,1,0.8)
        ba.textwidget(edit=self.hlg_text,
            text=str(porcentaje)+'%',color=color)

    def apperance_powerups(self, powerup: str, ID: str):
        max = 7
        if ID == "-":
            if powerups[powerup] == 0:
                powerups[powerup] = max
            else: powerups[powerup] -= 1
        elif ID == "+":
            if powerups[powerup] == max:
                powerups[powerup] = 0
            else: powerups[powerup] += 1
        enum = powerups[powerup]
        ba.textwidget(edit=self.listpower[powerup],
                      text=str(powerups[powerup]),
                      color=cls_pow_color()[enum])
           
    def _powerups_scale(self, ID: str):
        max = 1.5
        min = 0.5
        sc = 0.1
        if ID == "-":
            if config['Powerup Scale'] < (min+0.1):
                config['Powerup Scale'] = max
            else: config['Powerup Scale'] -= sc
        elif ID == "+":
            if config['Powerup Scale'] > (max-0.1):
                config['Powerup Scale'] = min
            else: config['Powerup Scale'] += sc
        config['Powerup Scale'] = round(config['Powerup Scale'],1)
        ba.textwidget(edit=self.txt_scale,
                      text=str(config['Powerup Scale']))
           
    def total_percentage(self, power):
        total = 0
        pw = powerups[power]
        for i,i2 in powerups.items():
            total += i2
        if total == 0:
            return float(total)
        else:
            ptg = (100*pw/total)
            result = round(ptg,2)
            return result
           
    def store_refresh(self, tag: str):
        if tag == 'Buy Firebombs':
            powerups['Fire Bombs'] = 3
            self.default_power_list.append('Fire Bombs')
        self._set_tab('Action 4')
           
    def _buy_object(self, tag: str, price: int):
        store = BearStore(value=tag, price=price,
                callback=ba.Call(self.store_refresh,tag))
        store.buy()
           
    def _promocode(self):
        code = ba.textwidget(query=self.promocode_text)
        promo = PromoCode(code=code)
        promo.code_confirmation()
        ba.textwidget(edit=self.promocode_text,text="")
           
    def _switches(self,tag,m):
        config[tag] = False if m==0 else True
        apg.apply_and_commit()
           
    def _percentage_window(self):
        self._set_tab('Percentage')
           
    def _back(self):
        ba.containerwidget(edit=self._root_widget,transition='out_left')
        browser.ProfileBrowserWindow()


def enable():

    #browser.ProfileBrowserWindow = NewProfileBrowserWindow
    pupbox.PowerupBoxFactory = NewPowerupBoxFactory
    pupbox.PowerupBox.__init__ = _pbx_
    Bomb.__init__ = _bomb_init
    SpazBot.handlemessage = bot_handlemessage
    Blast.handlemessage = bomb_handlemessage
    Spaz.handlemessage = new_handlemessage
    Spaz.__init__ = _init_spaz_
    Spaz._get_bomb_type_tex = new_get_bomb_type_tex
    Spaz.on_punch_press = spaz_on_punch_press
    Spaz.on_punch_release = spaz_on_punch_release
    MainMenuActivity.on_transition_in = new_on_transition_in
