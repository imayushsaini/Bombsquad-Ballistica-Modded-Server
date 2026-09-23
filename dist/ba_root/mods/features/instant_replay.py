from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import weakref

import babase
import bascenev1 as bs
import _bascenev1
import setting

if TYPE_CHECKING:
    from typing import Any, Callable

# Global storage
g_last_replay_file: str | None = None
g_is_recording: bool = False
g_last_scorer_info: dict[str, Any] | None = None
g_highest_scorer_info: dict[str, Any] | None = None
g_active_player: InstantReplayPlayer | None = None
_active_player_ref: weakref.ref[InstantReplayPlayer] | None = None
g_active_recorder: Any = None  # Backward compatibility stub


def record_player_score(
    player: bs.Player,
    points: int = 1,
    position: Any = None,
) -> None:
    """Record scoring event to identify last scorer for instant replay zoom."""
    global g_last_scorer_info
    if not is_enabled():
        return
    try:
        if not player or not player.exists():
            return
        name = player.getname(full=False)
        name_full = player.getname(full=True)
        pos = None
        if position is not None and len(position) >= 3:
            pos = (float(position[0]), float(position[1]), float(position[2]))
        elif player.actor and player.actor.node and player.actor.node.exists():
            try:
                p = player.actor.node.position
                pos = (float(p[0]), float(p[1]), float(p[2]))
            except Exception:
                pass

        g_last_scorer_info = {
            'name': name,
            'name_full': name_full,
            'position': pos,
            'points': points,
            'time': bs.time(),
        }

    except Exception as e:
        logging.warning(f'InstantReplay: error recording score: {e}')


def _get_config() -> dict[str, Any]:
    """Retrieve instant replay settings from setting.json."""
    try:
        data = setting.get_settings_data()
        return data.get('instant_replay', {})
    except Exception:
        return {}


def is_enabled() -> bool:
    """Check if instant replay is enabled in configuration."""
    cfg = _get_config()
    return bool(cfg.get('enable', True))


def get_replay_duration() -> float:
    """Returns estimated playback duration in seconds for score screen delay."""
    cfg = _get_config()
    duration = float(cfg.get('duration', 4.5))
    speed = float(cfg.get('playback_speed', cfg.get('speed', 1.0)))
    if speed <= 0:
        speed = 1.0
    return max(1.0, duration / speed)


def get_replay_bg_opacity() -> float:
    """Returns background opacity during replay (0.0 = completely transparent/no bg, 1.0 = solid)."""
    cfg = _get_config()
    try:
        val = float(cfg.get('background_opacity', 0.4))
        return max(0.0, min(1.0, val))
    except (ValueError, TypeError):
        return 0.4


def has_replay_data() -> bool:
    """Returns True if a rolling replay buffer is ready to be broadcast."""
    global g_last_replay_file
    return bool(g_last_replay_file and is_enabled())


def on_game_begin(activity: bs.GameActivity) -> None:
    """Call when a game activity begins to start rolling replay recording."""
    global g_is_recording, g_last_replay_file, g_last_scorer_info, g_highest_scorer_info
    g_last_replay_file = None
    g_last_scorer_info = None
    g_highest_scorer_info = None
    if not is_enabled():
        return

    cfg = _get_config()
    duration = float(cfg.get('duration', 5.0))
    if duration <= 0:
        duration = 5.0

    try:
        _bascenev1.start_rolling_replay(duration)
        g_is_recording = True

    except Exception as e:
        logging.exception(
            f'InstantReplay: failed to start rolling replay: {e}')


def on_game_end(
    activity: bs.GameActivity | None = None,
    results: Any = None,
) -> None:
    """Call when a game activity ends to capture the chosen rolling replay buffer."""
    global g_is_recording, g_last_replay_file, g_highest_scorer_info
    if not g_is_recording:
        return

    g_is_recording = False

    # Determine highest scorer if activity stats are available
    if activity is not None:
        try:
            records = getattr(activity.stats, 'get_records', lambda: {})()
            best_name = None
            best_name_full = None
            best_score = -999999
            best_pos = None

            for record_id, record in records.items():
                score = getattr(record, 'score', 0)
                if score > best_score:
                    best_score = score
                    best_name = record.name
                    best_name_full = record.name_full

            # Try to get position of best player's Spaz
            if best_name:
                for player in activity.players:
                    try:
                        if player.getname(full=False) == best_name:
                            if player.actor and player.actor.node and player.actor.node.exists():
                                p = player.actor.node.position
                                best_pos = (float(p[0]), float(
                                    p[1]), float(p[2]))
                                break
                    except Exception:
                        pass

            if best_name and best_score > 0:
                g_highest_scorer_info = {
                    'name': best_name,
                    'name_full': best_name_full,
                    'position': best_pos,
                    'score': best_score,
                }

        except Exception as e:
            logging.warning(
                f'InstantReplay: error calculating highest scorer: {e}')

    try:
        chosen = _bascenev1.stop_rolling_replay()
        if chosen:
            g_last_replay_file = chosen

        else:
            g_last_replay_file = None

    except Exception as e:
        g_last_replay_file = None
        logging.exception(f'InstantReplay: failed to stop rolling replay: {e}')


def _fade_in_full_background(
    activity: bs.ScoreScreenActivity, fade_time: float = 0.8
) -> None:
    """Transitions the score screen background to full opacity with logo."""
    from bascenev1 import classicassets
    from bascenev1lib.actor.background import Background
    import random

    bg = getattr(activity, '_background', None)
    if bg is not None and hasattr(bg, 'node') and bg.node and bg.node.exists():
        try:
            session = bs.getsession()
            with session.context:
                cur_opacity = float(bg.node.opacity)
                bs.animate(
                    bg.node,
                    'opacity',
                    {0.0: cur_opacity, fade_time: 1.0},
                    loop=False,
                )
                # Create and fade in the logo if not present
                if not hasattr(bg, 'logo') or not bg.logo or not bg.logo.exists():
                    logo_texture = classicassets.textures.logo.get()
                    logo_mesh = classicassets.meshes.logo.get()
                    logo_mesh_transparent = (
                        classicassets.meshes.logo_transparent.get()
                    )
                    bg.logo = bs.newnode(
                        'image',
                        owner=bg.node,
                        attrs={
                            'texture': logo_texture,
                            'mesh_opaque': logo_mesh,
                            'mesh_transparent': logo_mesh_transparent,
                            'scale': (0.7, 0.7),
                            'vr_depth': -250,
                            'color': (0.15, 0.15, 0.15),
                            'position': (0, 0),
                            'tilt_translate': -0.05,
                            'absolute_scale': False,
                        },
                    )
                    bs.animate(
                        bg.logo, 'opacity', {0.0: 0.0, fade_time: 1.0}, loop=False
                    )
                    if not bs.app.env.vr:
                        bg.cmb = bs.newnode(
                            'combine', owner=bg.node, attrs={'size': 2}
                        )
                        for attr in ['input0', 'input1']:
                            bs.animate(
                                bg.cmb,
                                attr,
                                {0.0: 0.693, 0.05: 0.7, 0.5: 0.693},
                                loop=True,
                            )
                        bg.cmb.connectattr('output', bg.logo, 'scale')
                        cmb = bs.newnode(
                            'combine', owner=bg.node, attrs={'size': 2}
                        )
                        cmb.connectattr('output', bg.logo, 'position')
                        keys = {}
                        timeval = 0.0
                        for _i in range(10):
                            keys[timeval] = (random.random() - 0.5) * 0.0015
                            timeval += random.random() * 0.1
                        bs.animate(cmb, 'input0', keys, loop=True)
                        keys = {}
                        timeval = 0.0
                        for _i in range(10):
                            keys[timeval] = (
                                random.random() - 0.5) * 0.0015 + 0.05
                            timeval += random.random() * 0.1
                        bs.animate(cmb, 'input1', keys, loop=True)

                    def _connect_logo() -> None:
                        try:
                            if (
                                bg
                                and hasattr(bg, 'node')
                                and bg.node
                                and bg.node.exists()
                                and hasattr(bg, 'logo')
                                and bg.logo
                                and bg.logo.exists()
                            ):
                                bg.node.connectattr(
                                    'opacity', bg.logo, 'opacity')
                        except Exception:
                            pass

                    bs.timer(fade_time, _connect_logo)
                return
        except Exception as e:
            logging.warning(
                f'InstantReplay: failed to animate existing background: {e}')

    # If background did not exist or failed, create a new one
    try:
        activity._background = Background(
            fade_time=fade_time,
            start_faded=False,
            show_logo=True,
        )
    except Exception as e:
        logging.warning(
            f'InstantReplay: failed to instantiate Background: {e}')


class InstantReplayPlayer:
    """Controls replay playback on score screen."""

    def __init__(
        self,
        activity: bs.ScoreScreenActivity,
        replay_file: str,
        speed: float = 1.0,
        on_complete: Callable[[], None] | None = None,
        zoom_bounds: Sequence[float] | None = None,
        target_player_name: str | None = None,
    ) -> None:
        self._activity_ref = weakref.ref(activity)
        self.replay_file = replay_file
        self.speed = speed
        self.on_complete = on_complete
        self.zoom_bounds = list(
            zoom_bounds) if zoom_bounds is not None else None
        self.target_player_name = target_player_name
        self.running = False
        self._broadcast_started = False
        self._tag_node: Any = None

    @property
    def activity(self) -> bs.ScoreScreenActivity | None:
        return self._activity_ref() if self._activity_ref is not None else None

    def start(self) -> bool:
        if not self.replay_file:
            self._finish()
            return False

        self.running = True
        self._broadcast_started = True
        try:
            success = _bascenev1.start_replay_broadcast(
                self.replay_file,
                self.speed,
                self._on_broadcast_done,
                self.zoom_bounds,
                self.target_player_name,
            )
            if not success:

                self._finish()
                return False

            actual_dur = _bascenev1.get_replay_broadcast_duration()

            # Synchronize score screen minimum view time with actual playback duration
            activity = self.activity
            if activity and not activity.has_ended():
                activity._min_view_time = max(5.0, actual_dur)

            # Create a stylish watermark on the score screen activity
            if activity and not activity.has_ended():
                try:
                    with activity.context:
                        from bascenev1lib.actor.text import Text
                        if self.target_player_name:
                            label = f'🔴 REPLAY  |  FOCUS: {self.target_player_name}'
                        else:
                            label = '🔴 REPLAY'
                        self._tag_node = Text(
                            label,
                            scale=0.85,
                            h_attach=Text.HAttach.LEFT,
                            v_attach=Text.VAttach.TOP,
                            h_align=Text.HAlign.LEFT,
                            v_align=Text.VAlign.CENTER,
                            position=(30, -30),
                            color=(1.0, 0.25, 0.25, 0.9),
                            shadow=1.0,
                            flatness=1.0,
                            transition=Text.Transition.FADE_IN,
                        )
                except Exception as e:
                    logging.warning(
                        f'InstantReplay: failed to show watermark: {e}')

            return True
        except Exception as e:
            logging.exception(
                f'InstantReplay: exception starting broadcast: {e}')
            self._finish()
            return False

    def _on_broadcast_done(self) -> None:

        activity = self.activity
        if activity and not activity.has_ended():
            try:
                with activity.context:
                    # Fade in the standard score background smoothly over the frozen replay frame
                    _fade_in_full_background(activity, fade_time=0.8)

                    # Assign player input so players can press button to continue immediately
                    for player in activity.players:
                        activity._safe_assign(player)

                    # Give 0.9s for background to fade in before deleting 3D replay nodes behind it
                    _bascenev1.timer(0.9, self.stop)
            except Exception as e:
                logging.warning(
                    f'InstantReplay: failed to fade in background: {e}')
                self.stop()
        else:
            self.stop()

        self._finish()

    def stop(self) -> None:
        if not self.running and not getattr(self, '_broadcast_started', False):
            return
        self.running = False
        self._broadcast_started = False
        try:
            _bascenev1.stop_replay_broadcast()
        except Exception as e:
            logging.exception(
                f'InstantReplay: exception stopping broadcast: {e}')
        self._finish()

    def _finish(self) -> None:
        self.running = False
        if getattr(self, '_tag_node', None) is not None:
            try:
                if self._tag_node.node and self._tag_node.node.exists():
                    bs.animate(self._tag_node.node, 'opacity',
                               {0.0: 1.0, 0.4: 0.0})
                    bs.timer(0.4, self._tag_node.node.delete)
            except Exception:
                pass
            self._tag_node = None

        cb = self.on_complete
        self.on_complete = None
        if cb is not None:
            try:
                cb()
            except Exception:
                pass


def play_replay_on_score_screen(
    score_activity: bs.ScoreScreenActivity,
    on_finished_callback: Any = None,
) -> bool:
    """Broadcasts the captured replay onto client screens during the score screen."""
    global g_last_replay_file, g_active_player, _active_player_ref
    if not g_last_replay_file or not is_enabled():
        if on_finished_callback:
            try:
                on_finished_callback()
            except Exception:
                pass
        return False

    if not score_activity or score_activity.has_ended() or score_activity.expired:
        g_last_replay_file = None
        if on_finished_callback:
            try:
                on_finished_callback()
            except Exception:
                pass
        return False

    replay_file = g_last_replay_file
    g_last_replay_file = None  # Consume the replay buffer

    cfg = _get_config()
    speed = float(cfg.get('playback_speed', cfg.get('speed', 1.0)))
    if speed <= 0:
        speed = 1.0

    zoom_on_player = bool(cfg.get('zoom_on_player', True))
    zoom_target = str(cfg.get('zoom_target', 'auto')).lower()
    zoom_box_size = float(cfg.get('zoom_box_size', 12.0))
    if zoom_box_size <= 2.0:
        zoom_box_size = 12.0

    target_info: dict[str, Any] | None = None
    if zoom_on_player:
        if zoom_target == 'last_scorer':
            target_info = g_last_scorer_info or g_highest_scorer_info
        elif zoom_target == 'highest_scorer':
            target_info = g_highest_scorer_info or g_last_scorer_info
        else:  # 'auto'
            target_info = g_last_scorer_info or g_highest_scorer_info

    zoom_bounds: list[float] | None = None
    target_player_name: str | None = None

    if target_info:
        target_player_name = target_info.get('name')
        pos = target_info.get('position')
        if not pos and g_highest_scorer_info:
            pos = g_highest_scorer_info.get('position')
        if not pos and g_last_scorer_info:
            pos = g_last_scorer_info.get('position')

        if pos and len(pos) >= 3:
            px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
            hw = zoom_box_size * 0.5
            hd = zoom_box_size * 0.5
            zoom_bounds = [
                px - hw,
                py - 1.5,
                pz - hd,
                px + hw,
                py + 5.5,
                pz + hd,
            ]

    # Configure background for replay
    bg_opacity = get_replay_bg_opacity()
    if bg_opacity <= 0.0:
        # Purge background actor completely
        try:
            bg = getattr(score_activity, '_background', None)
            if bg is not None:
                try:
                    bg.handlemessage(bs.DieMessage(immediate=True))
                except Exception:
                    pass
                try:
                    if hasattr(bg, 'node') and bg.node and bg.node.exists():
                        bg.node.delete()
                except Exception:
                    pass
                score_activity._background = None
        except Exception as e:
            logging.warning(f'InstantReplay: error purging background: {e}')
    else:
        # Ensure we have a clean background with bg_opacity and NO logo
        try:
            bg = getattr(score_activity, '_background', None)
            # If bg has logo or its node is dead, purge it
            if bg is not None and (
                getattr(bg, 'logo', None) is not None
                or not hasattr(bg, 'node')
                or not bg.node
                or not bg.node.exists()
            ):
                try:
                    bg.handlemessage(bs.DieMessage(immediate=True))
                except Exception:
                    pass
                try:
                    if hasattr(bg, 'node') and bg.node and bg.node.exists():
                        bg.node.delete()
                except Exception:
                    pass
                bg = None
                score_activity._background = None

            if bg is None:
                from bascenev1lib.actor.background import Background
                bg = Background(
                    fade_time=0.5, start_faded=True, show_logo=False)
                score_activity._background = bg
                with bs.getsession().context:
                    bg.node.opacity = bg_opacity
            else:
                with bs.getsession().context:
                    bg.node.opacity = bg_opacity
        except Exception as e:
            logging.warning(
                f'InstantReplay: error configuring replay background: {e}')

    player = InstantReplayPlayer(
        activity=score_activity,
        replay_file=replay_file,
        speed=speed,
        on_complete=on_finished_callback,
        zoom_bounds=zoom_bounds,
        target_player_name=target_player_name,
    )
    g_active_player = player
    _active_player_ref = weakref.ref(player)

    try:
        score_activity.customdata['instant_replay_player'] = player
    except Exception:
        pass

    return player.start()


def stop_replay() -> None:
    """Stops any active replay broadcast immediately."""
    global g_active_player
    if g_active_player:
        g_active_player.stop()
        g_active_player = None
    try:
        if _bascenev1.is_replay_broadcasting():
            _bascenev1.stop_replay_broadcast()
    except Exception:
        pass


def get_active_player() -> InstantReplayPlayer | None:
    """Returns the currently active replay player if any."""
    return _active_player_ref() if _active_player_ref is not None else None
