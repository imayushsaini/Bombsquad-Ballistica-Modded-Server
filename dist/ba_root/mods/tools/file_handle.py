"""Module to handle operations with file."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)


from __future__ import annotations

__all__ = ["OpenJson", "JsonFile", "PathNotExistsError"]


from typing import TYPE_CHECKING
from dataclasses import dataclass

import json
import os
import re

from filelock import FileLock

if TYPE_CHECKING:
    pass


class PathNotExistsError(Exception):
    """Error telling path does not exits."""


@dataclass
class JsonFile:
    """Object to handle simple operations with json file."""

    path: str

    def load(self, **kw) -> dict:
        """Loads the json file."""
        if not os.path.exists(self.path):
            PathNotExistsError(f"Path does not exists. {self.path}")

        with FileLock(self.path):
            with open(self.path, mode="r", encoding="utf-8") as json_file:
                try:
                    data = json.load(json_file, **kw)
                except json.JSONDecodeError:
                    print(f"Could not load json. {self.path}", end="")
                    print("Creating json in the file.", end="")
                    data = {}
                    self.dump(data)
            return data

    def dump(self, data: dict, **kw) -> None:
        """Dumps the json file."""
        if not os.path.exists(self.path):
            PathNotExistsError(f"Path does not exists. {self.path}")

        with FileLock(self.path):
            with open(self.path, mode="w", encoding="utf-8") as json_file:
                json.dump(data, json_file, **kw)

    def format(self, data: dict) -> None:
        """Dumps the json file."""
        if not os.path.exists(self.path):
            PathNotExistsError(f"Path does not exists. {self.path}")

        with FileLock(self.path):
            output = json.dumps(data, indent=4)
            output2 = re.sub(r'": \[\s+', '": [', output)
            output3 = re.sub(r'",\s+', '", ', output2)
            output4 = re.sub(r'"\s+\]', '"]', output3)

            with open(self.path, mode="w", encoding="utf-8") as json_file:
                json_file.write(output4)


class OpenJson:
    """Context manager to open json files.

    Json files opened with this will be file locked. If
    json file is not readable then It will create new dict."""

    def __init__(self, path: str) -> None:
        self.json_obj = JsonFile(path)

    def __enter__(self) -> JsonFile:
        return self.json_obj

    def __exit__(self, _type, value, traceback):
        if traceback:
            print(traceback)
