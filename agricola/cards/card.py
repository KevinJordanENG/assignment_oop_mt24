"""
Module defining ABC 'Card' to be inherited from by 
'MajorImprovements', 'MinorImprovements', & 'Occupations'.
"""

from abc import ABCMeta
from typing import Any

from ..type_defs import MajorImproveNames, MinorImproveNames, OccupationNames


CardDictKeys = MajorImproveNames | MinorImproveNames | OccupationNames
"""ReAlias of all possible card keys/names to allow ABC and type checking for dict."""

class Card(metaclass=ABCMeta):
    """
    ABC Card defining base card functions.
    """

    _name: CardDictKeys
    # Any is used here as values in dict are intentionally varied for functionality.
    _attributes: dict[str, Any]

    @property
    def name(self) -> CardDictKeys:
        """Get name of card."""
        return self._name

    @property
    def attributes(self) -> dict[str, Any]:
        """Property returning read only view of this card's various data."""
# FIXME! Need to make sure read only
        return self._attributes
