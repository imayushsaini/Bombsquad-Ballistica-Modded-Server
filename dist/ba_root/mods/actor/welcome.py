
"""Welcome banner module visible only to joining client."""

# ba_meta require api 9

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import bascenev1 as bs
import _bascenev1
import babase
from bascenev1 import classicassets

if TYPE_CHECKING:
    from typing import Any

_bg_node: bs.Node | None = None
_text_node: bs.Node | None = None


def nodes_exist() -> bool:
    """Check if both background image and welcome text nodes currently exist."""
    global _bg_node, _text_node
    return (
        _bg_node is not None
        and _bg_node.exists()
        and _text_node is not None
        and _text_node.exists()
    )


def ensure_nodes() -> bool:
    """Ensure image and text nodes exist in session.context, recreating if dead."""
    global _bg_node, _text_node
    if nodes_exist():
        return True

    session = bs.getsession(doraise=False)
    if session is None:
        return False

    try:
        with session.context:
            if _bg_node is None or not _bg_node.exists():
                _bg_node = bs.newnode(
                    'image',
                    attrs={
                        'fill_screen': False,
                        'texture': classicassets.textures.bg.get(),
                        'tilt_translate': -0.3,
                        'has_alpha_channel': False,
                        'color': (1, 1, 1),
                    },
                )
                bs.welcome_bg_node = _bg_node

            if _text_node is None or not _text_node.exists():
                _text_node = bs.newnode(
                    'text',
                    attrs={
                        'text': '',
                        'big': True,
                        'scale': 1,
                        'position': (0, -1),
                        'h_align': 'center',
                        'v_align': 'center',
                        'h_attach': 'center',
                        'v_attach': 'center',
                        'flatness': 1.0,
                        'shadow': 0.5,
                        'color': (1.0, 1.0, 1.0),
                        'front': True,
                    },
                )
                bs.welcome_text_node = _text_node
        return True
    except Exception as e:
        logging.exception(
            f"Error creating welcome banner nodes in session.context: {e}")
        return False


def is_game_in_progress() -> bool:
    """Returns True if ongoing activity is a game (not join activity or score screen)."""
    activity = bs.get_foreground_host_activity()
    if activity is None or activity.has_ended():
        return False
    if isinstance(activity, bs.ScoreScreenActivity):
        return False
    if isinstance(activity, bs.JoinActivity) or getattr(activity, 'is_joining_activity', False):
        return False
    if not isinstance(activity, bs.GameActivity):
        return False
    return True


def show_welcome_banner(
    client_id: int,
    display_name: str = '',
    duration: float = 3.5,
) -> None:
    """Targeted display of welcome banner to client_id, then revert after duration."""
    if client_id is None or client_id < 0:
        return

    if not ensure_nodes():
        return

    clean_name = display_name.strip() if display_name else ""
    welcome_text = f"Welcome {clean_name}!" if clean_name else "Welcome!"

    try:
        if _bg_node and _bg_node.exists():
            _bascenev1.set_targeted_node_attr(
                _bg_node, 'fill_screen', True, clients=[client_id]
            )
        if _text_node and _text_node.exists():
            _bascenev1.set_targeted_node_attr(
                _text_node, 'text', welcome_text, clients=[client_id]
            )
    except Exception as e:
        logging.warning(
            f"Failed to set targeted welcome banner for client {client_id}: {e}"
        )
        return

    def _revert() -> None:
        try:
            if _bg_node and _bg_node.exists():
                _bascenev1.set_targeted_node_attr(
                    _bg_node, 'fill_screen', False, clients=[client_id]
                )
            if _text_node and _text_node.exists():
                _bascenev1.set_targeted_node_attr(
                    _text_node, 'text', '', clients=[client_id]
                )
        except Exception as e:
            logging.warning(
                f"Failed to revert welcome banner for client {client_id}: {e}"
            )

    babase.apptimer(duration, _revert)


def on_player_entered_server(
    client_id: int,
    display_name: str = '',
    delay: float = 1.0,
    duration: float = 3.5,
) -> None:
    """Hook called when a player enters the server.

    Shows welcome banner only to client_id if ongoing activity is a game.
    """
    if client_id is None or client_id < 0:
        return

    # Check if ongoing activity is game (not join activity or score screen activity)
    if not is_game_in_progress():
        return

    # Ensure nodes exist in session.context
    ensure_nodes()

    def _display() -> None:
        if not is_game_in_progress():
            return
        show_welcome_banner(client_id, display_name, duration=duration)

    if delay > 0:
        babase.apptimer(delay, _display)
    else:
        _display()


# Attempt initialization if session is already running
try:
    ensure_nodes()
except Exception:
    pass
