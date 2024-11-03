"""
Module responsible for managing inventory of goods.

Module includes the TypedDict defining a base "Good",
as well as Supply class, the main class used to manage inventory per player.
"""
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
        # Error check for num_food.
        if num_food < 2:
            raise ValueError("Minimum starting food in inventory is 2.")
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
        count = 0
        for _, good in enumerate(self.__general_goods):
            count += 1 if good["goods_type"] == goods_type else 0
        return count

    def add(self, item: Good) -> None:
        """Adds a good to (general) inventory."""
        self.__general_goods.append(item)

    def remove(self, item: Good) -> None:
        """Removes a good from (general) inventory."""

    def move(self, item: Good, new_board: Location, new_coords: Coordinate) -> None:
        """Unified move routine handling board and coordinate changes."""
        # TODO: error checking & logic!
        self._change_board(item, new_board)
        self._change_coord(item, new_coords)

    def _init_limited_goods(self) -> list[Good]:
        """Initializes inventory of limited goods."""
        fence: Good = {"goods_type": "fence", "location": "inventory", "coordinate": (-1, -1)}
        stable: Good = {"goods_type": "stable", "location": "inventory", "coordinate": (-1, -1)}
        person: Good = {"goods_type": "person", "location": "inventory", "coordinate": (-1, -1)}
        return ([fence] * 15) + ([stable] * 4) + ([person] * 5)

    def _init_general_goods(self, num_food: int) -> list[Good]:
        """Initializes inventory of general goods, only food included at first."""
        food: Good = {"goods_type": "food", "location": "inventory", "coordinate": (-1, -1)}
        return [food] * num_food

    def _change_coord(self, item: Good, new_coords: Coordinate) -> None:
        """Moves good to new gameboard coordinate or into inventory coord = (-1, -1)."""

    def _change_board(self, item: Good, new_board: Location) -> None:
        """Changes gameboard of good."""
