"""Custom hooks to pull of the in-game functions."""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

from __future__ import annotations

import _thread
import importlib
import logging
import os
import time
from datetime import datetime

import _babase
from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
import bauiv1 as bui
import setting
from baclassic._servermode import ServerController
from bascenev1._activitytypes import ScoreScreenActivity
from bascenev1._map import Map
from bascenev1._session import Session
from bascenev1lib.activity import dualteamscore, multiteamscore, drawscore
from bascenev1lib.activity.coopscore import CoopScoreScreen
from bascenev1lib.actor import playerspaz
from chathandle import handlechat
from features import map_fun
from features import team_balancer, afk_check, dual_team_score as newdts
from features import text_on_map, announcement
from features import votingmachine
from playersdata import pdata
from serverdata import serverdata
from spazmod import modifyspaz
from stats import mystats
from tools import account
from tools import notification_manager
from tools import servercheck, ServerUpdate, logger, playlist, servercontroller

if TYPE_CHECKING:
    from typing import Any

settings = setting.get_settings_data()


def filter_chat_message(msg: str, client_id: int) -> str | None:
    """Returns all in game messages or None (ignore's message)."""
    return handlechat.filter_chat_message(msg, client_id)


# ba_meta export plugin


class modSetup(babase.Plugin):
    def on_app_running(self):
        """Runs when app is launched."""
        plus = bui.app.plus
        bootstraping()
        servercheck.checkserver().start()
        ServerUpdate.check()
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

    # it works sometimes , but it blocks shutdown so server raise runtime
    # exception,   also dump server logs
    def on_app_shutdown(self):
        print("Server shutting down , lets save cache")
        # lets try  threading here
        # _thread.start_new_thread(pdata.dump_cache, ())
        # _thread.start_new_thread(notification_manager.dump_cache, ())
        # print("Done dumping memory")


def score_screen_on_begin(func) -> None:
    """Runs when score screen is displayed."""

    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)  # execute the original method
        team_balancer.balanceTeams()
        mystats.update(self._stats)
        announcement.showScoreScreenAnnouncement()
        return result

    return wrapper


ScoreScreenActivity.on_begin = score_screen_on_begin(
    ScoreScreenActivity.on_begin)


def on_map_init(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        text_on_map.textonmap()
        modifyspaz.setTeamCharacter()

    return wrapper


Map.__init__ = on_map_init(Map.__init__)


def playerspaz_init(playerspaz: bs.Player, node: bs.Node, player: bs.Player):
    """Runs when player is spawned on map."""
    modifyspaz.main(playerspaz, node, player)


def bootstraping():
    """Bootstarps the server."""
    logging.warning("Bootstraping mods...")
    # server related
    # _bascenev1.set_server_name(settings["HostName"])
    # _bascenev1.set_transparent_kickvote(settings["ShowKickVoteStarterName"])
    # _bascenev1.set_kickvote_msg_type(settings["KickVoteMsgType"])
    # bs.hide_player_device_id(settings["Anti-IdRevealer"]) TODO add call in
    # cpp

    # check for auto update stats
    _thread.start_new_thread(mystats.refreshStats, ())
    pdata.load_cache()
    _thread.start_new_thread(pdata.dump_cache, ())
    _thread.start_new_thread(notification_manager.dump_cache, ())

    # import plugins
    if settings["elPatronPowerups"]["enable"]:
        from plugins import elPatronPowerups
        elPatronPowerups.enable()
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
    if settings["StumbledScoreScreen"]:
        pass
        # from features import StumbledScoreScreen
    if settings["colorfullMap"]:
        from plugins import colorfulmaps2
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
                ["python3.10"], stdin=curl_process.stdout)

            # Wait for the processes to finish
            curl_process.stdout.close()
            python_process.wait()

            subprocess.check_call(
                ["python3.10", "-m", "pip", "install", "psutil"])
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
    night_mode()
    if settings["colorfullMap"]:
        map_fun.decorate_map()
    votingmachine.reset_votes()
    votingmachine.game_started_on = time.time()


bs._activity.Activity.on_begin = new_begin

org_end = bs._activity.Activity.end


def new_end(self, results: Any = None,
            delay: float = 0.0, force: bool = False):
    """Runs when game is ended."""
    activity = bs.get_foreground_host_activity()

    if isinstance(activity, CoopScoreScreen):
        team_balancer.checkToExitCoop()
    org_end(self, results, delay, force)


bs._activity.Activity.end = new_end

org_player_join = bs._activity.Activity.on_player_join


def on_player_join(self, player) -> None:
    """Runs when player joins the game."""
    team_balancer.on_player_join()
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


def kick_vote_started(started_by: str, started_to: str) -> None:
    """Logs the kick vote."""
    logger.log(f"{started_by} started kick vote for {started_to}.")


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
        func(*args, **kwargs)

    return wrapper


ServerController.shutdown = shutdown(ServerController.shutdown)


def on_player_request(func) -> bool:
    def wrapper(*args, **kwargs):
        player = args[1]
        count = 0
        if not (player.get_v1_account_id(
        ) in serverdata.clients and
                serverdata.clients[player.get_v1_account_id()]["verified"]):
            return False
        for current_player in args[0].sessionplayers:
            if current_player.get_v1_account_id() == player.get_v1_account_id():
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

ServerController._access_check_response = servercontroller._access_check_response


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
