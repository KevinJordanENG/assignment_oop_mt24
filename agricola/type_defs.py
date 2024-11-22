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

Axis = Literal["v", "h"] | None
"""Type alias to tag fence coordinates as either vertical or horizontal spaces."""

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
    "unused",
    "blocked"
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

MajorImproveNames = Literal[
    "2_fireplace",
    "3_fireplace",
    "4_cooking_hearth",
    "5_cooking_hearth",
    "well",
    "clay_oven",
    "stone_oven",
    "joinery",
    "pottery",
    "basketmakers_workshop"
]
"""Type alias for major improvement card names, also keys to load properties from CSV."""

MinorImproveNames = Literal[
    "shifting_cultivation",
    "clay_embankment",
    "young_animal_market",
    "drinking_trough",
    "rammed_clay",
    "handplow",
    "threshing_board",
    "sleeping_corner",
    "manger",
    "big_country",
    "wool_blankets",
    "pond_hut",
    "milk_jug",
    "claypipe",
    "junk_room",
    "basket",
    "dutch_windmill",
    "corn_scoop",
    "large_greenhouse",
    "clearing_spade",
    "lumber_mill",
    "canoe",
    "stone_tongs",
    "shepherds_crook",
    "mini_pasture",
    "market_stall",
    "caravan",
    "carpenters_parlor",
    "mining_hammer",
    "moldboard_plow",
    "lasso",
    "bread_paddle",
    "mantlepiece",
    "bottles",
    "loom",
    "strawberry_patch",
    "herring_pot",
    "butter_churn",
    "brook",
    "scullery",
    "three_field_rotation",
    "pitchfork",
    "sack_cart",
    "beanfield",
    "thick_forest",
    "loam_pit",
    "hard_porcelain",
    "acorns_basket"
]
"""Type alias for minor improvement card names, also keys to load properties from CSV."""

OccupationNames = Literal[
    "animal_tamer",
    "conservator",
    "hedge_keeper",
    "plow_driver",
    "adoptive_parents",
    "stable_architect",
    "grocer",
    "mushroom_collector",
    "roughcaster",
    "wall_builder",
    "scythe_worker",
    "seasonal_worker",
    "wood_cutter",
    "firewood_collector",
    "clay_hut_builder",
    "frame_builder",
    "priest",
    "braggart",
    "harpooner",
    "stonecutter",
    "animal_dealer",
    "conjurer",
    "lutenist",
    "pig_breeder",
    "cottager",
    "groom",
    "assistant_tiller",
    "master_bricklayer",
    "scholar",
    "organic_farmer",
    "tutor",
    "consultant",
    "sheep_walker",
    "manservant",
    "oven_firing_boy",
    "paper_maker",
    "childless",
    "small_scale_farmer",
    "geologist",
    "roof_ballaster",
    "carpenter",
    "house_steward",
    "greengrocer",
    "brushwood_collector",
    "storehouse_keeper",
    "pastor",
    "sheep_whisperer",
    "cattle_feeder"
]
"""Type alias for occupations card names, also keys to load properties from CSV."""

GameStates = Literal[
    "not_started", # Access to inspection ops or 'start' ops no mods or init
    "stopped_early", # Error on all, raise error to try again
    "finished", # Access to scoring, inspection, not mods
    "running_game", # No access to init or start
    "running_round_prep", # only access to prep func & inspection
    "running_round_return_home", # only access to return home func & inspection
    "running_round_harvest", # only access to harvest func & inspection
    "running_work_player_1", # player turn logic
    "running_work_player_2",
    "running_work_player_3",
    "running_work_player_4"
]
"""Type alias for all various game states."""
