"""
Module containing Player class for controlling agricola game players.
"""
from typing import Any, Self

from .goods import Supply
from .gameboards import Farmyard

class Player:
    """
    Player class.
    """

    __player_id: int
    __starting_player: bool
    __supply: Supply
    __farmyard: Farmyard
# FIXME!!! Need to replace all `Any` once implemented!
    __major_imp_cards: Any
    __minor_imp_cards: Any
    __occupation_cards: Any
    __begging_markers: int

    def __new__(cls, player_id: int, starting: bool = False) -> Self:
        self = super().__new__(cls)
        self.__player_id = player_id
        self.__starting_player = starting
        self.__begging_markers = 0
        self.__supply = Supply(num_food=2 if starting else 3)
        self.__farmyard = Farmyard()
        self._init_persons()
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
    def begging_markers(self) -> int:
        """Number of begging markers player has."""
        return self.__begging_markers

    @property
    def supply(self) -> Supply:
        """Returns view of player's current supply."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__supply

    @property
    def farmyard(self) -> Farmyard:
        """Returns current view of player's farmyard board."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__farmyard

    def _init_persons(self) -> None:
        """Move a person piece from one coordinate & board to another."""
        self.__supply.move("person", "farmyard", (1,0), "inventory", (-1,-1))
        self.__supply.move("person", "farmyard", (2,0), "inventory", (-1,-1))
        self.__farmyard.set_person((1,0))
        self.__farmyard.set_person((2,0))
