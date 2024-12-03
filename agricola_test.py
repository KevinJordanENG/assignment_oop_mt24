"""
Test script for playing agricola via 'Game' API class.
"""

from agricola import Game, StateError

# Import Game API & StateError.

# OPTIONAL! Logging is imported to allow "change one place" toggle of all inspection optional console output.
# THIS IS NOT USED IN `agricola` PACKAGE! Just a UI/UX convenience for anyone running this script.
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.WARNING
)  # Change to level=logging.INFO to log inspection.

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
    # This is where you can see that yes, exception is thrown if logging set to INFO.
    logger.info(e)
    pass

# Call to game prompting update of turn to the 1st player.
game1.play_next_player_work_actions()

# It will now be the players' "work" turns phase. Each player (for all in game) takes
# a turn placing a 'person' on an open action space. Sometimes this prompts decisions,
# which will block the game's state until the respective player completes all required decisions.

# Behind this call to place a player on action spaces, a number of functions are dynamically evaluated
# depending on the action space chosen and its functions, costs, and other attributes.
# Space requested is 'forest', and as an accum. space will add 'wood' to player 1's supply.
initial_wood_num = game1.player.one.supply.count("wood")
# Place player 1's first person on gameboard. Uses `Game`s convenience method call.
game1.place_person_on_action_space((1, 2), (1, 0), player_id=1)
# Player 1 will now have more 'wood', verify this. Optional inspection via logging.INFO.
new_wood_num = game1.player.one.supply.count("wood")
logger.info(f"Prev. wood = {initial_wood_num}, New wood = {new_wood_num}")

# Play player 2's first 'person'. Uses player direct '.' access method.
game1.player.two.place_person_on_action_space((3, 1), (1, 0))

# The chosen action space will prompt player decision.
# Optional inspection of decision function & arg caches for logging.INFO.
logger.info("func: %s", game1.player.two.waiting_decision_function)
logger.info("args: %s", game1.player.two.required_decision_args_types[0])

# Try/except demonstrating state based blocking until decision chain is ended.
try:
    game1.play_next_player_work_actions()
except StateError as e:
    # This is where you can see that yes, exception is thrown if logging set to INFO.
    logger.info(e)
    pass

# Invoke decision of player 2 with proper args. Args provided as `list[str, ...]` for easy parsing.
game1.player.two.decision(["(2,4)"])

# Using `decision()` handles cleanup automatically performing various actions as needed, so now back to player 1's turn.
# We know this since it is still the 1st round so both players will have 2 starting 'person's.

# Try/except to show error if trying to place player on occupied space.
try:
    game1.place_person_on_action_space((3, 1), (2, 0), player_id=1)
except ValueError as e:
    # This is where you can see that yes, exception is thrown if logging set to INFO.
    logger.info(e)
    pass

# Place player 1's next person on an empty space.
game1.place_person_on_action_space((2, 1), (2, 0), player_id=1)

# Place player 2's next person on an empty space.
game1.player.two.place_person_on_action_space((5, 1), (2, 0))

# Both players are now out of 'person's to place, so game should now be in returning home state.
# Even though logically this would make it the next round, this must be set by calling
# start_next_round() as it handles accumulation, and prep actions for next round.
# adding new action space, & optional future goods getting (now present round).
game1.start_next_round()

# Optional logging at INFO level to check round number increased & new action space available.
# New action space will be selected at random from remaining for the game phase so will have
# nondeterministic return value when inspected.
logger.info("game round: %d", game1.round)
logger.info(game1.action_spaces.board[(0, 2)]["action"])

# New round but not yet in player work mode, so call to game prompting update of turn to the 1st player.
game1.play_next_player_work_actions()

# Back to being player turns, so do some player actions.
# Next round, so player 1 can use 'forest' again (he likes 'wood').
game1.place_person_on_action_space((1, 2), (1, 0), player_id=1)

# Now lets get crazy, lets try to start another game with same UUID.
game2 = Game(num_players=2, instance_uuid="GAME_ONE")
# It will return a pointer to the same object as seen in optional logging.INFO.
logger.info("game1 address = %s, game2 address = %s", game1, game2)

# Some more crazy actions, can we modify the UUID?
# Doesn't static type check, but will it error at runtime?
try:
    game1.instance_uuid = "NEW_NAME"  # type: ignore
except (                              # ^^^^^^^^^^^^ silence MyPy as I know it 
                                      # doesn't type check, using as demo.
    Exception
) as e:
    # Yes, this will throw exception.
    logger.info(e)
    pass

# What about collection types, surely they can be hacked with?
# Doesn't static type check, but will it error at runtime?
try:
    game1.player.two.supply.general_goods[0]["location"] = "farmyard"  # type: ignore
except Exception as e:                                                 # ^^^^^^^^^^^^ 
                                                    # silence MyPy as I know
    # This also is not allowed and will error.      # it doesn't type check, using as demo.
    logger.info(e)
    pass

# END OF DEMO, HAPPY PLAYING!
