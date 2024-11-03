"""
Action spaces module maintaining the main game board.
"""

# TODO: each action space can only be used by 1 person each round

import csv
from typing import Any, Final
from .board import BaseBoard
from ..type_defs import Coordinate


COORD_GROUPS: Final[dict[str, set[Coordinate]]] = {
    "1_and_2_player": set([(0,1), (1,1), (2,1), (3,1), (4,1), (5,1), (1,2), (2,2), (3,2), (4,2)]),
    "3_player_adtl": set([(1,0), (2,0), (3,0), (4,0)]),
    "4_player_adtl": set([(0,0), (1,0), (2,0), (3,0), (4,0), (5,0)]),
    "stage1": set([(0,2), (0,3), (1,3), (2,3)]),
    "stage2": set([(0,4), (1,4), (2,4)]),
    "stage3": set([(0,5), (1,5)]),
    "stage4": set([(0,6), (1,6)]),
    "stage5": set([(0,7), (1,7)]),
    "stage6": set([(0,8)])
}
"""
Dict containing named sets of coordinates per stage as defined in rulebook.
Marked as Final as these sets are predefined and illegal to modify.
"""


class ActionSpaces(BaseBoard):
    """Action spaces is the class for the main shared gameboard."""

    __csv_data: dict[str, Any] # Any is used here until length/types of trailing CSV data is known.

    def __init__(self, num_players: int = 1) -> None:
        """Initializer for Action Spaces gameboard."""
        # TODO: make sure not already created, maybe singleton within Game instance?
        super().__init__()
        # Set board type.
        self._board_type = "action_space"
        # Initialize starting spaces config depending on num_players.
        self._init_board_spaces(num_players)
        # Populate initial spaces.
        self._populate_spaces()

    def _init_board_spaces(self, num_players: int) -> None:
        """Initializes specific action spaces board based on number of players."""
        if num_players in (1,2):
            self._valid_spaces = COORD_GROUPS["1_and_2_player"]
        elif num_players == 3:
            self._valid_spaces = COORD_GROUPS["1_and_2_player"] | COORD_GROUPS["3_player_adtl"]
        elif num_players == 4:
            self._valid_spaces = COORD_GROUPS["1_and_2_player"] | COORD_GROUPS["4_player_adtl"]

    def _populate_spaces(self) -> None:
        """Populates gameboard initial coordinates with SpaceData."""
        self.__csv_data = {}
        self._load_csv()

    def _add_action_space(self, stage: int) -> None:
        """Adds action space (once per round) from remaining actions per stage."""
        # TODO: Use `ast.literal_eval("(2,3)")` for converting from strTup -> tuple.

    def _load_csv(self) -> None:
        """Handles CSV loading for actions spaces data loading."""
        with open("./agricola/data/actions.csv", 'r', encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                self.__csv_data[row.pop("key")] = row
        # TODO: need to make sure final CSV has no trailing comma otherwise adds extra empty k/v
