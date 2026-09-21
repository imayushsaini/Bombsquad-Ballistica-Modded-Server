"""Custom hooks to pull of the in-game functions."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

from __future__ import annotations
from tools import servercheck, server_update, logger, playlist, servercontroller
from tools import notification_manager
from tools import account
from stats import mystats
from spazmod import modifyspaz
from serverdata import serverdata
from playersdata import pdata
from features import votingmachine
from features import text_on_map, announcement
from features import team_balancer, afk_check, dual_team_score as newdts
from features import map_fun
from chathandle import handlechat
from bascenev1lib.actor import playerspaz
from bascenev1lib.activity.coopscore import CoopScoreScreen
from bascenev1lib.activity import dualteamscore, multiteamscore, drawscore
from bascenev1._session import Session
from bascenev1._map import Map
from bascenev1._activitytypes import ScoreScreenActivity
from baclassic._servermode import ServerController
from efro.terminal import Clr
import setting
import bauiv1 as bui
from baclassic._appmode import ClassicAppMode
import _bascenev1
import bascenev1 as bs
import babase
from typing import TYPE_CHECKING
import _babase

import _thread
import importlib
import logging
import os
import sys
import subprocess
import time
from datetime import datetime

# --- Auto dependency installer ---


def _check_and_install_dependencies():
    """Checks and installs ecdsa and flask to python-site-packages if missing."""
    needed = ["ecdsa", "flask", "waitress"]
    missing = []

    mods_dir = os.path.dirname(__file__)
    target_dir = os.path.abspath(os.path.join(
        mods_dir, "..", "..", "ba_data", "python-site-packages"))
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)

    for pkg in needed:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        logging.warning(
            f"Required dependencies {missing} are missing. Attempting to install them into {target_dir}...")
        try:
            python_exe = sys.executable or "python3"
            cmd = [
                python_exe,
                "-m",
                "pip",
                "install",
                "--target",
                target_dir,
                "--break-system-packages"
            ] + missing

            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                logging.warning(
                    f"Successfully installed {missing} to {target_dir}")
                importlib.invalidate_caches()
            else:
                logging.error(
                    f"Failed to install dependencies {missing}. pip output: {result.stderr}")
        except Exception as e:
            logging.exception(
                f"Exception during automatic dependency installation: {e}")


_check_and_install_dependencies()


if TYPE_CHECKING:
    from typing import Any

settings = setting.get_settings_data()


def filter_chat_message(msg: str, client_id: int) -> str | None:
    """Returns all in game messages or None (ignore's message)."""
    return handlechat.filter_chat_message(msg, client_id)


# ba_meta export babase.Plugin
class modSetup(babase.Plugin):
    def on_app_running(self):
        """Runs when app is launched."""
        plus = bui.app.plus
        bootstraping()
        servercheck.ServerCheck()
        server_update.check()
        # bs.apptimer(5, account.updateOwnerIps)
        if settings["afk_remover"]['enable']:
            afk_check.checkIdle().start()
        if (settings["useV2Account"]):

            if (plus.get_v1_account_state() ==
                    'signed_in' and plus.get_v1_account_type() == 'V2'):
                logging.debug("Account V2 is active")
            else:
                logging.warning("Account V2 login require ....stay tuned.")
                bs.apptimer(3, babase.Call(logging.debug,
                                           "Starting Account V2 login process...."))
                bs.apptimer(6, account.AccountUtil)
        else:
            plus.accounts.set_primary_credentials(None)
            plus.sign_in_v1('Local')
        bs.apptimer(60, playlist.flush_playlists)
        try:
            from actor import welcome
            bs.apptimer(2.0, welcome.ensure_nodes)
        except Exception:
            pass

    # it works sometimes , but it blocks shutdown so server raise runtime
    # exception,   also dump server logs
    def on_app_shutdown(self):
        print("Server shutting down , lets save cache")
        # lets try  threading here
        # _thread.start_new_thread(pdata.dump_cache, ())
        # _thread.start_new_thread(notification_manager.dump_cache, ())
        # print("Done dumping memory")


def is_victory_score_screen(activity: ScoreScreenActivity) -> bool:
    """Check if the activity is a final series victory score screen."""
    if getattr(activity, '_is_victory_screen', False):
        return True
    try:
        from bascenev1lib.activity import multiteamvictory
        if isinstance(activity, multiteamvictory.TeamSeriesVictoryScoreScreenActivity):
            return True
    except Exception:
        pass
    try:
        from features import stumbled_score_screen
        if isinstance(activity, stumbled_score_screen._TeamSeriesVictoryScoreScreenActivity):
            return True
    except Exception:
        pass
    return False


def get_victory_score_screen_mode() -> str:
    """Returns 'stumbled', 'replay', or 'original' for the final victory screen."""
    mode = str(settings.get("victory_score_screen", "")).lower().strip()
    if mode in ("stumbled", "replay", "original"):
        return mode
    gen_mode = str(settings.get("score_screen_mode", "")).lower().strip()
    if gen_mode in ("stumbled", "replay", "original"):
        return gen_mode
    if settings.get("StumbledScoreScreen", False):
        return "stumbled"
    if settings.get("instant_replay", {}).get("enable", True):
        return "replay"
    return "original"


def get_round_score_screen_mode() -> str:
    """Returns 'replay' or 'original' for match round score screens."""
    mode = str(settings.get("round_score_screen", "")).lower().strip()
    if mode in ("replay", "original"):
        return mode
    gen_mode = str(settings.get("score_screen_mode", "")).lower().strip()
    if gen_mode in ("replay", "original"):
        return gen_mode
    if settings.get("instant_replay", {}).get("enable", True):
        return "replay"
    return "original"


def should_play_replay_on_activity(activity: ScoreScreenActivity) -> bool:
    """Determines whether instant replay should play on this score screen."""
    if not settings.get("instant_replay", {}).get("enable", True):
        return False
    if is_victory_score_screen(activity):
        return get_victory_score_screen_mode() == "replay"
    return get_round_score_screen_mode() == "replay"


_orig_score_screen_init = ScoreScreenActivity.__init__


def score_screen_init(self, *args, **kwargs) -> None:
    _orig_score_screen_init(self, *args, **kwargs)
    if should_play_replay_on_activity(self):
        try:
            from features import instant_replay
            if instant_replay.has_replay_data():
                replay_duration = instant_replay.get_replay_duration()
                self._replay_duration = replay_duration
                self._min_view_time = max(self._min_view_time, replay_duration)
        except Exception as e:
            logging.exception(
                f"Error initializing instant replay duration: {e}")


ScoreScreenActivity.__init__ = score_screen_init


def score_screen_on_begin(func) -> None:
    """Runs when score screen is displayed."""

    def wrapper(self, *args, **kwargs):
        replay_duration = getattr(self, '_replay_duration', 0.0)
        if replay_duration <= 0.0 and should_play_replay_on_activity(self):
            try:
                from features import instant_replay
                if instant_replay.has_replay_data():
                    replay_duration = instant_replay.get_replay_duration()
                    self._replay_duration = replay_duration
                    self._min_view_time = max(
                        self._min_view_time, replay_duration)
            except Exception as e:
                logging.exception(f"Error preparing instant replay: {e}")

        result = func(self, *args, **kwargs)  # execute the original method
        team_balancer.balanceTeams()
        mystats.update(self._stats)

        if replay_duration > 0.0 and should_play_replay_on_activity(self):
            try:
                from features import instant_replay
                instant_replay.play_replay_on_score_screen(self)
            except Exception as e:
                logging.exception(f"Error playing instant replay: {e}")

        announcement.showScoreScreenAnnouncement()
        return result

    return wrapper


ScoreScreenActivity.on_begin = score_screen_on_begin(
    ScoreScreenActivity.on_begin)


def cleanup_session_background(activity=None) -> None:
    """Purge any Background actor on the score screen activity."""
    if activity is not None:
        try:
            bg = getattr(activity, '_background', None)
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
                activity._background = None
        except Exception as e:
            logging.exception(f"Error cleaning up activity background: {e}")


_orig_score_screen_transition_in = ScoreScreenActivity.on_transition_in


def score_screen_on_transition_in(self) -> None:
    replay_enabled = should_play_replay_on_activity(self)
    has_replay = False
    if replay_enabled:
        try:
            from features import instant_replay
            has_replay = instant_replay.has_replay_data()
        except Exception:
            pass

    if has_replay:
        # Replay is queued to play on this score screen!
        super(ScoreScreenActivity, self).on_transition_in()
        self._tips_text = None
        if self.default_music is not None:
            bs.setmusic(self.default_music)

        bg_opacity = 0.4
        try:
            from features import instant_replay
            bg_opacity = instant_replay.get_replay_bg_opacity()
        except Exception:
            pass

        if bg_opacity > 0.0:
            from bascenev1lib.actor.background import Background
            bg = Background(fade_time=0.5, start_faded=True, show_logo=False)
            self._background = bg
            try:
                session = bs.getsession()
                with session.context:
                    bg.node.opacity = 0.0
                    bs.animate(
                        bg.node,
                        'opacity',
                        {0.0: 0.0, 0.5: bg_opacity},
                        loop=False,
                    )
            except Exception as e:
                logging.warning(f"Error animating replay background: {e}")
        else:
            self._background = None
        return

    _orig_score_screen_transition_in(self)


ScoreScreenActivity.on_transition_in = score_screen_on_transition_in

_orig_score_screen_transition_out = ScoreScreenActivity.on_transition_out


def score_screen_on_transition_out(self) -> None:
    try:
        from features import instant_replay
        instant_replay.stop_replay()
    except Exception as e:
        logging.exception(
            f"Error stopping instant replay on transition out: {e}")
    cleanup_session_background(self)
    _orig_score_screen_transition_out(self)


ScoreScreenActivity.on_transition_out = score_screen_on_transition_out

_orig_score_screen_expire = ScoreScreenActivity.on_expire


def score_screen_on_expire(self) -> None:
    try:
        from features import instant_replay
        instant_replay.stop_replay()
    except Exception as e:
        logging.exception(f"Error stopping instant replay on expire: {e}")
    cleanup_session_background(self)
    _orig_score_screen_expire(self)


ScoreScreenActivity.on_expire = score_screen_on_expire

_orig_score_screen_player_press = ScoreScreenActivity._player_press


def score_screen_player_press(self) -> None:
    with self.context:
        _orig_score_screen_player_press(self)


ScoreScreenActivity._player_press = score_screen_player_press


def on_map_init(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        text_on_map.textonmap()
        modifyspaz.setTeamCharacter()
        try:
            import private_hud
            private_hud.apply_day_night_preferences()
        except Exception as e:
            print(f"Error applying day/night preferences on map init: {e}")

    return wrapper


Map.__init__ = on_map_init(Map.__init__)


def playerspaz_init(playerspaz: bs.Player, node: bs.Node, player: bs.Player):
    """Runs when player is spawned on map."""
    modifyspaz.main(playerspaz, node, player)


def verify_account_token() -> None:
    """Verifies the account API token on server start."""
    import urllib.request
    import urllib.error
    import json
    token = settings.get("accountApiToken")
    warning_msg = (
        "invalid token found , update settings.json with api token "
        "else server functionaly will break."
    )
    if not token:
        logging.warning(warning_msg)
        print(f'{Clr.BRED}{warning_msg}{Clr.RST}', flush=True)
        return

    try:
        url = "https://www.ballistica.net/api/v1/accounts/me"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            if status == 200:
                data = json.loads(response.read().decode('utf-8'))
                tag = data.get("tag", "unknown")
                print(
                    f"{Clr.BGRN}api token verified sucfessfuly using {tag} token.{Clr.RST}", flush=True)
                logging.info(
                    f"api token verified sucfessfuly using {tag} token.")
            else:
                logging.warning(warning_msg)
                print(f'{Clr.BRED}{warning_msg}{Clr.RST}', flush=True)
    except Exception:
        logging.warning(warning_msg)
        print(f'{Clr.BRED}{warning_msg}{Clr.RST}', flush=True)


def bootstraping():
    """Bootstarps the server."""
    logging.warning("Bootstraping mods...")
    # server related

    # check for auto update stats
    _thread.start_new_thread(mystats.refreshStats, ())
    _thread.start_new_thread(verify_account_token, ())
    pdata.load_cache()
    _thread.start_new_thread(pdata.dump_cache, ())
    _thread.start_new_thread(notification_manager.dump_cache, ())

    # import plugins
    if settings["elPatronPowerups"]["enable"]:
        from plugins import elPatronPowerups
        elPatronPowerups.enable()
        try:
            from plugins import creativePowerups
            creativePowerups.enable()
        except Exception as e:
            logging.exception("Failed to enable creativePowerups:")
    if settings["mikirogQuickTurn"]["enable"]:
        from plugins import wavedash  # pylint: disable=unused-import
    if settings["colorful_explosions"]["enable"]:
        from plugins import color_explosion
        color_explosion.enable()
    if settings["ballistica_web"]["enable"]:
        from plugins import bcs_plugin
        bcs_plugin.enable(settings["ballistica_web"]["server_password"])
    if settings["character_chooser"]["enable"]:
        from plugins import character_chooser
        character_chooser.enable()
    if settings["custom_characters"]["enable"]:
        from plugins import importcustomcharacters
        importcustomcharacters.enable()

    # Auto Replay Plugin (defaults to enabled unless explicitly configured as disabled)
    if settings.get("auto_replay", {}).get("enable", True):
        try:
            from plugins import auto_replay
            auto_replay.enable()
        except Exception as e:
            logging.exception("Failed to enable auto_replay:")
    # Final Victory Score Screen: 'stumbled', 'replay', or 'original'
    if get_victory_score_screen_mode() == "stumbled":
        try:
            from features import stumbled_score_screen
            stumbled_score_screen.enable()
        except Exception as e:
            logging.exception(f"Failed to enable StumbledScoreScreen: {e}")
    if settings["colorfullMap"]:
        from plugins import colorfulmaps2
    try:
        from plugins import kickvote_manager
        kickvote_manager.enable()
    except Exception as e:
        logging.exception("Failed to enable kickvote_manager:")
    try:
        pass
        # from tools import healthcheck
        # healthcheck.main()
    except Exception as e:
        print(e)
        try:
            import subprocess
            # Install psutil package
            # Download get-pip.py
            curl_process = subprocess.Popen(
                ["curl", "-sS", "https://bootstrap.pypa.io/get-pip.py"],
                stdout=subprocess.PIPE)

            # Install pip using python3.10
            python_process = subprocess.Popen(
                ["python3.14"], stdin=curl_process.stdout)

            # Wait for the processes to finish
            curl_process.stdout.close()
            python_process.wait()

            subprocess.check_call(
                ["python3.14", "-m", "pip", "install", "psutil"])
            # restart after installation
            print("dependency installed , restarting server")
            _babase.quit()
            from tools import healthcheck
            healthcheck.main()
        except BaseException:
            logging.warning("please install psutil to enable system monitor.")

    # import features
    if settings["whitelist"]:
        pdata.load_white_list()

    import_discord_bot()
    import_games()
    import_dual_team_score()
    logger.log("Server started")


def import_discord_bot() -> None:
    """Imports the discord bot."""
    if settings["discordbot"]["enable"]:
        from features import discord_bot
        discord_bot.token = settings["discordbot"]["token"]
        discord_bot.liveStatsChannelID = settings["discordbot"][
            "liveStatsChannelID"]
        discord_bot.logsChannelID = settings["discordbot"]["logsChannelID"]
        discord_bot.liveChat = settings["discordbot"]["liveChat"]
        discord_bot.BsDataThread()
        discord_bot.init()


def import_games():
    """Imports the custom games from games directory."""
    import sys
    sys.path.append(_babase.env()['python_directory_user'] + os.sep + "games")
    games = os.listdir("ba_root/mods/games")
    for game in games:
        if game.endswith(".so"):
            importlib.import_module("games." + game.replace(".so", ""))

    maps = os.listdir("ba_root/mods/maps")
    for _map in maps:
        if _map.endswith(".py") or _map.endswith(".so"):
            importlib.import_module(
                "maps." + _map.replace(".so", "").replace(".py", ""))


def import_dual_team_score() -> None:
    """Imports the dual team score."""
    if settings["newResultBoard"]:
        dualteamscore.TeamVictoryScoreScreenActivity = newdts.TeamVictoryScoreScreenActivity
        multiteamscore.MultiTeamScoreScreenActivity.show_player_scores = newdts.show_player_scores
        drawscore.DrawScoreScreenActivity = newdts.DrawScoreScreenActivity


org_begin = bs._activity.Activity.on_begin


def new_begin(self):
    """Runs when game is began."""
    org_begin(self)
    if isinstance(self, bs.GameActivity):
        cleanup_session_background(self)
        if settings.get("instant_replay", {}).get("enable", True):
            try:
                from features import instant_replay
                instant_replay.on_game_begin(self)
            except Exception as e:
                logging.exception(
                    f"Error starting instant replay recorder: {e}")
    night_mode()
    if settings["colorfullMap"]:
        map_fun.decorate_map()
    votingmachine.reset_votes()
    votingmachine.game_started_on = time.time()
    try:
        from actor import welcome
        welcome.ensure_nodes()
    except Exception as e:
        logging.exception(
            f"Error ensuring welcome banner nodes on game begin: {e}")
    try:
        import private_hud
        private_hud.apply_day_night_preferences()
    except Exception as e:
        print(f"Error applying day/night preferences on game begin: {e}")


bs._activity.Activity.on_begin = new_begin

org_end = bs._activity.Activity.end


def new_end(self, results: Any = None,
            delay: float = 0.0, force: bool = False):
    """Runs when game is ended."""
    if isinstance(self, bs.GameActivity):
        try:
            from features import instant_replay
            instant_replay.on_game_end(activity=self, results=results)
        except Exception as e:
            logging.exception(f"Error ending instant replay recorder: {e}")

    try:
        activity = bs.get_foreground_host_activity()
        if isinstance(activity, CoopScoreScreen):
            team_balancer.checkToExitCoop()
    except Exception:
        pass
    with self.context:
        org_end(self, results, delay, force)


bs._activity.Activity.end = new_end

# Hook Stats.player_scored to track scorers for instant replay zoom
try:
    _orig_player_scored = bs.Stats.player_scored

    def _wrapped_player_scored(self, player, base_points=1, *args, **kwargs):
        try:
            from features import instant_replay
            target_pos = kwargs.get('target', None)
            if target_pos is None and player and player.node:
                try:
                    target_pos = player.node.position
                except Exception:
                    pass
            instant_replay.record_player_score(
                player=player,
                points=base_points,
                position=target_pos,
            )
        except Exception:
            pass
        return _orig_player_scored(self, player, base_points, *args, **kwargs)

    bs.Stats.player_scored = _wrapped_player_scored
except Exception as e:
    logging.warning(f"Error hooking bs.Stats.player_scored: {e}")

# Hook Blast explosion events for instant replay
try:
    from bascenev1lib.actor.bomb import Blast
    _orig_blast_init = Blast.__init__

    def _wrapped_blast_init(self, *args, **kwargs):
        _orig_blast_init(self, *args, **kwargs)
        try:
            from features import instant_replay
            if instant_replay.g_active_recorder and instant_replay.g_active_recorder.running:
                pos = kwargs.get(
                    'position', (args[0] if args else (0.0, 1.0, 0.0)))
                b_type = kwargs.get('blast_type', 'normal')
                b_radius = kwargs.get('blast_radius', 2.0)
                instant_replay.g_active_recorder.record_blast(
                    pos, b_type, b_radius)
        except Exception:
            pass

    Blast.__init__ = _wrapped_blast_init
except Exception as e:
    logging.exception(f"Error hooking Blast for instant replay: {e}")


org_player_join = bs._activity.Activity.on_player_join


def on_player_join(self, player) -> None:
    """Runs when player joins the game. OR during game result screen"""
    team_balancer.on_player_join()

    try:
        from shop.shop_system import preload_player
        account_id = player.sessionplayer.get_account_id()
        if account_id:
            preload_player(account_id)
    except Exception as e:
        print(f"Error preloading player shop cache: {e}")

    try:
        sessionplayer = getattr(player, 'sessionplayer', None)
        if sessionplayer is not None:
            account_id = None
            if hasattr(sessionplayer, 'get_v1_account_id'):
                account_id = sessionplayer.get_v1_account_id()
            if not account_id and hasattr(sessionplayer, 'get_account_id'):
                account_id = sessionplayer.get_account_id()

            inputdevice = getattr(sessionplayer, 'inputdevice', None)
            client_id = getattr(inputdevice, 'client_id',
                                None) if inputdevice else None

            if account_id and client_id is not None and client_id != -1:
                import private_hud
                # Delay applying preferences on player join so client has finished loading the scene
                babase.apptimer(2.0, babase.Call(
                    private_hud.apply_preferences_for_client, client_id, account_id))
    except Exception as e:
        print(f"Error applying private HUD on player join: {e}")

    org_player_join(self, player)


bs._activity.Activity.on_player_join = on_player_join


def night_mode() -> None:
    """Checks the time and enables night mode."""

    if settings['autoNightMode']['enable']:

        start = datetime.strptime(
            settings['autoNightMode']['startTime'], "%H:%M")
        end = datetime.strptime(settings['autoNightMode']['endTime'], "%H:%M")
        now = datetime.now()

        if now.time() > start.time() or now.time() < end.time():
            activity = bs.get_foreground_host_activity()

            activity.globalsnode.tint = (0.5, 0.7, 1.0)

            if settings['autoNightMode']['fireflies']:
                try:
                    activity.fireflies_generator(
                        20, settings['autoNightMode']["fireflies_random_color"])
                except:
                    pass


# ------------------ Kick Vote Handling -------------------


def kick_vote_started(started_by: str, started_to: str) -> bool:
    """Checks restrictions and immunity via KickVoteManager, logs the attempt, and returns True to allow or False to block."""
    try:
        from plugins.kickvote_manager import KickVoteManager
        return KickVoteManager.get().check_and_handle_kick_vote(started_by, started_to)
    except Exception as e:
        logger.log(f"Error in kick_vote_started: {e}")
        return True


def on_kicked(account_id: str) -> None:
    """Runs when someone is kicked by kickvote."""
    logger.log(f"{account_id} kicked by kickvotes.")


def on_kick_vote_end():
    """Runs when kickvote is ended."""
    logger.log("Kick vote End")


def on_join_request(ip):
    servercheck.on_join_request(ip)


def shutdown(func) -> None:
    """Set the app to quit either now or at the next clean opportunity."""

    def wrapper(*args, **kwargs):
        # add screen text and tell players we are going to restart soon.
        bs.chatmessage(
            "Server will restart on next opportunity. (series end)")
        _babase.restart_scheduled = True
        bs.get_foreground_host_activity().restart_msg = bs.newnode('text',
                                                                   attrs={
                                                                       'text': "Server going to restart after this series.",
                                                                       'flatness': 1.0,
                                                                       'h_align': 'right',
                                                                       'v_attach': 'bottom',
                                                                       'h_attach': 'right',
                                                                       'scale': 0.5,
                                                                       'position': (
                                                                           -25,
                                                                           54),
                                                                       'color': (
                                                                           1,
                                                                           0.5,
                                                                           0.7)
                                                                   })
        import private_hud
        private_hud.register_node(
            bs.get_foreground_host_activity().restart_msg, 'next_match', 'scale', 0.5)
        func(*args, **kwargs)

    return wrapper


ServerController.shutdown = shutdown(ServerController.shutdown)


def on_player_request(func) -> bool:

    def wrapper(*args, **kwargs):
        player: bs.SessionPlayer = args[1]
        count = 0
        if not (player.get_account_id(
        ) in serverdata.clients and
                serverdata.clients[player.get_account_id()]["verified"]):

            return False
        for current_player in args[0].sessionplayers:
            if current_player.get_account_id() == player.get_account_id():
                count += 1
        if count >= settings["maxPlayersPerDevice"]:
            bs.broadcastmessage("Reached max players limit per device",
                                clients=[
                                    player.inputdevice.client_id],
                                transient=True, )
            return False
        return func(*args, **kwargs)

    return wrapper


Session.on_player_request = on_player_request(Session.on_player_request)


def on_access_check_response(self, data):
    if data is not None:
        addr = data['address']
        port = data['port']
        if settings["ballistica_web"]["enable"]:
            bs.set_public_party_stats_url(
                f'https://bombsquad-community.web.app/server-manager/?host={addr}&port={port}')

    servercontroller._access_check_response(self, data)


ServerController._access_check_response = on_access_check_response


def wrap_player_spaz_init(original_class):
    """
    Modify the __init__ method of the player_spaz.
    """

    class WrappedClass(original_class):
        def __init__(self, *args, **kwargs):
            # Custom code before the original __init__

            # Modify args or kwargs as needed
            player = args[0] if args else kwargs.get('player')
            character = args[3] if len(
                args) > 3 else kwargs.get('character', 'Spaz')

            # Modify the character value
            modified_character = modifyspaz.getCharacter(player, character)
            if len(args) > 3:
                args = args[:3] + (modified_character,) + args[4:]
            else:
                kwargs['character'] = modified_character

            # Call the original __init__
            super().__init__(*args, **kwargs)
            playerspaz_init(self, self.node, self._player)

    # Return the modified class
    return WrappedClass


playerspaz.PlayerSpaz = wrap_player_spaz_init(playerspaz.PlayerSpaz)

original_classic_app_mode_activate = ClassicAppMode.on_activate


def new_classic_app_mode_activate(*args, **kwargs):
    # Call the original function
    result = original_classic_app_mode_activate(*args, **kwargs)

    # Perform additional actions after the original function call
    on_classic_app_mode_active()

    return result


ClassicAppMode.on_activate = new_classic_app_mode_activate


def on_classic_app_mode_active():
    _bascenev1.set_server_name(settings["HostName"])
    _bascenev1.set_transparent_kickvote(settings["ShowKickVoteStarterName"])
    _bascenev1.set_kickvote_msg_type(settings["KickVoteMsgType"])
    _bascenev1.hide_player_device_id(settings["Anti-IdRevealer"])


def bcs_verify_client_account_ip(account_id: str, ip: str, client_id: int) -> str | None:
    """Verify a client account ID and IP address.
    """
    if settings["mfa"]["enable"]:
        _thread.start_new_thread(servercheck.account_check,
                                 (account_id, ip, client_id))


def player_entered_server(
    client_id: int,
    account_id: str,
    display_name: str,
    ip: str,
    device_id: str,
) -> bool | None:
    """Runs as soon as a player enters the server (after authentication is done).

    Return False to reject/disconnect the client, or True/None to allow.
    """

    try:
        from actor import welcome
        welcome.on_player_entered_server(client_id, display_name)
    except Exception as e:
        print(f"Error in player_entered_server welcome hook: {e}")

    return True
