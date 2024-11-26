"""
Module defining ABC 'Card' to be inherited from by 
'MajorImprovements', 'MinorImprovements', & 'Occupations'.
"""
from __future__ import annotations
from abc import ABCMeta
from typing import Any, TYPE_CHECKING

from ..type_defs import MajorImproveNames, MinorImproveNames, OccupationNames, GameStates
if TYPE_CHECKING:
    from ..game import Game


CardDictKeys = MajorImproveNames | MinorImproveNames | OccupationNames
"""ReAlias of all possible card keys/names to allow ABC and type checking for dict."""

class Card(metaclass=ABCMeta):
    """
    ABC Card defining base card functions.
    """

    _game: Game
    _name: CardDictKeys
    # Any is used here as values in dict are intentionally varied for functionality.
    _attributes: dict[str, Any]
    _played: bool

    @property
    def name(self) -> CardDictKeys:
        """Get name of card."""
        return self._name

    @property
    def played(self) -> bool:
        """Returns True if card has been played by player, else False if still in hand."""
        return self._played

    @property
    def attributes(self) -> dict[str, Any]:
        """Property returning read only view of this card's various data."""
# FIXME! Need to make sure read only
        return self._attributes

    def set_played(self) -> None:
        """Changes this card's state to played."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision"
        }
        self._game.state.is_valid_state_for_func(self._game.game_state, valid_states)
        self._played = True
