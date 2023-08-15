# Ported by your friend: Freaku


from bascenev1lib.game.chosenone import Player, ChosenOneGame


# ba_meta require api 8
# ba_meta export bascenev1.GameActivity
class FrozenOneGame(ChosenOneGame):
    name = 'Frozen One'

    def _set_chosen_one_player(self, player: Player) -> None:
        super()._set_chosen_one_player(player)
        if hasattr(player, 'actor'):
            player.actor.frozen = True
            player.actor.node.frozen = 1
