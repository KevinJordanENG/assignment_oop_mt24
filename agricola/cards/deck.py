"""
Deck module is a composition of major & minor improvements plus occupations.

Allows for bulk operations on cards such as init.
"""

from __future__ import annotations
from contextlib import contextmanager
import os
import csv
import ast
import random
from types import MappingProxyType
from typing import (
    Any,
    ClassVar,
    Iterator,
    Mapping,
    Self,
    cast,
    get_args,
    TYPE_CHECKING,
)
from .major_improvements import MajorImprovement
from .minor_improvements import MinorImprovement
from .occupations import Occupation
from .card import CardDictKeys
from ..type_defs import (
    MajorImproveNames,
    MinorImproveNames,
    OccupationNames,
    SpaceType,
    GameStates,
)

if TYPE_CHECKING:
    from ..game import Game


FuncNoEval = set(
    [
        "COOK||BAKE_BREAD",
        "GET_1_FOOD_NXT_X_RNDS",
        "BAKE_BREAD",
        "JOIN_POT_BASKET",
        "GET_GOODS",
        "INCREASE_PASTURE_CAPACITY",
        "ADD_CLAY_TO_FENCE_BUILD_MAT",
        "PLOW_FUTURE",
        "EXTRA+BAKE_BREAD",
        "USE_OCCUP_HAVE_KIDS",
        "GET_3_ME_1_OTHERS_FOOD_WHEN_CATTLE_MARKET_USE",
        "CHECK_GOT_7_BUILD_GOODS",
        "GET_1_FOOD_WHEN_PLAY_IMP",
        "TRADE_WOOD_FOOD_ON_WOOD_ACCUM",
        "UP_FOOD_FROM_BAKE_BREAD_AFTR_HARV",
        "EXTRA_GRAIN_WHEN_GRAIN_SEEDS_ACT",
        "GET_FUTURE_4_7_9_PLUS_ROUND",
        "MOVE_CROP_FROM_PLANTED_TO_NEW_FIELD",
        "DECREASE_WOOD_IMPR_COST",
        "MORE_GOODS_WHEN_FISH",
        "MORE_STONE_ON_ACCUM",
        "MORE_SHEEP",
        "FREE_FENCED_SPACE",
        "EXTRA_SPACE_1_PERSON",
        "DECREASE_WOOD_ROOM_COST",
        "FREE_STABLE_WHN_RENO",
        "PLOW_FUTURE_2X_ON_FARMLAND_ACT",
        "MOVE_2_PERS_IF_1_USE_MEAT_MRKT",
        "EXTRA_WHEN_PLY_OCCUP+BAKE_BREAD",
        "RENO_PROHIBIT",
        "HARVEST+COUNT_GOODS+GET_GOODS",
        "GET_1_FOOD_NXT_X_RNDS+WHEN_FISH",
        "USE_ACT_ABOVE_FISHING",
        "EXTRA_FOOD_IF_WOOD_ROOM_START_RND",
        "CHECK_FARMLAND_OCCUP_WHEN_PLAY_GRAIN_SEEDS",
        "GET_FUTURE_RND_5_8_11_14",
        "EXTRA_FIELD",
        "GET_FUTURE_EVEN_RNDS",
        "EXTRA_WHN_USE_DAY_LABORER+GET_GOODS",
        "EXCHANGE",
        "GET_FUTURE_10_11",
        "ALL_FARM_SPACE_USED",
        "EXACTLY_2_OCCUP",
        "MAX_3_OCCUP",
        "CLAY_OR_STONE_HOUSE",
        "IS_PERSON_FISHING",
        "TIMES_ROUNDS_LEFT",
        "+TIMES_ROUNDS_LEFT",
        "GET_GOODS+INCR_PETS_1_P_ROOM",
        "DIRECT_WOOD_TO_STONE_RENO",
        "3_FREE_FENCES_ON_BUILD_FENCES_ACT",
        "IF_STONE_HOUSE",
        "TAKE_ACT_W_KID_IMMEDIATE",
        "TRADE_WOOD_FOOD_ON_WOOD_ACCUM",
        "CLAY_ROOM_BUILD_OR_RENO_TO_STONE+GET_GOODS",
        "WHN_BUILD_ROOM+GET_1_FOOD_NXT_X_RNDS",
        "GET_GOODS+HARVEST_EXTRA_GRAIN",
        "EXTRA_WHN_USE_DAY_LABORER",
        "MORE_WOOD_ON_ACCUM",
        "EXTRA_WHN_FARMLAND_GRAIN_SEEDS_GRAIN_UTIL_CULTIVATION",
        "IF_CLAY_HOUSE+GET_CLAY_NEXT_5_RNDS",
        "IF_CLAY_HOUSE+COUNT_ROOMS",
        "USE_FISHING+EXCHANGE",
        "DECREASE_IMPR_COST",
        "MEAT_MRKT_USE+GET_GOODS",
        "EXTRA+USE_TRAVELING_PLAYERS",
        "GET_WHEN_OTHERS_USE_TRAVELING_PLAYERS+EXCHANGE",
        "GET_GOODS+BOAR_BREED_FUTURE_12",
        "BUILD_ROOM_OR_RENO_WHN_PLY_DAY_LABORER",
        "GET_GOODS+IF_STONE_HOUSE+BUILD_STABLE_1_WOOD",
        "USE_DAY_LABORER+PLOW",
        "DECREASE_IMPR_STONE_COST+COUNT_ROOMS",
        "IF_STONE_HOUSE+PLAY_OCCUP_OR_MINOR",
        "IF_STONE_HOUSE+GET_3_FOOD_REMAIN_RNDS",
        "USE_WOOD_ACCUM+BAKE_BREAD",
        "COUNT_OCCUP+EXCHANGE",
        "COUNT_ROOMS+COUNT_PEOPLE+GET_GOODS",
        "COUNT_ROOMS",
        "USE_FOREST_REED_BANK_CLAY_PIT+GET_GOODS",
        "COUNT_ROOMS+EXCHANGE",
        "DECREASE_IMPR_COST_BY_2",
        "USE_GRAIN_SEEDS+EXTRA+GET_GOODS",
        "USE_WOOD_INSTD_REED_WHN_ROOM_BUILD_OR_RENO",
        "USE_RESOURCE_MRKT+GET_GOODS",
        "GET_FUTURE_2_5_8_10_PLUS_RND",
        "USE_GRAIN_SEEDS+EXCHANGE",
        "PLAYER_W_MOST_ROOMS",
        "EACH_OCCUP_AFTER_THIS",
        "EACH_PASTURE_W_1_AND_SPACE_FOR_3_MORE",
        "PER_UNFENCED_STABLE",
        "GET_ANIMAL",
        "MEAT_MRKT_USE+GET_ANIMAL",
        "GET_ANIMAL+BOAR_BREED_FUTURE_12",
        "GET_GOODS||GET_ANIMAL",
        "plow()",
    ]
)
# TODO: replace with real funcs as ready.


NoEvalTokens: set[str] = set(get_args(SpaceType)) | FuncNoEval
"""
Special set of tokens to NOT eval when loading CSV.
This is used to preserve str names and str representation of function calls to execute actions.
"""


class Deck:
    """
    Deck class is a composition class allowing uniform batch operations on card types.
    """

    __is_constructing_cards: ClassVar[bool] = False

    @staticmethod
    def _is_constructing_cards() -> bool:
        """Class wide flag ensuring Cards are only instantiated by Deck via context manager."""
        return Deck.__is_constructing_cards

    @staticmethod
    @contextmanager
    def __constructing_cards() -> Iterator[None]:
        """
        Context manager helping ensure objects are only instantiated by 'Deck' not Agricola user directly.
        """
        assert not Deck.__is_constructing_cards
        Deck.__is_constructing_cards = True
        try:
            yield None
        finally:
            Deck.__is_constructing_cards = False

    __game: Game
    __deck_type: str
    __cards: dict[
        CardDictKeys, MajorImprovement | MinorImprovement | Occupation
    ]

    def __new__(
        cls,
        game: Game,
        deck_type: str,
        *,
        path: str | None,
        num_players: int = 2,
    ) -> Self:
        """Constructor for decks using Game's context manager to ensure not build directly."""
        # Dynamic to avoid circular imports, and error if not being built in proper context.
        from ..game import Game

        if not Game._is_constructing_decks():
            raise TypeError(
                "Decks can only be instantiated by 'Game' or 'Player', not directly."
            )
        # Construct.
        self = super().__new__(cls)
        self.__game = game
        self.__deck_type = deck_type
        # If we have a path, we're loading in from CSV for init.
        if path is not None:
            # Set manager for valid Card creation context.
            with Deck.__constructing_cards():
                self.__load_csv(path, num_players)
        # Otherwise we're dynamically creating new empty Deck somewhere within the game.
        else:
            # TODO: Add player context manager checks for Major Imps.
            self.__cards = {}
        return self

    @property
    def deck_type(self) -> str:
        """Get type of deck."""
        return self.__deck_type

    @property
    def cards(
        self,
    ) -> Mapping[
        CardDictKeys, MajorImprovement | MinorImprovement | Occupation
    ]:
        """Property to return read only view of cards in this deck object."""
        return MappingProxyType(self.__cards)

    def is_in_deck(self, card_name: CardDictKeys) -> bool:
        """Returns bool if card of specified key exists in deck or not."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "not_started",
            "finished",
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        for key in self.__cards:
            if key == card_name:
                return True
        return False

    def get_prereqs_minor_imp(
        self, key: MinorImproveNames
    ) -> Any:  # Any used as various types/structures of prereqs.
        """Gets prerequisites for playing minor improvement."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"current_player_decision"}
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        return self.__cards[key].attributes["prereq"]

    def get_build_cost(self, key: CardDictKeys) -> Any:  # Cost is varied.
        """Fetches the build cost of requested card."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "not_started",
            "finished",
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        if self.deck_type == "occupation":
            raise ValueError("Occupations do not have 'build_cost' attribute.")
        return self.__cards[key].attributes["build_cost"]

    def get_func_cost(self, key: CardDictKeys) -> Any:  # Cost is varied.
        """Fetches the build cost of requested card."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "not_started",
            "finished",
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        return self.__cards[key].attributes["func_cost"]

    def count_num_played(self) -> int:
        """Counts the number of cards played in given hand/deck."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "finished",
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        count = 0
        for card in self.__cards.values():
            if card.played:
                count += 1
        return count

    def _get_seven_rand_cards(self) -> Deck:
        """
        Returns a deck of 7 random cards for player init.

        Also removes these cards from global/game scope so no 2 players can get the same card.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        # Only applies to occupations & minor improvements so check for this.
        if self.__deck_type == "major":
            raise ValueError(
                "Getting 7 cards is for occupations & minor improvements only."
            )
        # Create a new (empty) deck to return. Only ever called in Game init so will be in proper context there.
        seven_cards = Deck(self.__game, self.deck_type, path=None)
        # Get 7 random cards.
        rand_keys: list[CardDictKeys] = random.sample(
            list(self.__cards.keys()), 7
        )
        # Add them to new deck & remove from main deck.
        for key in rand_keys:
            seven_cards._add_card_to_deck(key, self.__cards[key])
            self.__cards.pop(key)
        return seven_cards

    def _add_card_to_deck(
        self,
        key: CardDictKeys,
        card: MajorImprovement | MinorImprovement | Occupation,
    ) -> None:
        """Adds card to deck from attributes & names."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "not_started",
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        # Error check request card & deck type match.
        if self.__deck_type == "major":
            if key not in get_args(MajorImproveNames):
                raise ValueError("Invalid card/key for deck type.")
        elif self.__deck_type == "minor":
            if key not in get_args(MinorImproveNames):
                raise ValueError("Invalid card/key for deck type.")
        elif self.__deck_type == "occupation":
            if key not in get_args(OccupationNames):
                raise ValueError("Invalid card/key for deck type.")
        self.__cards[key] = card

    def _play_card(self, key: CardDictKeys) -> str | None:
        """Plays card from deck. Protected as should only be invoked by 'Player' object, not user."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        self.__cards[key]._set_played()
        return self.__cards[key].func

    def _pop(
        self, key: CardDictKeys
    ) -> MajorImprovement | MinorImprovement | Occupation:
        """
        Pops card from deck.

        Pop is a well known func and is exposed here to simplify popping a Card and supports
        syntax of my_deck._pop() vs my_deck.cards.pop() for intuitive UX.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
        }
        self.__game.state._is_valid_state_for_func(
            self.__game.game_state, valid_states
        )
        card = self.__cards[key]
        del self.__cards[key]
        return card

    def __load_major(self, path: str) -> None:
        """Loads deck with all major improvement cards."""
        with open(path, "r", encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                # Get name of card.
                name = cast(MajorImproveNames, row.pop("key"))
                # Get all its various attributes.
                attributes: dict[str, Any] = {}
                for k, v in row.items():
                    if v in NoEvalTokens:
                        attributes[k] = v
                    else:
                        attributes[k] = ast.literal_eval(v)
                # Build card.
                card = MajorImprovement(self.__game, name, attributes)
                self.__cards[name] = card

    def __load_minor(self, path: str) -> None:
        """Loads deck with all minor improvement cards."""
        with open(path, "r", encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                # Get name of card.
                name = cast(MinorImproveNames, row.pop("key"))
                # Get all its various attributes.
                attributes: dict[str, Any] = {}
                for k, v in row.items():
                    if v in NoEvalTokens:
                        attributes[k] = v
                    else:
                        attributes[k] = ast.literal_eval(v)
                # Build card.
                card = MinorImprovement(self.__game, name, attributes)
                self.__cards[name] = card

    def __load_occup(self, path: str, num_players: int) -> None:
        """Loads deck with occupation cards based on num_players."""
        with open(path, "r", encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                # Check here if it belongs in this num_player version of deck.
                if int(row["num_players"]) > num_players:
                    continue
                # Get name of card.
                name = cast(OccupationNames, row.pop("key"))
                # Get all its various attributes.
                attributes: dict[str, Any] = {}
                for k, v in row.items():
                    if v in NoEvalTokens:
                        attributes[k] = v
                    else:
                        attributes[k] = ast.literal_eval(v)
                # Build card.
                card = Occupation(self.__game, name, attributes)
                self.__cards[name] = card

    def __load_csv(self, path: str, num_players: int) -> None:
        """Loads card data from CSV for specified card type."""
        # Decide what deck type and how to init.
        self.__cards = {}
        if self.__deck_type == "major":
            self.__load_major(os.path.join(path, "major.csv"))
        elif self.__deck_type == "minor":
            self.__load_minor(os.path.join(path, "minor.csv"))
        elif self.__deck_type == "occupation":
            self.__load_occup(os.path.join(path, "occupation.csv"), num_players)
        else:
            raise ValueError("Received bad deck card type specifier.")
