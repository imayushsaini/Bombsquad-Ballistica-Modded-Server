# Released under the MIT License. See LICENSE for details.
"""Compact Server Host DocUI interface for client_id -1 (Server Host)."""

from __future__ import annotations

import time
import logging
from typing import TYPE_CHECKING

import bacommon.docui.v2 as dui2
from baclassic._hostuiparts import host_ui_text
import babase
import bascenev1 as bs

from customize_server_docui import CustomizeServerMainRoute

if TYPE_CHECKING:
    from bacommon.docui.routes import DocUIRoute

logger = logging.getLogger('ba.server_host_docui')


def get_settings() -> dict:
    """Load latest server settings."""
    try:
        from setting import get_settings_data
        return get_settings_data()
    except Exception as exc:
        logger.warning('Could not read settings: %s', exc)
        return {}


def get_server_info() -> dict[str, str]:
    """Retrieve owner details, admins, credits, custom text, and discord link."""
    settings = get_settings()
    s_info = settings.get('server_info')
    if not isinstance(s_info, dict):
        s_info = {}

    owner = s_info.get('owner') or settings.get('owner') or 'Owner'
    admins = s_info.get('admins') or settings.get('admins') or ''
    credits_text = s_info.get('credits') or settings.get('credits') or 'BCSv2'
    custom_text = (
        s_info.get('custom_text')
        or s_info.get('description')
        or settings.get('custom_text')
        or ''
    )
    discord = (
        s_info.get('discord_link')
        or settings.get('discord_link')
        or settings.get('ballistica_web', {}).get('discord_link')
        or 'https://discord.gg/ucyaesh'
    )
    return {
        'owner': str(owner),
        'admins': str(admins),
        'credits': str(credits_text),
        'custom_text': str(custom_text),
        'discord_link': str(discord),
    }


def get_server_title() -> str:
    """Return the display title for the host page."""
    settings = get_settings()
    return settings.get('HostName', 'Server Host')


def get_physics_info() -> str:
    """Determine whether server is using Legacy Physics or New Physics."""
    classic = getattr(babase.app, 'classic', None)
    is_legacy = bool(getattr(classic, 'legacy_spaz_physics', False))
    return 'Legacy (v1.4)' if is_legacy else 'New (v1.7+)'


def get_end_vote_status(viewer: int, viewer_acc: str | None) -> dict:
    """Query current end vote status from votingmachine."""
    try:
        from features import votingmachine
        vm = getattr(votingmachine, 'vote_machine', {}).get('end', {})
        voters = list(vm.get('voters', []))
        last_vote_start_time = vm.get('last_vote_start_time', 0.0)
        vote_duration = vm.get('vote_duration', 50.0)
        now = time.time()
        is_active = (now <= last_vote_start_time + vote_duration) and len(voters) > 0

        roster = bs.get_game_roster()
        roster_count = len(roster)
        needed = (
            votingmachine.max_votes_required(roster_count)
            if hasattr(votingmachine, 'max_votes_required')
            else 3
        )

        has_voted = (viewer_acc is not None and viewer_acc in voters) or (
            f'client_{viewer}' in voters
        )
        return {
            'is_active': is_active,
            'voters_count': len(voters),
            'needed': max(1, needed),
            'has_voted': has_voted,
        }
    except Exception as exc:
        logger.warning('Error getting end vote status: %s', exc)
        return {
            'is_active': False,
            'voters_count': 0,
            'needed': 3,
            'has_voted': False,
        }


def build_server_host_page(
    route: DocUIRoute, viewer: int, notice: str | None = None
) -> dui2.Response:
    """Build the compact Host DocUI page for client_id == -1."""
    from plugins.kickvote_manager import clientid_to_accountid, is_admin_viewer

    viewer_acc = clientid_to_accountid(viewer)
    info = get_server_info()
    physics_name = get_physics_info()
    vote_status = get_end_vote_status(viewer, viewer_acc)
    admin = is_admin_viewer(viewer)

    rows: list[dui2.Row] = []

    # 1. Notice Banner (if any action occurred)
    if notice:
        rows.append(
            dui2.ButtonRow(
                title=host_ui_text(notice),
                title_color=(0.3, 0.9, 0.4, 1.0),
                buttons=[],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

    # 2. Compact Info Row 1: Host Name, Owner, Admins, Physics
    admin_str = f" | Admins: {info['admins']}" if info['admins'] else ''
    info_sub1 = f"Owner: {info['owner']}{admin_str} | Physics: {physics_name}"
    rows.append(
        dui2.ButtonRow(
            title=host_ui_text(get_server_title()),
            subtitle=host_ui_text(info_sub1),
            buttons=[],
            layout=dui2.ButtonRowLayout.FIXED,
        )
    )

    # 3. Compact Info Row 2: Custom text / Credits & Discord
    desc = info['custom_text'] if info['custom_text'] else f"Credits: {info['credits']}"
    info_sub2 = f"{desc} | Discord: {info['discord_link']}"
    rows.append(
        dui2.ButtonRow(
            subtitle=host_ui_text(info_sub2),
            buttons=[],
            layout=dui2.ButtonRowLayout.FIXED,
        )
    )

    # 4. Action Buttons (Discord, Vote End, Customize)
    voters = vote_status['voters_count']
    needed = vote_status['needed']

    if vote_status['has_voted']:
        vote_label = f"Voted ({voters}/{needed})"
        vote_action: dui2.Action = dui2.PopupText(
            text=host_ui_text(
                f"You already voted!\n{voters}/{needed} votes cast to skip map."
            )
        )
        vote_color = (0.25, 0.45, 0.30, 0.8)
    elif vote_status['is_active']:
        vote_label = f"Vote End ({voters}/{needed})"
        vote_action = dui2.Replace(
            request=dui2.Request(
                path='/member/action',
                args={'c': -1, 'a': 'endvote'},
            )
        )
        vote_color = (0.20, 0.55, 0.40, 1.0)
    else:
        vote_label = "Vote End Map"
        vote_action = dui2.Replace(
            request=dui2.Request(
                path='/member/action',
                args={'c': -1, 'a': 'endvote'},
            )
        )
        vote_color = (0.20, 0.55, 0.40, 1.0)

    btn_row_1 = [
        dui2.Button(
            label=host_ui_text('Discord'),
            action=dui2.Replace(
                request=dui2.Request(
                    path='/member/action',
                    args={'c': -1, 'a': 'discord'},
                )
            ),
            color=(0.35, 0.40, 0.85, 1.0),
            size=(140.0, 36.0),
        ),
        dui2.Button(
            label=host_ui_text(vote_label),
            action=vote_action,
            color=vote_color,
            size=(140.0, 36.0),
        ),
        dui2.Button(
            label=host_ui_text('Customize'),
            action=CustomizeServerMainRoute().browse(
                layout=dui2.WindowLayout.WIDE_TALL,
            ),
            color=(0.22, 0.45, 0.75, 1.0),
            size=(140.0, 36.0),
        ),
    ]
    rows.append(
        dui2.ButtonRow(
            buttons=btn_row_1,
            layout=dui2.ButtonRowLayout.FIXED,
        )
    )

    # 5. Admin instant skip button (only visible to admins)
    if admin:
        rows.append(
            dui2.ButtonRow(
                buttons=[
                    dui2.Button(
                        label=host_ui_text('⚡ Skip Map (Admin)'),
                        action=dui2.Replace(
                            request=dui2.Request(
                                path='/member/action',
                                args={'c': -1, 'a': 'skip_map'},
                            )
                        ),
                        color=(0.75, 0.30, 0.20, 1.0),
                        size=(180.0, 34.0),
                    )
                ],
                layout=dui2.ButtonRowLayout.FIXED,
            )
        )

    return dui2.Response(
        page=dui2.Page(
            title=host_ui_text(get_server_title()),
            rows=rows,
            center_vertically=False,
        )
    )


def handle_server_action(
    action: str, viewer: int, viewer_acc: str | None, target_name: str
) -> dui2.Response:
    """Process actions targeted at the Server Host (client_id == -1)."""
    import bacommon.docui.routes.classichost as hroutes
    from plugins.kickvote_manager import is_admin_viewer

    notice: str | None = None

    if action == 'endvote':
        try:
            from features import votingmachine
            vote_acc = viewer_acc or f'client_{viewer}'
            votingmachine.vote(vote_acc, viewer, 'end')
            notice = "End vote recorded!"
        except Exception as exc:
            logger.exception('Error registering end vote: %s', exc)
            notice = f'Error starting end vote: {exc}'

    elif action == 'skip_map':
        if not is_admin_viewer(viewer):
            notice = 'Permission denied.'
        else:
            try:
                activity = bs.get_foreground_host_activity()
                if activity is not None:
                    with activity.context:
                        try:
                            activity.end_game()
                        except Exception:
                            results = bs.GameResults()
                            for team in activity.teams:
                                results.set_team_score(team, team.score)
                            activity.end(results=results)
                    notice = 'Map skipped by Admin.'
                    bs.broadcastmessage(
                        'Map skipped by Admin.',
                        color=(1.0, 0.8, 0.2),
                        transient=True,
                    )
                else:
                    notice = 'No active game activity.'
            except Exception as exc:
                logger.exception('Error skipping map: %s', exc)
                notice = f'Error: {exc}'

    elif action == 'discord':
        info = get_server_info()
        discord_url = info['discord_link']
        try:
            # If viewer is the local host, open URL in local browser directly
            if viewer == -1:
                try:
                    import _babase
                    _babase.open_url(discord_url)
                except Exception:
                    pass

            # Send chat message to player so they can tap/copy the link
            bs.chatmessage(
                f'Discord: {discord_url}',
                clients=[viewer] if viewer != -1 else None,
            )
            notice = 'Discord link sent to chat!'
        except Exception as exc:
            logger.warning('Error sending discord message: %s', exc)
            notice = f'Discord: {discord_url}'

    return build_server_host_page(
        hroutes.Client(client_id=-1), viewer, notice=notice
    )
