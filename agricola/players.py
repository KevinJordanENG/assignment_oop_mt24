"""
Module containing Player class for controlling agricola game players.
"""
from __future__ import annotations
from typing import Self, TYPE_CHECKING

from .goods import Supply
from .gameboards import Farmyard, MoveRequest
from .cards import Deck
from .rounds_server import GameState
from .type_defs import GoodsType, Coordinate, Action, SpaceType, Location
if TYPE_CHECKING:
    from .game import Game

# TODO: Add state checks to all funcs!


class Player:
    """
    Player class.
    """

    __game: Game
    __state: GameState
    __player_id: int
    __starting_player: bool
    __supply: Supply
    __farmyard: Farmyard
    __player_major_imp_cards: Deck | None
    __minor_imp_cards: Deck
    __occupation_cards: Deck
    __begging_markers: int
    __has_future_goods_on_action_spaces: bool
    __future_goods: list[tuple[int,GoodsType]]
                             # ^^^round_num
    __decision_func_cache: str # str version of func to be executed.
    __decision_args_cache: list[str] # list of types of args required for cached decision func.
    __decision_initial_caller: str # FIXME! Decide if worth it or not...

    def __new__(
            cls,
            game: Game,
            state_server: GameState,
            minor_imp_cards: Deck,
            occup_cards: Deck,
            num_players: int,
            *,
            player_id: int,
            starting: bool = False
        ) -> Self:
        self = super().__new__(cls)
        self.__game = game
        self.__state = state_server
        self.__player_id = player_id
        self.__starting_player = starting
        self.__begging_markers = 0
        if num_players == 1:
            self.__supply = Supply(num_food=0)
        else:
            self.__supply = Supply(num_food=2 if starting else 3)
        self.__farmyard = Farmyard()
        self._init_persons()
        self.__player_major_imp_cards = None
        self.__minor_imp_cards = minor_imp_cards
        self.__occupation_cards = occup_cards
        self.__has_future_goods_on_action_spaces = False
        self.__future_goods = []
        self.__decision_args_cache = []
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

    def grains_or_veg_to_food(self, good_type: GoodsType, number: int) -> None:
        """Player action that can be called at any time turning crops into food."""

    def move_animals_anytime(self) -> None:
        """Player action that can be called at any time moving animals around farmyard."""

    def build_fence(self) -> None:
        """Performs build fence action. Delegates to farmyard's & supply's method."""
        self.__farmyard.build_fence()
        self.__supply.build_fence()

    def get_goods_from_future_action_spaces(self, round_num: int) -> None:
        """If player has items on future action spaces, this add them to player's inventory."""
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
            self.__state.round_server.player_action_server.set_current_player_decision()
        else:
            self.__state.round_server.player_action_server.play_next_player_actions()

    def get_goods(self, action: Action | None = None) -> bool:
        """Gets goods and adds them to inventory."""
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

    def get_animals(self) -> bool:
        """Gets animals and prompts decision of where to place animals."""
        # Check if we have a major improvement for cooking immediately.
        if self.__player_major_imp_cards is not None:
            # If has option to cook, return cook as decision func.
            if (self.__player_major_imp_cards.is_in_deck("2_fireplace")
                or self.__player_major_imp_cards.is_in_deck("3_fireplace")
                or self.__player_major_imp_cards.is_in_deck("4_cooking_hearth")
                or self.__player_major_imp_cards.is_in_deck("5_cooking_hearth")):
                # FIXME!
                self.__decision_func_cache = "self.cook()"
                self.__decision_args_cache.append("")
                return True
        # If no cooking improvement return move_items as decision func.
        # FIXME!
        self.__decision_func_cache = "self.move_items()"
        self.__decision_args_cache.append("")
        return True

    def build_rooms_and_or_stables(self) -> bool:
        """Function from action space allowing building of rooms &| stables."""
        self.__decision_func_cache = "self.choose_room_or_stable('{}')"
        self.__decision_args_cache.extend(["room_or_stable"])
        return True

    def choose_room_or_stable(self, room_or_stable: str) -> bool:
        """Takes choice of room or stable and furthers decision logic for 'farm_expansion'."""
        if room_or_stable not in {"room", "stable"}:
            raise ValueError("Invalid choice, must be either 'room' or 'stable'.")
        if room_or_stable == "room":
            room_or_stable = self.__farmyard.get_house_type()
        # We're for sure using 'farm_expansion' right?
        costs = self.__game.action_spaces.get_action_func_cost('farm_expansion')
        cost_of_interest = costs[room_or_stable]
        if room_or_stable == "stable":
            count = self.__supply.count(cost_of_interest[1])
            if count < cost_of_interest[0]:
# FIXME! Decide if we should actually clear the decision caches or not.
                # Clear func & arg caches.
                self.__decision_func_cache = ""
                self.__decision_args_cache = []
                # If no more decisions set state to next player.
                self.__state.round_server.player_action_server.play_next_player_actions()
                raise ValueError("Not enough resources for requested build.")
        else:
            # For sure some type of room.
            count_1 = self.__supply.count(cost_of_interest[0][1])
            count_2 = self.__supply.count(cost_of_interest[1][1])
            if count_1 < cost_of_interest[0][0] or count_2 < cost_of_interest[1][0]:
# FIXME! Decide if we should actually clear the decision caches or not.
                # Clear func & arg caches.
                self.__decision_func_cache = ""
                self.__decision_args_cache = []
                # If no more decisions set state to next player.
                self.__state.round_server.player_action_server.play_next_player_actions()
                raise ValueError("Not enough resources for requested build.")
        # All checks passed, now choose space to build.
        temp_str = f"self.choose_space(requested_space_type='{room_or_stable}'"
        self.__decision_func_cache = temp_str + ", destination_coord={})"
        self.__decision_args_cache.extend(["Coordinate"])
        return True

    def choose_space(
            self,
            requested_space_type: SpaceType,
            destination_coord: Coordinate
            ) -> bool:
        """Chooses space to try to accomplish action."""
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
        return False

    def decision(self, decision_args: list[str]) -> None:
        """Function to make a decision based on possible options from game effects."""
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
            self.__state.round_server.player_action_server.play_next_player_actions()
        # If more decisions, the functions will have set the func & args caches,
        # so no further action.

    def move_items(self, move_request: MoveRequest) -> None:
        """Player call to move selected item(s) around player controlled spaces."""
        self.__farmyard.move(**move_request)
        self.__game.action_spaces.move(**move_request)
        self.__supply.move(**move_request)

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
