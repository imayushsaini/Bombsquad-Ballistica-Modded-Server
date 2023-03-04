# Released under the MIT License. See LICENSE for details.
#
"""Elimination mini-game."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba,_ba
from bastd.actor.spazfactory import SpazFactory
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects
if TYPE_CHECKING:
    from typing import Any, Sequence, Optional, Union
import random
from games.lib import Player,Team,Icon,eli
from bastd.game.elimination import EliminationGame

# ba_meta export game
class BlockDashGame(EliminationGame):
    """Game type where last player(s) left alive win."""

    name = 'Block Dash'
    description = 'Last remaining alive wins.'
    scoreconfig = ba.ScoreConfig(label='Survived',
                                 scoretype=ba.ScoreType.SECONDS,
                                 none_is_winner=True)
    # Show messages when players die since it's meaningful here.
    announce_player_deaths = True

    allow_mid_activity_joins = False



    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ["Wooden Floor"]

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared=SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._start_time: Optional[float] = None
        self._vs_text: Optional[ba.Actor] = None
        self._round_end_timer: Optional[ba.Timer] = None
        self._epic_mode = bool(settings['Epic Mode'])
        self._lives_per_player =1
        self._time_limit = float(settings['Time Limit'])
        self._balance_total_lives = bool(
            settings.get('Balance Total Lives', False))
        self._solo_mode = bool(settings.get('Solo Mode', False))

        # Base class overrides:
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC
                              if self._epic_mode else ba.MusicType.SURVIVAL)
        self.laser_material=ba.Material()
        self.laser_material.add_actions(
            conditions=('they_have_material',
                        shared.player_material),
            actions=(('modify_part_collision', 'collide',True),
                    ('message','their_node','at_connect',ba.DieMessage()))
            )


    def get_instance_description(self) -> Union[str, Sequence]:
        return 'Last team standing wins.' if isinstance(
            self.session, ba.DualTeamSession) else 'Last one standing wins.'

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return 'last team standing wins' if isinstance(
            self.session, ba.DualTeamSession) else 'last one standing wins'

    def on_player_join(self, player: Player) -> None:
        player.lives = self._lives_per_player

        if self._solo_mode:
            player.team.spawn_order.append(player)
            self._update_solo_mode()
        else:
            # Create our icon and spawn.
            # player.icons = [Icon(player, position=(0, 50), scale=0.8)]
            if player.lives > 0:
                self.spawn_player(player)

        # Don't waste time doing this until begin.
        if self.has_begun():
            self._update_icons()

    def on_begin(self) -> None:
        super().on_begin()
        self._start_time = ba.time()
        self.setup_standard_time_limit(self._time_limit)
        # self.setup_standard_powerup_drops()
        self.add_wall()

        if self._solo_mode:
            self._vs_text = ba.NodeActor(
                ba.newnode('text',
                           attrs={
                               'position': (0, 105),
                               'h_attach': 'center',
                               'h_align': 'center',
                               'maxwidth': 200,
                               'shadow': 0.5,
                               'vr_depth': 390,
                               'scale': 0.6,
                               'v_attach': 'bottom',
                               'color': (0.8, 0.8, 0.3, 1.0),
                               'text': ba.Lstr(resource='vsText')
                           }))

        # If balance-team-lives is on, add lives to the smaller team until
        # total lives match.
        if (isinstance(self.session, ba.DualTeamSession)
                and self._balance_total_lives and self.teams[0].players
                and self.teams[1].players):
            if self._get_total_team_lives(
                    self.teams[0]) < self._get_total_team_lives(self.teams[1]):
                lesser_team = self.teams[0]
                greater_team = self.teams[1]
            else:
                lesser_team = self.teams[1]
                greater_team = self.teams[0]
            add_index = 0
            while (self._get_total_team_lives(lesser_team) <
                   self._get_total_team_lives(greater_team)):
                lesser_team.players[add_index].lives += 1
                add_index = (add_index + 1) % len(lesser_team.players)

        self._update_icons()

        # We could check game-over conditions at explicit trigger points,
        # but lets just do the simple thing and poll it.
        ba.timer(1.0, self._update, repeat=True)

    def _update_solo_mode(self) -> None:
        # For both teams, find the first player on the spawn order list with
        # lives remaining and spawn them if they're not alive.
        for team in self.teams:
            # Prune dead players from the spawn order.
            team.spawn_order = [p for p in team.spawn_order if p]
            for player in team.spawn_order:
                assert isinstance(player, Player)
                if player.lives > 0:
                    if not player.is_alive():
                        self.spawn_player(player)
                    break

    def _update_icons(self) -> None:
        return
        # lets do nothing ;Eat 5 Star

    def _get_spawn_point(self, player: Player) -> Optional[ba.Vec3]:
        del player  # Unused.

        # In solo-mode, if there's an existing live player on the map, spawn at
        # whichever spot is farthest from them (keeps the action spread out).
        if self._solo_mode:
            living_player = None
            living_player_pos = None
            for team in self.teams:
                for tplayer in team.players:
                    if tplayer.is_alive():
                        assert tplayer.node
                        ppos = tplayer.node.position
                        living_player = tplayer
                        living_player_pos = ppos
                        break
            if living_player:
                assert living_player_pos is not None
                player_pos = ba.Vec3(living_player_pos)
                points: list[tuple[float, ba.Vec3]] = []
                for team in self.teams:
                    start_pos = ba.Vec3(self.map.get_start_position(team.id))
                    points.append(
                        ((start_pos - player_pos).length(), start_pos))
                # Hmm.. we need to sorting vectors too?
                points.sort(key=lambda x: x[0])
                return points[-1][1]
        return None

    def spawn_player(self, player: Player) -> ba.Actor:
        p=[-6,-4.3,-2.6,-0.9,0.8,2.5,4.2,5.9]
        q=[-4,-2.3,-0.6,1.1,2.8,4.5]

        x=random.randrange(0,len(p))
        y=random.randrange(0,len(q))
        actor = self.spawn_player_spaz(player, position=(0,1.8,0))
        actor.connect_controls_to_player(enable_punch=False,
                                        enable_bomb=False,
                                        enable_pickup=False)
        if not self._solo_mode:
            ba.timer(0.3, ba.Call(self._print_lives, player))

        # If we have any icons, update their state.
        for icon in player.icons:
            icon.handle_player_spawned()
        return actor

    def _print_lives(self, player: Player) -> None:
        from bastd.actor import popuptext

        # We get called in a timer so it's possible our player has left/etc.
        if not player or not player.is_alive() or not player.node:
            return

        popuptext.PopupText('x' + str(player.lives - 1),
                            color=(1, 1, 0, 1),
                            offset=(0, -0.8, 0),
                            random_offset=0.0,
                            scale=1.8,
                            position=player.node.position).autoretain()

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
        player.icons = []

        # Remove us from spawn-order.
        if self._solo_mode:
            if player in player.team.spawn_order:
                player.team.spawn_order.remove(player)

        # Update icons in a moment since our team will be gone from the
        # list then.
        ba.timer(0, self._update_icons)

        # If the player to leave was the last in spawn order and had
        # their final turn currently in-progress, mark the survival time
        # for their team.
        if self._get_total_team_lives(player.team) == 0:
            assert self._start_time is not None
            player.team.survival_seconds = int(ba.time() - self._start_time)

    def _get_total_team_lives(self, team: Team) -> int:
        return sum(player.lives for player in team.players)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)
            player: Player = msg.getplayer(Player)

            player.lives -= 1
            if player.lives < 0:
                ba.print_error(
                    "Got lives < 0 in Elim; this shouldn't happen. solo:" +
                    str(self._solo_mode))
                player.lives = 0

            # If we have any icons, update their state.
            for icon in player.icons:
                icon.handle_player_died()

            # Play big death sound on our last death
            # or for every one in solo mode.
            if self._solo_mode or player.lives == 0:
                ba.playsound(SpazFactory.get().single_player_death_sound)

            # If we hit zero lives, we're dead (and our team might be too).
            if player.lives == 0:
                # If the whole team is now dead, mark their survival time.
                if self._get_total_team_lives(player.team) == 0:
                    assert self._start_time is not None
                    player.team.survival_seconds = int(ba.time() -
                                                       self._start_time)
            else:
                # Otherwise, in regular mode, respawn.
                if not self._solo_mode:
                    self.respawn_player(player)

            # In solo, put ourself at the back of the spawn order.
            if self._solo_mode:
                player.team.spawn_order.remove(player)
                player.team.spawn_order.append(player)

    def _update(self) -> None:
        if self._solo_mode:
            # For both teams, find the first player on the spawn order
            # list with lives remaining and spawn them if they're not alive.
            for team in self.teams:
                # Prune dead players from the spawn order.
                team.spawn_order = [p for p in team.spawn_order if p]
                for player in team.spawn_order:
                    assert isinstance(player, Player)
                    if player.lives > 0:
                        if not player.is_alive():
                            self.spawn_player(player)
                            self._update_icons()
                        break

        # If we're down to 1 or fewer living teams, start a timer to end
        # the game (allows the dust to settle and draws to occur if deaths
        # are close enough).
        if len(self._get_living_teams()) < 2:
            self._round_end_timer = ba.Timer(0.5, self.end_game)

    def _get_living_teams(self) -> list[Team]:
        return [
            team for team in self.teams
            if len(team.players) > 0 and any(player.lives > 0
                                             for player in team.players)
        ]

    def end_game(self) -> None:
        if self.has_ended():
            return
        results = ba.GameResults()
        self._vs_text = None  # Kill our 'vs' if its there.
        for team in self.teams:
            results.set_team_score(team, team.survival_seconds)
        self.end(results=results)
    def add_wall(self):
        # FIXME: Chop this into vr and non-vr chunks.

        shared = SharedObjects.get()
        pwm=ba.Material()
        cwwm=ba.Material()
        # pwm.add_actions(
        #     actions=('modify_part_collision', 'friction', 0.0))
        # anything that needs to hit the wall should apply this.

        pwm.add_actions(
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
            ))
        self.mat = ba.Material()
        self.mat.add_actions(

            actions=( ('modify_part_collision','physical',False),
                      ('modify_part_collision','collide',False))
            )

        ud_1_r=ba.newnode('region',attrs={'position': (-2,0,-4),'scale': (14.5,1,14.5),'type': 'box','materials': [shared.footing_material,pwm ]})

        node = ba.newnode('prop',
                                    owner=ud_1_r,
                                    attrs={
                                    'model':ba.getmodel('image1x1'),
                                    'light_model':ba.getmodel('powerupSimple'),
                                    'position':(2,7,2),
                                    'body':'puck',
                                    'shadow_size':0.0,
                                    'velocity':(0,0,0),
                                    'color_texture':ba.gettexture('flagColor'),
                                    'model_scale':14.5,
                                    'reflection_scale':[1.5],
                                    'materials':[self.mat, shared.object_material,shared.footing_material],
                                    })
        mnode = ba.newnode('math',
                               owner=ud_1_r,
                               attrs={
                                   'input1': (0, 0.7, 0),
                                   'operation': 'add'
                               })

        node.changerotation(1,0,0)

        ud_1_r.connectattr('position', mnode, 'input2')
        mnode.connectattr('output', node, 'position')
        ba.timer(8,ba.Call(self.create_block_wall_easy))
        self.gate_count=4
        self.wall_count=0

    def create_wall(self):
        x=-9
        for i in range(0,17):
            self.create_block(x,0.5)
            self.create_block(x,1.2)
            x=x+0.85

    def create_block_wall_hardest(self):
        x=-3

        for i in range(0,7):
            self.create_block(x,0.4)
            x=x+0.85
        ba.timer(1.5,ba.Call(self.create_wall))
        ba.timer(15,ba.Call(self.create_block_wall_hardest))

    def create_block_wall_hard(self):
        x=-9
        self.wall_count+=1
        for i in range(0,17):
            self.create_block(x,0.4)
            x=x+0.85
        if self.wall_count <4:
            ba.timer(12,ba.Call(self.create_block_wall_hard))
        else:
            ba.timer(7,ba.Call(self.create_block_wall_hard))  #hardest too heavy to play


    def create_block_wall_easy(self):
        x=-9
        c=0
        for i in range(0,17):
            if random.randrange(0,2) and c<self.gate_count:
                pass
            else:
                self.create_block(x,0.5)
                c+=1
            x=x+0.85
        self.wall_count+=1
        if self.wall_count < 5:
            ba.timer(11,ba.Call(self.create_block_wall_easy))
        else:
            self.wall_count=0
            ba.timer(15,ba.Call(self.create_block_wall_hard))



    def create_block(self,x,y):

        shared = SharedObjects.get()
        pwm=ba.Material()
        cwwm=ba.Material()
        # pwm.add_actions(
        #     actions=('modify_part_collision', 'friction', 0.0))
        # anything that needs to hit the wall should apply this.

        pwm.add_actions(
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
            ))
        self.mat = ba.Material()
        self.mat.add_actions(

            actions=( ('modify_part_collision','physical',False),
                      ('modify_part_collision','collide',False))
            )
        cmodel = ba.getcollidemodel('courtyardPlayerWall')
        ud_1_r=ba.newnode('region',attrs={'position': (x,y,-13),'scale': (1,1.5,1),'type': 'box','materials': [shared.footing_material,pwm ]})

        node = ba.newnode('prop',
                                    owner=ud_1_r,
                                    attrs={
                                    'model':ba.getmodel('tnt'),
                                    'light_model':ba.getmodel('powerupSimple'),
                                    'position':(2,7,2),
                                    'body':'puck',
                                    'shadow_size':0.0,
                                    'velocity':(0,0,0),
                                    'color_texture':ba.gettexture('tnt'),
                                    'model_scale':1.2,
                                    'reflection_scale':[1.5],
                                    'materials':[self.mat, shared.object_material,shared.footing_material],

                                    'density':9000000000
                                    })
        mnode = ba.newnode('math',
                               owner=ud_1_r,
                               attrs={
                                   'input1': (0, 0.5, 0),
                                   'operation': 'add'
                               })

        node.changerotation(1,0,0)

        ud_1_r.connectattr('position', mnode, 'input2')
        mnode.connectattr('output', node, 'position')
        _rcombine=ba.newnode('combine',
                                   owner=ud_1_r,
                                   attrs={
                                       'input0':x,
                                       'input1':y,
                                       'size':3
                                   })
        ba.animate(_rcombine,'input2',{
                0:-12,
                11:4
            })
        _rcombine.connectattr('output',ud_1_r,'position')

        ba.timer(11,ba.Call(ud_1_r.delete))


