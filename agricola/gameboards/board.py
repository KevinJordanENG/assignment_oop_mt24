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
    stabled: bool
    accumulate: bool
    accum_number: int
    goods_type: GoodsType | None
    num_present: int
    action: Action | None


class MoveRequest(TypedDict):
    """Bundle used in move semantics throughout game."""
    goods_type: GoodsType
    num_goods: int
    destination_board: Location
    destination_coord: Coordinate
    source_board: Location
    source_coord: Coordinate


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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["occupied"]

    def is_stabled(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinates has stable built."""
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["stabled"]

    def get_space_type(self, coord: Coordinate) -> SpaceType:
        """Returns type of space of supplied coordinates."""
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["space_type"]

    def get_goods_type(self, coord: Coordinate) -> GoodsType | None:
        """Returns type of goods on the space of supplied coordinates if present, else None."""
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["goods_type"]

    def is_accumulate(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinates is an accumulation space."""
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["accumulate"]

    def get_num_goods_present(self, coord: Coordinate) -> int:
        """Gets number of goods present on space if any, else 0."""
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["num_present"]

    def get_action(self, coord: Coordinate) -> Action | None:
        """Gets action for given coords, or None if not action space."""
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["action"]

    def move(
            self,
            goods_type: GoodsType,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """
        Unified move routine handling board and coordinate changes for space data.
        
        Uses subfunctions to handle error checking around specific goods types,
        placements, and prohibited movements.
        """
        if goods_type == "fence":
            raise ValueError (
                "Fences cannot use general move method due to different coord system."
            )
        if goods_type == "person":
            self._move_person(destination_board, destination_coord, source_board, source_coord)
        if goods_type == "stable":
            self._move_stable(destination_board, destination_coord, source_board, source_coord)
        if goods_type == "food":
            self._move_food(
                num_goods, destination_board, destination_coord, source_board, source_coord
            )
        if goods_type in {"sheep", "boar", "cattle"}:
            self._move_animals(
                num_goods, destination_board, destination_coord, source_board, source_coord
            )
        if goods_type in {"wood", "clay", "reed", "stone"}:
            self._move_building_material(
                num_goods, destination_board, destination_coord, source_board, source_coord
            )
        if goods_type in {"grain", "vegetable"}:
            self._move_crops(
                num_goods, destination_board, destination_coord, source_board, source_coord
            )


        # Determine if any changes are needed.
        if source_board == self.board_type:
            space_data = self._board[source_coord]
            # Check if we're trying to move back to inventory and shouldn't.
# FIXME! Revisit to make sure list is complete once more funcs built.
            if goods_type in {"person", "stable"} and destination_board == "inventory":
                raise ValueError(f"Cannot move {goods_type} from farmyard back to inventory.")
            # Check value & type of request.
            else:
                if goods_type != space_data["goods_type"]:
                    raise ValueError(
                        "Goods requested to be moved don't match type present as source coordinate."
                    )
                if num_goods > space_data["num_present"]:
                    raise ValueError(
                        "Requested to move more goods than are present at source coordinate."
                    )
            # Do mods now that verified valid move request.
            if goods_type == "person":
                space_data["occupied"] = False
            elif goods_type == "stable":
                raise ValueError("Cannot move 'stable' from farmyard.")
            else:
                if space_data["num_present"] == num_goods:
                    space_data["goods_type"] = None
                space_data["num_present"] -= num_goods
        # Moving goods_type(s) onto farmyard.
        elif destination_board == self.board_type:
            space_data = self._board[destination_coord]
            if goods_type == "person":
                if space_data["space_type"] not in {"wood_room", "clay_room", "stone_room"}:
                    raise ValueError("Person can only be placed in rooms.")
                space_data["occupied"] = True
            elif goods_type == "stable":
                if space_data["space_type"] not in {"pasture", "unused"}:
                    raise ValueError("Can only place stable on unused or pasture spaces.")

                #self.change_space_type(destination_coord, )
            elif goods_type in {"sheep", "boar", "cattle"}:
                if space_data["space_type"] not in {"pasture", "unused"}:
                    raise ValueError(
                        "Animals must be properly housed in 'pasture' or unused space with stable."
                    )
                if space_data["num_present"] != 0 and space_data["goods_type"] != goods_type:
                    raise ValueError(
                        "Cannot put requested goods on space containing goods of different type."
                    )
                space_data["goods_type"] = goods_type
                space_data["num_present"] += num_goods
            #do work
        else:
            return

    def _move_person(
            self,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves 'person' according to game rules."""
        # Decide if addition, removal, or no action is required.
        if source_board == self.board_type:
            pass
        elif destination_board == self.board_type:
            pass
        else:
            return

    def _move_stable(
            self,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves 'stable' according to game rules."""
        # Decide if addition, removal, or no action is required.
        if source_board == self.board_type:
            pass
        elif destination_board == self.board_type:
            pass
        else:
            return

    def _move_animals(
            self,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves animals according to game rules."""
        # Decide if addition, removal, or no action is required.
        if source_board == self.board_type:
            pass
        elif destination_board == self.board_type:
            pass
        else:
            return

    def _move_building_material(
            self,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves building materials according to game rules."""
        # Decide if addition, removal, or no action is required.
        if source_board == self.board_type:
            pass
        elif destination_board == self.board_type:
            pass
        else:
            return

    def _move_crops(
            self,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves crops according to game rules."""
        # Decide if addition, removal, or no action is required.
        if source_board == self.board_type:
            pass
        elif destination_board == self.board_type:
            pass
        else:
            return

    def _move_food(
            self,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves food according to game rules."""
        # Decide if addition, removal, or no action is required.
        if source_board == self.board_type:
            pass
        elif destination_board == self.board_type:
            pass
        else:
            return

    def _change_space_data(self, new_space_data: SpaceData) -> None:
        """Changes/updates space info from player move action."""
        self._board[new_space_data["coordinate"]] = new_space_data
