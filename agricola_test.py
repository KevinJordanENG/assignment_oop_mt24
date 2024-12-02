"""
Test script for playing agricola via 'Game' API class.
"""
from agricola import Game, StateError
# Import Game API & StateError.

# Instantiate an instance of the agricola game.
game1 = Game(num_players=2, instance_uuid="GAME_ONE")

# Call to public method to start the newly created game.
game1.start_game()

# Call to start the next round of the game. Handles accumulation,
# adding new action space, & optional future goods getting (now present round).
game1.start_next_round()

# Try/except to show that out of order method invocation is blocked.
try:
    # This will fail as we have already started round, StateError will be raised.
    game1.start_next_round()
except StateError as e:
    # This is where you can uncomment to see that yes, exception is thrown.
    #print(e)
    pass

# Call to game prompting update of turn to the 1st or subsequent player.
game1.play_next_player_work_actions()

# It will now be the players' "work" turns phase. Each player (for all in game) takes
# a turn placing a 'person' on an open action space. Sometimes this prompts decisions,
# which will block the game's state until the respective player completes all required decisions.

# Space requested is 'forest', and as an accum. space will add 'wood' to player 1's supply.
initial_wood_num = game1.player.one.supply.count('wood')
# Place player 1's first person on gameboard. Uses `Game`s convenience method call.
game1.place_person_on_action_space((1,2),(1,0), player_id=1)
# Player 1 will now have more 'wood', verify this. Optional uncomment to print.
new_wood_num = game1.player.one.supply.count('wood')
#print(f"Prev. wood = {initial_wood_num}, New wood = {new_wood_num}")

# Play player 2's first 'person'. Uses player direct '.' access method.
game1.player.two.place_person_on_action_space((3,1),(1,0))

# The chosen action space will prompt player decision.
# Optional uncomment to inspect decision function & arg caches.
#print("func: ", game1.player.two.waiting_decision_function)
#print("args: ", game1.player.two.required_decision_args_types)

# Try/except demonstrating state based blocking until decision chain is ended.
try:
    game1.play_next_player_work_actions()
except StateError as e:
    # This is where you can uncomment to see that yes, exception is thrown.
    #print(e)
    pass

# Invoke decision of player 2 with proper args. Args provided as `list[str, ...]` for easy parsing.
game1.player.two.decision(["(2,4)"])

# Using `decision()` handles cleanup automatically, so now back to player 1's turn.

# Try/except to show error if trying to place player on occupied space.
try:
    game1.place_person_on_action_space((3,1),(2,0), player_id=1)
except ValueError as e:
    # This is where you can uncomment to see that yes, exception is thrown.
    #print(e)
    pass

