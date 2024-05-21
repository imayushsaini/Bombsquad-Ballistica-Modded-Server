#Made by your friend: Freaku / @[Just] Freak#4999


import ba, random
from bastd.actor.bomb import Bomb
from bastd.game.meteorshower import Player, MeteorShowerGame


# ba_meta require api 7
# ba_meta export game
class IcyEmitsGame(MeteorShowerGame):
    name = 'Icy Emits'

    @classmethod
    def get_supported_maps(cls, sessiontype):
        return ['Lake Frigid','Hockey Stadium']

    def _drop_bomb_cluster(self) -> None:
        delay = 0.0
        for _i in range(random.randrange(1, 3)):
            # Drop them somewhere within our bounds with velocity pointing
            # toward the opposite side.
            pos = (-7.3 + 15.3 * random.random(), 5.3,
                   -5.5 + 2.1 * random.random())
            dropdir = (-1.0 if pos[0] > 0 else 1.0)
            vel = (0,10,0)
            ba.timer(delay, ba.Call(self._drop_bomb, pos, vel))
            delay += 0.1
        self._set_meteor_timer()

    def _drop_bomb(self, position, velocity):
        random_xpositions = [-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10]
        random_zpositions = [-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]
        bomb_position = (random.choice(random_xpositions), 0.2,random.choice(random_zpositions))
        Bomb(position=bomb_position, velocity=velocity, bomb_type = 'ice').autoretain()




# ba_meta export plugin
class byFreaku(ba.Plugin):
    def __init__(self):
        ## Campaign support ##
        randomPic = ['lakeFrigidPreview','hockeyStadiumPreview']
        ba.app.add_coop_practice_level(ba.Level(name='Icy Emits', displayname='${GAME}', gametype=IcyEmitsGame, settings={}, preview_texture_name=random.choice(randomPic)))