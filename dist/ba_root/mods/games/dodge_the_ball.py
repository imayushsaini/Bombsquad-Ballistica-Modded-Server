"""

    DondgeTheBall minigame by EmperoR#4098

"""

# Feel free to edit.

# ba_meta require api 8
from __future__ import annotations

from enum import Enum
from random import choice

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1lib.actor.bomb import Blast
from bascenev1lib.actor.onscreencountdown import OnScreenCountdown
from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.actor.powerupbox import PowerupBox
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import NoReturn, Sequence, Any


# Type of ball in this game
class BallType(Enum):
    """ Types of ball """
    EASY = 0
    # Decrease the next ball shooting speed(not ball speed).
    # Ball color is yellow.
    MEDIUM = 1
    # increase the next ball shooting speed(not ball speed).
    # target the head of player.
    # Ball color is purple.
    HARD = 2
    # Target player according to player movement (not very accurate).
    # Taget: player head.
    # increase the next ball speed but less than MEDIUM.
    # Ball color is crimson(purple+red = pinky color type).


# this dict decide the ball_type spawning rate like powerup box
ball_type_dict: dict[BallType, int] = {
    BallType.EASY: 3,
    BallType.MEDIUM: 2,
    BallType.HARD: 1,
}


class Ball(bs.Actor):
    """ Shooting Ball """

    def __init__(self,
                 position: Sequence[float],
                 velocity: Sequence[float],
                 texture: babase.Texture,
                 body_scale: float = 1.0,
                 gravity_scale: float = 1.0,
                 ) -> NoReturn:

        super().__init__()

        shared = SharedObjects.get()

        ball_material = bs.Material()
        ball_material.add_actions(
            conditions=(
                (
                    ('we_are_younger_than', 100),
                    'or',
                    ('they_are_younger_than', 100),
                ),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'body': 'sphere',
                'position': position,
                'velocity': velocity,
                'body_scale': body_scale,
                'mesh': bs.getmesh('frostyPelvis'),
                'mesh_scale': body_scale,
                'color_texture': texture,
                'gravity_scale': gravity_scale,
                'density': 4.0,
                # increase density of ball so ball collide with player with heavy force. # ammm very bad grammer
                'materials': (ball_material,),
            },
        )

        # die the ball manually incase the ball doesn't fall the outside of the map
        bs.timer(2.5, bs.WeakCall(self.handlemessage, bs.DieMessage()))

    # i am not handling anything in this ball Class(except for diemessage).
    # all game things and logics going to be in the box class
    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.DieMessage):
            self.node.delete()
        else:
            super().handlemessage(msg)


class Box(bs.Actor):
    """ A box that spawn midle of map as a decoration perpose """

    def __init__(self,
                 position: Sequence[float],
                 velocity: Sequence[float],
                 ) -> NoReturn:

        super().__init__()

        shared = SharedObjects.get()
        # self.ball_jump = 0.0;
        no_hit_material = bs.Material()
        # we don't need that the box was move and collide with objects.
        no_hit_material.add_actions(
            conditions=(
                ('they_have_material', shared.pickup_material),
                'or',
                ('they_have_material', shared.attack_material),
            ),
            actions=('modify_part_collision', 'collide', False),
        )

        no_hit_material.add_actions(
            conditions=(
                ('they_have_material', shared.object_material),
                'or',
                ('they_dont_have_material', shared.footing_material),
            ),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
            ),
        )

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'body': 'box',
                'position': position,
                'mesh': bs.getmesh('powerup'),
                'light_mesh': bs.getmesh('powerupSimple'),
                'shadow_size': 0.5,
                'body_scale': 1.4,
                'mesh_scale': 1.4,
                'color_texture': bs.gettexture('landMineLit'),
                'reflection': 'powerup',
                'reflection_scale': [1.0],
                'materials': (no_hit_material,),
            },
        )
        # light
        self.light = bs.newnode(
            "light",
            owner=self.node,
            attrs={
                'radius': 0.2,
                'intensity': 0.8,
                'color': (0.0, 1.0, 0.0),
            }
        )
        self.node.connectattr("position", self.light, "position")
        # Drawing circle and circleOutline in radius of 3,
        # so player can see that how close he is to the box.
        # If player is inside this circle the ball speed will increase.
        circle = bs.newnode(
            "locator",
            owner=self.node,
            attrs={
                'shape': 'circle',
                'color': (1.0, 0.0, 0.0),
                'opacity': 0.1,
                'size': (6.0, 0.0, 6.0),
                'draw_beauty': False,
                'additive': True,
            },
        )
        self.node.connectattr("position", circle, "position")
        # also adding a outline cause its look nice.
        circle_outline = bs.newnode(
            "locator",
            owner=self.node,
            attrs={
                'shape': 'circleOutline',
                'color': (1.0, 1.0, 0.0),
                'opacity': 0.1,
                'size': (6.0, 0.0, 6.0),
                'draw_beauty': False,
                'additive': True,
            },
        )
        self.node.connectattr("position", circle_outline, "position")

        # all ball attribute that we need.
        self.ball_type: BallType = BallType.EASY
        self.shoot_timer: bs.Timer | None = None
        self.shoot_speed: float = 0.0
        # this force the shoot if player is inside the red circle.
        self.force_shoot_speed: float = 0.0
        self.ball_mag = 3000
        self.ball_gravity: float = 1.0
        self.ball_tex: babase.Texture | None = None
        # only for Hard ball_type
        self.player_facing_direction: list[float, float] = [0.0, 0.0]
        # ball shoot soound.
        self.shoot_sound = bs.getsound('laserReverse')

        # same as "powerupdist"
        self.ball_type_dist: list[BallType] = []

        for ball in ball_type_dict:
            for _ in range(ball_type_dict[ball]):
                self.ball_type_dist.append(ball)

    # Here main logic of game goes here.
    # like shoot balls, shoot speed, anything we want goes here(except for some thing).
    def start_shoot(self) -> NoReturn:

        # getting all allive players in a list.
        alive_players_list = self.activity.get_alive_players()

        # make sure that list is not Empty.
        if len(alive_players_list) > 0:

            # choosing a random player from list.
            target_player = choice(alive_players_list)
            # highlight the target player
            self.highlight_target_player(target_player)

            # to finding difference between player and box.
            # we just need to subtract player pos and ball pos.
            # Same logic as eric applied in Target Practice Gamemode.
            difference = babase.Vec3(target_player.position) - babase.Vec3(
                self.node.position)

            # discard Y position so ball shoot more straight.
            difference[1] = 0.0

            # and now, this length method returns distance in float.
            # we're gonna use this value for calculating player analog stick
            distance = difference.length()

            # shoot a random BallType
            self.upgrade_ball_type(choice(self.ball_type_dist))

            # and check the ball_type and upgrade it gravity_scale, texture, next ball speed.
            self.check_ball_type(self.ball_type)

            # For HARD ball i am just focusing on player analog stick facing direction.
            # Not very accurate and that's we need.
            if self.ball_type == BallType.HARD:
                self.calculate_player_analog_stick(target_player, distance)
            else:
                self.player_facing_direction = [0.0, 0.0]

            pos = self.node.position

            if self.ball_type == BallType.MEDIUM or self.ball_type == BallType.HARD:
                # Target head by increasing Y pos.
                # How this work? cause ball gravity_scale is ......
                pos = (pos[0], pos[1] + .25, pos[2])

            # ball is generating..
            ball = Ball(
                position=pos,
                velocity=(0.0, 0.0, 0.0),
                texture=self.ball_tex,
                gravity_scale=self.ball_gravity,
                body_scale=1.0,
            ).autoretain()

            # shoot Animation and sound.
            self.shoot_animation()

            # force the shoot speed if player try to go inside the red circle.
            if self.force_shoot_speed != 0.0:
                self.shoot_speed = self.force_shoot_speed

            # push the ball to the player
            ball.node.handlemessage(
                'impulse',
                self.node.position[0],  # ball spawn position X
                self.node.position[1],  # Y
                self.node.position[2],  # Z
                0, 0, 0,  # velocity x,y,z
                self.ball_mag,  # magnetude
                0.000,  # magnetude velocity
                0.000,  # radius
                0.000,  # idk
                difference[0] + self.player_facing_direction[0],
                # force direction X
                difference[1],  # force direction Y
                difference[2] + self.player_facing_direction[1],
                # force direction Z
            )
            # creating our timer and shoot the ball again.(and we create a loop)
            self.shoot_timer = bs.Timer(self.shoot_speed, self.start_shoot)

    def upgrade_ball_type(self, ball_type: BallType) -> NoReturn:

        self.ball_type = ball_type

    def check_ball_type(self, ball_type: BallType) -> NoReturn:

        if ball_type == BallType.EASY:
            self.shoot_speed = 0.8
            self.ball_gravity = 1.0
            # next ball shoot speed
            self.ball_mag = 3000
            # box light color and ball tex
            self.light.color = (1.0, 1.0, 0.0)
            self.ball_tex = bs.gettexture('egg4')
        elif ball_type == BallType.MEDIUM:
            self.ball_mag = 3000
            # decrease the gravity scale so, ball shoot without falling and straight.
            self.ball_gravity = 0.0
            # next ball shoot speed.
            self.shoot_speed = 0.4
            # box light color and ball tex.
            self.light.color = (1.0, 0.0, 1.0)
            self.ball_tex = bs.gettexture('egg3')
        elif ball_type == BallType.HARD:
            self.ball_mag = 2500
            self.ball_gravity = 0.0
            # next ball shoot speed.
            self.shoot_speed = 0.6
            # box light color and ball tex.
            self.light.color = (1.0, 0.2, 1.0)
            self.ball_tex = bs.gettexture('egg1')

    def shoot_animation(self) -> NoReturn:

        bs.animate(
            self.node,
            "mesh_scale", {
                0.00: 1.4,
                0.05: 1.7,
                0.10: 1.4,
            }
        )
        # playing shoot sound.
        # self.shoot_sound, position = self.node.position.play();
        self.shoot_sound.play()

    def highlight_target_player(self, player: bs.Player) -> NoReturn:

        # adding light
        light = bs.newnode(
            "light",
            owner=self.node,
            attrs={
                'radius': 0.0,
                'intensity': 1.0,
                'color': (1.0, 0.0, 0.0),
            }
        )
        bs.animate(
            light,
            "radius", {
                0.05: 0.02,
                0.10: 0.07,
                0.15: 0.15,
                0.20: 0.13,
                0.25: 0.10,
                0.30: 0.05,
                0.35: 0.02,
                0.40: 0.00,
            }
        )
        # And a circle outline with ugly animation.
        circle_outline = bs.newnode(
            "locator",
            owner=player.actor.node,
            attrs={
                'shape': 'circleOutline',
                'color': (1.0, 0.0, 0.0),
                'opacity': 1.0,
                'draw_beauty': False,
                'additive': True,
            },
        )
        bs.animate_array(
            circle_outline,
            'size',
            1, {
                0.05: [0.5],
                0.10: [0.8],
                0.15: [1.5],
                0.20: [2.0],
                0.25: [1.8],
                0.30: [1.3],
                0.35: [0.6],
                0.40: [0.0],
            }
        )

        # coonect it and...
        player.actor.node.connectattr("position", light, "position")
        player.actor.node.connectattr("position", circle_outline, "position")

        # immediately delete the node after another player has been targeted.
        self.shoot_speed = 0.5 if self.shoot_speed == 0.0 else self.shoot_speed
        bs.timer(self.shoot_speed, light.delete)
        bs.timer(self.shoot_speed, circle_outline.delete)

    def calculate_player_analog_stick(self, player: bs.Player,
                                      distance: float) -> NoReturn:
        # at first i was very confused how i can read the player analog stick \
        # then i saw TheMikirog#1984 autorun plugin code.
        # and i got it how analog stick values are works.
        # just need to store analog stick facing direction and need some calculation according how far player pushed analog stick.
        # Notice that how vertical direction is inverted, so we need to put a minus infront of veriable.(so ball isn't shoot at wrong direction).
        self.player_facing_direction[0] = player.actor.node.move_left_right
        self.player_facing_direction[1] = -player.actor.node.move_up_down

        # if player is too close and the player pushing his analog stick fully the ball shoot's too far away to player.
        # so, we need to reduce the value of "self.player_facing_direction" to fix this problem.
        if distance <= 3:
            self.player_facing_direction[0] = 0.4 if \
            self.player_facing_direction[0] > 0 else -0.4
            self.player_facing_direction[1] = 0.4 if \
            self.player_facing_direction[0] > 0 else -0.4
        # same problem to long distance but in reverse, the ball can't reach to the player,
        # its because player analog stick value is between 1 and -1,
        # and this value is low to shoot ball forward to Player if player is too far from the box.
        # so. let's increase to 1.5 if player pushed analog stick fully.
        elif distance > 6.5:
            # So many calculation according to how analog stick pushed by player.
            # Horizontal(left-right) calculation
            if self.player_facing_direction[0] > 0.4:
                self.player_facing_direction[0] = 1.5
            elif self.player_facing_direction[0] < -0.4:
                self.player_facing_direction[0] = -1.5
            else:
                if self.player_facing_direction[0] > 0.0:
                    self.player_facing_direction[0] = 0.2
                elif self.player_facing_direction[0] < 0.0:
                    self.player_facing_direction[0] = -0.2
                else:
                    self.player_facing_direction[0] = 0.0

            # Vertical(up-down) calculation.
            if self.player_facing_direction[1] > 0.4:
                self.player_facing_direction[1] = 1.5
            elif self.player_facing_direction[1] < -0.4:
                self.player_facing_direction[1] = -1.5
            else:
                if self.player_facing_direction[1] > 0.0:
                    self.player_facing_direction[1] = 0.2
                elif self.player_facing_direction[1] < 0.0:
                    self.player_facing_direction[1] = -0.2
                else:
                    self.player_facing_direction[1] = -0.0

    # if we want stop the ball shootes
    def stop_shoot(self) -> NoReturn:
        # Kill the timer.
        self.shoot_timer = None


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""


# almost 80 % for game we done in box class.
# now remain things, like name, seetings, scoring, cooldonw,
# and main thing don't allow player to camp inside of box are going in this class.

# ba_meta export bascenev1.GameActivity


class DodgeTheBall(bs.TeamGameActivity[Player, Team]):
    # defining name, description and settings..
    name = 'Dodge the ball'
    description = 'Survive from shooting balls'

    available_settings = [
        bs.IntSetting(
            'Cooldown',
            min_value=20,
            default=45,
            increment=5,
        ),
        bs.BoolSetting('Epic Mode', default=False)
    ]

    # Don't allow joining after we start.
    allow_mid_activity_joins = False

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        # We support team and ffa sessions.
        return issubclass(sessiontype, bs.FreeForAllSession) or issubclass(
            sessiontype, bs.DualTeamSession,
        )

    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        # This Game mode need a flat and perfect shape map where can player fall outside map.
        # bombsquad have "Doom Shroom" map.
        # Not perfect map for this game mode but its fine for this gamemode.
        # the problem is that Doom Shroom is not a perfect circle and not flat also.
        return ['Doom Shroom']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._epic_mode = bool(settings['Epic Mode'])
        self.countdown_time = int(settings['Cooldown'])

        self.check_player_pos_timer: bs.Timer | None = None
        self.shield_drop_timer: bs.Timer | None = None
        # cooldown and Box
        self._countdown: OnScreenCountdown | None = None
        self.box: Box | None = None

        # this lists for scoring.
        self.joined_player_list: list[bs.Player] = []
        self.dead_player_list: list[bs.Player] = []

        # normally play RUN AWAY music cause is match with our gamemode at.. my point,
        # but in epic switch to EPIC.
        self.slow_motion = self._epic_mode
        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.RUN_AWAY
        )

    def get_instance_description(self) -> str | Sequence:
        return 'Keep away as possible as you can'

    # add a tiny text under our game name.
    def get_instance_description_short(self) -> str | Sequence:
        return 'Dodge the shooting balls'

    def on_begin(self) -> NoReturn:
        super().on_begin()

        # spawn our box at middle of the map
        self.box = Box(
            position=(0.5, 2.7, -3.9),
            velocity=(0.0, 0.0, 0.0),
        ).autoretain()

        # create our cooldown
        self._countdown = OnScreenCountdown(
            duration=self.countdown_time,
            endcall=self.play_victory_sound_and_end,
        )

        # and starts the cooldown and shootes.
        bs.timer(5.0, self._countdown.start)
        bs.timer(5.0, self.box.start_shoot)

        # start checking all player pos.
        bs.timer(5.0, self.check_player_pos)

        # drop shield every ten Seconds
        # need five seconds delay Because shootes start after 5 seconds.
        bs.timer(15.0, self.drop_shield)

    # This function returns all alive players in game.
    # i thinck you see this function in Box class.
    def get_alive_players(self) -> Sequence[bs.Player]:

        alive_players = []

        for team in self.teams:
            for player in team.players:
                if player.is_alive():
                    alive_players.append(player)

        return alive_players

    # let's disallowed camping inside of box by doing a blast and increasing ball shoot speed.
    def check_player_pos(self):

        for player in self.get_alive_players():

            # same logic as applied for the ball
            difference = babase.Vec3(player.position) - babase.Vec3(
                self.box.node.position)

            distance = difference.length()

            if distance < 3:
                self.box.force_shoot_speed = 0.2
            else:
                self.box.force_shoot_speed = 0.0

            if distance < 0.5:
                Blast(
                    position=self.box.node.position,
                    velocity=self.box.node.velocity,
                    blast_type='normal',
                    blast_radius=1.0,
                ).autoretain()

                PopupText(
                    position=self.box.node.position,
                    text='Keep away from me',
                    random_offset=0.0,
                    scale=2.0,
                    color=self.box.light.color,
                ).autoretain()

        # create our timer and start looping it
        self.check_player_pos_timer = bs.Timer(0.1, self.check_player_pos)

    # drop useless shield's too give player temptation.
    def drop_shield(self) -> NoReturn:

        pos = self.box.node.position

        PowerupBox(
            position=(pos[0] + 4.0, pos[1] + 3.0, pos[2]),
            poweruptype='shield',
        ).autoretain()

        PowerupBox(
            position=(pos[0] - 4.0, pos[1] + 3.0, pos[2]),
            poweruptype='shield',
        ).autoretain()

        self.shield_drop_timer = bs.Timer(10.0, self.drop_shield)

    # when cooldown time up i don't want that the game end immediately.
    def play_victory_sound_and_end(self) -> NoReturn:

        # kill timers
        self.box.stop_shoot()
        self.check_player_pos_timer = None
        self.shield_drop_timer = None

        bs.timer(2.0, self.end_game)

    # this function runs when A player spawn in map
    def spawn_player(self, player: Player) -> NoReturn:
        spaz = self.spawn_player_spaz(player)

        # reconnect this player's controls.
        # without bomb, punch and pickup.
        spaz.connect_controls_to_player(
            enable_punch=False, enable_bomb=False, enable_pickup=False,
        )

        # storing all players for ScorinG.
        self.joined_player_list.append(player)

        # Also lets have them make some noise when they die.
        spaz.play_big_death_sound = True

    # very helpful function to check end game when player dead or leav.
    def _check_end_game(self) -> bool:

        living_team_count = 0
        for team in self.teams:
            for player in team.players:
                if player.is_alive():
                    living_team_count += 1
                    break

        if living_team_count <= 0:
            # kill the coutdown timer incase the all players dead before game is about to going to be end.
            # so, countdown won't call the function.
            # FIXE ME: it's that ok to kill this timer?
            # self._countdown._timer = None;
            self.end_game()

    # this function called when player leave.
    def on_player_leave(self, player: Player) -> NoReturn:
        # Augment default behavior.
        super().on_player_leave(player)

        # checking end game.
        self._check_end_game()

    # this gamemode needs to handle only one msg "PlayerDiedMessage".
    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)

            # and storing the dead player records in our dead_player_list.
            self.dead_player_list.append(msg.getplayer(Player))

            # check the end game.
            bs.timer(1.0, self._check_end_game)

    def end_game(self):
        # kill timers
        self.box.stop_shoot()
        self.check_player_pos_timer = None
        self.shield_drop_timer = None

        # here  the player_dead_list and joined_player_list gonna be very helpful.
        for team in self.teams:
            for player in team.players:

                # for scoring i am just following the index of the player_dead_list.
                # for dead list...
                # 0th index player dead first.
                # 1st index player dead second.
                # and so on...
                # i think you got it... maybe
                # sometime we also got a empty list
                # if we got a empty list that means all players are survived or maybe only one player playing and he/she survived.
                if len(self.dead_player_list) > 0:

                    for index, dead_player in enumerate(self.dead_player_list):
                        # if this condition is true we find the dead player \
                        # and his index with enumerate function.
                        if player == dead_player:
                            # updating with one, because i don't want to give 0 score to first dead player.
                            index += 1
                            break
                        # and if this statement is true we just find a survived player.
                        # for survived player i am giving the highest score according to how many players are joined.
                        elif index == len(self.dead_player_list) - 1:
                            index = len(self.joined_player_list)
                # for survived player i am giving the highest score according to how many players are joined.
                else:
                    index = len(self.joined_player_list)

                # and here i am following Table of 10 for scoring.
                # very lazY.
                score = int(10 * index)

                self.stats.player_scored(player, score, screenmessage=False)

        # Ok now calc game results: set a score for each team and then tell \
        # the game to end.
        results = bs.GameResults()

        # Remember that 'free-for-all' mode is simply a special form \
        # of 'teams' mode where each player gets their own team, so we can \
        # just always deal in teams and have all cases covered.
        # hmmm... some eric comments might be helpful to you.
        for team in self.teams:

            max_index = 0
            for player in team.players:
                # for the team,  we choose only one player who survived longest.
                # same logic..
                if len(self.dead_player_list) > 0:
                    for index, dead_player in enumerate(self.dead_player_list):
                        if player == dead_player:
                            index += 1
                            break
                        elif index == len(self.dead_player_list) - 1:
                            index = len(self.joined_player_list)
                else:
                    index = len(self.joined_player_list)

                max_index = max(max_index, index)
            # set the team score
            results.set_team_score(team, int(10 * max_index))
        # and end the game
        self.end(results=results)
