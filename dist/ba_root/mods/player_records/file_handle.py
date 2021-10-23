"""A module to provide helper functions operations regarding files."""

from __future__ import annotations
from functools import lru_cache
import json


@lru_cache(maxsize=None)
def read(path: str) -> dict | None:
    """Return the loaded json data of given path."""
    with open(path, mode="r") as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            print(f"could not load {path} file as json.")
            return None
        except FileNotFoundError:
            return None


def write(path: str, data: dict) -> None:
    """Writes a dictionary data into json file."""
    try:
        with open(path, mode="w") as file:
            json.dump(data, file, indent=2)
    except FileNotFoundError:
        pass
