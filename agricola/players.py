"""
Module containing Player class for controlling agricola game players.
"""
from __future__ import annotations
from typing import Self, TYPE_CHECKING, cast

from .goods import Supply
from .gameboards import Farmyard, MoveRequest
from .cards import Deck
from .type_defs import (
    GoodsType,
    Coordinate,
    Action,
    SpaceType,
    MinorImproveNames,
    OccupationNames,
    MajorImproveNames,
    GameStates
)
if TYPE_CHECKING:
    from .game import Game

# TODO: Add state checks to all funcs!


class Player:
    """
    Player class.
    """

    __game: Game
    __player_id: int
    __starting_player: bool
    __supply: Supply
    __farmyard: Farmyard
    __player_major_imp_cards: Deck | None
    __minor_imp_cards: Deck
    __occupation_cards: Deck
    __begging_markers: int
    __has_future_goods_on_action_spaces: bool
    __future_goods: list[tuple[int, GoodsType]]
                             # ^^^ round_num
    __decision_func_cache: str # str version of func to be executed.
    __decision_args_cache: list[str] # List of types of args required for cached decision func.
    __pending_payment: tuple[tuple[int,str], ...] # Sometimes required when decision chains present.

    def __new__(
            cls,
            game: Game,
            minor_imp_cards: Deck,
            occup_cards: Deck,
            num_players: int,
            *,
            player_id: int,
            starting: bool = False
        ) -> Self:
        self = super().__new__(cls)
        self.__game = game
        self.__player_id = player_id
        self.__starting_player = starting
        self.__begging_markers = 0
        if num_players == 1:
            self.__supply = Supply(game, num_food=0)
        else:
            self.__supply = Supply(game, num_food=2 if starting else 3)
        self.__farmyard = Farmyard(game)
        self._init_persons()
        self.__player_major_imp_cards = None
        self.__minor_imp_cards = minor_imp_cards
        self.__occupation_cards = occup_cards
        self.__has_future_goods_on_action_spaces = False
        self.__future_goods = []
        self.__decision_args_cache = []
        self.__pending_payment = ()
        return self

    @property
    def game(self) -> str:
        """Returns the game instance that the player is a part of."""
        return self.__game.instance_uuid

    @property
    def player_id(self) -> int:
        """Player ID."""
        return self.__player_id

    @property
    def starting_player(self) -> int:
        """Does this player have the 'starting player' token?"""
        return self.__starting_player

    @property
    def begging_markers(self) -> int:
        """Number of begging markers player has."""
        return self.__begging_markers

    @property
    def waiting_decision_function(self) -> str:
        """Returns the 'str' function call that is waiting to be executed."""
        return self.__decision_func_cache

    @property
    def required_decision_args_types(self) -> list[str]:
        """Returns list of required arg types to be passed to decision() func."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__decision_args_cache

    @property
    def supply(self) -> Supply:
        """Returns view of player's current supply."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__supply

    @property
    def farmyard(self) -> Farmyard:
        """Returns current view of player's farmyard board."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__farmyard

    @property
    def major_improvements(self) -> Deck | None:
        """Returns player's major improvement cards if any, else None."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__player_major_imp_cards

    @property
    def minor_improvements(self) -> Deck:
        """Returns player's minor improvement cards."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__minor_imp_cards

    @property
    def occupations(self) -> Deck:
        """Returns player's occupations cards."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__occupation_cards

    def discard_goods(self, good_type: GoodsType, number: int) -> None:
        """Player action that can be called at any time to discard unwanted goods."""
        raise NotImplementedError()

    def grains_or_veg_to_food(self, good_type: GoodsType, number: int) -> None:
        """Player action that can be called at any time turning crops into food."""
        raise NotImplementedError()

    def move_animals_anytime(self) -> None:
        """Player action that can be called at any time moving animals around farmyard."""
        raise NotImplementedError()

    def build_fence(self) -> None:
        """Performs build fence action. Delegates to farmyard's & supply's method."""
        #self.__farmyard.build_fence()
        #self.__supply.build_fence()
        raise NotImplementedError()

    def get_goods_from_future_action_spaces(self, round_num: int) -> None:
        """If player has items on future action spaces, this add them to player's inventory."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"running_round_prep"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Get future goods if present.
        if self.__has_future_goods_on_action_spaces:
            for future_good in self.__future_goods:
                if future_good[0] == round_num:
                    self.__supply.add(
                        {
                            "goods_type": future_good[1],
                            "location": "inventory",
                            "coordinate": (-1,-1)
                        }
                    )

    def place_person_on_action_space(
            self,
            destination_coord: Coordinate,
            source_coord: Coordinate
        ) -> None:
        """Player public method to place a 'person' on the action spaces board."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Early reject if space occupied.
        if destination_coord not in self.__game.action_spaces.open_spaces:
            raise ValueError("Coordinate is already occupied.")
        self.__farmyard.move(
            "person", 1, "action_space", destination_coord, "farmyard", source_coord
        )
        self.__game.action_spaces.move(
            "person", 1, "action_space", destination_coord, "farmyard", source_coord
        )
        self.__supply.move("person", 1, "action_space", destination_coord, "farmyard", source_coord)
        action_key = self.__game.action_spaces.board[destination_coord]["action"]
        if action_key is None:
            raise ValueError("Missing action at requested space.")
        str_func = self.__game.action_spaces.get_action_function(action_key)
        # WARNING! Known to be extremely brittle & dangerous in normal setting.
        # Used here as caching functions & args in the CSV containing space data makes maintaining
        # the large number of unique actions tractable for this game in shorter development time.
        decision = eval(str_func)
        if decision:
            self.__game.state.set_current_player_decision()
        else:
            self.__game.state.play_next_player_actions()

    def get_goods(self, action: Action | None = None) -> bool:
        """Gets goods and adds them to inventory."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Action space variants. Accum only valid here.
        if action is not None:
            space = self.__game.action_spaces.get_space_data_from_action(action)
            if space is None:
                raise ValueError("Did not find action space on board. Maybe not yet in play.")
            source_coord, space_data = space[0], space[1]
            # Accum spaces.
            if space_data["accumulate"]:
                good = space_data["goods_type"]
                if good is None:
                    raise ValueError("Missing GoodsType at requested get_goods action space.")
                self.__game.action_spaces.move(
                    good, space_data["num_present"],
                    "inventory", (-1,-1), "action_space", source_coord
                )
                self.__supply.move(
                    good, space_data["num_present"],
                    "inventory", (-1,-1), "action_space", source_coord
                )
                return False # No further decision needed.
            # Non-accum spaces.
            if not space_data["accumulate"]:
                output = self.__game.action_spaces.get_action_func_output(action)
                for _ in range(output[0]):
                    self.__supply.add(
                        {"goods_type": output[1], "location": "inventory", "coordinate": (-1,-1)}
                    )
                return False # No further decision needed.
        # Getting from general inventory.
        elif action is None:
# TODO: Build this logic for minor imp. & occup calls to get_goods().
            pass
        return False

    def build_rooms_and_or_stables(self) -> bool:
        """Function from action space allowing building of rooms &| stables."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Set decision caches.
        self.__decision_func_cache = "self.choose_room_or_stable('{}')"
        self.__decision_args_cache = ["arg0: room OR stable"]
        return True

    def choose_room_or_stable(self, room_or_stable: str) -> bool:
        """Takes choice of room or stable and furthers decision logic for 'farm_expansion'."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Check valid input.
        if room_or_stable not in {"room", "stable"}:
            raise ValueError("Invalid choice, must be either 'room' or 'stable'.")
        if room_or_stable == "room":
            room_or_stable = self.__farmyard.get_house_type()
        # We're for sure using 'farm_expansion' right?
        costs = self.__game.action_spaces.get_action_func_cost('farm_expansion')
        cost_of_interest = costs[room_or_stable]
        if room_or_stable == "stable":
            count = self.__supply.count(cost_of_interest[0][1])
            if count < cost_of_interest[0][0]:
# FIXME! Decide if we should actually clear the decision caches or not.
                # Clear func & arg caches.
                self.__decision_func_cache = ""
                self.__decision_args_cache = []
                # If no more decisions set state to next player.
                self.__game.state.play_next_player_actions()
                raise ValueError("Not enough resources for requested build.")
            self.__pending_payment = cost_of_interest
        else:
            # For sure some type of room.
            count_1 = self.__supply.count(cost_of_interest[0][1])
            count_2 = self.__supply.count(cost_of_interest[1][1])
            if count_1 < cost_of_interest[0][0] or count_2 < cost_of_interest[1][0]:
# FIXME! Decide if we should actually clear the decision caches or not.
    # TODO: TODO TODO: probably DONT clear as allows try/catch in test script & re-exec of cached funcs!
                # Clear func & arg caches.
                self.__decision_func_cache = ""
                self.__decision_args_cache = []
                # If no more decisions set state to next player.
                self.__game.state.play_next_player_actions()
                raise ValueError("Not enough resources for requested build.")
            self.__pending_payment = cost_of_interest
        # All checks passed, now choose space to build.
        temp_str = f"self.choose_space(requested_space_type='{room_or_stable}'"
        self.__decision_func_cache = temp_str + ", destination_coord={})"
        self.__decision_args_cache = ["agr0: Coordinate"]
        return True

    def choose_space(
            self,
            requested_space_type: SpaceType,
            destination_coord: Coordinate
            ) -> bool:
        """Chooses space to try to accomplish action."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Check if valid space type.
        if not self.__farmyard.check_space_change_validity(requested_space_type, destination_coord):
            # If no --> end decision, raise error.
# FIXME! Decide if we should actually clear the decision caches or not.
            # Clear func & arg caches.
            self.__decision_func_cache = ""
            self.__decision_args_cache = []
            raise ValueError("Not valid space request.")
        # Passed checks, change space type.
        self.__farmyard.change_space_type(requested_space_type, destination_coord)
        # Pay for it (if it costs anything)!
        if len(self.__pending_payment) > 0:
            self.__supply.pay(self.__pending_payment)
        self.__pending_payment = () # Assign empty tuple (payment no longer pending).
        return False

    def take_start_player_token(self) -> bool:
        """Action from action spaces that makes current player 'starting'."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Set current player as start if not already.
        if self.__starting_player:
            pass
        # Search for other player in game that is currently starting.
        else:
            for player in self.__game.player.players_tup:
                # Set them to starting = False.
                if player.starting_player:
                    player.set_not_starting()
        # Send back decision of playing minor imp. card.
        self.__decision_func_cache = "self.play_minor_improvement('{}')"
        self.__decision_args_cache = ["arg0: MinorImproveNames"]
        return True

    def set_not_starting(self) -> None:
        """Sets player starting token to false."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        self.__starting_player = False

    def play_minor_improvement(self, minor_imp: MinorImproveNames) -> bool:
        """
        Player gets to play a minor improvement from their hand.
        Function takes in a MinorImproveNames, assuming it exists in hand and errors if not found.
        Useful to query first using 'deck.is_in_deck()' to confirm presence to avoid exception.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Check if card is present in hand.
        if not self.__minor_imp_cards.is_in_deck(minor_imp):
            raise ValueError("Card requested to be played not found in this player's hand.")
        # If present, get prereqs if any.
        prereqs = self.__minor_imp_cards.get_prereqs_minor_imp(minor_imp)
        if prereqs is not None:
            # Check prereqs if present.
            if not self.minor_imp_prereq_check():
                raise ValueError("Prerequisites for playing selected card not met.")
        # Get cost to play.
        build_cost = self.__minor_imp_cards.get_build_cost(minor_imp)
        # Check if we can pay for it.
        if build_cost is not None:
            # Check build cost if present.
            if not self._check_inventory(build_cost):
                raise ValueError("Not enough resources to pay card build cost.")
            # Pay build cost.
            self.__supply.pay(build_cost)
        # Checks passed, play card & get its func.
        card_func = self.__minor_imp_cards.play_card(minor_imp)
        # If no func return F -> decision will cleanup.
        if card_func is None:
            return False
        decision = eval(card_func) # Otherwise eval card func.
        # If we've gotten to the point of card func eval, the card IS played so do pass_left.
        if self.__minor_imp_cards.cards[minor_imp].attributes["pass_left"]:
            self.__game.player.pass_minor_imp_card_left(self.__game, self.player_id, minor_imp)
        # If func that doesn't require decision, execute & return F -> decision cleanup.
        # If func that req dec, exec, return T to decision (assumes caches set by card func).
        if decision:
            return True
        return False

    def minor_imp_prereq_check(self) -> bool:
        """Checks players items/status to confirm has needed prereqs."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # FIXME! plz build: currently just pass-through of True assumes prereqs are met.
        return True

    def plow(self) -> bool:
        """Takes plow action, returns choose_space decision."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        string = "self.choose_space(requested_space_type='field', destination_coord={})"
        self.__decision_func_cache = string
        self.__decision_args_cache = ["arg0: Coordinate"]
        return True

    def choose_occupation_to_play(self, action: Action) -> bool:
        """Decision prompt to choose an occupation card to play."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Get costs for different lessons spaces based on space & num already played.
        count = self.__occupation_cards.count_num_played()
        if action == "lessons":
            costs = self.__game.action_spaces.get_action_func_cost('lessons')
            # Decide which cost item to use.
            if count == 0:
                cost = costs["first"]
            else:
                cost = costs["second"]
        elif action == "3_lessons":
            costs = self.__game.action_spaces.get_action_func_cost('3_lessons')
            cost = costs["all"]
        elif action == "4_lessons":
            costs = self.__game.action_spaces.get_action_func_cost('4_lessons')
            # Decide which cost item to use.
            if count < 2:
                cost = costs["one_and_two"]
            else:
                cost = costs["three_plus"]
        else:
            raise ValueError("Invalid action space to play occupation from.")
        # Check that we can pay for it.
        if cost is not None:
            if not self._check_inventory(cost):
                raise ValueError("Not enough resources to pay card play cost.")
            # Pay for it.
            self.__supply.pay(cost)
        # Pass on decision for which card to play.
        self.__decision_func_cache = "self.play_occupation('{}')"
        self.__decision_args_cache = ["arg0: OccupationNames"]
        return True

    def play_occupation(self, occup: OccupationNames) -> bool:
        """
        Player gets to play an occupation card from their hand.
        Function takes in a OccupationNames, assuming it exists in hand and errors if not found.
        Useful to query first using 'deck.is_in_deck()' to confirm presence to avoid exception.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Check if card is present in hand.
        if not self.__occupation_cards.is_in_deck(occup):
            raise ValueError("Card requested to be played not found in this player's hand.")
        # Checks passed, play card & get its func.
        card_func = self.__occupation_cards.play_card(occup)
        # If no func return F -> decision will cleanup.
        if card_func is None:
            return False
        # Eval func.
        decision = eval(card_func)
        # If func that doesn't require decision, execute & return F -> decision cleanup.
        # If func that req dec, exec, return T to decision (assumes caches set by card func).
        if decision:
            return True
        return False

    def play_major_improvement(self, major_imp: MajorImproveNames) -> bool:
        """
        Player gets to play a major improvement from the main game and put it in their game space.
        Function takes in a MajorImproveNames, assuming it exists and errors if not found.
        Useful to query first using 'deck.is_in_deck()' to confirm presence to avoid exception.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Check if card is present in hand.
        if not self.__game.major_imp_cards.is_in_deck(major_imp):
            raise ValueError("Card requested not available.")
        # Get cost to play.
        build_cost = self.__game.major_imp_cards.get_build_cost(major_imp)
        # If we requested the cooking hearths, this prompts another decision so kick out & handle.
        if major_imp in {"4_cooking_hearth", "5_cooking_hearth"}:
            self.__pending_payment = build_cost
            self.__decision_func_cache = "self.return_fireplace_or_buy_hearth(buy_or_return='{}')"
            self.__decision_args_cache = ["arg0: buy OR return"]
            return True
        # Check if we can pay for it.
        if build_cost is not None:
            # Check build cost if present.
            if not self._check_inventory(build_cost):
                raise ValueError("Not enough resources to pay card build cost.")
            # Pay build cost.
            self.__supply.pay(build_cost)

# FIXME! left off here

        return True

    def return_fireplace_or_buy_hearth(self, buy_or_return: str) -> bool:
        """
        Sub-decision when playing a major imp. to 
        either return a held fireplace OR just buy the hearth.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # If return-fireplace.
        # Check that we have one to return.
        # If not, raise error.
        # If yes, return it.
        # Get hearth.
        # Set False, return, let decision clean up.
        # Else we're trying to buy it.
        # Check if we can pay for it (cost was cached as pending payment).
        if self.__pending_payment is not None:
            # Check build cost if present.
            if not self._check_inventory(self.__pending_payment):
                raise ValueError("Not enough resources to pay card build cost.")
            # Pay build cost.
            self.__supply.pay(self.__pending_payment)
            self.__pending_payment = ()
        
# FIXME! left off here

        return False

    def load_decision_cache_with_funcs(self, func_1: str, func_2: str) -> bool:
        """Function to load 2 game action functions to choose from."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Set cache & args.
        self.__decision_func_cache = "self.choose_action_function(chosen_func='{}')"
        self.__decision_args_cache = ["arg0: " + func_1 + " OR " + func_2]
        return True

    def choose_action_function(self, chosen_func: str) -> bool:
        """Takes the function chosen and loads it in cache."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        self.__decision_func_cache = chosen_func
        # Need a large if else tree to match chosen func to args.
        # Limited number of times functions are chosen between, so ugly/unscalable but works.
        # Minor imp.
        if chosen_func == "self.play_minor_improvement('{}')":
            self.__decision_args_cache = ["arg0: MinorImproveNames"]
        # Major imp.
        elif chosen_func == "self.play_major_improvement('{}')":
            self.__decision_args_cache = ["aeg0: MajorImproveNames"]
# TODO: finish list
        # Sow.
        # Bake bread.
        # Get goods.
        # Get animal.
        # Cook.
        return True

    def decision(self, decision_args: list[str]) -> None:
        """
        Function to make a decision based on possible options from game effects.
        If func eval'd in decision has no further/chained decisions, decision() will cleanup state.
        If there is a subsequent decision, the eval'd func will update the decision caches.
        NOTE: decision() expects all args in list to be of type 'str'.
        It converts them internally, and allows simple single type inputs.
        Example: input of a Coordinate, arg should be str "(0,2)" not tuple (0,2).
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Take args cache & input into func cache str.
        filled_str = self.__decision_func_cache.format(*decision_args)
        # Eval func.
        decision = eval(filled_str)
        # If no more decisions.
        if not decision:
            # Clear func & arg caches.
            self.__decision_func_cache = ""
            self.__decision_args_cache = []
            # If no more decisions set state to next player.
            self.__game.state.play_next_player_actions()
        # If more decisions, the functions will have set the func & args caches,
        # so no further action.

    def move_items(self, move_request: MoveRequest) -> None:
        """Player call to move selected item(s) around player controlled spaces."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest"
        }
        self.__game.state.is_valid_state_for_func(self.__game.game_state, valid_states)
        # Move items.
        self.__farmyard.move(**move_request)
        self.__game.action_spaces.move(**move_request)
        self.__supply.move(**move_request)

    def _check_inventory(self, cost: tuple[tuple[int,str], ...]) -> bool:
        """Check function verifying player has all items to pay for given cost."""
        flag = True
        for item in cost:
            count = self.__supply.count(cast(GoodsType, item[1]))
            # If we find that even 1 goods type does not have enough stock, we can't pay at all.
            if count < item[0]:
                return False
        return flag

    def _check_if_persons_still_to_move(self) -> bool:
        """Checks if player has any more 'person' pieces to place."""
        return False

    def _init_persons(self) -> None:
        """Move a person piece from one coordinate & board to another."""
        self.__farmyard.move("person", 1, "farmyard", (1,0), "inventory", (-1,-1))
        self.__farmyard.move("person", 1, "farmyard", (2,0), "inventory", (-1,-1))
        self.__supply.move("person", 1, "farmyard", (1,0), "inventory", (-1,-1))
        self.__supply.move("person", 1, "farmyard", (2,0), "inventory", (-1,-1))


class Players:
    """
    Combination/convenience class that unifies all 4 possible players 
    for easy '.' access to player methods as well as iterable collection.
    """

    __one: Player
    __two: Player
    __three: Player
    __four: Player
    __num_players: int
    __players_tup: tuple[Player, ...]

    def __new__(cls, players_tup: tuple[Player, ...]) -> Self:
        self = super().__new__(cls)
        self.__players_tup = players_tup
        self.__num_players = len(players_tup)
        if self.num_players == 1:
            self.__one = players_tup[0]
        elif self.num_players == 2:
            self.__one = players_tup[0]
            self.__two = players_tup[1]
        elif self.num_players == 3:
            self.__one = players_tup[0]
            self.__two = players_tup[1]
            self.__three = players_tup[2]
        elif self.num_players == 4:
            self.__one = players_tup[0]
            self.__two = players_tup[1]
            self.__three = players_tup[2]
            self.__four = players_tup[3]
        return self

    @property
    def one(self) -> Player:
        """Returns player one & their methods."""
        return self.__one

    @property
    def two(self) -> Player:
        """Returns player two & their methods."""
        return self.__two

    @property
    def three(self) -> Player:
        """Returns player three & their methods."""
        return self.__three

    @property
    def four(self) -> Player:
        """Returns player four & their methods."""
        return self.__four

    @property
    def num_players(self) -> int:
        """Returns number of players in current game."""
        return self.__num_players

    @property
    def players_tup(self) -> tuple[Player, ...]:
        """Returns iterable collection of players for easier batch ops."""
# FIXME! Need to make sure read only
        return self.__players_tup

    def pass_minor_imp_card_left(
            self,
            game: Game,
            current_player_id: int,
            minor_imp: MinorImproveNames
            ) -> None:
        """Moves the card to the left (player_id++) hand."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        game.state.is_valid_state_for_func(game.game_state, valid_states)
        if self.__num_players == 1:
            # Just remove it.
            self.__one.minor_improvements.pop(minor_imp)
        if current_player_id == self.__num_players:
            # Next player is actually player 1.
            # Remove from current player.
            card = self.__players_tup[current_player_id-1].minor_improvements.pop(minor_imp)
            self.__one.minor_improvements.add_card_to_deck(minor_imp, card)
        else:
            # Increment player_id.
            card = self.__players_tup[current_player_id-1].minor_improvements.pop(minor_imp)
            self.__players_tup[current_player_id].minor_improvements.add_card_to_deck(
                minor_imp, card
            )
