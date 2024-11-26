"""
Farmyards module containing concrete implementation of individual player boards.
Uses BaseBoard ABC to handle unified board logic.
"""
from __future__ import annotations
from typing import TypedDict, cast, TYPE_CHECKING

from .board import BaseBoard, SpaceData
from ..type_defs import Coordinate, SpaceType, Axis, GameStates
if TYPE_CHECKING:
    from ..game import Game


class PerimeterData(TypedDict):
    """Lightweight way of keeping data on current perimeter usage."""
    coordinate: Coordinate
    space_type: SpaceType
    occupied: bool


class Farmyard(BaseBoard):
    """Farmyard is the board given to each player to develop."""

    _valid_perimeters: dict[Axis, set[Coordinate]]
    _board_perimeters: dict[tuple[Axis, Coordinate], PerimeterData]

    def __init__(self, game: Game) -> None:
        """Initializer for Farmyard gameboard."""
        super().__init__()
        self._game = game
        # Set board type.
        self._board_type = "farmyard"
        # Set valid spaces.
        self._init_board_spaces()
        # Init perimeter map.
        self._init_perimeter()
        # Init board spaces & perimeters.
        self._populate_spaces()

    @property
    def valid_perimeters(self) -> dict[Axis, set[Coordinate]]:
        """Property to return read only view of valid perimeter spaces in current board."""
# FIXME! Need to make sure read only
        return self._valid_perimeters

    @property
    def board_perimeters(self) -> dict[tuple[Axis, Coordinate], PerimeterData]:
        """Property returning read only view of current board perimeter spaces and their data."""
# FIXME! Need to make sure read only
        return self._board_perimeters

    @property
    def open_perimeters(self) -> dict[Axis, set[Coordinate]]:
        """Returns read only view of open perimeter spaces."""
# FIXME! Need to make sure read only
        sub_dict: dict[Axis, set[Coordinate]] = {"v": set(), "h": set()}
        for tup, data in self._board_perimeters.items():
            if not data["occupied"]:
                sub_dict[tup[0]].add(tup[1])
        return sub_dict

    def build_fence(self) -> None:
        """Performs build fence action. Can only move fence from inventory to farmyard."""
        raise NotImplementedError()

    def change_space_type(self, space_type: SpaceType, coord: Coordinate) -> None:
        """Changes space type (assumes the check_space_change_validity() func already called)."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        self._board[coord]["space_type"] = space_type

    def check_space_change_validity(self, space_type: SpaceType, coord: Coordinate) -> bool:
        """Returns bool if requested new space type is valid at specified coord."""
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
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        # Handle room requests.
        if space_type in {"wood_room", "clay_room", "stone_room"}:
            valid_adj = self._check_adjacency(space_type, coord)
            valid_current = (self._board[coord]["space_type"] == "unused"
                             and not self._board[coord]["stabled"])
            return valid_adj and valid_current
        if space_type == "field":
            return self._board[coord]["space_type"] == "unused"
# FIXME! add logic for other change requests
        return False

    def get_house_type(self) -> SpaceType:
        """Checks & returns house type."""
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
            "running_round_harvest"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        house_type = None
        for space_data in self._board.values():
            if space_data["space_type"] in {"wood_room", "clay_room", "stone_room"}:
                house_type = space_data["space_type"]
        if house_type is None:
            raise ValueError("Could not determine house type.")
        return house_type

    def _check_adjacency(self, space_type: SpaceType, coord: Coordinate) -> bool:
        """Checks that all adjacent spaces are of valid type for request."""
        row, col = coord[0], coord[1]
        # False if off the board, else check if its same type.
        up = False if row-1 < 0 else (self._board[(row-1,col)]["space_type"] == space_type)
        down = False if row+1 > 2 else (self._board[(row+1,col)]["space_type"] == space_type)
        left = False if col-1 < 0 else (self._board[(row,col-1)]["space_type"] == space_type)
        right = False if col+1 > 4 else (self._board[(row,col+1)]["space_type"] == space_type)
        return up or down or left or right

    def _init_board_spaces(self) -> None:
        """Sets the valid spaces for a farmyard."""
        self._valid_spaces = set([(0,0), (0,1), (0,2), (0,3), (0,4),
                                  (1,0), (1,1), (1,2), (1,3), (1,4),
                                  (2,0), (2,1), (2,2), (2,3), (2,4)])

    def _init_perimeter(self) -> None:
        """Initializes the possible perimeter spaces of farmyard."""
        vertical = set([(0,0), (0,1), (0,2), (0,3), (0,4), (0,5),
                        (1,0), (1,1), (1,2), (1,3), (1,4), (1,5),
                        (2,0), (2,1), (2,2), (2,3), (2,4), (2,5)])
        horizontal = set([(0,0), (0,1), (0,2), (0,3), (0,4),
                          (1,0), (1,1), (1,2), (1,3), (1,4),
                          (2,0), (2,1), (2,2), (2,3), (2,4),
                          (3,0), (3,1), (3,2), (3,3), (3,4)])
        self._valid_perimeters = {"v": vertical, "h": horizontal}
        self._board_perimeters = {}

    def _populate_spaces(self) -> None:
        """Populates initial space values for game start."""
        # Assign perimeters with blocked if starting houses in the way.
        for k, v in self._valid_perimeters.items():
            for i in iter(v):
                if k == "v" and i in {(1,0), (2,0)}:
                    space_type = "blocked"
                    occ = True
                elif k == "h" and i in {(2,0), (3,0)}:
                    space_type = "blocked"
                    occ = True
                else:
                    space_type = "unused"
                    occ = False
                perimeter: PerimeterData = {
                    "coordinate": i,
                    "space_type": cast(SpaceType, space_type),
                    "occupied": occ
                }
                self._board_perimeters[(k, i)] = perimeter
        # Assign spaces as unused unless starting houses.
        for j in iter(self._valid_spaces):
            if j in {(1,0), (2,0)}:
                space_type = "wood_room"
            else:
                space_type = "unused"
            space: SpaceData = {
                "coordinate": j,
                "space_type": cast(SpaceType, space_type),
                "occupied": False,
                "child": False,
                "stabled": False,
                "accumulate": False,
                "accum_number": 0,
                "goods_type": None,
                "num_present": 0,
                "action": None
            }
            self._board[j] = space
