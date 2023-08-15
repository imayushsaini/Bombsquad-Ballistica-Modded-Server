# Released under the MIT License. See LICENSE for details.
#
"""Snippets of code for use by the c++ layer."""
# (most of these are self-explanatory)
# pylint: disable=missing-function-docstring
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import _bauiv1

if TYPE_CHECKING:
    from typing import Sequence


def ticket_icon_press() -> None:
    from babase import app

    if app.classic is None:
        logging.exception('Classic not present.')
        return

    app.classic.ticket_icon_press()


def trophy_icon_press() -> None:
    print('TROPHY ICON PRESSED')


def level_icon_press() -> None:
    print('LEVEL ICON PRESSED')


def coin_icon_press() -> None:
    print('COIN ICON PRESSED')


def empty_call() -> None:
    pass


def back_button_press() -> None:
    _bauiv1.back_press()


def friends_button_press() -> None:
    print('FRIEND BUTTON PRESSED!')


def party_icon_activate(origin: Sequence[float]) -> None:
    from babase import app

    if app.classic is not None:
        app.classic.party_icon_activate(origin)
    else:
        logging.warning('party_icon_activate: no classic.')


def quit_window() -> None:
    from babase import app

    if app.classic is None:
        logging.exception('Classic not present.')
        return

    app.classic.quit_window()


def device_menu_press(device_id: int | None) -> None:
    from babase import app

    if app.classic is None:
        logging.exception('Classic not present.')
        return

    app.classic.device_menu_press(device_id)


def show_url_window(address: str) -> None:
    from babase import app

    if app.classic is None:
        logging.exception('Classic not present.')
        return

    app.classic.show_url_window(address)
