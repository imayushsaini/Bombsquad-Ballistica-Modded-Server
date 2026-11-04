# Released under the MIT License. See LICENSE for details.
"""Host DocUI interface and in-game menu integration for Customize Server / HUD."""

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

import private_hud

if TYPE_CHECKING:
    from typing import Awaitable

logger = logging.getLogger('ba.customize')


# -----------------------------------------------------------------------------
# DocUI Routes for Customize Server
# -----------------------------------------------------------------------------


class CustomizeServerRoute(DocUIRoute):
    """Family class for server customization / private HUD routes."""

    @override
    @classmethod
    def get_route_types(cls) -> tuple[type[DocUIRoute], ...]:
        return family_members(AnyCustomizeServerRoute)


@ioprepped
@dataclass
class CustomizeServerMainRoute(CustomizeServerRoute, path='/customize'):
    """Main route viewing customize server settings."""

    msg: Annotated[str | None, IOAttrs('m', store_default=False)] = None


@ioprepped
@dataclass
class CustomizeServerToggleRoute(
    CustomizeServerRoute, path='/customize/toggle', method=dui2.RequestMethod.POST
):
    """Toggle a specific HUD element checkbox."""

    item: Annotated[str, IOAttrs('i')]


@ioprepped
@dataclass
class CustomizeServerPresetRoute(
    CustomizeServerRoute, path='/customize/preset', method=dui2.RequestMethod.POST
):
    """Apply a preset mode (all, clean, leaderboard, next, notags, onlytags)."""

    preset: Annotated[str, IOAttrs('p')]


@ioprepped
@dataclass
class CustomizeServerDayNightRoute(
    CustomizeServerRoute,
    path='/customize/daynight',
    method=dui2.RequestMethod.POST,
):
    """Set Day or Night mode."""

    mode: Annotated[str, IOAttrs('m')]  # 'day' or 'night'


@ioprepped
@dataclass
class CustomizeServerZoomRoute(
    CustomizeServerRoute, path='/customize/zoom', method=dui2.RequestMethod.POST
):
    """Toggle personal camera zoom."""


AnyCustomizeServerRoute = (
    CustomizeServerMainRoute
    | CustomizeServerToggleRoute
    | CustomizeServerPresetRoute
    | CustomizeServerDayNightRoute
    | CustomizeServerZoomRoute
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
# Customize Server HostUI Handler
# -----------------------------------------------------------------------------


class CustomizeServerHostUIHandler(HostUIHandler):
    """Serves Customize Server DocUI pages to clients."""

    def __init__(self, prev_handler: HostUIHandler | None = None) -> None:
        super().__init__()
        self.prev_handler = prev_handler

    @override
    def fulfill_request(
        self, request: dui2.Request, client_id: int
    ) -> dui2.Response | Awaitable[dui2.Response]:
        try:
            route = CustomizeServerRoute.from_request(request)
        except DocUIRouteError:
            if self.prev_handler is not None:
                return self.prev_handler.fulfill_request(request, client_id)
            return super().fulfill_request(request, client_id)

        return self.handle_customize_route(route, client_id)

    def handle_customize_route(
        self, route: AnyCustomizeServerRoute, client_id: int
    ) -> dui2.Response:
        """Processes customize server routes and dispatches actions."""
        account_id = clientid_to_accountid(client_id)
        effective_acc = account_id or f'client_{client_id}'
        msg: str | None = None

        match route:
            case CustomizeServerMainRoute():
                msg = route.msg

            case CustomizeServerToggleRoute():
                item = route.item.strip().lower()
                current_list = list(private_hud.get_preference(effective_acc))
                if item in current_list:
                    current_list.remove(item)
                    action_str = 'disabled'
                else:
                    current_list.append(item)
                    action_str = 'enabled'

                private_hud.set_preference(effective_acc, current_list)
                private_hud.apply_preferences_for_client(client_id, effective_acc)
                msg = f"HUD element '{item}' {action_str}."

            case CustomizeServerPresetRoute():
                preset = route.preset.strip().lower()
                if preset in private_hud.MODES:
                    mode_categories = list(private_hud.MODES[preset])
                    private_hud.set_preference(effective_acc, mode_categories)
                    private_hud.apply_preferences_for_client(
                        client_id, effective_acc
                    )
                    msg = f"Applied HUD preset '{preset}'."

            case CustomizeServerDayNightRoute():
                mode = route.mode.strip().lower()
                private_hud.set_day_night_preference(
                    mode, effective_acc, client_id
                )
                private_hud.apply_day_night_for_client(client_id, effective_acc)
                msg = f'Lighting set to {mode.capitalize()} mode.'

            case CustomizeServerZoomRoute():
                is_zoomed = private_hud.is_zoom_enabled(client_id, effective_acc)
                new_zoom = not is_zoomed
                private_hud.set_zoom_enabled(client_id, new_zoom, effective_acc)
                private_hud.apply_zoom_for_client(client_id)
                msg = f"Personal camera zoom {'enabled' if new_zoom else 'disabled'}."

        return self.build_customize_page(client_id, effective_acc, msg=msg)

    def build_customize_page(
        self, client_id: int, effective_acc: str, msg: str | None = None
    ) -> dui2.Response:
        """Constructs the Customize Server DocUI page with checkboxes and controls."""
        current_prefs = private_hud.get_preference(effective_acc)
        current_day_night = (
            private_hud.get_day_night_preference(effective_acc, client_id)
            or 'day'
        )
        is_zoomed = private_hud.is_zoom_enabled(client_id, effective_acc)

        state_dict: dict[str, bool] = {
            'tag': 'tag' in current_prefs,
            'rank': 'rank' in current_prefs,
            'hptag': 'hptag' in current_prefs,
            'ping': 'ping' in current_prefs,
            'leaderboard': 'leaderboard' in current_prefs,
            'next_match': 'next_match' in current_prefs,
            'highlight': 'highlight' in current_prefs,
            'watermark': 'watermark' in current_prefs,
            'zoom': is_zoomed,
        }

        rows: list[dui2.Row] = []

        # 1. Header Info
        rows.append(
            dui2.ButtonRow(
                title=host_ui_text('Server & HUD Customization'),
                subtitle=host_ui_text(
                    'Customize HUD visibility, tags, lighting, and camera'
                ),
                buttons=[],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

        # 2. Notice Banner (if any action occurred)
        if msg:
            rows.append(
                dui2.ButtonRow(
                    title=host_ui_text(f'Notice: {msg}'),
                    title_color=(0.3, 0.9, 0.4, 1.0),
                    buttons=[],
                    layout=dui2.ButtonRowLayout.FIXED,
                )
            )

        # 3. Quick Presets Section
        rows.append(
            dui2.ButtonRow(
                title=host_ui_text('Quick Presets (/hud)'),
                subtitle=host_ui_text('Instant UI visibility configurations'),
                buttons=[],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

        preset_buttons_row1 = [
            dui2.Button(
                label=host_ui_text('Show All'),
                action=CustomizeServerPresetRoute(preset='all').replace(),
                color=(0.22, 0.45, 0.75, 1.0),
                size=(140.0, 36.0),
            ),
            dui2.Button(
                label=host_ui_text('Clean UI'),
                action=CustomizeServerPresetRoute(preset='clean').replace(),
                color=(0.22, 0.45, 0.75, 1.0),
                size=(140.0, 36.0),
            ),
            dui2.Button(
                label=host_ui_text('Leaderboard'),
                action=CustomizeServerPresetRoute(preset='leaderboard').replace(),
                color=(0.22, 0.45, 0.75, 1.0),
                size=(140.0, 36.0),
            ),
        ]
        rows.append(
            dui2.ButtonRow(
                buttons=preset_buttons_row1, layout=dui2.ButtonRowLayout.FIXED
            )
        )

        preset_buttons_row2 = [
            dui2.Button(
                label=host_ui_text('Next Match'),
                action=CustomizeServerPresetRoute(preset='next').replace(),
                color=(0.22, 0.45, 0.75, 1.0),
                size=(140.0, 36.0),
            ),
            dui2.Button(
                label=host_ui_text('No Head Tags'),
                action=CustomizeServerPresetRoute(preset='notags').replace(),
                color=(0.22, 0.45, 0.75, 1.0),
                size=(140.0, 36.0),
            ),
            dui2.Button(
                label=host_ui_text('Only Head Tags'),
                action=CustomizeServerPresetRoute(preset='onlytags').replace(),
                color=(0.22, 0.45, 0.75, 1.0),
                size=(140.0, 36.0),
            ),
        ]
        rows.append(
            dui2.ButtonRow(
                buttons=preset_buttons_row2, layout=dui2.ButtonRowLayout.FIXED
            )
        )

        # 4. Checkboxes: Player Head Tags
        rows.append(
            dui2.ButtonRow(
                title=host_ui_text('--- Player Head Tags ---'),
                buttons=[],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

        head_tags = [
            ('tag', 'Custom Player Tag', 'Custom text/role tags above players'),
            ('rank', 'Player Rank Tag', 'Display rank numbers (#1, #2, etc.)'),
            ('hptag', 'Player HP / Health Bar', 'Health text and damage meter'),
            ('ping', 'Network Ping Text', 'Latency in milliseconds (ms)'),
        ]
        for key, label, sub in head_tags:
            rows.append(
                dui2.CheckboxRow(
                    name=key,
                    label=host_ui_text(label),
                    subtitle=host_ui_text(sub),
                    on_change=CustomizeServerToggleRoute(item=key).replace(),
                )
            )

        # 5. Checkboxes: Map Overlays & Text
        rows.append(
            dui2.ButtonRow(
                title=host_ui_text('--- Map Overlays & Text ---'),
                buttons=[],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

        map_overlays = [
            (
                'leaderboard',
                'Live Match Leaderboard',
                'In-game scores and standings text on map',
            ),
            (
                'next_match',
                'Next Match Info',
                'Upcoming game name and playlist status',
            ),
            (
                'highlight',
                'Match Highlights',
                'Top player MVP spotlight notifications',
            ),
            (
                'watermark',
                'Server Watermark',
                'Server banner and branding text',
            ),
        ]
        for key, label, sub in map_overlays:
            rows.append(
                dui2.CheckboxRow(
                    name=key,
                    label=host_ui_text(label),
                    subtitle=host_ui_text(sub),
                    on_change=CustomizeServerToggleRoute(item=key).replace(),
                )
            )

        # 6. Environment & Camera Settings
        rows.append(
            dui2.ButtonRow(
                title=host_ui_text('--- Environment & Camera ---'),
                buttons=[],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

        is_day = current_day_night == 'day'
        lighting_buttons = [
            dui2.Button(
                label=host_ui_text('☀️ Day Mode' + (' (Active)' if is_day else '')),
                action=(
                    None
                    if is_day
                    else CustomizeServerDayNightRoute(mode='day').replace()
                ),
                color=(
                    (0.28, 0.55, 0.28, 1.0)
                    if is_day
                    else (0.22, 0.25, 0.28, 0.8)
                ),
                size=(180.0, 36.0),
            ),
            dui2.Button(
                label=host_ui_text(
                    '🌙 Night Mode' + (' (Active)' if not is_day else '')
                ),
                action=(
                    None
                    if not is_day
                    else CustomizeServerDayNightRoute(mode='night').replace()
                ),
                color=(
                    (0.25, 0.35, 0.7, 1.0)
                    if not is_day
                    else (0.22, 0.25, 0.28, 0.8)
                ),
                size=(180.0, 36.0),
            ),
        ]
        rows.append(
            dui2.ButtonRow(
                buttons=lighting_buttons, layout=dui2.ButtonRowLayout.FIXED
            )
        )

        rows.append(
            dui2.CheckboxRow(
                name='zoom',
                label=host_ui_text('Personal Camera Zoom (/zoom)'),
                subtitle=host_ui_text(
                    'Locks the camera view onto your character'
                ),
                on_change=CustomizeServerZoomRoute().replace(),
            )
        )

        return dui2.Response(
            page=dui2.Page(
                title=host_ui_text('Customize Server'),
                rows=rows,
                state=state_dict,
                center_vertically=False,
            )
        )


# -----------------------------------------------------------------------------
# Host UI Registration & Plugin
# -----------------------------------------------------------------------------


def setup_customize_server_host_ui() -> None:
    """Installs the Customize Server DocUI handler and in-game menu button."""
    try:
        classic = getattr(babase.app, 'classic', None)
        if classic is None or getattr(classic, 'host_ui', None) is None:
            return

        host_ui = classic.host_ui

        # 1. Chain handler if not already installed
        if not isinstance(host_ui.handler, CustomizeServerHostUIHandler):
            host_ui.handler = CustomizeServerHostUIHandler(host_ui.handler)

        # 2. Add 'Customize Server' button to in-game menu
        current_buttons = host_ui.get_buttons()
        has_btn = any(
            getattr(b, 'label', None) in ('Customize Server', '⚙️ Customize Server')
            or (
                getattr(getattr(b, 'browse', None), 'request', None) is not None
                and getattr(b.browse.request, 'path', '').startswith('/customize')
            )
            for b in current_buttons
        )

        if not has_btn:
            button = HostUIButton(
                label='Customize Server',
                browse=CustomizeServerMainRoute().browse(
                    layout=dui2.WindowLayout.WIDE_TALL,
                ),
                placement='in_game_menu',
            )
            current_buttons.append(button)
            host_ui.set_buttons(current_buttons)
            logger.info(
                'Registered Customize Server button on host_ui in-game menu.'
            )

    except Exception as exc:
        logger.exception('Failed to setup customize server host UI: %s', exc)


# ba_meta export babase.Plugin
class CustomizeServerPlugin(babase.Plugin):
    """Customize Server Plugin providing DocUI and in-game menu button."""

    def on_app_running(self) -> None:
        setup_customize_server_host_ui()
