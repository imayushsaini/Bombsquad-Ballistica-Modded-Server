"""Module to update `setting.json`."""

# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import json
from functools import lru_cache

import _babase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

SETTINGS_PATH = _babase.env().get("python_directory_user", "") + "/setting.json"


@lru_cache(maxsize=None)
def get_settings_data() -> dict:
    """Returns the dictionary of settings related to the server.

    Returns
    -------
    dict
        settings related to server
    """
    with open(SETTINGS_PATH, mode="r", encoding="utf-8") as data:
        return json.load(data)


def refresh_cache() -> None:
    get_settings_data.cache_clear()
    # lets cache it again
    get_settings_data()


def commit(data: dict) -> None:
    """Commits the data in setting file.

    Parameters
    ----------
    data : dict
            data to be commited
    """
    with open(SETTINGS_PATH, mode="w", encoding="utf-8") as setting_file:
        json.dump(data, setting_file, indent=4)
    # settings updated ok now update the cache
    refresh_cache()
