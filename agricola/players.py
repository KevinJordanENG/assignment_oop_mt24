"""
Module containing Player class for controlling agricola game players.
"""
from typing import Any, Self
from .goods.goods import Supply


class Player:
    """
    Player class.
    """

    __player_id: int
    __starting_player: bool
    __supply: Supply
    __farmyard: Any # FIXME!!! Need to get once implemented
    __major_imp_cards: Any # FIXME!!! Need to get once implemented
    __minor_imp_cards: Any # FIXME!!! Need to get once implemented
    __occupation_cards: Any # FIXME!!! Need to get once implemented

    def __new__(cls, player_id: int, starting: bool = False) -> Self:
        self = super().__new__(cls)
        self.__player_id = player_id
        self.__starting_player = starting
        self.__supply = Supply(num_food=2 if starting else 3)
        return self

    @property
    def player_id(self) -> int:
        """Player ID."""
        return self.__player_id

    @property
    def starting_player(self) -> int:
        """Does this player have the 'starting player' token?"""
        return self.__starting_player

    @property
    def supply(self) -> Supply:
        """Returns view of player's current supply."""
        # FIXME! Need to make sure ACTUALLY returns read only.
        return self.__supply
