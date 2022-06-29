"""Module to Keeps the log of multiple things."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass, field

import os
import datetime
import threading
import setting
import _ba

if TYPE_CHECKING:
    pass


SETTINGS = setting.get_settings_data()
SERVER_DATA_PATH = os.path.join(
    _ba.env()["python_directory_user"], "serverData" + os.sep
)


if SETTINGS["discordbot"]["enable"]:
    from features import discord_bot


@dataclass
class RecentLogs:
    """Saves the recent logs."""

    chats: list[str] = field(default_factory=list)
    joinlog: list[str] = field(default_factory=list)
    cmndlog: list[str] = field(default_factory=list)
    misclogs: list[str] = field(default_factory=list)

logs = RecentLogs()

def log(msg: str, mtype: str = "sys") -> None:
    """Cache and dumps the log."""

    if SETTINGS["discordbot"]["enable"]:
        message = msg.replace("||", "|")
        discord_bot.push_log("***" + mtype + ":***" + message)

    current_time = datetime.datetime.now()
    msg = f"{current_time} + : {msg} \n"

    if mtype == "chat":
        logs.chats.append(msg)
        if len(logs.chats) > 10:
            dumplogs(logs.chats, "chat").start()
            logs.chats = []

    elif mtype == "playerjoin":
        logs.joinlog.append(msg)
        if len(logs.joinlog) > 3:
            dumplogs(logs.joinlog, "joinlog").start()
            logs.joinlog = []

    elif mtype == "chatcmd":
        logs.cmndlog.append(msg)
        if len(logs.cmndlog) > 3:
            dumplogs(logs.cmndlog, "cmndlog").start()
            logs.cmndlog = []

    else:
        logs.misclogs.append(msg)
        if len(logs.misclogs) > 5:
            dumplogs(logs.misclogs, "sys").start()
            logs.misclogs = []


class dumplogs(threading.Thread):
    """Dumps the logs in the server data."""

    def __init__(self, msg, mtype="sys"):
        super().__init__()
        self.msg = msg
        self.type = mtype

    def run(self):

        if self.type == "chat":
            log_path = SERVER_DATA_PATH + "Chat Logs.log"
        elif self.type == "joinlog":
            log_path = SERVER_DATA_PATH + "joining.log"
        elif self.type == "cmndlog":
            log_path = SERVER_DATA_PATH + "cmndusage.log"
        else:
            log_path = SERVER_DATA_PATH + "logs.log"

        with open(log_path, mode="a+", encoding="utf-8") as file:
            for msg in self.msg:
                file.write(msg)
