"""
Module defining MinorImprovement cards.
"""
from __future__ import annotations
from typing import Any, Self, TYPE_CHECKING
from .card import Card
from ..type_defs import MinorImproveNames
if TYPE_CHECKING:
    from ..game import Game


class MinorImprovement(Card):
    """
    Minor improvement card.
    """

    _func: str

    def __new__(cls, game: Game, name: MinorImproveNames, attributes: dict[str, Any]) -> Self:
        # Any is used purposefully here as values in attributes dict are intentionally varied for functionality.
        """Constructor for new minor improvement cards."""
        self = super().__new__(cls, game)
        self._name = name
        self._attributes = attributes
        self._func = attributes["func"]
        self._played = False
        return self

    @property
    def func(self) -> str:
        """Returns str version of function call associated with card."""
        return self._func
