# Released under the MIT License. See LICENSE for details.
#
"""Provides ui for network related testing."""

from __future__ import annotations

import time
import copy
import weakref
from threading import Thread
from typing import TYPE_CHECKING

import _ba
import ba
from bastd.ui.settings.testing import TestingWindow

if TYPE_CHECKING:
    from typing import Callable, Any, Optional


class NetTestingWindow(ba.Window):
    """Window that runs a networking test suite to help diagnose issues."""

    def __init__(self, transition: str = 'in_right'):
        self._width = 820
        self._height = 500
        self._printed_lines: list[str] = []
        uiscale = ba.app.ui.uiscale
        super().__init__(root_widget=ba.containerwidget(
            size=(self._width, self._height),
            scale=(1.56 if uiscale is ba.UIScale.SMALL else
                   1.2 if uiscale is ba.UIScale.MEDIUM else 0.8),
            stack_offset=(0.0, -7 if uiscale is ba.UIScale.SMALL else 0.0),
            transition=transition))
        self._done_button = ba.buttonwidget(parent=self._root_widget,
                                            position=(40, self._height - 77),
                                            size=(120, 60),
                                            scale=0.8,
                                            autoselect=True,
                                            label=ba.Lstr(resource='doneText'),
                                            on_activate_call=self._done)

        self._copy_button = ba.buttonwidget(parent=self._root_widget,
                                            position=(self._width - 200,
                                                      self._height - 77),
                                            size=(100, 60),
                                            scale=0.8,
                                            autoselect=True,
                                            label=ba.Lstr(resource='copyText'),
                                            on_activate_call=self._copy)

        self._settings_button = ba.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 100, self._height - 77),
            size=(60, 60),
            scale=0.8,
            autoselect=True,
            label=ba.Lstr(value='...'),
            on_activate_call=self._show_val_testing)

        twidth = self._width - 450
        ba.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 55),
            size=(0, 0),
            text=ba.Lstr(resource='settingsWindowAdvanced.netTestingText'),
            color=(0.8, 0.8, 0.8, 1.0),
            h_align='center',
            v_align='center',
            maxwidth=twidth)

        self._scroll = ba.scrollwidget(parent=self._root_widget,
                                       position=(50, 50),
                                       size=(self._width - 100,
                                             self._height - 140),
                                       capture_arrows=True,
                                       autoselect=True)
        self._rows = ba.columnwidget(parent=self._scroll)

        ba.containerwidget(edit=self._root_widget,
                           cancel_button=self._done_button)

        # Now kick off the tests.
        # Pass a weak-ref to this window so we don't keep it alive
        # if we back out before it completes. Also set is as daemon
        # so it doesn't keep the app running if the user is trying to quit.
        Thread(
            daemon=True,
            target=ba.Call(_run_diagnostics, weakref.ref(self)),
        ).start()

    def print(self, text: str, color: tuple[float, float, float]) -> None:
        """Print text to our console thingie."""
        for line in text.splitlines():
            txt = ba.textwidget(parent=self._rows,
                                color=color,
                                text=line,
                                scale=0.75,
                                flatness=1.0,
                                shadow=0.0,
                                size=(0, 20))
            ba.containerwidget(edit=self._rows, visible_child=txt)
            self._printed_lines.append(line)

    def _copy(self) -> None:
        if not ba.clipboard_is_supported():
            ba.screenmessage('Clipboard not supported on this platform.',
                             color=(1, 0, 0))
            return
        ba.clipboard_set_text('\n'.join(self._printed_lines))
        ba.screenmessage(f'{len(self._printed_lines)} lines copied.')

    def _show_val_testing(self) -> None:
        ba.app.ui.set_main_menu_window(NetValTestingWindow().get_root_widget())
        ba.containerwidget(edit=self._root_widget, transition='out_left')

    def _done(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.advanced import AdvancedSettingsWindow
        ba.app.ui.set_main_menu_window(
            AdvancedSettingsWindow(transition='in_left').get_root_widget())
        ba.containerwidget(edit=self._root_widget, transition='out_right')


def _run_diagnostics(weakwin: weakref.ref[NetTestingWindow]) -> None:
    # pylint: disable=too-many-statements

    from efro.util import utc_now

    have_error = [False]

    # We're running in a background thread but UI stuff needs to run
    # in the logic thread; give ourself a way to pass stuff to it.
    def _print(text: str, color: tuple[float, float, float] = None) -> None:

        def _print_in_logic_thread() -> None:
            win = weakwin()
            if win is not None:
                win.print(text, (1.0, 1.0, 1.0) if color is None else color)

        ba.pushcall(_print_in_logic_thread, from_other_thread=True)

    def _print_test_results(call: Callable[[], Any]) -> None:
        """Run the provided call; return success/fail text & color."""
        starttime = time.monotonic()
        try:
            call()
            duration = time.monotonic() - starttime
            _print(f'Succeeded in {duration:.2f}s.', color=(0, 1, 0))
        except Exception:
            import traceback
            duration = time.monotonic() - starttime
            _print(traceback.format_exc(), color=(1.0, 1.0, 0.3))
            _print(f'Failed in {duration:.2f}s.', color=(1, 0, 0))
            have_error[0] = True

    try:
        _print(f'Running network diagnostics...\n'
               f'ua: {_ba.app.user_agent_string}\n'
               f'time: {utc_now()}.')

        if bool(False):
            _print('\nRunning dummy success test...')
            _print_test_results(_dummy_success)

            _print('\nRunning dummy fail test...')
            _print_test_results(_dummy_fail)

        # V1 ping
        baseaddr = _ba.get_master_server_address(source=0, version=1)
        _print(f'\nContacting V1 master-server src0 ({baseaddr})...')
        _print_test_results(lambda: _test_fetch(baseaddr))

        # V1 alternate ping
        baseaddr = _ba.get_master_server_address(source=1, version=1)
        _print(f'\nContacting V1 master-server src1 ({baseaddr})...')
        _print_test_results(lambda: _test_fetch(baseaddr))

        _print(f'\nV1-test-log: {ba.app.net.v1_test_log}')

        for srcid, result in sorted(ba.app.net.v1_ctest_results.items()):
            _print(f'\nV1 src{srcid} result: {result}')

        curv1addr = _ba.get_master_server_address(version=1)
        _print(f'\nUsing V1 address: {curv1addr}')

        _print('\nRunning V1 transaction...')
        _print_test_results(_test_v1_transaction)

        # V2 ping
        baseaddr = _ba.get_master_server_address(version=2)
        _print(f'\nContacting V2 master-server ({baseaddr})...')
        _print_test_results(lambda: _test_fetch(baseaddr))

        # Get V2 nearby region
        with ba.app.net.region_pings_lock:
            region_pings = copy.deepcopy(ba.app.net.region_pings)
        nearest_region = (None if not region_pings else sorted(
            region_pings.items(), key=lambda i: i[1])[0])

        if nearest_region is not None:
            nearstr = f'{nearest_region[0]}: {nearest_region[1]:.0f}ms'
        else:
            nearstr = '-'
        _print(f'\nChecking nearest V2 region ping ({nearstr})...')
        _print_test_results(lambda: _test_nearby_region_ping(nearest_region))

        if have_error[0]:
            _print('\nDiagnostics complete. Some diagnostics failed.',
                   color=(10, 0, 0))
        else:
            _print('\nDiagnostics complete. Everything looks good!',
                   color=(0, 1, 0))
    except Exception:
        import traceback
        _print(
            f'An unexpected error occurred during testing;'
            f' please report this.\n'
            f'{traceback.format_exc()}',
            color=(1, 0, 0))


def _dummy_success() -> None:
    """Dummy success test."""
    time.sleep(1.2)


def _dummy_fail() -> None:
    """Dummy fail test case."""
    raise RuntimeError('fail-test')


def _test_v1_transaction() -> None:
    """Dummy fail test case."""
    if _ba.get_account_state() != 'signed_in':
        raise RuntimeError('Not signed in.')

    starttime = time.monotonic()

    # Gets set to True on success or string on error.
    results: list[Any] = [False]

    def _cb(cbresults: Any) -> None:
        # Simply set results here; our other thread acts on them.
        if not isinstance(cbresults, dict) or 'party_code' not in cbresults:
            results[0] = 'Unexpected transaction response'
            return
        results[0] = True  # Success!

    def _do_it() -> None:
        # Fire off a transaction with a callback.
        _ba.add_transaction(
            {
                'type': 'PRIVATE_PARTY_QUERY',
                'expire_time': time.time() + 20,
            },
            callback=_cb,
        )
        _ba.run_transactions()

    ba.pushcall(_do_it, from_other_thread=True)

    while results[0] is False:
        time.sleep(0.01)
        if time.monotonic() - starttime > 10.0:
            raise RuntimeError('timed out')

    # If we got left a string, its an error.
    if isinstance(results[0], str):
        raise RuntimeError(results[0])


def _test_fetch(baseaddr: str) -> None:
    # pylint: disable=consider-using-with
    import urllib.request
    response = urllib.request.urlopen(urllib.request.Request(
        f'{baseaddr}/ping', None, {'User-Agent': _ba.app.user_agent_string}),
                                      timeout=10.0)
    if response.getcode() != 200:
        raise RuntimeError(
            f'Got unexpected response code {response.getcode()}.')
    data = response.read()
    if data != b'pong':
        raise RuntimeError('Got unexpected response data.')


def _test_nearby_region_ping(
        nearest_region: Optional[tuple[str, float]]) -> None:
    """Try to ping nearest v2 region."""
    if nearest_region is None:
        raise RuntimeError('No nearest region.')
    if nearest_region[1] > 500:
        raise RuntimeError('Ping too high.')


class NetValTestingWindow(TestingWindow):
    """Window to test network related settings."""

    def __init__(self, transition: str = 'in_right'):

        entries = [
            {
                'name': 'bufferTime',
                'label': 'Buffer Time',
                'increment': 1.0
            },
            {
                'name': 'delaySampling',
                'label': 'Delay Sampling',
                'increment': 1.0
            },
            {
                'name': 'dynamicsSyncTime',
                'label': 'Dynamics Sync Time',
                'increment': 10
            },
            {
                'name': 'showNetInfo',
                'label': 'Show Net Info',
                'increment': 1
            },
        ]
        super().__init__(
            title=ba.Lstr(resource='settingsWindowAdvanced.netTestingText'),
            entries=entries,
            transition=transition,
            back_call=lambda: NetTestingWindow(transition='in_left'))
