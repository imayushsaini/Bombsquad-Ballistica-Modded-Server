# Released under the MIT License. See LICENSE for details.

import fcntl
import _ba
import os
clients = {}
cachedclients = []
muted = False
coopmode = False
ips = {}
recents = []


SERVER_DATA_PATH = os.path.join(
    _ba.env()["python_directory_user"], "serverData" + os.sep
)


def get_stats_index():
    return [x for x in os.listdir(SERVER_DATA_PATH) if "log" in x]


def read_logs(filename):
    file_path = SERVER_DATA_PATH+filename
    if not os.path.exists(file_path):
        return ""
    file = open(file_path, "r")
    fcntl.flock(file.fileno(), fcntl.LOCK_SH)
    contents = ""
    try:
        contents = file.read()

    finally:
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)
        file.close()

    return contents
