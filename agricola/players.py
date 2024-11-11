"""
Module containing Player class for controlling agricola game players.
"""
from __future__ import annotations
from typing import Any, Self, TYPE_CHECKING

from .goods import Supply
from .gameboards import Farmyard
from .cards import Deck
from .type_defs import GoodsType, Location, Coordinate
if TYPE_CHECKING:
    from .game import Game


class Player:
    """
    Player class.
    """

    __game: Game
    __player_id: int
    __starting_player: bool
    __supply: Supply
    __farmyard: Farmyard
    __player_major_imp_cards: Deck | None
# FIXME!!! Need to replace all `Any` once implemented!
    __minor_imp_cards: Any
    __occupation_cards: Any
    __begging_markers: int

    def __new__(cls, game: Game, player_id: int, starting: bool = False) -> Self:
        self = super().__new__(cls)
        self.__game = game
        self.__player_id = player_id
        self.__starting_player = starting
        self.__begging_markers = 0
        self.__supply = Supply(num_food=2 if starting else 3)
        self.__farmyard = Farmyard()
        self._init_persons()
        self.__player_major_imp_cards = None
        return self

    @property
    def game(self) -> str:
        """Returns the game instance that the player is a part of."""
        return self.__game.instance_uuid

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

    @property
    def major_improvements(self) -> Deck | None:
        """Returns player's major improvement cards if any, else None."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__player_major_imp_cards

    def move_items(
            self,
            item: GoodsType,
            num_goods: int,
            new_board: Location,
            new_coords: Coordinate,
            prev_board: Location,
            prev_coord: Coordinate
        ) -> None:
        """Player call to move selected item(s) around player controlled spaces."""
        self.__supply.move(item, new_board, new_coords, prev_board, prev_coord)
        self.__farmyard.move(item, num_goods, new_board, new_coords, prev_board, prev_coord)

    def _init_persons(self) -> None:
        """Move a person piece from one coordinate & board to another."""
        self.__supply.move("person", "farmyard", (1,0), "inventory", (-1,-1))
        self.__supply.move("person", "farmyard", (2,0), "inventory", (-1,-1))
        self.__farmyard.set_person((1,0))
        self.__farmyard.set_person((2,0))
