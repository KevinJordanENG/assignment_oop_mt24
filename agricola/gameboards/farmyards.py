"""
Farmyards module containing concrete implementation of individual player boards.
Uses BaseBoard ABC to handle unified board logic.
"""

from typing import TypedDict, cast

from .board import BaseBoard, SpaceData
from ..type_defs import Coordinate, SpaceType, GoodsType, Location

class PerimeterData(TypedDict):
    """Lightweight way of keeping data on current perimeter usage."""
    coordinate: Coordinate
    space_type: SpaceType
    occupied: bool

class Farmyard(BaseBoard):
    """Farmyard is the board given to each player to develop."""

    _valid_perimeters: dict[str, set[Coordinate]]
    _board_perimeters: dict[tuple[str, Coordinate], PerimeterData]

    def __init__(self) -> None:
        """Initializer for Farmyard gameboard(s)."""
        super().__init__()
        # Set board type.
        self._board_type = "farmyard"
        # Set valid spaces.
        self._init_board_spaces()
        # Init perimeter map.
        self._init_perimeter()
        # Init board spaces & perimeters.
        self._populate_spaces()

    @property
    def valid_perimeters(self) -> dict[str, set[Coordinate]]:
        """Property to return read only view of valid perimeter spaces in current board."""
# FIXME! Need to make sure read only
        return self._valid_perimeters

    @property
    def board_perimeters(self) -> dict[tuple[str, Coordinate], PerimeterData]:
        """Property returning read only view of current board perimeter spaces and their data."""
# FIXME! Need to make sure read only
        return self._board_perimeters

    def move(
            self,
            item: GoodsType,
            num_goods: int,
            new_board: Location,
            new_coords: Coordinate,
            prev_board: Location,
            prev_coord: Coordinate
        ) -> None:
        """Farmyard specific move implementation."""
# TODO: Please build!

    def change_space_type(self, coord: Coordinate, space_type: SpaceType) -> None:
        """Changes space type if request is valid/allowed."""
# TODO: Error checking for valid space change reqs.

    def _check_adjacency(self) -> None:
        """"""

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
                elif k == "h" and i in {(2,0), (3,0)}:
                    space_type = "blocked"
                else:
                    space_type = "unused"
                perimeter: PerimeterData = {
                    "coordinate": i,
                    "space_type": cast(SpaceType, space_type),
                    "occupied": True
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
                "accumulate": False,
                "goods_type": None,
                "num_present": 0,
                "action": None
            }
            self._board[j] = space
