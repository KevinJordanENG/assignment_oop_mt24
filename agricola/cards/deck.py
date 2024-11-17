"""
Deck module is a composition of major & minor improvements plus occupations.

Allows for bulk operations on cards such as init.
"""

from __future__ import annotations
import os
import csv
import ast
import random
from typing import Any, Self, cast, get_args

from .major_improvements import MajorImprovement
from .minor_improvements import MinorImprovement
from .occupations import Occupation
from .card import CardDictKeys
from ..type_defs import MajorImproveNames, MinorImproveNames, OccupationNames, SpaceType


FuncNoEval = set([
    "COOK||BAKE_BREAD",
    "GET_1_FOOD_NXT_X_RNDS",
    "BAKE_BREAD",
    "JOIN_POT_BASKET",
    "PLOW",
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
    "PER_UNFENCED_STABLE"
])

NoEvalTokens: set[str] = set(get_args(SpaceType)) | FuncNoEval

class Deck:
    """
    Deck class is a composition class allowing uniform batch operations on card types.
    """

    __deck_type: str
    __cards: dict[CardDictKeys, MajorImprovement|MinorImprovement|Occupation]

    def __new__(cls, deck_type: str, *, path: str | None, num_players: int = 2) -> Self:
        """Constructor for decks."""
        self = super().__new__(cls)
        self.__deck_type = deck_type
        if path is not None:
            self._load_csv(path, num_players)
        else:
            self.__cards = {}
        return self

    @property
    def deck_type(self) -> str:
        """Get type of deck."""
        return self.__deck_type

    @property
    def cards(self) -> dict[CardDictKeys, MajorImprovement|MinorImprovement|Occupation]:
        """Property to return read only view of cards in this deck object."""
# FIXME! Need to make sure read only
        return self.__cards

    def get_seven_rand_cards(self) -> Deck:
        """
        Returns a deck of 7 random cards for player init.
        
        Also removes these cards from global/game scope so no 2 players can get the same card.
        """
        # Only applies to occupations & minor improvements so check for this.
        if self.__deck_type == "major":
            raise ValueError("Getting 7 cards is for occupations & minor improvements only.")
        # Create a new (empty) deck to return.
        seven_cards = Deck(self.deck_type, path=None)
        # Get 7 random cards.
        rand_keys: list[CardDictKeys] = random.sample(list(self.__cards.keys()), 7)
        # Add them to new deck & remove from main deck.
        for key in rand_keys:
            seven_cards.add_card_to_deck(key, self.__cards[key])
            self.__cards.pop(key)
        return seven_cards

    def get_next_action_space(self) -> None:
        """"""

    def add_card_to_deck(
            self,
            key: CardDictKeys,
            card: MajorImprovement|MinorImprovement|Occupation
        ) -> None:
        """Adds card to deck from attributes & names."""
        self.__cards[key] = card


    def _load_major(self, path: str) -> None:
        """Loads deck with all major improvement cards."""
        with open(path, 'r', encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                name = cast(MajorImproveNames, row.pop("key"))
                attributes: dict[str, Any] = {}
                for k, v in row.items():
                    if v in NoEvalTokens:
                        attributes[k] = v
                    else:
                        attributes[k] = ast.literal_eval(v)
                card = MajorImprovement(name, attributes)
                self.__cards[name] = card


    def _load_minor(self, path: str) -> None:
        """Loads deck with all minor improvement cards."""
        with open(path, 'r', encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                name = cast(MinorImproveNames, row.pop("key"))
                attributes: dict[str, Any] = {}
                for k, v in row.items():
                    if v in NoEvalTokens:
                        attributes[k] = v
                    else:
                        attributes[k] = ast.literal_eval(v)
                card = MinorImprovement(name, attributes)
                self.__cards[name] = card

    def _load_occup(self, path: str, num_players: int) -> None:
        """Loads deck with occupation cards based on num_players."""
        with open(path, 'r', encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                # Check here if it belongs in this num_player version of deck.
                if int(row["num_players"]) > num_players:
                    continue
                name = cast(OccupationNames, row.pop("key"))
                attributes: dict[str, Any] = {}
                for k, v in row.items():
                    if v in NoEvalTokens:
                        attributes[k] = v
                    else:
                        attributes[k] = ast.literal_eval(v)
                card = Occupation(name, attributes)
                self.__cards[name] = card

    def _load_csv(self, path: str, num_players: int) -> None:
        """Loads card data from CSV for specified card type."""
        # Decide what deck type and how to init.
        self.__cards = {}
        if self.__deck_type == "major":
            self._load_major(os.path.join(path, "major.csv"))
        elif self.__deck_type == "minor":
            self._load_minor(os.path.join(path, "minor.csv"))
        elif self.__deck_type == "occupation":
            self._load_occup(os.path.join(path, "occupation.csv"), num_players)
        else:
            raise ValueError("Received bad deck card type specifier.")
