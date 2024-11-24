"""
Test script for playing agricola via 'Game' API class.
"""

from agricola import Game

# Instantiate an instance of the agricola game.
game1 = Game(num_players=2)

game1.start_game()

game1.start_next_round()

game1.play_next_player_work_actions()

game1.place_person_on_action_space((1,1),(1,0), player_id=1)

game1.player.one.minor_improvements.is_in_deck("basket")

game1.player.one.decision(["basket"])

move_request = game1.bundle_move_request(
    goods_type="wood",
    num_goods=3,
    destination_board="inventory",
    destination_coord=(-1,-1),
    source_board="action_space",
    source_coord=(1,2)
)

game1.player.one.move_items(move_request)

print(game1.player.one.supply.count("wood"))

print()
