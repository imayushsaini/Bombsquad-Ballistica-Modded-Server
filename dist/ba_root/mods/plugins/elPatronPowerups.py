# ba_meta require api 9
from __future__ import annotations
import setting
from bascenev1lib.actor.bomb import BombFactory
from bascenev1lib.actor.spaz import *
from bauiv1lib.confirm import ConfirmWindow
from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.mainmenu import (MainMenuActivity, MainMenuSession)
from bauiv1lib.popup import (PopupWindow, PopupMenu)
from bascenev1lib.actor.spazbot import SpazBot
from bascenev1lib.actor import powerupbox as pupbox
from bascenev1lib.actor import bomb
from bauiv1lib.profile import browser
import bauiv1 as bui
import babase

_sp_ = ('\n')


if TYPE_CHECKING:
    pass


# === Mod made by @Patron_Modz ===

def getlanguage(text, subs: str = None, almacen: list = []):
    if almacen == []:
        almacen = list(range(1000))
    lang = bui.app.lang.language
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
                     {"Spanish": "ConfiguraciÃƒÂ³n",
                      "English": "Settings",
                      "Portuguese": "DefiniÃƒÂ§ÃƒÂµes"},
                 "Action 3":
                     {"Spanish": "Extras",
                      "English": "Extras",
                      "Portuguese": "Extras"},
                 "Action 4":
                     {"Spanish": "Tienda",
                      "English": "Store",
                      "Portuguese": "Loja"},
                 "Action 5":
                     {"Spanish": "Canjear cÃƒÂ³digo",
                      "English": "Enter Code",
                      "Portuguese": "CÃƒÂ³digo promocional"},
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
                     {"Spanish": "Ã‚Â¡Hasta luego!",
                      "English": "Goodbye!",
                      "Portuguese": "Adeus!"},
                 "Healing Damage":
                     {"Spanish": "Auto-curaciÃƒÂ³n",
                      "English": "Healing Damage",
                      "Portuguese": "Auto-cura"},
                 "Tank Shield":
                     {"Spanish": "SÃƒÂºper blindaje",
                      "English": "Reinforced shield",
                      "Portuguese": "Escudo reforÃƒÂ§ado"},
                 "Tank Shield PTG":
                     {"Spanish": "Porcentaje de disminuciÃƒÂ³n",
                      "English": "Percentage decreased",
                      "Portuguese": "Percentual reduzido"},
                 "Healing Damage PTG":
                     {"Spanish": "Porcentaje de recuperaciÃƒÂ³n de salud",
                      "English": "Percentage of health recovered",
                      "Portuguese": "Porcentagem de recuperaÃƒÂ§ÃƒÂ£o de saÃƒÂºde"},
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
                     {"Spanish": "TamaÃƒÂ±o del potenciador",
                      "English": "Powerups size",
                      "Portuguese": "Tamanho de powerups"},
                 "Powerup With Shield":
                     {"Spanish": "Potenciadores con escudo",
                      "English": "Powerups with shield",
                      "Portuguese": "Powerups com escudo"},
                 "Powerup Time":
                     {"Spanish": "Mostrar Temporizador",
                      "English": "Show end time",
                      "Portuguese": "Mostrar cronÃƒÂ´metro"},
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
                     {"Spanish": "SÃƒÂ³lo Accesorios",
                      "English": "Only utensils",
                      "Portuguese": "Apenas utensilios"},
                 "New":
                     {"Spanish": "Nuevo",
                      "English": "New",
                      "Portuguese": "Novo"},
                 "Only Bombs":
                     {"Spanish": "SÃƒÂ³lo Bombas",
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
                     {"Spanish": "Ya has comprado este artÃƒÂ­culo",
                      "English": "You've already bought this",
                      "Portuguese": "Voce ja comprou isto"},
                 "Bought":
                     {"Spanish": "Comprado",
                      "English": "Bought",
                      "Portuguese": "Comprou"},
                 "Confirm Purchase":
                     {
                         "Spanish": f'Tienes {subs} monedas. {_sp_} Ã‚Â¿Deseas comprar esto?',
                         "English": f'You have {subs} coins. {_sp_} Do you want to buy this?',
                         "Portuguese": f'VocÃƒÂª tem {subs} moedas. {_sp_} Deseja comprar isto?'},
                 "FireBombs Store":
                     {"Spanish": 'Bombas de fuego',
                      "English": 'Fire bombs',
                      "Portuguese": 'Bombas de incÃƒÂªndio'},
                 "Timer Store":
                     {"Spanish": 'Temporizador',
                      "English": 'Timer',
                      "Portuguese": 'Timer'},
                 "Percentages Store":
                     {"Spanish": 'Extras',
                      "English": 'Extras',
                      "Portuguese": 'Extras'},
                 "Block Option Store":
                     {
                         "Spanish": f"Uuups..{_sp_}Esta opciÃƒÂ³n estÃƒÂ¡ bloqueada.{_sp_} Para acceder a ella puedes {_sp_} comprarla en la tienda.{_sp_} Gracias...",
                         "English": f"Oooops...{_sp_}This option is blocked. {_sp_} To access it you can buy {_sp_} it in the store.{_sp_} Thank you...",
                         "Portuguese": f"Ooops...{_sp_}Esta opÃƒÂ§ÃƒÂ£o estÃƒÂ¡ bloqueada. {_sp_} Para acessÃƒÂ¡-lo, vocÃƒÂª pode {_sp_} comprÃƒÂ¡-lo na loja.{_sp_} Obrigado..."},
                 "True Code":
                     {"Spanish": "Ã‚Â¡CÃƒÂ³digo canjeado!",
                      "English": "Successful code!",
                      "Portuguese": "Ã‚Â¡CÃƒÂ³digo vÃƒÂ¡lido!"},
                 "False Code":
                     {"Spanish": "CÃƒÂ³digo ya canjeado",
                      "English": "Expired code",
                      "Portuguese": "CÃƒÂ³digo expirado"},
                 "Invalid Code":
                     {"Spanish": "CÃƒÂ³digo invÃƒÂ¡lido",
                      "English": "Invalid code",
                      "Portuguese": "CÃƒÂ³digo invÃƒÂ¡lido"},
                 "Reward Code":
                     {"Spanish": f"Ã‚Â¡Felicitaciones! Ã‚Â¡Ganaste {subs} monedas!",
                      "English": f"Congratulations! You've {subs} coins",
                      "Portuguese": f"ParabÃƒÂ©ns! VocÃƒÂª tem {subs} moedas"},
                 "Creator":
                     {"Spanish": "Mod creado por @PatrÃƒÂ³nModz",
                      "English": "Mod created by @PatrÃƒÂ³nModz",
                      "Portuguese": "Mod creado by @PatrÃƒÂ³nModz"},
                 "Mod Info":
                     {
                         "Spanish": f"Un mod genial que te permite gestionar {_sp_} los potenciadores a tu antojo. {_sp_} tambiÃƒÂ©n incluye 8 potenciadores extra{_sp_} dejando 17 en total... Ã‚Â¡Guay!",
                         "English": f"A cool mod that allows you to manage {_sp_} powerups at your whims. {_sp_} also includes 8 extra powerups{_sp_} leaving 17 in total... Wow!",
                         "Portuguese": f"Um mod legal que permite que vocÃƒÂª gerencie os{_sp_} powerups de de acordo com seus caprichos. {_sp_} tambÃƒÂ©m inclui 8 powerups extras,{_sp_} deixando 17 no total... Uau!"},
                 "Coins Message":
                     {"Spanish": f"Recompensa: {subs} Monedas",
                      "English": f"Reward: {subs} Coins",
                      "Portuguese": f"Recompensa: {subs} Moedas"},
                 "Coins Limit Message":
                     {
                         "Spanish": f"Ganaste {almacen[0]} Monedas.{_sp_} Pero has superado el lÃƒÂ­mite de {almacen[1]}",
                         "English": f"You won {almacen[0]} Coins. {_sp_} But you have exceeded the limit of {almacen[1]}",
                         "Portuguese": f"VocÃƒÂª ganhou {almacen[0]} Moedas. {_sp_} Mas vocÃƒÂª excedeu o limite de {almacen[1]}"},
                 }
    languages = ['Spanish', 'Portuguese', 'English']
    if lang not in languages:
        lang = 'English'

    if text not in translate:
        return text

    return translate[text][lang]


settings = setting.get_settings_data()


def settings_distribution():
    return settings["elPatronPowerups"]["settings"]


apg = babase.app.config

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
    return {"G-Am54igO42Os": [True, 1100],
            "P-tRo8nM8dZ": [True, 2800],
            "Y-tU2B3S": [True, 500],
            "B-0mB3RYT2z": [True, 910],
            "B-Asd14mON9G0D": [True, 910],
            "D-rAcK0cJ23": [True, 910],
            "E-a27ZO6f3Y": [True, 600],
            "E-Am54igO42Os": [True, 600],
            "E-M4uN3K34XB": [True, 840],
            "PM-731ClcAF": [True, 50000]}


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

for i, j in store_items().items():
    store = apg['Bear Store']
    if i not in store:
        if store.get(i) is None:
            store[i] = j
    apg.apply_and_commit()

STORE = apg['Bear Store']

if STORE.get('Promo Code') is None:
    STORE['Promo Code'] = promo_codes()

for i, x in promo_codes().items():
    pmcode = STORE['Promo Code']
    if i not in pmcode:
        if pmcode.get(i) is None:
            pmcode[i] = x

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
            bs.broadcastmessage(
                babase.Lstr(resource='submittingPromoCodeText'), (0, 1, 0))
            bs.timer(2, babase.Call(self.validate_code))

    def validate_code(self):
        if self.code in self.codes_store:
            if self.promo_code_expire:
                bs.timer(1.5, babase.Call(self.successful_code))
                bs.broadcastmessage(getlanguage('True Code'), (0, 1, 0))
                bs.getsound('cheer').play()
                self.code_type[0] = False
            else:
                bs.broadcastmessage(getlanguage('False Code'), (1, 0, 0))
                bs.getsound('error').play()
        else:
            bs.broadcastmessage(getlanguage('Invalid Code'), (1, 0, 0))
            bs.getsound('error').play()

    def successful_code(self):
        apg['Bear Coin'] += self.promo_code_amount
        bs.broadcastmessage(getlanguage('Reward Code',
                                        subs=self.promo_code_amount), (0, 1, 0))
        bs.getsound('cashRegister2').play()


MainMenuActivity.super_transition_in = MainMenuActivity.on_transition_in


SpazBot.super_handlemessage = SpazBot.handlemessage


def bot_handlemessage(self, msg: Any):
    self.super_handlemessage(msg)
    if isinstance(msg, bs.DieMessage):
        if not self.die:
            self.die = True
            self.limit = 8400
            self.free_coins = random.randint(1, 25)
            self.bear_coins = apg['Bear Coin']

            if not self.bear_coins >= (self.limit):
                self.bear_coins += self.free_coins
                GLOBAL['Coins Message'].append(self.free_coins)

                if self.bear_coins >= (self.limit):
                    self.bear_coins = self.limit

                apg['Bear Coin'] = int(self.bear_coins)
                apg.apply_and_commit()

            else:
                GLOBAL['Coins Message'].append(self.free_coins)


def cls_pow_color():
    return [(1, 0.1, 0.1), (0.1, 0.5, 0.9), (0.1, 0.9, 0.9),
            (0.1, 0.9, 0.1), (0.1, 1, 0.5), (1, 1, 0.2), (2, 0.5, 0.5),
            (1, 0, 6)]


def random_color():
    a = random.random() * 3
    b = random.random() * 3
    c = random.random() * 3
    return (a, b, c)


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
            ('speed', powerups['Speed']),
            ('health_damage', powerups['Healing Damage']),
            ('goodbye', powerups['Goodbye']),
            ('ice_man', powerups['Ice Man']),
            ('tank_shield', powerups['Tank Shield']),
            ('impairment_bombs', powerups['Impairment Bombs']),
            ('fire_bombs', powerups['Fire Bombs']),
            ('fly_bombs', powerups['Fly Bombs']))


def percentage_tank_shield():
    percentage = config['Tank Shield PTG']
    percentage_text = ('0.') + str(percentage)
    return float(percentage_text)


def percentage_health_damage():
    percentage = config['Healing Damage PTG']
    percentage_text = ('0.') + str(percentage)
    return float(percentage_text)


class NewPowerupBoxFactory(pupbox.PowerupBoxFactory):
    def __init__(self) -> None:
        super().__init__()
        self.tex_speed = bs.gettexture('powerupSpeed')
        self.tex_health_damage = bs.gettexture('heart')
        self.tex_goodbye = bs.gettexture('achievementOnslaught')
        self.tex_ice_man = bs.gettexture('ouyaUButton')
        self.tex_tank_shield = bs.gettexture('achievementSuperPunch')
        self.tex_impairment_bombs = bs.gettexture('levelIcon')
        self.tex_fire_bombs = bs.gettexture('ouyaOButton')
        self.tex_fly_bombs = bs.gettexture('star')

        self._powerupdist = []
        for powerup, freq in powerup_dist():
            for _i in range(int(freq)):
                self._powerupdist.append(powerup)

    def get_random_powerup_type(self, forcetype=None, excludetypes=None):

        try:
            self.mapa = bs.getactivity()._map.getname()
        except:
            self.mapa = None

        speed_banned_maps = ['Hockey Stadium', 'Lake Frigid', 'Happy Thoughts']

        if self.mapa in speed_banned_maps:
            powerup_disable = ['speed']
        else:
            powerup_disable = []

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
                    if ptype not in excludetypes and ptype not in powerup_disable:
                        break
        self._lastpoweruptype = ptype
        return ptype


def fire_effect(self):
    if self.node.exists():
        bs.emitfx(position=self.node.position,
                  scale=3, count=50 * 2, spread=0.3,
                  chunk_type='sweat')
    else:
        self.fire_effect_time = None


# BOMBS
Bomb._pm_old_bomb = Bomb.__init__


def _bomb_init(self,
               position: Sequence[float] = (0.0, 1.0, 0.0),
               velocity: Sequence[float] = (0.0, 0.0, 0.0),
               bomb_type: str = 'normal',
               blast_radius: float = 2.0,
               bomb_scale: float = 1.0,
               source_player: bs.Player = None,
               owner: bs.Node = None):

    self.bm_type = bomb_type
    new_bomb_type = 'ice' if bomb_type in [
        'ice_bubble', 'impairment', 'fire', 'fly'] else bomb_type

    # Call original __init__
    self._pm_old_bomb(position=position,
                      velocity=velocity,
                      bomb_type=new_bomb_type,
                      blast_radius=blast_radius,
                      bomb_scale=bomb_scale,
                      source_player=source_player,
                      owner=owner)

    tex = self.node.color_texture

    if self.bm_type == 'ice_bubble':
        self.bomb_type = self.bm_type
        self.node.mesh = None
        self.shield_ice = bs.newnode('shield', owner=self.node,
                                     attrs={'color': (0.5, 1.0, 7.0), 'radius': 0.6})
        self.node.connectattr('position', self.shield_ice, 'position')

    elif self.bm_type == 'fire':
        self.bomb_type = self.bm_type
        self.node.mesh = None
        self.shield_fire = bs.newnode('shield', owner=self.node,
                                      attrs={'color': (6.5, 6.5, 2.0), 'radius': 0.6})
        self.node.connectattr('position', self.shield_fire, 'position')
        self.fire_effect_time = bs.Timer(
            0.1, babase.Call(fire_effect, self), repeat=True)

    elif self.bm_type == 'impairment':
        self.bomb_type = self.bm_type
        tex = bs.gettexture('eggTex3')

    elif self.bm_type == 'fly':
        self.bomb_type = self.bm_type
        tex = bs.gettexture('eggTex1')

    self.node.color_texture = tex
    self.hit_subtype = self.bomb_type

    if self.bomb_type == 'ice_bubble':
        self.blast_radius *= 1.2
    elif self.bomb_type == 'fly':
        self.blast_radius *= 2.2


def bomb_handlemessage(self, msg: Any) -> Any:
    assert not self.expired

    if isinstance(msg, bs.DieMessage):
        if self.node:
            self.node.delete()

    elif isinstance(msg, bomb.ExplodeHitMessage):
        node = bs.getcollision().opposingnode
        assert self.node
        nodepos = self.node.position
        mag = 2000.0
        if self.blast_type in ('ice', 'ice_bubble'):
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
            bs.HitMessage(pos=nodepos,
                          velocity=(0, 0, 0),
                          magnitude=mag,
                          hit_type=self.hit_type,
                          hit_subtype=self.hit_subtype,
                          radius=self.radius,
                          source_player=babase.existing(self._source_player)))
        if self.blast_type in ('ice', 'ice_bubble'):
            bomb.BombFactory.get().freeze_sound.play(10, position=nodepos)
            node.handlemessage(bs.FreezeMessage())

    return None


def powerup_translated(self, type: str):
    powerups_names = {'triple_bombs': babase.Lstr(
        resource='helpWindow.' + 'powerupBombNameText'),
        'ice_bombs': babase.Lstr(
        resource='helpWindow.' + 'powerupIceBombsNameText'),
        'punch': babase.Lstr(
        resource='helpWindow.' + 'powerupPunchNameText'),
        'impact_bombs': babase.Lstr(
        resource='helpWindow.' + 'powerupImpactBombsNameText'),
        'land_mines': babase.Lstr(
        resource='helpWindow.' + 'powerupLandMinesNameText'),
        'sticky_bombs': babase.Lstr(
        resource='helpWindow.' + 'powerupStickyBombsNameText'),
        'shield': babase.Lstr(
        resource='helpWindow.' + 'powerupShieldNameText'),
        'health': babase.Lstr(
        resource='helpWindow.' + 'powerupHealthNameText'),
        'curse': babase.Lstr(
        resource='helpWindow.' + 'powerupCurseNameText'),
        'speed': getlanguage('Speed'),
        'health_damage': getlanguage('Healing Damage'),
        'goodbye': getlanguage('Goodbye'),
        'ice_man': getlanguage('Ice Man'),
        'tank_shield': getlanguage('Tank Shield'),
        'impairment_bombs': getlanguage('Impairment Bombs'),
        'fire_bombs': getlanguage('Fire Bombs'),
        'fly_bombs': getlanguage('Fly Bombs')}
    self.texts['Name'].text = powerups_names[type]


# POWERUP
pupbox.PowerupBox._old_pbx_ = pupbox.PowerupBox.__init__


def _pbx_(self, position: Sequence[float] = (0.0, 1.0, 0.0),
          poweruptype: str = 'triple_bombs',
          expire: bool = True):
    self.news: list = []
    for x, i in powerup_dist():
        self.news.append(x)

    self.box: list = []
    self.texts = {}
    self.news = self.news[9:]
    self.box.append(poweruptype)
    self.npowerup = self.box[0]
    factory = NewPowerupBoxFactory.get()

    if self.npowerup in self.news:
        new_poweruptype = 'shield'
    else:
        new_poweruptype = poweruptype
    self._old_pbx_(position, new_poweruptype, expire)

    type = new_poweruptype
    tex = self.node.color_texture
    mesh = self.node.mesh

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
    self.node.mesh = mesh
    self.node.color_texture = tex
    n_scale = config['Powerup Scale']
    style = config['Powerup Style']

    curve = bs.animate(self.node, 'mesh_scale', {
                       0: 0, 0.14: 1.6, 0.2: n_scale})
    bs.timer(0.2, curve.delete)

    def util_text(type: str, text: str, scale: float = 1,
                  color: list = [1, 1, 1],
                  position: list = [0, 0.7, 0], colors_name: bool = False):
        m = bs.newnode('math', owner=self.node, attrs={'input1':
                                                       (position[0],
                                                        position[1],
                                                        position[2]),
                                                       'operation': 'add'})
        self.node.connectattr('position', m, 'input2')
        self.texts[type] = bs.newnode('text', owner=self.node,
                                      attrs={'text': str(text),
                                             'in_world': True,
                                             'scale': 0.02,
                                             'shadow': 0.5,
                                             'flatness': 1.0,
                                             'color': (
                                             color[0], color[1], color[2]),
                                             'h_align': 'center'})
        m.connectattr('output', self.texts[type], 'position')
        bs.animate(self.texts[type], 'scale',
                   {0: 0.017, 0.4: 0.017, 0.5: 0.01 * scale})

        if colors_name:
            bs.animate_array(self.texts[type], 'color', 3,
                             {0: (1, 0, 0),
                              0.2: (1, 0.5, 0),
                              0.4: (1, 1, 0),
                              0.6: (0, 1, 0),
                              0.8: (0, 1, 1),
                              1.0: (1, 0, 1),
                              1.2: (1, 0, 0)})

    def update_time(time):
        if self.texts['Time'].exists():
            self.texts['Time'].text = str(time)

    if config['Powerup Time']:
        interval = int(pupbox.DEFAULT_POWERUP_INTERVAL)
        time2 = (interval - 1)
        time = 1

        util_text('Time', time2, scale=1.5, color=(2, 2, 2),
                  position=[0, 0.9, 0], colors_name=False)

        while (interval + 3):
            bs.timer(time - 1, babase.Call(update_time, f'{time2}s'))

            if time2 == 0:
                break

            time += 1
            time2 -= 1

    if config['Powerup With Shield']:
        scale = config['Powerup Scale']
        self.shield = bs.newnode('shield', owner=self.node,
                                 attrs={'color': (1, 1, 0),
                                        'radius': 1.3 * scale})
        self.node.connectattr('position', self.shield, 'position')
        bs.animate_array(self.shield, 'color', 3,
                         {0: (2, 0, 0), 0.5: (0, 2, 0), 1: (0, 1, 6),
                          1.5: (2, 0, 0)}, True)

    if config['Powerup Name']:
        util_text('Name', self.poweruptype, scale=1.2,
                  position=[0, 0.4, 0], colors_name=True)
        powerup_translated(self, self.poweruptype)

    if style == 'SY: BALL':
        self.node.mesh = bs.getmesh('frostyPelvis')
    elif style == 'SY: Impact':
        self.node.mesh = bs.getmesh('impactBomb')
    elif style == 'SY: Egg':
        self.node.mesh = bs.getmesh('egg')


# SPAZ
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
        bs.getsound('powerdown01').play()


def _ice_man_off_flash(self):
    if self.node:
        factory = NewPowerupBoxFactory.get()
        self.node.billboard_texture = factory.tex_ice_man
        self.node.billboard_opacity = 1.0
        self.node.billboard_cross_out = True


def _ice_man_wear_off(self):
    if self.node:
        f = self.color[0]
        i = (0, 1, 4)

        bomb = self.bmb_color[0]
        if bomb != 'ice_bubble':
            self.bomb_type = bomb
        else:
            self.bomb_type = 'normal'

        self.freeze_punch = False
        self.node.billboard_opacity = 0.0
        bs.animate_array(self.node, 'color', 3, {0: f, 0.3: i, 0.6: f})
        bs.getsound('powerdown01').play()


Spaz._pm2_spz_old = Spaz.__init__


def _init_spaz_(self, *args, **kwargs):
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

            shield = bs.newnode('shield', owner=self.node,
                                attrs={'color': (4, 1, 4), 'radius': 1.3})
            self.node.connectattr('position_center', shield, 'position')

            self.tankshield['Shield'] = shield
        except:
            pass


Spaz._super_on_punch_release = Spaz.on_punch_release


def spaz_on_punch_release(self) -> None:
    self._super_on_punch_release()
    try:
        self.tankshield['Shield'].delete()
        self.tankshield['Reduction'] = False
    except:
        pass


def new_get_bomb_type_tex(self):
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

    if isinstance(msg, bs.PickedUpMessage):
        if self.node:
            self.node.handlemessage('hurt_sound')
            self.node.handlemessage('picked_up')

        self._num_times_hit += 1

    elif isinstance(msg, bs.ShouldShatterMessage):
        bs.timer(0.001, babase.Call(self.shatter))

    elif isinstance(msg, bs.ImpactDamageMessage):
        bs.timer(0.001, babase.Call(self._hit_self, msg.intensity))

    elif isinstance(msg, bs.PowerupMessage):
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
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_1_start_time = t_ms
                self.node.mini_billboard_1_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._multi_bomb_wear_off_timer = (bs.Timer(
                    (POWERUP_WEAR_OFF_TIME - 2000),
                    babase.Call(self._multi_bomb_wear_off_flash)))
                self._multi_bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    babase.Call(self._multi_bomb_wear_off)))
        elif msg.poweruptype == 'land_mines':
            self.set_land_mine_count(min(self.land_mine_count + 3, 3))
        elif msg.poweruptype == 'impact_bombs':
            self.bomb_type = 'impact'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
            if self.powerups_expire:
                self.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    babase.Call(self._bomb_wear_off_flash)))
                self._bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    babase.Call(self._bomb_wear_off)))
        elif msg.poweruptype == 'sticky_bombs':
            self.bomb_type = 'sticky'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
            if self.powerups_expire:
                self.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    babase.Call(self._bomb_wear_off_flash)))
                self._bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    babase.Call(self._bomb_wear_off)))
        elif msg.poweruptype == 'punch':
            self._has_boxing_gloves = True
            tex = PowerupBoxFactory.get().tex_punch
            self._flash_billboard(tex)
            self.equip_boxing_gloves()
            if self.powerups_expire:
                self.node.boxing_gloves_flashing = False
                self.node.mini_billboard_3_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_3_start_time = t_ms
                self.node.mini_billboard_3_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._boxing_gloves_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    bs.WeakCall(self._gloves_wear_off_flash)))
                self._boxing_gloves_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    bs.WeakCall(self._gloves_wear_off),))
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
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    bs.WeakCall(self._bomb_wear_off_flash)))
                self._bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    bs.WeakCall(self._bomb_wear_off)))
        elif msg.poweruptype == 'health':
            if self.edg_eff:
                f = self.color[0]
                r = (2, 0, 0)
                g = (0, 2, 0)
                bs.animate_array(self.node, 'color', 3, {0: r, 0.6: g, 1.0: f})
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
            i = (2, 0.5, 2)
            bs.animate_array(self.node, 'color', 3, {0: i, 0.5: i, 0.6: f})
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
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    bs.WeakCall(self._bomb_wear_off_flash)))
                self._bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    bs.WeakCall(self._bomb_wear_off)))

        elif msg.poweruptype == 'fire_bombs':
            self.bomb_type = 'fire'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
            if self.powerups_expire:
                self.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    bs.WeakCall(self._bomb_wear_off_flash)))
                self._bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    bs.WeakCall(self._bomb_wear_off)))

        elif msg.poweruptype == 'impairment_bombs':
            self.bomb_type = 'impairment'
            tex = self._get_bomb_type_tex()
            self._flash_billboard(tex)
            if self.powerups_expire:
                self.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (
                    t_ms + POWERUP_WEAR_OFF_TIME)
                self._bomb_wear_off_flash_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME - 2000,
                    bs.WeakCall(self._bomb_wear_off_flash)))
                self._bomb_wear_off_timer = (bs.Timer(
                    POWERUP_WEAR_OFF_TIME,
                    bs.WeakCall(self._bomb_wear_off)))

        elif msg.poweruptype == 'ice_man':
            tex = factory.tex_ice_man
            self.bomb_type = 'ice_bubble'
            self.freeze_punch = True
            self.edg_eff = False
            self.node.color = (0, 1, 4)
            self._flash_billboard(tex)

            if self.powerups_expire:
                ice_man_time = 17000
                self.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (t_ms + ice_man_time)

                self.ice_man_flash_timer = (bs.Timer(
                    ice_man_time - 2000,
                    babase.Call(_ice_man_off_flash, self)))

                self.ice_man_timer = (bs.Timer(ice_man_time,
                                               babase.Call(_ice_man_wear_off,
                                                           self)))

        elif msg.poweruptype == 'speed':
            self.node.hockey = True
            tex = factory.tex_speed
            self._flash_billboard(tex)
            if self.powerups_expire:
                speed_time = 15000
                self.node.mini_billboard_2_texture = tex
                t_ms = int(bs.time() * 1000)
                assert isinstance(t_ms, int)
                self.node.mini_billboard_2_start_time = t_ms
                self.node.mini_billboard_2_end_time = (t_ms + speed_time)

                self.speed_flash_timer = (bs.Timer(
                    speed_time - 2000,
                    babase.Call(_speed_off_flash, self)))

                self.speed_timer = (bs.apptimer(speed_time,
                                                babase.Call(_speed_wear_off,
                                                            self)))

        self.bmb_color: list = []
        self.bmb_color.append(self.bomb_type)

        self.node.handlemessage('flash')
        if msg.sourcenode:
            msg.sourcenode.handlemessage(bs.PowerupAcceptMessage())
        return True

    elif isinstance(msg, bs.FreezeMessage):
        if not self.node:
            return None
        if self.node.invincible:
            SpazFactory.get().block_sound.play(1.0, position=self.node.position)
            return None
        if self.shield:
            return None
        if not self.frozen:
            self.frozen = True
            self.node.frozen = True
            bs.timer(5.0, babase.Call(self.handlemessage,
                                      bs.ThawMessage()))
            if self.hitpoints <= 0:
                self.shatter()
        if self.freeze_punch:
            self.handlemessage(bs.ThawMessage())

    elif isinstance(msg, bs.ThawMessage):
        if self.frozen and not self.shattered and self.node:
            self.frozen = False
            self.node.frozen = False

    elif isinstance(msg, bs.HitMessage):
        if not self.node:
            return None
        if self.node.invincible:
            SpazFactory.get().block_sound.play(1.0, position=self.node.position)
            return True

        local_time = int(bs.time() * 1000)
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
                    bs.emitfx(position=self.node.position,
                              scale=3, count=50 * 2, spread=0.3,
                              chunk_type='sweat')
                    self.node.handlemessage('celebrate', 560)
                else:
                    self._fire_time = None
            else:
                self._fire_time = None

        def fire(time, damage):
            if not self.shield and not self._dead:
                self.hitpoints -= damage
                bs.show_damage_count(f'-{damage}HP',
                                     self.node.position,
                                     msg.force_direction)
                bs.getsound('fuse01').play()

            if duration != time:
                self._fire_time = bs.Timer(0.1, babase.Call(fire_effect),
                                           repeat=True)
            else:
                self._fire_time = None

            if self.hitpoints < 0:
                self.node.handlemessage(bs.DieMessage())

        if msg.hit_subtype == 'fly':
            damage_scale = 0.0

            if self.shield:
                self.shield_hitpoints -= 300

                if self.shield_hitpoints < 0:
                    self.shield.delete()
                    self.shield = None
                    SpazFactory.get().shield_down_sound.play(1.0,
                                                             position=self.node.position)
        elif msg.hit_subtype == 'fire':
            index = 1
            duration = 5
            damage = 103
            if not self.shield:
                for firex in range(duration):
                    bs.timer(index, babase.Call(fire, index, damage))
                    self._fire_time = bs.Timer(0.1, babase.Call(fire_effect),
                                               repeat=True)
                    index += 1
            else:
                self.shield_hitpoints -= 80
                if self.shield_hitpoints < 1:
                    self.shield.delete()
                    self.shield = None
                    SpazFactory.get().shield_down_sound.play(1.0,
                                                             position=self.node.position)
        elif msg.hit_subtype == 'impairment':
            damage_scale = 0

            if self.shield:
                self.shield.delete()
                self.shield = None
                SpazFactory.get().shield_down_sound.play(1.0,
                                                         position=self.node.position)
            else:
                hitpoints = int(self.hitpoints * 0.80)
                self.hitpoints -= int(hitpoints)
                bs.show_damage_count((f'-{int(hitpoints / 10)}%'),
                                     self.node.position,
                                     msg.force_direction)

                if self.hitpoints < 0 or hitpoints < 95:
                    self.node.handlemessage(bs.DieMessage())

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
                SpazFactory.get().shield_down_sound.play(1.0,
                                                         position=self.node.position)

                npos = self.node.position
                bs.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                          velocity=self.node.velocity,
                          count=random.randrange(20, 30),
                          scale=1.0,
                          spread=0.6,
                          chunk_type='spark')

            else:
                SpazFactory.get().shield_hit_sound.play(0.5,
                                                        position=self.node.position)

            assert msg.force_direction is not None
            bs.emitfx(position=msg.pos,
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
            dism = int(damage * porcentaje)
            damage = int(damage - dism)

            bs.show_damage_count('-' + str(int(damage / 10)) + '%',
                                 msg.pos, msg.force_direction)

        self.node.handlemessage('hurt_sound')

        if self.edg_eff:
            porcentaje = percentage_health_damage()
            dmg_dism = int(damage * porcentaje)
            self.hitpoints += dmg_dism

            PopupText(text=f'+{int(dmg_dism / 10)}%', scale=1.5,
                      position=self.node.position, color=(0, 1, 0)).autoretain()
            bs.animate_array(self.node, 'color', 3,
                             {0: (0, 1, 0), 0.39: (0, 2, 0),
                              0.4: self.color[0]})
            bs.getsound('healthPowerup').play()

        if msg.hit_type == 'punch':
            self.on_punched(damage)

            try:
                if msg.get_source_player(bs.Player).actor.freeze_punch:
                    self.node.color = (0, 1, 4)
                    bs.getsound('freeze').play()
                    self.node.handlemessage(bs.FreezeMessage())
            except:
                pass

            if damage > 350:
                assert msg.force_direction is not None
                bs.show_damage_count('-' + str(int(damage / 10)) + '%',
                                     msg.pos, msg.force_direction)

            if msg.hit_subtype == 'super_punch':
                SpazFactory.get().punch_sound_stronger.play(1.0,
                                                            position=self.node.position)
            if damage > 500:
                sounds = SpazFactory.get().punch_sound_strong
                sound = sounds[random.randrange(len(sounds))]
            else:
                sound = SpazFactory.get().punch_sound
            sound.play(1.0, position=self.node.position)

            assert msg.force_direction is not None
            bs.emitfx(position=msg.pos,
                      velocity=(msg.force_direction[0] * 0.5,
                                msg.force_direction[1] * 0.5,
                                msg.force_direction[2] * 0.5),
                      count=min(10, 1 + int(damage * 0.0025)),
                      scale=0.3,
                      spread=0.03)

            bs.emitfx(position=msg.pos,
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
            light = bs.newnode(
                'light',
                attrs={
                    'position': punchpos,
                    'radius': 0.12 + hurtiness * 0.12,
                    'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                    'height_attenuated': False,
                    'color': flash_color
                })
            bs.timer(0.06, light.delete)

            flash = bs.newnode('flash',
                               attrs={
                                   'position': punchpos,
                                   'size': 0.17 + 0.17 * hurtiness,
                                   'color': flash_color
                               })
            bs.timer(0.06, flash.delete)

        if msg.hit_type == 'impact':
            assert msg.force_direction is not None
            bs.emitfx(position=msg.pos,
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
                bs.timer(
                    0.05,
                    babase.Call(self.curse_explode,
                                msg.get_source_player(bs.Player)))

            if self.frozen and (damage > 200 or self.hitpoints <= 0):
                self.shatter()
            elif self.hitpoints <= 0:
                self.node.handlemessage(
                    bs.DieMessage(how=bs.DeathType.IMPACT))

        if self.hitpoints <= 0:
            damage_avg = self.node.damage_smoothed * damage_scale
            if damage_avg > 1000:
                self.shatter()

    elif isinstance(msg, BombDiedMessage):
        self.bomb_count += 1

    elif isinstance(msg, bs.DieMessage):
        def drop_bomb():
            for xbomb in range(3):
                p = self.node.position
                pos = (p[0] + xbomb, p[1] + 5, p[2] - xbomb)
                ball = bomb.Bomb(position=pos, bomb_type='impact').autoretain()
                ball.node.mesh_scale = 0.6
                ball.node.mesh = bs.getmesh('egg')
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
                SpazFactory.get().single_player_death_sound.play()
            self.node.dead = True
            bs.timer(2.0, self.node.delete)

            t = 0
            if self.kill_eff:
                for bombs in range(3):
                    bs.timer(t, babase.Call(drop_bomb))
                    t += 0.15
                self.kill_eff = False

    elif isinstance(msg, bs.OutOfBoundsMessage):
        self.handlemessage(bs.DieMessage(how=bs.DeathType.FALL))

    elif isinstance(msg, bs.StandMessage):
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
        node = bs.getcollision().opposingnode

        if node and (node not in self._punched_nodes):

            punch_momentum_angular = (self.node.punch_momentum_angular *
                                      self._punch_power_scale)
            punch_power = self.node.punch_power * self._punch_power_scale

            if node.getnodetype() != 'spaz':
                sounds = SpazFactory.get().impact_sounds_medium
                sound = sounds[random.randrange(len(sounds))]
                sound.play(1.0, position=self.node.position)

            ppos = self.node.punch_position
            punchdir = self.node.punch_velocity
            vel = self.node.punch_momentum_linear

            self._punched_nodes.add(node)
            node.handlemessage(
                bs.HitMessage(
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
            collision = bs.getcollision()
            opposingnode = collision.opposingnode
            opposingbody = collision.opposingbody
        except bs.NotFoundError:
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
    elif isinstance(msg, bs.CelebrateMessage):
        if self.node:
            self.node.handlemessage('celebrate', int(msg.duration * 1000))

    return None


def enable():
    # browser.ProfileBrowserWindow = NewProfileBrowserWindow
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
