"""
Action spaces module maintaining the main game board.
"""
from __future__ import annotations
import os
import csv
import ast
import random
from typing import Any, Final, cast, get_args, TYPE_CHECKING
from .board import BaseBoard, SpaceData
from ..type_defs import Coordinate, Action, GoodsType, SpaceType, GameStates
if TYPE_CHECKING:
    from ..game import Game

ActionCSVLine = tuple[Action, dict[str, Any]]
"""
Type Alias used locally in action spaces frequently representing one line of loaded CSV.
Each CSV line contains all data of a specific action space.
Uses 'Any' purposefully as values loaded represent functional data.
Examples are coordinate tuples, integer values of goods quantity, etc.
Decision was made to immediately evaluate these read in CSV str into their proper datatype
instead of waiting for their needed use to evaluate them, except reserved names and functions.
"""


START_COORDS: Final[dict[str, set[Coordinate]]] = {
    "1_and_2_player": set([(0,1), (1,1), (2,1), (3,1), (4,1), (5,1), (1,2), (2,2), (3,2), (4,2)]),
    "3_player_adtl": set([(1,0), (2,0), (3,0), (4,0)]),
    "4_player_adtl": set([(0,0), (1,0), (2,0), (3,0), (4,0), (5,0)])
}
"""
Dict containing named sets of starting coordinates as defined in rulebook.
Marked as Final as these sets are predefined and illegal to modify.
"""


ROUND_COORDS: Final[list[Coordinate]] = [
    (0,2), (0,3), (1,3), (2,3), # Phase 1
    (0,4), (1,4), (2,4), # Phase 2
    (0,5), (1,5), # Phase 3
    (0,6), (1,6), # Phase 4
    (0,7), (1,7), # Phase 5
    (0,8) # Phase 6
]
"""List containing ordered coordinates available per stage as defined in rulebook."""


# TODO: change these to real functions once they exist
FuncNoEval = set([
    "PLAY_MINOR_IMPR||PLAY_MAJOR_IMPR",
    "BUILD_FENCES",
    "SOW||BAKE_BREAD",
    "GET_ANIMAL",
    "HAVE_KIDS+PLAY_MINOR_IMPR",
    "RENOVATION+PLAY_MAJOR_IMPR||PLAY_MINOR_IMPR",
    "HAVE_KIDS",
    "PLOW+SOW",
    "RENOVATION+BUILD_FENCES",
    "GET_MARKET_GOODS",
    "self.get_goods(action='forest')",
    "self.get_goods(action='grain_seeds')",
    "self.get_goods(action='day_laborer')",
    "self.get_goods(action='clay_pit')",
    "self.get_goods(action='reed_bank')",
    "self.get_goods(action='fishing')",
    "self.get_goods(action='western_quarry')",
    "self.get_goods(action='vegetable_seeds')",
    "self.get_goods(action='eastern_quarry')",
    "self.get_goods(action='copse')",
    "self.get_goods(action='grove')",
    "self.get_goods(action='3_hollow')",
    "self.get_goods(action='4_hollow')",
    "self.get_goods(action='traveling_players')",
    "self.build_rooms_and_or_stables()",
    "self.take_start_player_token()",
    "self.plow()",
    "self.choose_occupation_to_play(action='lessons')",
    "self.choose_occupation_to_play(action='3_lessons')",
    "self.choose_occupation_to_play(action='4_lessons')"
])
"""Set of functions used to call action space effects, stored in dict as str."""


NoEvalTokens: set[str] = set(get_args(GoodsType)) | set(get_args(SpaceType)) | FuncNoEval
"""
Special set of tokens to NOT eval when loading CSV.
This is used to preserve str names and str representation of function calls to execute actions.
"""


class ActionSpaces(BaseBoard):
    """Action spaces is the class for the main shared gameboard."""

    # Any is used here as values in dict are intentionally varied for functionality.
    __csv_data: dict[Action, dict[str, Any]]

    def __init__(self, game: Game, num_players: int, path: str) -> None:
        """Initializer for Action Spaces gameboard."""
        super().__init__()
        self._game = game
        # Set board type.
        self._board_type = "action_space"
        # Initialize starting spaces config depending on num_players.
        self.__init_board_spaces(num_players)
        # Populate initial spaces.
        self.__populate_spaces(num_players, path)

    def get_action_function(self, action: Action) -> str:
        """Gets the function (as str) associated with action key."""
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
            "running_round_harvest"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        return str(self.__csv_data[action]["func"])

    def get_action_func_output(self, action: Action) -> Any: # Any used here as output is varied.
        """Gets the output from specified action key."""
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
            "running_round_harvest"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        return self.__csv_data[action]["output"]

    def get_action_func_cost(self, action: Action) -> Any: # Any used here as cost is varied.
        """Gets the cost of specified action key."""
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
            "running_round_harvest"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        return self.__csv_data[action]["costs"]

    def get_space_data_from_action(self, action: Action) -> tuple[Coordinate, SpaceData] | None:
        """Returns space data for requested action key."""
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
            "running_round_harvest"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        for key, value in self._board.items():
            if value["action"] == action:
                return (key, value)
        return None

    def add_action_space(self, round_num: int, stage: int) -> None:
        """Public method to add action space."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"running_round_prep"}
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        line: ActionCSVLine = self.__fetch_csv_line(round_num=round_num, stage=stage)
        self._board[ROUND_COORDS[round_num-1]] = self.__bundle_space_data(line)
        self._valid_spaces.add(ROUND_COORDS[round_num-1])

    def accumulate_all(self) -> None:
        """Increases all accumulation spaces' goods by their respective amount."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"running_round_prep"}
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        for data in self._board.values():
            if data["accumulate"]:
                data["num_present"] += data["accum_number"]

    def __init_board_spaces(self, num_players: int) -> None:
        """Initializes specific action spaces board based on number of players."""
        if num_players in (1,2):
            self._valid_spaces = START_COORDS["1_and_2_player"]
        elif num_players == 3:
            self._valid_spaces = START_COORDS["1_and_2_player"] | START_COORDS["3_player_adtl"]
        elif num_players == 4:
            self._valid_spaces = START_COORDS["1_and_2_player"] | START_COORDS["4_player_adtl"]

    def __populate_spaces(self, num_players: int, path: str) -> None:
        """Populates gameboard initial coordinates with SpaceData."""
        self.__csv_data = {}
        self.__load_csv(path)
        for space in self._valid_spaces:
            line = self.__fetch_csv_line(round_num=0, space=space)
            self._board[space] = self.__bundle_space_data(line, num_players)

    def __find_in_csv_data(self, key: str, value: Any) -> ActionCSVLine:
        """Iterates over all action items looking in their dicts for specified k/v pair."""
        ans = None
        for line in self.__csv_data.items():
            if line[1][key] == value:
                ans = line
                break
        if ans is None:
            raise ValueError("Key / value pair for action data in CSV not found.")
        return ans

    def __select_rand_round_action(self, round_num: int, stage: int) -> ActionCSVLine:
        """Randomly selects from remaining stage action spaces for the stage."""
        sub_set = []
        for item in self.__csv_data.items():
            if (item[1]["stage"] == stage) and (item[1]["coord"] == (-1,-1)):
                sub_set.append(item)
        rnd = random.randint(0, len(sub_set)-1)
        sub_set[rnd][1]["coord"] = ROUND_COORDS[round_num-1]
        return sub_set[rnd]

    def __fetch_csv_line(
            self,
            *,
            round_num: int,
            stage: int = 0,
            space: Coordinate|None = None
        ) -> ActionCSVLine:
        """
        Fetches loaded CSV line info from stored dict.
        
        If stage provided (0<stage<7), then selects at random from remaining stage actions.
        If space provided (Coord.), then selects the action at this space.
        """
        if space is not None and stage == 0:
            return self.__find_in_csv_data("coord", space)
        if space is None and (0 < stage < 7):
            return self.__select_rand_round_action(round_num, stage)
        raise ValueError(
            "Cannot request action space by both coordinate and stage at same time."
        )

    def __bundle_space_data(self, csv_line: ActionCSVLine, num_players: int = -1) -> SpaceData:
        """Adds action space (once per round) from remaining actions per stage."""
        if csv_line[0] == "forest" and num_players == 1:
            csv_line[1]["num_good"] = 2
        space_data: SpaceData = {
            "coordinate": csv_line[1]["coord"],
            "space_type": "action",
            "occupied": False,
            "child": False,
            "stabled": False,
            "accumulate": csv_line[1]["accum"],
            "accum_number": csv_line[1]["num_good"],
            "goods_type": csv_line[1]["goods_type"],
            "num_present": 0,
            "action": csv_line[0]
        }
        return space_data

    def __load_csv(self, path: str) -> None:
        """Handles CSV loading for actions spaces data loading."""
        with open(os.path.join(path, "actions.csv"), 'r', encoding="utf-8") as data:
            dict_reader = csv.DictReader(data)
            for row in dict_reader:
                self.__csv_data[action := cast(Action, row.pop("key"))] = {}
                for k, v in row.items(): #^^^^ All keys will be part of this type alias, so cast.
                    # Uses NoEvalTokens to keep select values as str for names or later execution.
                    if v in NoEvalTokens:
                        self.__csv_data[action][k] = v
                    else:
                        self.__csv_data[action][k] = ast.literal_eval(v)
