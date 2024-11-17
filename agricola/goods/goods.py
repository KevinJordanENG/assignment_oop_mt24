"""
Module responsible for managing inventory of goods.

Module includes the TypedDict defining a base "Good",
as well as Supply class, the main class used to manage inventory per player.
"""
from copy import deepcopy
from typing import Self, TypedDict
from ..type_defs import Location, Coordinate, GoodsType

# TODO: eval if the pattern is needed once further building / testing done
# LISTING_STATES: Final[tuple[ListingState, ...]] = (
#     "draft", "active", "sold", "cancelled"
# )
# """
# Tuple of listings states, for use at runtime.

# Technically, we can get them from ListingState.__args__, but the internals of
# type alias have a tendency to change once in a while, so that is only an option
# if you are willing to keep up to date with breaking changes in the typing lib.
# """

class Good(TypedDict):
    """
    Generalized agricola good with type, gameboard coordinates, and location.
    
    Small lightweight TypedDict of TypeAlias used for efficient/portable data representation.
    """
    goods_type: GoodsType
    location: Location
    coordinate: Coordinate


class Supply:
    """
    Supply class.

    An inventory of goods initialized and maintained per player.
    """

    __limited_goods: list[Good]
    __general_goods: list[Good]

    def __new__(cls, *, num_food: int) -> Self:
        self = super().__new__(cls)
        self.__limited_goods = self._init_limited_goods()
        self.__general_goods = self._init_general_goods(num_food)
        return self

    @property
    def limited_goods(self) -> tuple[Good, ...]:
        """Property to show read only info of limited goods."""
# FIXME! Need to assure read only!
        return tuple(self.__limited_goods)

    @property
    def general_goods(self) -> tuple[Good, ...]:
        """Property to show read only info of general goods."""
# FIXME! Need to assure read only!
        return tuple(self.__general_goods)

    def count(self, goods_type: GoodsType) -> int:
        """Counts number of specified goods type in current inventory."""
# FIXME! Maybe try and use list comp here if poss/time.
        if goods_type in {"fence", "stable", "person"}:
            stock_type = self.__limited_goods
        else:
            stock_type = self.__general_goods
        count = 0
        for _, good in enumerate(stock_type):
            count += 1 if good["goods_type"] == goods_type else 0
        return count

    def add(self, item: Good) -> None:
        """Adds a good to (general) inventory."""
        self.__general_goods.append(item)

    def remove(self, item: Good) -> None:
        """Removes a good from (general) inventory."""

    def move(
            self,
            item: GoodsType,
            new_board: Location,
            new_coords: Coordinate,
            prev_board: Location | None = None,
            prev_coord: Coordinate | None = None
        ) -> None:
        """Unified move routine handling board and coordinate changes."""
        # Fetch item matching type and optionally previous coords/board if provided.
        fetch = self.get_good(item, prev_board, prev_coord)
        self._change_good_board(fetch, new_board)
        self._change_good_coord(fetch, new_coords)

    def _init_limited_goods(self) -> list[Good]:
        """Initializes inventory of limited goods."""
        fence: Good = {"goods_type": "fence", "location": "inventory", "coordinate": (-1, -1)}
        stable: Good = {"goods_type": "stable", "location": "inventory", "coordinate": (-1, -1)}
        person: Good = {"goods_type": "person", "location": "inventory", "coordinate": (-1, -1)}
        # Use of deepcopy to assure each Good is its own unique object.
        fences = [deepcopy(fence) for _ in range(15)]
        stables = [deepcopy(stable) for _ in range(4)]
        persons = [deepcopy(person) for _ in range(5)]
        return fences + stables + persons

    def _init_general_goods(self, num_food: int) -> list[Good]:
        """Initializes inventory of general goods, only food included at first."""
        food: Good = {"goods_type": "food", "location": "inventory", "coordinate": (-1, -1)}
        # Use of deepcopy to assure each Good is its own unique object.
        return [deepcopy(food) for _ in range(num_food)]

    def get_good(
            self,
            item: GoodsType,
            prev_board: Location | None,
            prev_coord: Coordinate | None
        ) -> Good:
        """Finds specified good with given descriptors."""
        if item in {"fence", "stable", "person"}:
            stock_type = self.__limited_goods
        else:
            stock_type = self.__general_goods
        good: Good
        for _, good in enumerate(stock_type):
            if good["goods_type"] == item and prev_board is None and prev_coord is None:
                break
            if (good["goods_type"] == item
                and good["location"] == prev_board
                and prev_coord is None):
                break
            if (good["goods_type"] == item
                and prev_board is None
                and good["coordinate"] == prev_coord):
                break
            if (good["goods_type"] == item
                and good["location"] == prev_board
                and good["coordinate"] == prev_coord):
                break
        return good

    def _change_good_coord(self, item: Good, new_coords: Coordinate) -> None:
        """Moves good to new gameboard coordinate or into inventory coord = (-1, -1)."""
        item["coordinate"] = new_coords

    def _change_good_board(self, item: Good, new_board: Location) -> None:
        """Changes gameboard of good."""
        item["location"] = new_board
