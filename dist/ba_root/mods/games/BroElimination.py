
# ba_meta require api 7
from plugins import auto_stunt
from bastd.game.elimination import EliminationGame
import ba
# ba_meta export game
class BroEliminaition(EliminationGame):
    name = 'BroElimination'
    description = 'Elimination Game with dual character control'

    def spawn_player(self, player) -> ba.Actor:
        super().spawn_player(player)
        auto_stunt.spawn_mirror_spaz(player)
