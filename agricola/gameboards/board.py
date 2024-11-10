"""
Module defining ABC BaseBoard to be inherited from by 'farmyards' and 'action_spaces'.
"""
from abc import ABCMeta, abstractmethod
from typing import TypedDict

from ..type_defs import Coordinate, Location, GoodsType, SpaceType, Action


class SpaceData(TypedDict):
    """TypedDict defining metadata about respective space."""
    coordinate: Coordinate
    space_type: SpaceType
    occupied: bool
    accumulate: bool
    goods_type: GoodsType | None
    num_present: int
    action: Action | None


class BaseBoard(metaclass=ABCMeta):
    """Abstract Base Class of gameboards/spaces."""

    # Protected attributes allowing extension from inherited concrete class.
    _board_type: Location
    _valid_spaces: set[Coordinate]
    _board: dict[Coordinate, SpaceData]

    @abstractmethod
    def __init__(self) -> None:
        """
        Abstract as the required constructors for different board types are varied.
        
        Initializes empty structs as MyPy thinks unsafe to Call to abstract method
        "__init__" of "BaseBoard" with trivial body via super() from subclasses.
        """
        self._valid_spaces = set()
        self._board = {}

    @property
    def board_type(self) -> Location:
        """Property to check type of current board."""
        return self._board_type

    @property
    def valid_spaces(self) -> set[Coordinate]:
        """Property to return read only view of valid spaces in current board."""
# FIXME! Need to make sure read only
        return self._valid_spaces

    @property
    def board(self) -> dict[Coordinate, SpaceData]:
        """Property returning read only view of current board spaces and their data."""
# FIXME! Need to make sure read only
        return self._board

    @property
    def open_spaces(self) -> set[Coordinate]:
        """Returns read only view of open spaces on current board, delegates to 'is_occupied()'."""
# FIXME! Need to make sure read only
        return set(coord for coord in self._valid_spaces if not self.is_occupied(coord))

    def is_occupied(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinates is occupied."""
        return self._board[coord]["occupied"]

    def get_space_type(self, coord: Coordinate) -> SpaceType:
        """Returns type of space of supplied coordinates."""
        return self._board[coord]["space_type"]

    def get_goods_type(self, coord: Coordinate) -> GoodsType | None:
        """Returns type of goods on the space of supplied coordinates if present, else None."""
        return self._board[coord]["goods_type"]

    def is_accumulate(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinates is an accumulation space."""
        return self._board[coord]["accumulate"]

    def get_num_goods_present(self, coord: Coordinate) -> int:
        """Gets number of goods present on space if any, else 0."""
        return self._board[coord]["num_present"]

    def get_action(self, coord: Coordinate) -> Action | None:
        """Gets action for given coords, or None if not action space."""
        return self._board[coord]["action"]

    def set_person(
            self,
            new_coords: Coordinate,
            prev_coord: Coordinate | None = None
        ) -> None:
# FIXME! Revisit this, probably needs fixing!
        """Sets person in new place and updates game boards accordingly."""
        self._board[new_coords]["occupied"] = True
        if prev_coord is not None:
            self._board[prev_coord]["occupied"] = False
