"""
Module for limited tiles.

Tiles are special as when you use one side you also remove the other side
from the global inventory. Example: you Plow and place 1 field tile,
but when you do this the number of possible wood rooms left to build also decrements.
"""

from typing import Self

from ..type_defs import SpaceType


class Tiles:
    """
    Class that handles the special tile game objects.
    """

    __type_pair: tuple[SpaceType, SpaceType]
    __tiles_avail: int
    __slots__ = ("__type_pair", "__tiles_avail")

    def __new__(cls, type_pair: tuple[SpaceType, SpaceType]) -> Self:
        """Constructor for tiles with error checking for proper context (Game only caller)."""
        # Dynamic to avoid circular imports, and error if not being built in proper context.
        from ..game import Game
        if not Game._is_constructing_tiles():
            raise TypeError("Tiles can only be instantiated by 'Game', not directly.")
        self = super().__new__(cls)
        self.__init_and_check_pair(type_pair)
        return self

    @property
    def type_pair(self) -> tuple[SpaceType, SpaceType]:
        """Returns the pair type of the tile."""
        return self.__type_pair

    @property
    def tiles_avail(self) -> int:
        """Returns the number of the specific pair type of the tile available."""
        return self.__tiles_avail

    def __init_and_check_pair(self, type_pair: tuple[SpaceType, SpaceType]) -> None:
        """Initializes & error checks for bad pair."""
        if type_pair == ("wood_room", "field"):
            self.__tiles_avail = 23
            self.__type_pair = type_pair
        elif type_pair == ("field", "wood_room"):
            self.__tiles_avail = 23
            self.__type_pair = ("wood_room", "field")
        elif type_pair == ("clay_room", "stone_room"):
            self.__tiles_avail = 16
            self.__type_pair = type_pair
        elif type_pair == ("stone_room", "clay_room"):
            self.__tiles_avail = 16
            self.__type_pair = ("clay_room", "stone_room")
        else:
            raise ValueError(
                "Valid tile type pairs are ('wood_room','field') and ('clay_room','stone_room')."
            )
