# ba_meta require api 6

"""
  BombWar Mini game 

  by : Mr.Smoothy 
  discord : mr.smoothy#5824
  download more , contribute : https://discord.gg/ucyaesh

 """
from __future__ import annotations

from typing import TYPE_CHECKING
import ba
from bastd.game.deathmatch import DeathMatchGame, Player, Team
from bastd.actor.bomb import Bomb
import bastd
if TYPE_CHECKING:
    from typing import Sequence

from bastd.gameutils import SharedObjects
# ba_meta export game
class BombWar(DeathMatchGame):
    name = 'Bomb War'

    def __init__(self, settings: dict):
        super().__init__(settings)
        
        
        shared = SharedObjects.get()
        self._wall_material=ba.Material()
        self._fake_wall_material=ba.Material()
        self._wall_material.add_actions(
            
            actions=(
                ('modify_part_collision', 'friction', 100000),
             ))
        self._wall_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=(
                ('modify_part_collision', 'collide', False),
            ))

        self._wall_material.add_actions(
            conditions=(('we_are_younger_than', 100),
            'and',
            ('they_have_material',shared.object_material)),
            actions=(
                ('modify_part_collision', 'collide', False),
            ))
        self._wall_material.add_actions(
            conditions=('they_have_material',shared.footing_material),
            actions=(
                ('modify_part_collision', 'friction', 9999.5),
            ))
        self._wall_material.add_actions(
            conditions=('they_have_material', bastd.actor.bomb.BombFactory.get().blast_material),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False)
                
            ))
        self._fake_wall_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', True)
                
            ))
        self.blocks=[]

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        factory = bastd.actor.bomb.BombFactory.get()
        
        shared = SharedObjects.get()
        for i in [-5.5,-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5]:

            self.blocks.append(ba.newnode(
                'prop',
                delegate=self,
                attrs={
                    'body': 'puck',
                    'position': (-0.1,3,i),
                    'model': ba.getmodel('tnt'),
                    # 'light_model': factory.tnt_model,
                    'shadow_size': 0.5,
                    'gravity_scale':7.5,
                    'color_texture': ba.gettexture('puckColor'),
                    'reflection': 'soft',
                    'reflection_scale': [1.0],
                    'materials': (shared.object_material,self._wall_material,)
                }) )
        for i in [-5.5,-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.3]:

            self.blocks.append(ba.newnode(
                'prop',
                delegate=self,
                attrs={
                    'body': 'puck',
                    'position': (-0.1,5,i),
                    'model': ba.getmodel('tnt'),
                    # 'light_model': factory.tnt_model,
                    'shadow_size': 0.5,
                    'gravity_scale':7.5,
                    'color_texture': ba.gettexture('puckColor'),
                    'reflection': 'soft',
                    'reflection_scale': [1.0],
                    'materials': (shared.object_material,self._wall_material,)
                }) )
        self.blocks.append(ba.NodeActor(ba.newnode('region',attrs={'position': (0,3,-6),'scale': (2,5,20),'type': 'box','materials': (self._fake_wall_material, )})))

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = (self._kills_to_win_per_player *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()