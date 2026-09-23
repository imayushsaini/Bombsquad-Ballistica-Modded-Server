"""Avalancha mini-game."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
import random
from typing import TYPE_CHECKING

import babase
import bauiv1 as bui
import bascenev1 as bs
from bascenev1lib.actor.bomb import Bomb
from bascenev1lib.actor.onscreentimer import OnScreenTimer
from bascenev1lib.game.meteorshower import *
from bascenev1lib.actor.spazbot import *
from bascenev1lib.actor.spaz import PunchHitMessage
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence, Optional, List, Dict, Type, Type

## MoreMinigames.py support ##
randomPic = ["lakeFrigidPreview", "hockeyStadiumPreview"]


def ba_get_api_version():
    return 9


def ba_get_levels():
    return [
        bs.Level(
            "Icy Emits",
            gametype=IcyEmitsGame,
            settings={},
            preview_texture_name=random.choice(randomPic),
        )
    ]


## MoreMinigames.py support ##


class PascalBot(BrawlerBot):
    color = (0, 0, 3)
    highlight = (0.2, 0.2, 1)
    character = "Pascal"
    bouncy = True
    punchiness = 0.7

    def handlemessage(self, msg: Any) -> Any:
        assert not self.expired
        if isinstance(msg, bs.FreezeMessage):
            return
        else:
            super().handlemessage(msg)


# ba_meta export bascenev1.GameActivity
class AvalanchaGame(MeteorShowerGame):
    """Minigame involving dodging falling bombs."""

    name = "Avalanche"
    description = "Dodge the ice-bombs."
    available_settings = [
        bs.BoolSetting("Epic Mode", default=False),
        bs.IntSetting("Difficulty", default=1, min_value=1, max_value=3, increment=1),
    ]
    scoreconfig = bs.ScoreConfig(
        label="Survived", scoretype=bs.ScoreType.MILLISECONDS, version="B"
    )

    announce_player_deaths = True

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return ["Tip Top"]

    def __init__(self, settings: dict):
        super().__init__(settings)

        self._epic_mode = settings.get("Epic Mode", False)
        self._last_player_death_time: Optional[float] = None
        self._meteor_time = 2.0
        if settings["Difficulty"] == 1:
            self._min_delay = 0.4
        elif settings["Difficulty"] == 2:
            self._min_delay = 0.3
        else:
            self._min_delay = 0.1

        self._timer: Optional[OnScreenTimer] = None
        self._bots = SpazBotSet()

        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.SURVIVAL
        )
        if self._epic_mode:
            self.slow_motion = True

    def on_transition_in(self) -> None:
        super().on_transition_in()
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.5, 0.5, 1)

        act = bs.getactivity().map
        shared = SharedObjects.get()
        mat = bs.Material()
        mat.add_actions(actions=("modify_part_collision", "friction", 0.18))

        act.node.color = act.bottom.color = (1, 1, 1.2)
        act.node.reflection = act.bottom.reflection = "soft"
        act.node.materials = [shared.footing_material, mat]

    def _set_meteor_timer(self) -> None:
        bs.timer(
            (1.0 + 0.2 * random.random()) * self._meteor_time, self._drop_bomb_cluster
        )

    def _drop_bomb_cluster(self) -> None:
        defs = self.map.defs
        delay = 0.0
        for _i in range(random.randrange(1, 3)):
            pos = defs.points["flag_default"]
            pos = (pos[0], pos[1] + 0.4, pos[2])
            dropdir = -1.0 if pos[0] > 0 else 1.0
            vel = (random.randrange(-4, 4), 7.0, random.randrange(0, 4))
            bs.timer(delay, babase.CallPartial(self._drop_bomb, pos, vel))
            delay += 0.1
        self._set_meteor_timer()

    def _drop_bomb(self, position: Sequence[float], velocity: Sequence[float]) -> None:
        Bomb(position=position, velocity=velocity, bomb_type="ice").autoretain()

    def _decrement_meteor_time(self) -> None:
        if self._meteor_time < self._min_delay:
            return
        self._meteor_time = max(0.01, self._meteor_time * 0.9)
        if random.choice([0, 0, 1]) == 1:
            pos = self.map.defs.points["flag_default"]
            self._bots.spawn_bot(PascalBot, pos=pos, spawn_time=2)
