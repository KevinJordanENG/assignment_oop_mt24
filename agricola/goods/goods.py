"""
Module responsible for managing inventory of goods.

Module includes the TypedDict defining a base "Good",
as well as Supply class, the main class used to manage inventory per player.
"""
from __future__ import annotations
from copy import deepcopy
from types import MappingProxyType
from typing import NotRequired, Self, TypedDict, cast, TYPE_CHECKING

from ..type_defs import Location, Coordinate, GoodsType, Axis, GameStates
if TYPE_CHECKING:
    from ..game import Game


class Good(TypedDict, total=True):
    """
    Generalized agricola good with type, coordinates, location, and optional axis for fences.
    
    Small lightweight TypedDict of TypeAlias used for efficient/portable data representation.
    """
    goods_type: GoodsType
    location: Location
    coordinate: Coordinate
    axis: NotRequired[Axis]


class Supply:
    """
    Supply class.

    An inventory of goods initialized and maintained per player.
    """

    __game: Game
    __limited_goods: list[Good] # Never created or destroyed, just moved.
    __general_goods: list[Good] # Supports add & remove ops.

    def __new__(cls, game: Game, *, num_food: int) -> Self:
        """Constructor for player supply using Player context manager to ensure Player only init."""
        # Dynamic to avoid circular imports, and error if not being built in proper context.
        from ..players import Player
        if not Player._is_constructing_supply():
            raise TypeError("Supply can only be instantiated by 'Player', not directly.")
        self = super().__new__(cls)
        self.__game = game
        self.__limited_goods = self.__init_limited_goods()
        self.__general_goods = self.__init_general_goods(num_food)
        return self

    @property
    def limited_goods(self) -> tuple[MappingProxyType[str, object], ...]:
                                                         # ^^^^^^ object use suggested by MyPy as better than 'Any' and allows
                                                         #        varied value types to be returned for each key in TypedDict.
        """Property to show read only info of limited goods."""
        temp: list[MappingProxyType[str, object]] = [] # Temp list copy but used to store the MappingProxyType version of our Good TypedDict.
        for good in self.__limited_goods:
            temp.append(MappingProxyType(good))
        return tuple(temp)

    @property
    def general_goods(self) -> tuple[MappingProxyType[str, object], ...]:
        """Property to show read only info of general goods."""
        # Same code pattern as limited_goods property above.
        temp: list[MappingProxyType[str, object]] = []
        for good in self.__general_goods:
            temp.append(MappingProxyType(good))
        return tuple(temp)

    def count(self, goods_type: GoodsType) -> int:
        """Counts number of specified goods type in current inventory."""
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
        self.__game.state._is_valid_state_for_func(self.__game.game_state, valid_states)
        # Decide which list to search in.
        if goods_type in {"fence", "stable", "person"}:
            stock_type = self.__limited_goods
        else:
            stock_type = self.__general_goods
        count = 0
        for _, good in enumerate(stock_type):
            count += 1 if good["goods_type"] == goods_type else 0
        return count

    def _add(self, item: Good) -> None:
        """Adds a good to (general) inventory."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision"
        }
        self.__game.state._is_valid_state_for_func(self.__game.game_state, valid_states)
        self.__general_goods.append(item)

    def _build_fence(self) -> None:
        """Builds fence / moves it from inventory to farmyard."""
        raise NotImplementedError()

    def _pay(self, payment: tuple[tuple[int,str], ...]) -> None:
        """Routine to 'pay' for game actions, removing items from inventory."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision"
        }
        self.__game.state._is_valid_state_for_func(self.__game.game_state, valid_states)
        for item in payment: # For each unique good type / number tuple.
            for _ in range(item[0]): # For num_goods of this goods type.
                goods_type = cast(GoodsType, item[1])
                fetch = self.__get_general_good(goods_type, "inventory", (-1,-1))
                if fetch is None:
                    raise ValueError("Tried to pay with nonexistent good.")
                self.__remove(fetch[1])

    def _move(
            self,
            goods_type: GoodsType,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location | None = None,
            source_coord: Coordinate | None = None,
        ) -> None:
        """
        Unified move routine handling board and coordinate changes of Goods.
        None for source implies inventory.
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
        self.__game.state._is_valid_state_for_func(self.__game.game_state, valid_states)
        # Fences are handled elsewhere.
        if goods_type == "fence":
            raise ValueError(
                "Cannot use general move method for fence as uses different coordinates."
            )
        # Decide if in limited or general goods.
        if goods_type in {"stable", "person"}:
            self.__move_limited(
                goods_type,
                destination_board,
                destination_coord,
                source_board if source_board is not None else "inventory",
                source_coord if source_coord is not None else (-1,-1)
            )
        else:
            self.__move_general(
                goods_type,
                num_goods,
                destination_board,
                destination_coord,
                source_board if source_board is not None else "inventory",
                source_coord if source_coord is not None else (-1,-1)
            )

    def __remove(self, ind: int) -> None:
        """Removes a good from (general) inventory by index."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision"
        }
        self.__game.state._is_valid_state_for_func(self.__game.game_state, valid_states)
        del self.__general_goods[ind]

    def __move_limited(
            self,
            goods_type: GoodsType,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Move routine for limited goods ('person', 'stable')."""
        # Fetch item matching type and optionally previous coords/board if provided.
        fetch = self.__get_limited_good(goods_type, source_board, source_coord)
        if fetch is None:
            raise ValueError("Limited good not found at requested coordinates.")
        if goods_type == "stable":
            if source_board == "inventory" and destination_board == "farmyard":
                pass # This is only valid request so allow to pass.
            else:
                raise ValueError("Illegal move requested.")
        elif goods_type == "person":
            if source_board in {"farmyard", "action_space"} and destination_board == "inventory":
                raise ValueError("Illegal move requested.")
        fetch["location"] = destination_board
        fetch["coordinate"] = destination_coord

    def __move_general(
            self,
            goods_type: GoodsType,
            num_goods: int,
            destination_board: Location,
            destination_coord: Coordinate,
            source_board: Location,
            source_coord: Coordinate
        ) -> None:
        """Move routine for general goods."""
        # Early error reject if not valid path.
        if source_board == "farmyard" and destination_board == "action_space":
            raise ValueError("Illegal move requested.")
        # Move for num_goods.
        for _ in range(num_goods):
            # farm/act -> inv
            if source_board in {"farmyard", "action_space"} and destination_board == "inventory":
                if goods_type in {"wood", "clay", "stone", "reed", "grain", "vegetable", "food"}:
                    # Instantiate good.
                    good: Good = {
                        "goods_type": goods_type,
                        "location": "inventory",
                        "coordinate": destination_coord
                    }
                    # Add good to inventory.
                    self._add(good)
                else:
                    raise ValueError("Illegal move requested.")
            # inv -> farm
            elif source_board == "inventory" and destination_board == "farmyard":
                fetch = self.__get_general_good(goods_type, source_board, source_coord)
                if fetch is None:
                    raise ValueError("Good not found at requested coordinates.")
                good, ind = fetch[0], fetch[1]
                if goods_type in {"grain", "vegetable"}:
                    # Remove from inventory.
                    self.__remove(ind)
                else:
                    raise ValueError("Illegal move requested.")
            # Some redundant error checking of board to board data transfer,
            # even tho handled by SpaceData.
            # act -> farm
            elif source_board == "action_space" and destination_board == "farmyard":
                # Check if appropriate goods type.
                if goods_type in {"sheep", "boar", "cattle"}:
                    pass # Goods info handled via SpaceData
                else:
                    raise ValueError("Illegal move requested.")
            # farm -> farm
            elif source_board == "farmyard" and destination_board == "farmyard":
                if goods_type in {"sheep", "boar", "cattle", "grain", "vegetable"}:
                    pass # Goods info handled via SpaceData
                else:
                    raise ValueError("Illegal move requested.")

    def __get_limited_good(
            self,
            item: GoodsType,
            source_board: Location,
            source_coord: Coordinate
        ) -> Good | None:
        """Finds specified limited good with given descriptors."""
        for _, good in enumerate(self.__limited_goods):
            if (good["goods_type"] == item
                and good["location"] == source_board
                and good["coordinate"] == source_coord):
                return good
        return None

    def __get_general_good(
            self,
            item: GoodsType,
            source_board: Location,
            source_coord: Coordinate
        ) -> tuple[Good,int] | None:
        """Finds general good if present and returns Good and its index in supply."""
        for i, good in enumerate(self.__general_goods):
            if (good["goods_type"] == item
                and good["location"] == source_board
                and good["coordinate"] == source_coord):
                return (good, i)
        return None

    def __init_limited_goods(self) -> list[Good]:
        """Initializes inventory of limited goods."""
        fence: Good = {
            "goods_type": "fence", "location": "inventory", "coordinate": (-1, -1), "axis": None
        }
        stable: Good = {"goods_type": "stable", "location": "inventory", "coordinate": (-1, -1)}
        person: Good = {"goods_type": "person", "location": "inventory", "coordinate": (-1, -1)}
        # Use of deepcopy to assure each Good is its own unique object.
        fences = [deepcopy(fence) for _ in range(15)]
        stables = [deepcopy(stable) for _ in range(4)]
        persons = [deepcopy(person) for _ in range(5)]
        return fences + stables + persons

    def __init_general_goods(self, num_food: int) -> list[Good]:
        """Initializes inventory of general goods, only food included at first."""
        food: Good = {"goods_type": "food", "location": "inventory", "coordinate": (-1, -1)}
        # Use of deepcopy to assure each Good is its own unique object.
        return [deepcopy(food) for _ in range(num_food)]
