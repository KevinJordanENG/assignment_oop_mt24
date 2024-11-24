"""
Module defining Occupation cards.
"""

from typing import Any, Self

from .card import Card
from ..type_defs import OccupationNames


class Occupation(Card):
    """
    Occupation card.
    """

    _func: str

    def __new__(cls, name: OccupationNames, attributes: dict[str, Any]) -> Self:
        """Constructor for new occupation cards."""
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
