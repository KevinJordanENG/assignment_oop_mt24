"""
Module defining MinorImprovement cards.
"""

from typing import Any, Self

from .card import Card
from ..type_defs import MinorImproveNames

class MinorImprovement(Card):
    """
    Minor improvement card.
    """

    _func: str
    _played: bool

    def __new__(cls, name: MinorImproveNames, attributes: dict[str, Any]) -> Self:
        """Constructor for new minor improvement cards."""
        self = super().__new__(cls)
        self._name = name
        self._attributes = attributes
        self._func = attributes["func"]
        self._played = False
        return self

    @property
    def func(self) -> str:
        """Returns str version of function call associated with card."""
        return self._func

    @property
    def played(self) -> bool:
        """Returns True if card has been played by player, else False if still in hand."""
        return self._played
    
# TODO: traveling cards are just removed from play after played in 1 p game!
