"""
Test script for playing agricola via 'Game' API class.
"""

from agricola import Game

# Instantiate an instance of the agricola game.
game1 = Game(num_players=2)

game1.start_game()

game1.start_next_round()

game1.play_next_player_work_actions()



print()
