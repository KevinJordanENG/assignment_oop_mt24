"""
Test script for playing agricola via 'Game' API class.
"""
from agricola import Game

# Instantiate an instance of the agricola game.
game1 = Game(num_players=2, instance_uuid="GAME_ONE")

game1 = Game(num_players=2, instance_uuid="GAME_ONE")

game1.start_game()

game1.start_next_round()

game1.play_next_player_work_actions()

game1.place_person_on_action_space((1,1),(1,0), player_id=1)

game1.player.one.minor_improvements.is_in_deck("basket")

game1.player.one.decision(["basket"])

print()
