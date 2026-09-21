# ba_meta require api 9
# ba_meta export babase.Plugin

import os
import time
import datetime
import threading
import babase
import bascenev1 as bs

class AutoReplayManager:
    def __init__(self) -> None:
        self._recording = False
        self._recording_start_time = 0.0
        self._check_timer = None
        self._recorded_session = None
        self._current_filename = ""

    def start(self) -> None:
        # Schedule check timer every 3 seconds.
        # We hold a strong reference to the timer in self._check_timer to prevent it from being deallocated.
        self._check_timer = babase.AppTimer(3.0, self._check, repeat=True)
        # Run an initial check immediately.
        self._check()

        # Run cleanup once on server boot in a separate thread.
        try:
            replays_dir = babase.get_replays_dir()
            thread = threading.Thread(target=self._run_cleanup_thread, args=(replays_dir,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"AutoReplay: Failed to spawn cleanup thread: {e}")

    def _has_players(self, session: bs.Session | None) -> bool:
        """Check whether there are actual players/clients on the server."""
        # Check 1: Active players in the session
        if session is not None:
            try:
                if len(session.sessionplayers) > 0:
                    return True
            except Exception:
                pass

        # Check 2: Connected clients in the party roster (excluding server host -1)
        try:
            for client in bs.get_game_roster():
                if client.get('client_id', -1) != -1:
                    return True
        except Exception:
            pass

        return False

    def _check(self) -> None:
        session = bs.get_foreground_host_session()
        has_players = self._has_players(session)
        now = time.time()

        if has_players and session is not None:
            # If the session changed while recording (e.g. playlist series ended),
            # clean up previous recording state and start fresh.
            if self._recording and self._recorded_session != session:
                print("AutoReplay: HostSession changed, restarting recording.")
                self._stop_recording(now)

            if not self._recording:
                # Start new recording
                self._start_recording(session, now)
            else:
                # We are recording. Check if we reached the 10-minute limit (600 seconds).
                if now - self._recording_start_time >= 600.0:
                    print("AutoReplay: 10 minutes limit reached, restarting recording.")
                    self._stop_recording(now)
                    self._start_recording(session, now)
        else:
            if self._recording:
                print("AutoReplay: No players or no active session, stopping recording.")
                self._stop_recording(now)

    def _start_recording(self, session: bs.Session, now: float) -> None:
        dt = datetime.datetime.fromtimestamp(now)
        timestamp_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"replay_{timestamp_str}"
        self._current_filename = filename
        
        print(f"AutoReplay: Starting replay recording: {filename}")
        try:
            with session.context:
                bs.start_replay_recording(filename)
            self._recording = True
            self._recording_start_time = now
            self._recorded_session = session
        except Exception as e:
            print(f"AutoReplay: Failed to start recording: {e}")
            self._current_filename = ""

    def _stop_recording(self, now: float | None = None) -> None:
        if now is None:
            now = time.time()
        duration = now - self._recording_start_time if self._recording_start_time > 0 else 0.0
        filename = self._current_filename

        session = self._recorded_session or bs.get_foreground_host_session()
        try:
            if session is not None:
                with session.context:
                    bs.stop_replay_recording()
            else:
                bs.stop_replay_recording()
        except Exception as e:
            print(f"AutoReplay: Failed to stop recording: {e}")

        self._recording = False
        self._recording_start_time = 0.0
        self._recorded_session = None
        self._current_filename = ""

        # Discard recordings that lasted less than 15 seconds (e.g. empty or instant disconnect)
        if duration < 15.0 and filename:
            try:
                replays_dir = babase.get_replays_dir()
                filepath = os.path.join(replays_dir, f"{filename}.brp")
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"AutoReplay: Discarded short replay ({duration:.1f}s): {filename}")
            except Exception as e:
                print(f"AutoReplay: Error removing short replay: {e}")

    def _run_cleanup_thread(self, replays_dir: str) -> None:
        try:
            if not os.path.exists(replays_dir):
                return
            
            now = time.time()
            # 2 days in seconds = 2 * 24 * 60 * 60 = 172800
            max_age = 2 * 24 * 60 * 60
            
            for name in os.listdir(replays_dir):
                if name.endswith('.brp'):
                    file_path = os.path.join(replays_dir, name)
                    if os.path.isfile(file_path):
                        mtime = os.path.getmtime(file_path)
                        if now - mtime > max_age:
                            print(f"AutoReplay: Deleting old replay: {name} (age: {now - mtime:.1f}s)")
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                print(f"AutoReplay: Error removing {name}: {e}")
        except Exception as e:
            print(f"AutoReplay: Error in background cleanup: {e}")

# Global instance to keep the manager alive.
_manager = None

def enable() -> None:
    global _manager
    if _manager is None:
        _manager = AutoReplayManager()
        _manager.start()

# Plugin entry point (for general compatibility if loaded as standard plugin).
class AutoReplayPlugin(babase.Plugin):
    def on_app_running(self) -> None:
        enable()
