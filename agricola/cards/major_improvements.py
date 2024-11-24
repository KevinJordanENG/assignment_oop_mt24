"""
Module defining MajorImprovement cards.
"""

from typing import Any, Self

from .card import Card
from ..type_defs import MajorImproveNames


class MajorImprovement(Card):
    """
    Major improvement card.
    """

    _func: str

    def __new__(cls, name: MajorImproveNames, attributes: dict[str, Any]) -> Self:
        """Constructor for new major improvement cards."""
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

# TODO: joinery, pottery, basket only can action on harvest rounds
