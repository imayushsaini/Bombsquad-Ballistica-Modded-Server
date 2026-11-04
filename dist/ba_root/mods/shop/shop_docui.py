# Released under the MIT License. See LICENSE for details.
"""Host DocUI interface and in-game menu integration for the Shop system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, override
import logging

from efro.dataclassio import ioprepped, IOAttrs
from bacommon.docui.routes import DocUIRoute, DocUIRouteError, family_members
import bacommon.docui.v2 as dui2
from baclassic._hostuihandler import HostUIHandler
from baclassic._hostuibutton import HostUIButton
from baclassic._hostuiparts import host_ui_text

import babase
import bascenev1 as bs

from shop import shop_system

if TYPE_CHECKING:
    from typing import Awaitable

logger = logging.getLogger('ba.shop')


# -----------------------------------------------------------------------------
# DocUI Routes for Shop
# -----------------------------------------------------------------------------


class ShopRoute(DocUIRoute):
    """Family class for server shop routes."""

    @override
    @classmethod
    def get_route_types(cls) -> tuple[type[DocUIRoute], ...]:
        return family_members(AnyShopRoute)


@ioprepped
@dataclass
class ShopMainRoute(ShopRoute, path='/shop'):
    """Main shop route for viewing a category."""

    category: Annotated[str, IOAttrs('c', store_default=False)] = 'effects'
    msg: Annotated[str | None, IOAttrs('m', store_default=False)] = None


@ioprepped
@dataclass
class ShopBuyRoute(ShopRoute, path='/shop/buy', method=dui2.RequestMethod.POST):
    """Route to purchase an item (effect or command)."""

    item_type: Annotated[str, IOAttrs('t')]
    item_id: Annotated[str, IOAttrs('id')]
    category: Annotated[str, IOAttrs('c', store_default=False)] = 'effects'


@ioprepped
@dataclass
class ShopEquipRoute(
    ShopRoute, path='/shop/equip', method=dui2.RequestMethod.POST
):
    """Route to equip a cosmetic effect."""

    effect_id: Annotated[str, IOAttrs('id')]
    category: Annotated[str, IOAttrs('c', store_default=False)] = 'effects'


@ioprepped
@dataclass
class ShopUnequipRoute(
    ShopRoute, path='/shop/unequip', method=dui2.RequestMethod.POST
):
    """Route to unequip an active effect."""

    effect_id: Annotated[str, IOAttrs('id')]
    category: Annotated[str, IOAttrs('c', store_default=False)] = 'effects'


@ioprepped
@dataclass
class ShopClaimRoute(
    ShopRoute, path='/shop/claim', method=dui2.RequestMethod.POST
):
    """Route to claim free daily tickets."""

    category: Annotated[str, IOAttrs('c', store_default=False)] = 'effects'


AnyShopRoute = (
    ShopMainRoute
    | ShopBuyRoute
    | ShopEquipRoute
    | ShopUnequipRoute
    | ShopClaimRoute
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def clientid_to_accountid(client_id: int) -> str | None:
    """Resolve a client id to a V2 account id."""
    if client_id == -1:
        plus = getattr(babase.app, 'plus', None)
        primary = (
            None
            if plus is None or plus.accounts is None
            else plus.accounts.primary
        )
        return None if primary is None else primary.accountid
    try:
        for entry in bs.get_game_roster():
            if entry.get('client_id') == client_id:
                return entry.get('account_id')
    except Exception:
        pass
    return None


# -----------------------------------------------------------------------------
# Shop HostUI Handler
# -----------------------------------------------------------------------------


class ShopHostUIHandler(HostUIHandler):
    """Serves the shop DocUI pages to clients."""

    def __init__(self, prev_handler: HostUIHandler | None = None) -> None:
        super().__init__()
        self.prev_handler = prev_handler

    @override
    def fulfill_request(
        self, request: dui2.Request, client_id: int
    ) -> dui2.Response | Awaitable[dui2.Response]:
        try:
            route = ShopRoute.from_request(request)
        except DocUIRouteError:
            if self.prev_handler is not None:
                return self.prev_handler.fulfill_request(request, client_id)
            return super().fulfill_request(request, client_id)

        return self.handle_shop_route(route, client_id)

    def handle_shop_route(
        self, route: AnyShopRoute, client_id: int
    ) -> dui2.Response:
        """Processes shop routes and dispatches actions."""
        account_id = clientid_to_accountid(client_id)
        category = 'effects'
        msg: str | None = None

        match route:
            case ShopMainRoute():
                category = route.category
                msg = route.msg
            case ShopBuyRoute():
                category = route.category
                if not account_id:
                    msg = 'Sign in with an account to make purchases.'
                else:
                    msg = shop_system.buy_item(account_id, route.item_id)
            case ShopEquipRoute():
                category = route.category
                if not account_id:
                    msg = 'Sign in with an account to equip effects.'
                else:
                    msg = shop_system.equip_effect(account_id, route.effect_id)
            case ShopUnequipRoute():
                category = route.category
                if not account_id:
                    msg = 'Sign in with an account to manage effects.'
                else:
                    try:
                        from spazmod.effects_inventory import unequip_effect

                        _ok, msg = unequip_effect(account_id, route.effect_id)
                    except Exception as exc:
                        msg = f'Error unequipping effect: {exc}'
            case ShopClaimRoute():
                category = route.category
                if not account_id:
                    msg = 'Sign in with an account to claim daily tickets.'
                else:
                    msg = shop_system.claim_daily_tickets(account_id)

        return self.build_shop_page(account_id, category=category, msg=msg)

    def build_shop_page(
        self,
        account_id: str | None,
        category: str = 'effects',
        msg: str | None = None,
    ) -> dui2.Response:
        """Constructs the Shop DocUI page."""
        tickets = shop_system.get_tickets(account_id) if account_id else 0
        rows: list[dui2.Row] = []

        # 1. Top Bar: Ticket Balance & Daily Claim
        balance_title = f'🎟️ Tickets: {tickets}'
        account_label = (
            f'Account: {account_id}'
            if account_id
            else 'Guest Account (Sign in to earn/buy)'
        )

        header_buttons = [
            dui2.Button(
                label=host_ui_text('🎁 Daily 100 🎟️'),
                action=ShopClaimRoute(category=category).replace(),
                color=(0.15, 0.55, 0.35, 1.0),
                size=(150.0, 38.0),
            )
        ]

        rows.append(
            dui2.ButtonRow(
                title=host_ui_text(balance_title),
                subtitle=host_ui_text(account_label),
                buttons=header_buttons,
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

        # 2. Feedback Message (e.g. after purchase, equip, or claim)
        if msg:
            is_good = any(
                k in msg.lower() for k in ('success', 'claimed', 'equipped')
            )
            color = (0.3, 0.9, 0.4, 1.0) if is_good else (1.0, 0.4, 0.4, 1.0)
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text(f'Notice: {msg}'),
                    title_color=color,
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )

        # 3. Navigation Tabs
        tabs = [
            ('effects', '✨ Effects'),
            ('commands', '⚡ Commands'),
            ('inventory', '🎒 My Items'),
            ('leaderboard', '🏆 Top Rich'),
        ]
        tab_buttons: list[dui2.Button] = []
        for cat_key, cat_name in tabs:
            is_active = category == cat_key
            tab_buttons.append(
                dui2.Button(
                    label=host_ui_text(cat_name),
                    action=(
                        None
                        if is_active
                        else ShopMainRoute(category=cat_key).replace()
                    ),
                    color=(
                        (0.28, 0.52, 0.88, 1.0)
                        if is_active
                        else (0.2, 0.22, 0.26, 0.75)
                    ),
                    size=(150.0, 38.0),
                )
            )
        rows.append(
            dui2.ButtonRow(
                buttons=tab_buttons, layout=dui2.ButtonRowLayout.FIXED
            )
        )

        # 4. Tab Content
        if category == 'effects':
            self._add_effects_rows(rows, account_id, tickets, category)
        elif category == 'commands':
            self._add_commands_rows(rows, account_id, tickets, category)
        elif category == 'inventory':
            self._add_inventory_rows(rows, account_id, category)
        elif category == 'leaderboard':
            self._add_leaderboard_rows(rows)

        return dui2.Response(
            page=dui2.Page(
                title=host_ui_text('Server Shop'),
                rows=rows,
                center_vertically=False,
            )
        )

    def _add_effects_rows(
        self,
        rows: list[dui2.Row],
        account_id: str | None,
        tickets: int,
        category: str,
    ) -> None:
        """Generates item rows for cosmetic effects."""
        purchases = (
            shop_system.get_player_purchases(account_id) if account_id else []
        )
        owned_effects = {
            p['item_id'] for p in purchases if p.get('item_type') == 'effect'
        }
        equipped_effect = (
            shop_system.get_equipped_effect(account_id) if account_id else None
        )

        for effect_id, info in shop_system.EFFECTS_SHOP.items():
            cost = info['cost']
            desc = info['description']
            display_title = f'{effect_id.capitalize()}  ({cost} 🎟️)'

            is_owned = effect_id in owned_effects
            is_equipped = effect_id == equipped_effect

            if is_equipped:
                btn = dui2.Button(
                    label=host_ui_text('Equipped (Unequip)'),
                    action=ShopUnequipRoute(
                        effect_id=effect_id, category=category
                    ).replace(),
                    color=(0.18, 0.65, 0.35, 1.0),
                    size=(160.0, 36.0),
                )
            elif is_owned:
                btn = dui2.Button(
                    label=host_ui_text('Equip'),
                    action=ShopEquipRoute(
                        effect_id=effect_id, category=category
                    ).replace(),
                    color=(0.22, 0.52, 0.82, 1.0),
                    size=(160.0, 36.0),
                )
            else:
                can_afford = tickets >= cost
                btn_color = (
                    (0.75, 0.45, 0.15, 1.0)
                    if can_afford
                    else (0.35, 0.35, 0.35, 0.6)
                )
                btn = dui2.Button(
                    label=host_ui_text(f'Buy ({cost} 🎟️)'),
                    action=ShopBuyRoute(
                        item_type='effect', item_id=effect_id, category=category
                    ).replace(),
                    color=btn_color,
                    size=(160.0, 36.0),
                )

            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text(display_title),
                    subtitle=host_ui_text(desc),
                    buttons=[btn],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )

    def _add_commands_rows(
        self,
        rows: list[dui2.Row],
        account_id: str | None,
        tickets: int,
        category: str,
    ) -> None:
        """Generates item rows for purchasable chat commands."""
        shop_cmds = shop_system.get_shop_commands()
        purchases = (
            shop_system.get_player_purchases(account_id) if account_id else []
        )
        owned_cmds = {
            p['item_id']: p.get('usages_left', 0)
            for p in purchases
            if p.get('item_type') == 'command'
        }

        if not shop_cmds:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text('No commands are currently in the shop.'),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )
            return

        for cmd_name, info in shop_cmds.items():
            cost = info['cost']
            desc = info['description']
            usages_left = owned_cmds.get(cmd_name)

            title_text = f'/{cmd_name}  ({cost} 🎟️)'
            subtitle_parts = [desc, '3 uses/buy']
            if usages_left is not None and usages_left > 0:
                subtitle_parts.append(f'Active uses: {usages_left}')
            subtitle_text = '  |  '.join(subtitle_parts)

            can_afford = tickets >= cost
            btn_color = (
                (0.75, 0.45, 0.15, 1.0)
                if can_afford
                else (0.35, 0.35, 0.35, 0.6)
            )
            btn = dui2.Button(
                label=host_ui_text(f'Buy ({cost} 🎟️)'),
                action=ShopBuyRoute(
                    item_type='command', item_id=cmd_name, category=category
                ).replace(),
                color=btn_color,
                size=(160.0, 36.0),
            )

            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text(title_text),
                    subtitle=host_ui_text(subtitle_text),
                    buttons=[btn],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )

    def _add_inventory_rows(
        self,
        rows: list[dui2.Row],
        account_id: str | None,
        category: str,
    ) -> None:
        """Generates rows showing player's current inventory & active effects."""
        if not account_id:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text(
                        'Sign in with an account to view your inventory.'
                    ),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )
            return

        purchases = shop_system.get_player_purchases(account_id)
        if not purchases:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text('Your inventory is empty.'),
                    subtitle=host_ui_text(
                        'Visit the Effects or Commands tab to purchase items!'
                    ),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )
            return

        equipped_effect = shop_system.get_equipped_effect(account_id)

        # List active effects
        effects = [p for p in purchases if p.get('item_type') == 'effect']
        if effects:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text('--- Owned Effects ---'),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )
            for eff in effects:
                eff_id = eff['item_id']
                duration = eff.get('duration_display', 'Permanent')
                is_equipped = (eff_id == equipped_effect) or eff.get(
                    'is_equipped', False
                )

                if is_equipped:
                    btn = dui2.Button(
                        label=host_ui_text('Equipped (Unequip)'),
                        action=ShopUnequipRoute(
                            effect_id=eff_id, category=category
                        ).replace(),
                        color=(0.18, 0.65, 0.35, 1.0),
                        size=(160.0, 36.0),
                    )
                else:
                    btn = dui2.Button(
                        label=host_ui_text('Equip'),
                        action=ShopEquipRoute(
                            effect_id=eff_id, category=category
                        ).replace(),
                        color=(0.22, 0.52, 0.82, 1.0),
                        size=(160.0, 36.0),
                    )

                rows.append(
                    dui2.ButtonRow(
                        title=host_ui_text(eff_id.capitalize()),
                        subtitle=host_ui_text(f'Duration: {duration}'),
                        buttons=[btn],
                        layout=dui2.ButtonRowLayout.FIXED,
                    )
                )

        # List active commands
        commands = [p for p in purchases if p.get('item_type') == 'command']
        if commands:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text('--- Purchased Commands ---'),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )
            for cmd in commands:
                cmd_id = cmd['item_id']
                usages = cmd.get('usages_left', 0)
                rows.append(
                    dui2.ButtonRow(
                        title=host_ui_text(f'/{cmd_id}'),
                        subtitle=host_ui_text(f'Remaining uses: {usages}'),
                        buttons=[],
                        layout=dui2.ButtonRowLayout.FIXED,
                    )
                )

    def _add_leaderboard_rows(self, rows: list[dui2.Row]) -> None:
        """Generates leaderboard rows for top ticket holders."""
        leaderboard = shop_system.get_economy_leaderboard(limit=10)
        if not leaderboard:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text('No leaderboard data available yet.'),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )
            return

        for index, entry in enumerate(leaderboard, start=1):
            name = entry.get('name') or 'Unknown'
            tickets = entry.get('tickets', 0)
            tag = entry.get('v2Tag')
            tag_str = f' [{tag}]' if tag else ''

            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text(f'#{index}  {name}{tag_str}'),
                    subtitle=host_ui_text(f'{tickets} 🎟️ Tickets'),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )


# -----------------------------------------------------------------------------
# Host UI Registration & Plugin
# -----------------------------------------------------------------------------


def setup_shop_host_ui() -> None:
    """Installs the Shop DocUI handler and in-game menu button."""
    try:
        classic = getattr(babase.app, 'classic', None)
        if classic is None or getattr(classic, 'host_ui', None) is None:
            return

        host_ui = classic.host_ui

        # 1. Chain handler if not already installed
        if not isinstance(host_ui.handler, ShopHostUIHandler):
            host_ui.handler = ShopHostUIHandler(host_ui.handler)

        # 2. Add 'Shop' button to in-game menu
        current_buttons = host_ui.get_buttons()
        has_shop = any(
            getattr(b, 'label', None) in ('Shop', '🛒 Shop')
            or (
                getattr(getattr(b, 'browse', None), 'request', None) is not None
                and getattr(b.browse.request, 'path', '').startswith('/shop')
            )
            for b in current_buttons
        )

        if not has_shop:
            shop_button = HostUIButton(
                label='Shop',
                browse=ShopMainRoute().browse(
                    layout=dui2.WindowLayout.WIDE_TALL,
                ),
                placement='in_game_menu',
            )
            current_buttons.append(shop_button)
            host_ui.set_buttons(current_buttons)
            logger.info('Registered Shop button on host_ui in-game menu.')

    except Exception as exc:
        logger.exception('Failed to setup shop host UI: %s', exc)


# ba_meta export babase.Plugin
class ShopPlugin(babase.Plugin):
    """Server Shop Plugin providing DocUI and in-game menu button."""

    def on_app_running(self) -> None:
        setup_shop_host_ui()
