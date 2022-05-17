"""Custom hooks to pull of the in-game functions."""

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)

# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

import _thread
import importlib
import time
import os
import ba
import _ba

from ba import _hooks
from bastd.activity import dualteamscore, multiteamscore, drawscore
from bastd.activity.coopscore import CoopScoreScreen
import setting

from chatHandle import handlechat
from features import team_balancer, afk_check, fire_flies, dual_team_score as newdts
from stats import mystats
from spazmod import modifyspaz
from tools import servercheck, ServerUpdate, logger
from playersData import pdata
from features import EndVote

if TYPE_CHECKING:
    from typing import Optional, Any

settings = setting.get_settings_data()


def filter_chat_message(msg: str, client_id: int) -> str | None:
    """Returns all in game messages or None (ignore's message)."""
    return handlechat.filter_chat_message(msg, client_id)


def on_app_launch() -> None:
    """Runs when app is launched."""
    bootstraping()
    servercheck.checkserver().start()
    ServerUpdate.check()

    if settings["afk_remover"]['enable']:
        afk_check.checkIdle().start()


def score_screen_on_begin(_stats: ba.Stats) -> None:
    """Runs when score screen is displayed."""
    team_balancer.balanceTeams()
    mystats.update(_stats)


def playerspaz_init(playerspaz: ba.Player, node: ba.Node, player: ba.Player):
    """Runs when player is spawned on map."""
    modifyspaz.main(playerspaz, node, player)


def bootstraping():
    """Bootstarps the server."""
    # server related
    _ba.set_server_device_name(settings["HostDeviceName"])
    _ba.set_server_name(settings["HostName"])
    _ba.set_transparent_kickvote(settings["ShowKickVoteStarterName"])
    _ba.set_kickvote_msg_type(settings["KickVoteMsgType"])

    # check for auto update stats
    _thread.start_new_thread(mystats.refreshStats, ())
    pdata.load_cache()
    _thread.start_new_thread(pdata.dump_cache, ())

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
        bcs_plugin.enable()
    if settings["character_chooser"]["enable"]:
        from plugins import CharacterChooser
        CharacterChooser.enable()
    if settings["custom_characters"]["enable"]:
        from plugins import importcustomcharacters
        importcustomcharacters.enable()
    if settings["StumbledScoreScreen"]:
        from features import StumbledScoreScreen

    # import features
    if settings["whitelist"]:
        pdata.load_white_list()

    import_discord_bot()
    import_games()
    import_dual_team_score()


def import_discord_bot() -> None:
    """Imports the discord bot."""
    if settings["discordbot"]["enable"]:
        from features import discord_bot
        discord_bot.token = settings["discordbot"]["token"]
        discord_bot.liveStatsChannelID = settings["discordbot"]["liveStatsChannelID"]
        discord_bot.logsChannelID = settings["discordbot"]["logsChannelID"]
        discord_bot.liveChat = settings["discordbot"]["liveChat"]
        discord_bot.BsDataThread()
        discord_bot.init()


def import_games():
    """Imports the custom games from games directory."""
    import sys
    sys.path.append(_ba.env()['python_directory_user'] + os.sep + "games")
    games = os.listdir("ba_root/mods/games")
    for game in games:
        if game.endswith(".so"):
            importlib.import_module("games." + game.replace(".so", ""))

    maps = os.listdir("ba_root/mods/maps")
    for _map in maps:
        if _map.endswith(".py") or _map.endswith(".so"):
            importlib.import_module("maps." + _map.replace(".so", "").replace(".py", ""))


def import_dual_team_score() -> None:
    """Imports the dual team score."""
    if settings["newResultBoard"]:
        dualteamscore.TeamVictoryScoreScreenActivity = newdts.TeamVictoryScoreScreenActivity
        multiteamscore.MultiTeamScoreScreenActivity.show_player_scores = newdts.show_player_scores
        drawscore.DrawScoreScreenActivity = newdts.DrawScoreScreenActivity


org_begin = ba._activity.Activity.on_begin


def new_begin(self):
    """Runs when game is began."""
    org_begin(self)
    night_mode()
    EndVote.voters = []
    EndVote.game_started_on = time.time()


ba._activity.Activity.on_begin = new_begin

org_end = ba._activity.Activity.end


def new_end(self, results: Any = None, delay: float = 0.0, force: bool = False):
    """Runs when game is ended."""
    activity = _ba.get_foreground_host_activity()
    if isinstance(activity, CoopScoreScreen):
        team_balancer.checkToExitCoop()
    org_end(self, results, delay, force)


ba._activity.Activity.end = new_end

org_player_join = ba._activity.Activity.on_player_join


def on_player_join(self, player) -> None:
    """Runs when player joins the game."""
    team_balancer.on_player_join()
    org_player_join(self, player)


ba._activity.Activity.on_player_join = on_player_join


def night_mode() -> None:
    """Checks the time and enables night mode."""

    if settings['autoNightMode']['enable']:

        start = datetime.strptime(settings['autoNightMode']['startTime'], "%H:%M")
        end = datetime.strptime(settings['autoNightMode']['endTime'], "%H:%M")
        now = datetime.now()

        if now.time() > start.time() or now.time() < end.time():
            activity = _ba.get_foreground_host_activity()

            activity.globalsnode.tint = (0.5, 0.7, 1.0)

            if settings['autoNightMode']['fireflies']:
                fire_flies.factory(settings['autoNightMode']["fireflies_random_color"])


def kick_vote_started(started_by: str, started_to: str) -> None:
    """Logs the kick vote."""
    logger.log(f"{started_by} started kick vote for {started_to}.")


def on_kicked(account_id: str) -> None:
    """Runs when someone is kicked by kickvote."""
    logger.log(f"{account_id} kicked by kickvotes.")


def on_kick_vote_end():
    """Runs when kickvote is ended."""
    logger.log("Kick vote End")


_hooks.kick_vote_started = kick_vote_started
_hooks.on_kicked = on_kicked
