"""
Module containing Player class for controlling agricola game players.
"""

from typing import Self

# TODO: typed dict for player exclusive goods (fence, people, stables)


class Player:
    """
    Player class.
    """
    def __new__(cls) -> Self:
        self = super().__new__(cls)
        return self

