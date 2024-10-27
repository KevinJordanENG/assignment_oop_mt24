"""
Module responsible for managing inventory of goods.

Module class Goods is meant to be used both for global game supply,
as well as individual player's supply(ies).
"""

from typing import Literal, Self, TypedDict



GoodsType = Literal[
    "sheep",
    "boar",
    "cattle",
    "wood",
    "clay",
    "reed",
    "stone",
    "grain",
    "vegetable",
    "food",
    "fence",
    "stable",
    "person"
]
"""Type alias for various types of goods."""

Location = Literal["farmyard", "action_space", "inventory"]
"""Type alias for where good is located."""

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
    """Generalized agricola good with type, gameboard coordinates, and location."""
    goods_type: GoodsType
    location: Location
    coordinate: tuple[int, int] # (row, col) pair

class Supply:
    """
    Supply class.

    An inventory of goods initialized and maintained per player.
    """

    # TODO: determine if better data struct to hold goods (bag maybe?)
    __limited_goods: list[Good]
    __general_goods: list[Good]

    def __new__(cls, num_food: int) -> Self:
        self = super().__new__(cls)

        return self
    
