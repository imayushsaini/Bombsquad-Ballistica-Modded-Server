# ba_meta require api 8
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.game.deathmatch import DeathMatchGame

if TYPE_CHECKING:
    from typing import Sequence

lang = bs.app.lang.language

if lang == 'Spanish':
    name = 'Super Boxeo'
    description = ('¡Sin bombas!\n'
                   '¡Noquea a los enemigos con tus propias manos!\n')
    super_jump_text = 'Super Salto'
    enable_powerups = 'Habilitar Potenciadores'
else:
    name = 'Super Boxing'
    description = ('No bombs!\n'
                   'Knock out your enemies using your bare hands!\n')
    super_jump_text = 'Super Jump'
    enable_powerups = 'Enable Powerups'


class NewPlayerSpaz(PlayerSpaz):

    def __init__(self,
                 player: bs.Player,
                 color: Sequence[float] = (1.0, 1.0, 1.0),
                 highlight: Sequence[float] = (0.5, 0.5, 0.5),
                 character: str = 'Spaz',
                 powerups_expire: bool = True,
                 super_jump: bool = False):
        super().__init__(player=player,
                         color=color,
                         highlight=highlight,
                         character=character,
                         powerups_expire=powerups_expire)
        from bascenev1lib.gameutils import SharedObjects
        shared = SharedObjects.get()
        self._super_jump = super_jump
        self.jump_mode = False
        self.super_jump_material = bs.Material()
        self.super_jump_material.add_actions(
            conditions=('they_have_material', shared.footing_material),
            actions=(
                ('call', 'at_connect', babase.Call(self.jump_state, True)),
                ('call', 'at_disconnect', babase.Call(self.jump_state, False))
            ),
        )
        self.node.roller_materials += (self.super_jump_material,)

    def jump_state(self, mode: bool) -> None:
        self.jump_mode = mode

    def on_jump_press(self) -> None:
        """
        Called to 'press jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node:
            return
        t_ms = int(bs.time() * 1000.0)
        assert isinstance(t_ms, int)
        if t_ms - self.last_jump_time_ms >= self._jump_cooldown:
            self.node.jump_pressed = True
            self.last_jump_time_ms = t_ms
            if self._player.is_alive() and self.jump_mode and (
                self._super_jump):
                def do_jump():
                    self.node.handlemessage(
                        'impulse',
                        self.node.position[0],
                        self.node.position[1],
                        self.node.position[2],
                        0, 0, 0, 95, 95, 0, 0, 0, 1, 0
                    )

                bs.timer(0.0, do_jump)
                bs.timer(0.1, do_jump)
                bs.timer(0.2, do_jump)
        self._turbo_filter_add_press('jump')


# ba_meta export bascenev1.GameActivity
class BoxingGame(DeathMatchGame):
    name = name
    description = description

    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[babase.Setting]:
        settings = [
            bs.IntSetting(
                'Kills to Win Per Player',
                min_value=1,
                default=5,
                increment=1,
            ),
            bs.IntChoiceSetting(
                'Time Limit',
                choices=[
                    ('None', 0),
                    ('1 Minute', 60),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600),
                    ('20 Minutes', 1200),
                ],
                default=0,
            ),
            bs.FloatChoiceSetting(
                'Respawn Times',
                choices=[
                    ('Shorter', 0.25),
                    ('Short', 0.5),
                    ('Normal', 1.0),
                    ('Long', 2.0),
                    ('Longer', 4.0),
                ],
                default=1.0,
            ),
            bs.BoolSetting(super_jump_text, default=False),
            bs.BoolSetting(enable_powerups, default=False),
            bs.BoolSetting('Epic Mode', default=False),
        ]

        # In teams mode, a suicide gives a point to the other team, but in
        # free-for-all it subtracts from your own score. By default we clamp
        # this at zero to benefit new players, but pro players might like to
        # be able to go negative. (to avoid a strategy of just
        # suiciding until you get a good drop)
        if issubclass(sessiontype, bs.FreeForAllSession):
            settings.append(
                bs.BoolSetting('Allow Negative Scores', default=False)
            )

        return settings

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: int | None = None
        self._dingsound = bs.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(settings['Kills to Win Per Player'])
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False)
        )
        self._super_jump = bool(settings[super_jump_text])
        self._enable_powerups = bool(settings[enable_powerups])

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.TO_THE_DEATH
        )

    def on_begin(self) -> None:
        bs.TeamGameActivity.on_begin(self)
        self.setup_standard_time_limit(self._time_limit)
        if self._enable_powerups:
            self.setup_standard_powerup_drops()

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = self._kills_to_win_per_player * max(
            1, max(len(t.players) for t in self.teams)
        )
        self._update_scoreboard()

    def _standard_drop_powerup(self, index: int, expire: bool = True) -> None:
        # pylint: disable=cyclic-import
        from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory

        PowerupBox(
            position=self.map.powerup_spawn_points[index],
            poweruptype=PowerupBoxFactory.get().get_random_powerup_type(
                excludetypes=['triple_bombs', 'ice_bombs', 'impact_bombs',
                              'land_mines', 'sticky_bombs', 'punch']
            ),
            expire=expire,
        ).autoretain()

    def spawn_player(self, player: Player) -> bs.Actor:
        import random
        from babase import _math
        from bascenev1._gameutils import animate

        if isinstance(self.session, bs.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            # otherwise do free-for-all spawn locations
            position = self.map.get_ffa_start_position(self.players)
        angle = None
        name = player.getname()
        color = player.color
        highlight = player.highlight

        light_color = _math.normalized_color(color)
        display_color = babase.safecolor(color, target_intensity=0.75)

        spaz = NewPlayerSpaz(color=color,
                             highlight=highlight,
                             character=player.character,
                             player=player,
                             super_jump=self._super_jump)

        player.actor = spaz
        assert spaz.node

        spaz.node.name = name
        spaz.node.name_color = display_color

        # Move to the stand position and add a flash of light.
        spaz.handlemessage(
            bs.StandMessage(
                position,
                angle if angle is not None else random.uniform(0, 360)))
        self._spawn_sound.play(1, position=spaz.node.position)
        light = bs.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        bs.timer(0.5, light.delete)

        # custom
        spaz.connect_controls_to_player(enable_bomb=False)
        spaz.equip_boxing_gloves()

        return spaz
