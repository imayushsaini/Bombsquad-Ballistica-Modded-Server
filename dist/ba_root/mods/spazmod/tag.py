# Released under the MIT License. See LICENSE for details.
"""Module to handle player overhead tags (custom tags, rank, hp, ping)."""

import setting
from playersdata import pdata
from stats import mystats

import babase
import bascenev1 as bs
import _bascenev1

sett = setting.get_settings_data()


def addtag(node, player):
    session_player = player.sessionplayer
    account_id = session_player.get_account_id()
    customtag_ = pdata.get_custom()
    customtag = customtag_['customtag']
    roles = pdata.get_roles()
    p_roles = pdata.get_player_roles(account_id)
    tag = None
    col = (0.5, 0.5, 1)  # default color for custom tags
    if account_id in customtag:
        tag = customtag[account_id]
    elif p_roles != []:
        for role in roles:
            if role in p_roles:
                tag = roles[role]['tag']
                col = (
                    0.7, 0.7, 0.7) if 'tagcolor' not in roles[role] else \
                    roles[role]['tagcolor']
                break
    if tag:
        Tag(node, tag, col)


def addrank(node, player):
    session_player = player.sessionplayer
    account_id = session_player.get_account_id()
    rank = mystats.getRank(account_id)

    if rank:
        Rank(node, rank)


def addhp(node, spaz):
    hp_tag = HitPoint(owner=node, position=(0, 1.75, 0), shad=1.4)

    def showHP():
        if not spaz.node.exists() or not node.exists():
            spaz.hptimer = None
            return
        hp_tag.update(spaz.hitpoints)

    showHP()
    spaz.hptimer = bs.Timer(1.5, babase.CallStrict(showHP), repeat=True)


def addping(node, player):
    session_player = player.sessionplayer
    client_id = getattr(session_player.inputdevice, 'client_id', -1)
    Ping(owner=node, client_id=client_id)


class Tag(object):
    def __init__(self, owner=None, tag="somthing", col=(1, 1, 1)):
        self.node = owner

        mnode = bs.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 1.5, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')
        if '\\' in tag:
            tag = tag.replace('\\d', ('\ue048'))
            tag = tag.replace('\\c', ('\ue043'))
            tag = tag.replace('\\h', ('\ue049'))
            tag = tag.replace('\\s', ('\ue046'))
            tag = tag.replace('\\n', ('\ue04b'))
            tag = tag.replace('\\f', ('\ue04f'))
            tag = tag.replace('\\g', ('\ue027'))
            tag = tag.replace('\\i', ('\ue03a'))
            tag = tag.replace('\\m', ('\ue04d'))
            tag = tag.replace('\\t', ('\ue01f'))
            tag = tag.replace('\\bs', ('\ue01e'))
            tag = tag.replace('\\j', ('\ue010'))
            tag = tag.replace('\\e', ('\ue045'))
            tag = tag.replace('\\l', ('\ue047'))
            tag = tag.replace('\\a', ('\ue020'))
            tag = tag.replace('\\b', ('\ue00c'))

        self.tag_text = bs.newnode('text',
                                   owner=self.node,
                                   attrs={
                                       'text': tag,
                                       'in_world': True,
                                       'shadow': 1.0,
                                       'flatness': 1.0,
                                       'color': tuple(col),
                                       'scale': 0.01,
                                       'h_align': 'center'
                                   })
        mnode.connectattr('output', self.tag_text, 'position')

        import private_hud
        private_hud.register_node(self.tag_text, 'tag', 'scale', 0.01)

        if sett.get("enableTagAnimation", False):
            bs.animate_array(node=self.tag_text, attr='color', size=3, keys={
                0.2: (2, 0, 2),
                0.4: (2, 2, 0),
                0.6: (0, 2, 2),
                0.8: (2, 0, 2),
                1.0: (1, 1, 0),
                1.2: (0, 1, 1),
                1.4: (1, 0, 1)
            }, loop=True)


class Rank(object):
    def __init__(self, owner=None, rank=99):
        self.node = owner
        mnode = bs.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 1.2, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')
        if (rank == 1):
            rank = '\ue01f' + "#" + str(rank) + '\ue01f'
        elif (rank == 2):
            rank = '\ue01f' + "#" + str(rank) + '\ue01f'
        elif (rank == 3):
            rank = '\ue01f' + "#" + str(rank) + '\ue01f'
        else:
            rank = "#" + str(rank)

        self.rank_text = bs.newnode('text',
                                    owner=self.node,
                                    attrs={
                                        'text': rank,
                                        'in_world': True,
                                        'shadow': 1.0,
                                        'flatness': 1.0,
                                        'color': (1, 1, 1),
                                        'scale': 0.01,
                                        'h_align': 'center'
                                    })
        mnode.connectattr('output', self.rank_text, 'position')

        import private_hud
        private_hud.register_node(self.rank_text, 'rank', 'scale', 0.01)


class HitPoint(object):
    def __init__(self, position=(0, 1.75, 0), owner=None, shad=1.4):
        self.position = position
        self.node = owner
        self.m = bs.newnode('math', owner=self.node, attrs={
            'input1': self.position, 'operation': 'add'})
        self.node.connectattr('torso_position', self.m, 'input2')
        self._Text = bs.newnode('text',
                                owner=self.node,
                                attrs={
                                    'text': '',
                                    'in_world': True,
                                    'shadow': shad,
                                    'flatness': 1.0,
                                    'color': (1, 1, 1),
                                    'scale': 0.01,
                                    'h_align': 'center'})
        self.m.connectattr('output', self._Text, 'position')

        import private_hud
        private_hud.register_node(self._Text, 'hptag', 'scale', 0.01)

    def update(self, hp):
        if not self._Text or not self._Text.exists():
            return
        prefix = int(hp) / 10
        preFix = u"\ue047" + str(prefix) + u"\ue047"
        self._Text.text = preFix
        self._Text.color = (1, 1, 1) if int(prefix) >= 20 else (1.0, 0.2, 0.2)


class Ping(object):
    def __init__(self, owner=None, client_id=-1):
        self.node = owner
        self.client_id = client_id
        self.m = bs.newnode('math',
                            owner=self.node,
                            attrs={
                                'input1': (0, 2.0, 0),
                                'operation': 'add'
                            })
        self.node.connectattr('torso_position', self.m, 'input2')

        self.ping_text = bs.newnode('text',
                                    owner=self.node,
                                    attrs={
                                        'text': '',
                                        'in_world': True,
                                        'shadow': 1.0,
                                        'flatness': 1.0,
                                        'color': (0.2, 1.0, 0.2),
                                        'scale': 0.01,
                                        'h_align': 'center'
                                    })
        self.m.connectattr('output', self.ping_text, 'position')

        import private_hud
        private_hud.register_node(self.ping_text, 'ping', 'scale', 0.01)

        self.update()
        self.timer = bs.Timer(1.5, babase.CallStrict(self.update), repeat=True)

    def update(self):
        if not self.node or not self.node.exists() or not self.ping_text or not self.ping_text.exists():
            self.timer = None
            return

        try:
            if self.client_id == -1:
                ping = 0
            else:
                ping = _bascenev1.get_client_ping(int(self.client_id))
        except Exception:
            ping = None

        if ping is None or ping < 0:
            ping_val = 0
            ping_str = "0ms"
        else:
            ping_val = int(ping)
            ping_str = f"{ping_val}ms"

        # Colors based on ping value: Green (<80ms), Yellow (80-160ms), Red (>=160ms)
        if ping_val < 80:
            col = (0.2, 1.0, 0.2)
        elif ping_val < 160:
            col = (1.0, 1.0, 0.2)
        else:
            col = (1.0, 0.2, 0.2)

        self.ping_text.text = ping_str
        self.ping_text.color = col
