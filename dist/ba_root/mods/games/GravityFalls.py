## Made by MattZ45986 on GitHub
## Ported by: Freaku / @[Just] Freak#4999


import ba
from bastd.game.elimination import EliminationGame



# ba_meta require api 6
# ba_meta export game
class GFGame(EliminationGame):
    name = 'Gravity Falls'

    def spawn_player(self, player):
        actor = self.spawn_player_spaz(player, (0,5,0))
        if not self._solo_mode:
            ba.timer(0.3, ba.Call(self._print_lives, player))

        # If we have any icons, update their state.
        for icon in player.icons:
            icon.handle_player_spawned()
        ba.timer(1,ba.Call(self.raise_player, player))
        return actor

    def raise_player(self, player):
        if player.is_alive():
            try:
                player.actor.node.handlemessage("impulse",player.actor.node.position[0],player.actor.node.position[1]+.5,player.actor.node.position[2],0,5,0, 3,10,0,0, 0,5,0)
            except: pass
            ba.timer(0.05,ba.Call(self.raise_player,player))