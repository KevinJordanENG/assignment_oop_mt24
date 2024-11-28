"""
Module defining ABC BaseBoard to be inherited from by 'farmyards' and 'action_spaces'.
"""
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import TypedDict, TYPE_CHECKING

from ..type_defs import Coordinate, Location, GoodsType, SpaceType, Action, GameStates
if TYPE_CHECKING:
    from ..game import Game


class SpaceData(TypedDict):
    """TypedDict defining metadata about respective space."""
    coordinate: Coordinate
    space_type: SpaceType
    occupied: bool
    child: bool
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
    _game: Game
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["occupied"]

    def child_present(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinate has child present."""
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["child"]

    def is_stabled(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinates has stable built."""
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["stabled"]

    def get_space_type(self, coord: Coordinate) -> SpaceType:
        """Returns type of space of supplied coordinates."""
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["space_type"]

    def get_goods_type(self, coord: Coordinate) -> GoodsType | None:
        """Returns type of goods on the space of supplied coordinates if present, else None."""
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["goods_type"]

    def is_accumulate(self, coord: Coordinate) -> bool:
        """Checks if supplied coordinates is an accumulation space."""
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["accumulate"]

    def get_num_goods_present(self, coord: Coordinate) -> int:
        """Gets number of goods present on space if any, else 0."""
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
        if coord not in self._valid_spaces:
            raise KeyError("Coordinate is not valid on this board.")
        return self._board[coord]["num_present"]

    def is_action(self, coord: Coordinate) -> Action | None:
        """Gets action for given coords, or None if not action space."""
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
        if goods_type == "fence":
            raise ValueError (
                "Fences cannot use general move method due to different coord system."
            )
        elif goods_type == "person":
            self.__move_person(destination_board, destination_coord, source_board, source_coord)
        elif goods_type == "stable":
            self.__move_stable(destination_board, destination_coord, source_board)
        elif goods_type == "food":
            self.__move_food(num_goods, destination_board, source_board, source_coord)
        elif goods_type in {"sheep", "boar", "cattle"}:
            self.__move_animals(
                goods_type, num_goods, destination_board,
                destination_coord, source_board, source_coord
            )
        elif goods_type in {"wood", "clay", "reed", "stone"}:
            self.__move_building_material(
                goods_type, num_goods, destination_board, source_board, source_coord
            )
        elif goods_type in {"grain", "vegetable"}:
            self.__move_crops(
                goods_type, num_goods, destination_board,
                destination_coord, source_board, source_coord
            )

    def __check_pasture_size_and_stables(self) -> int:
        """
        Checks the total size of pasture & total number of stables to determine capacity of space.
        """
        raise NotImplementedError()

# ---------------------- Move Functions ------------------------------------------------------------
# These functions are knowingly long as lots of integral error checking are performed within.
# While each error check could maybe be another sub-subfunction,
# their usage is inherently joined and decided simpler when kept together.

    def __move_person(
            self,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves 'person' according to game rules."""
        # Decide if move path is valid & perform source/dest. actions as needed.
        # inv -> farm
        if source_board == "inventory" and destination_board == "farmyard":
            # Can only be dest. board.
            if self.board_type == "farmyard":
                # Check if valid space type on farm.
                if (self._board[destination_coord]["space_type"]
                    not in {"wood_room", "clay_room", "stone_room"}):
                    raise ValueError("Destination space is not a room.")
                self._board[destination_coord]["occupied"] = True
            else:
                pass # No effect if action space as not involved here.
        # inv -> act
        elif source_board == "inventory" and destination_board == "action_space":
            # Means we're taking 'have_kids' action.
            if self.board_type == "action_space":
                # Can't use twice so check if already a child present.
                if self._board[destination_coord]["child"]:
                    raise ValueError("Can't have 2nd child.")
                self._board[destination_coord]["child"] = True
            else:
                pass # No effect if farmyard as not involved here.
        # farm -> act
        elif source_board == "farmyard" and destination_board == "action_space":
            # We're a source.
            if self.board_type == "farmyard":
                self._board[source_coord]["occupied"] = False
            # We're a dest.
            else:
                self._board[destination_coord]["occupied"] = True
        # act -> farm
        elif source_board == "action_space" and destination_board == "farmyard":
            # We're a source.
            if self.board_type == "action_space":
                self._board[source_coord]["occupied"] = False
            # We're a dest.
            else:
                self._board[destination_coord]["occupied"] = True
        else:
            # Invalid move path.
            raise ValueError("Illegal move of 'person' requested.")

    def __move_stable(
            self,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location
        ) -> None:
        """Moves 'stable' according to game rules."""
        # Decide if move path is valid & perform source/dest. actions as needed.
        # inv -> farm
        if source_board == "inventory" and destination_board == "farmyard":
            if self.board_type == "farmyard":
                # Can only be dest. board.
                self._board[destination_coord]["stabled"] = True
            else:
                pass # No effect if action space as not involved here.
        else:
            # All other move paths invalid.
            raise ValueError("Only valid move of stable is from inventory to farmyard.")

    def __move_animals(
            self,
            goods_type: GoodsType,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves animals according to game rules."""
        # Decide if move path is valid & perform source/dest. actions as needed.
        # act -> farm
        if source_board == "action_space" and destination_board == "farmyard":
            # We're dest.
            if self.board_type == "farmyard":
                # Check if valid space type.
                if (self._board[destination_coord]["space_type"]
                    not in {"wood_room", "clay_room", "stone_room", "pasture", "unused"}):
                    raise ValueError(f"Not valid space type to move {goods_type!r} to.")
                # Conditions for rooms.
                if (self._board[destination_coord]["space_type"]
                    in {"wood_room", "clay_room", "stone_room"}):
                    if self._board[destination_coord]["num_present"] != 0 or num_goods != 1:
                        raise ValueError("Can only have 1 pet.")
                    # Put pet in room.
                    self._board[destination_coord]["goods_type"] = goods_type
                    self._board[destination_coord]["num_present"] = num_goods
                # Conditions for unused.
                elif self._board[destination_coord]["space_type"] == "unused":
                    if not self._board[destination_coord]["stabled"]:
                        raise ValueError(
                            f"Destination space not stabled & unused, cannot place {goods_type!r}."
                        )
                    if self._board[destination_coord]["num_present"] != 0 or num_goods != 1:
                        raise ValueError(
                            "Cannot place more than 1 animal in unfenced space with stable."
                        )
                    self._board[destination_coord]["goods_type"] = goods_type
                    self._board[destination_coord]["num_present"] = num_goods
                # Conditions for pasture.
                elif self._board[destination_coord]["space_type"] == "pasture":
                    # Check type.
                    if (self._board[destination_coord]["goods_type"] is not None
                        and self._board[destination_coord]["goods_type"] != goods_type):
                        raise ValueError("Animals in same pasture need to be same type.")
                    # Check number.
                    space_capacity = self.__check_pasture_size_and_stables()
                    if self._board[destination_coord]["num_present"] + num_goods > space_capacity:
                        raise ValueError("Move requested would break capacity of pasture.")
                    self._board[destination_coord]["goods_type"] = goods_type
                    self._board[destination_coord]["num_present"] += num_goods
            else:
                # We're a source.
                if goods_type != self._board[source_coord]["goods_type"]:
                    raise ValueError("Requested goods do not match source space goods type.")
                if num_goods != self._board[source_coord]["num_present"]:
                    raise ValueError("Must take all goods on accumulate space.")
                self._board[source_coord]["num_present"] -= num_goods
        # farm -> farm
        if source_board == "farmyard" and destination_board == "farmyard":
            if self.board_type == "farmyard":
                # Check both valid space types.
                if (self._board[source_coord]["space_type"]
                    not in {"wood_room", "clay_room", "stone_room", "pasture", "unused"}):
                    raise ValueError("Not valid source space type.")
                if (self._board[destination_coord]["space_type"]
                    not in {"wood_room", "clay_room", "stone_room", "pasture", "unused"}):
                    raise ValueError("Not valid destination space type.")
                # room/unused -> pasture
                if (self._board[source_coord]["space_type"] in
                    {"wood_room", "clay_room", "stone_room", "unused"}
                    and self._board[destination_coord]["space_type"] == "pasture"):
                    # Check source num.
                    if num_goods != 1:
                        raise ValueError("Can only source max 1 animal from room or stable space.")
                    # Check dest. type.
                    if (self._board[destination_coord]["goods_type"] is not None
                        and self._board[destination_coord]["goods_type"] != goods_type):
                        raise ValueError("Animals in same pasture need to be same type.")
                    # Check dest. value.
                    space_capacity = self.__check_pasture_size_and_stables()
                    if self._board[destination_coord]["num_present"] + num_goods > space_capacity:
                        raise ValueError("Move requested would break capacity of pasture.")
                    self._board[destination_coord]["goods_type"] = goods_type
                    self._board[destination_coord]["num_present"] += num_goods
                # room/pasture -> unused
                elif (self._board[source_coord]["space_type"] in
                    {"wood_room", "clay_room", "stone_room", "pasture"}
                    and self._board[destination_coord]["space_type"] == "unused"):
                    if not self._board[destination_coord]["stabled"]:
                        raise ValueError(
                            f"Destination space not stabled & unused, cannot place {goods_type!r}."
                        )
                    if self._board[destination_coord]["num_present"] != 0 or num_goods != 1:
                        raise ValueError(
                            "Cannot place more than 1 animal in unfenced space with stable."
                        )
                    self._board[destination_coord]["goods_type"] = goods_type
                    self._board[destination_coord]["num_present"] = num_goods
                # unused/pasture -> room
                elif (self._board[source_coord]["space_type"] in {"pasture", "unused"}
                    and self._board[destination_coord]["space_type"]
                    in {"wood_room", "clay_room", "stone_room"}):
                    if self._board[destination_coord]["num_present"] != 0 or num_goods != 1:
                        raise ValueError("Can only have 1 pet.")
                    # Put pet in room.
                    self._board[destination_coord]["goods_type"] = goods_type
                    self._board[destination_coord]["num_present"] = num_goods
# FIXME! decide if needed to have pasture -> pasture
                else:
                    raise ValueError("Incompatible source & destination space types.")
            else:
                pass # No action possible.
        else:
            # All other move paths invalid.
            raise ValueError(f"Illegal move of {goods_type!r} requested.")

    def __move_building_material(
            self,
            goods_type: GoodsType,
            num_goods: int,
            destination_board: Location,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves building materials according to game rules."""
        # Decide if move path is valid & perform source/dest. actions as needed.
        # act -> inv
        if source_board == "action_space" and destination_board == "inventory":
            # We're source.
            if self.board_type == "action_space":
                if goods_type != self._board[source_coord]["goods_type"]:
                    raise ValueError("Requested goods do not match source space goods type.")
                if num_goods != self._board[source_coord]["num_present"]:
                    raise ValueError("Must take all goods on accumulate space.")
                self._board[source_coord]["num_present"] -= num_goods
            else:
                pass # No action possible.
        else:
            # All other move paths invalid.
            raise ValueError(f"Illegal move of {goods_type!r} requested.")

    def __move_crops(
            self,
            goods_type: GoodsType,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves crops according to game rules."""
        # Decide if move path is valid & perform source/dest. actions as needed.
        # inv -> farm
        if source_board == "inventory" and destination_board == "farmyard":
            # Must be dest. (and taking "sow" action.)
            if self.board_type == "farmyard":
                # Check space type.
                if self._board[destination_coord]["space_type"] != "field":
                    raise ValueError("Can only place crops on 'field' spaces.")
                if self._board[destination_coord]["goods_type"] is not None:
                    raise ValueError("Can only place crops in empty field.")
                if self._board[destination_coord]["num_present"] != 0 or num_goods != 1:
                    raise ValueError(f"Can only place 1 {goods_type!r} in field at a time.")
                self._board[destination_coord]["goods_type"] = goods_type
                self._board[destination_coord]["num_present"] += num_goods + 2
            else:
                pass # No other actions possible.
        # farm -> inv
        if source_board == "farmyard" and destination_board == "inventory":
            # Must be source. (and taking "harvest_crops" action.)
            if self.board_type == "farmyard":
                if self._board[source_coord]["space_type"] != "field":
                    raise ValueError("Can only get crops from 'field' farmyard spaces.")
                if self._board[source_coord]["goods_type"] is None:
                    raise ValueError("Cannot get crops from empty field.")
                if self._board[source_coord]["num_present"] == 0 or num_goods != 1:
                    raise ValueError(f"Can only get 1 {goods_type!r} from field at a time.")
                if self._board[source_coord]["num_present"] == 1:
                    self._board[source_coord]["goods_type"] = None
                self._board[source_coord]["num_present"] -= num_goods
            else:
                pass # No other actions possible.
# FIXME! Make farm -> farm case if time for all minor imp cards.
        else:
            # All other move paths invalid.
            raise ValueError(f"Illegal move of {goods_type!r} requested.")

    def __move_food(
            self,
            num_goods: int,
            destination_board: Location,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Moves food according to game rules."""
        # Decide if move path is valid & perform source/dest. actions as needed.
        # act -> inv
        if source_board == "action_space" and destination_board == "inventory":
            # We're source.
            if self.board_type == "action_space":
                if self._board[source_coord]["goods_type"] != "food":
                    raise ValueError("Requested food does not match source space goods type.")
                if num_goods != self._board[source_coord]["num_present"]:
                    raise ValueError("Must take all food on accumulate space.")
                self._board[source_coord]["num_present"] -= num_goods
            else:
                pass # No other actions possible.
        else:
            # All other move paths invalid.
            raise ValueError("Illegal move of 'food' requested.")
