"""
Module containing TypeAlias' of common use items throughout agricola pkg.
"""
from typing import Literal


Location = Literal["farmyard", "action_space", "inventory"]
"""Type alias for where good is located."""

Coordinate = tuple[int, int]
"""
Type alias of coordinate where good is on respective gameboard, or inventory.
Represented as (row, col) pair, and inventory defined as coord = (-1, -1).
"""

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

SpaceType = Literal[
    "wood_room",
    "clay_room",
    "stone_room",
    "field",
    "action",
    "pasture",
    "unused"
]
"""Type alias for various gameboard space usage types."""

Action = Literal[
    "farm_expansion",
    "meeting_place",
    "grain_seeds",
    "farmland",
    "lessons",
    "day_laborer",
    "forest",
    "clay_pit",
    "reed_bank",
    "fishing",
    "major_improvement",
    "fencing",
    "grain_utilization",
    "sheep_market",
    "basic_wish_for_children",
    "house_redevelopment",
    "western_quarry",
    "vegetable_seeds",
    "pig_market",
    "cattle_market",
    "eastern_quarry",
    "urgent_wish_for_children",
    "cultivation",
    "farm_redevelopment",
    "copse",
    "grove",
    "3_hollow",
    "4_hollow",
    "3_resource_market",
    "4_resource_market",
    "3_lessons",
    "4_lessons",
    "traveling_players"
]
"""Type alias for actions in action spaces, also keys to load properties from CSV."""
