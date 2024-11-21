"""
Module containing Player class for controlling agricola game players.
"""
from __future__ import annotations
from typing import Self, TYPE_CHECKING

from .goods import Supply
from .gameboards import Farmyard, MoveRequest
from .cards import Deck
from .type_defs import GoodsType, Coordinate
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
    __minor_imp_cards: Deck
    __occupation_cards: Deck
    __begging_markers: int
    __has_future_goods_on_action_spaces: bool
    __future_goods: list[tuple[int,GoodsType]]
                             # ^^^round_num

    def __new__(
            cls,
            game: Game,
            minor_imp_cards: Deck,
            occup_cards: Deck,
            num_players: int,
            *,
            player_id: int,
            starting: bool = False
        ) -> Self:
        self = super().__new__(cls)
        self.__game = game
        self.__player_id = player_id
        self.__starting_player = starting
        self.__begging_markers = 0
        if num_players == 1:
            self.__supply = Supply(num_food=0)
        else:
            self.__supply = Supply(num_food=2 if starting else 3)
        self.__farmyard = Farmyard()
        self._init_persons()
        self.__player_major_imp_cards = None
        self.__minor_imp_cards = minor_imp_cards
        self.__occupation_cards = occup_cards
        self.__has_future_goods_on_action_spaces = False
        self.__future_goods = []
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

    @property
    def minor_improvements(self) -> Deck:
        """Returns player's minor improvement cards."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__minor_imp_cards

    @property
    def occupations(self) -> Deck:
        """Returns player's occupations cards."""
# FIXME! Need to make sure ACTUALLY returns read only.
        return self.__occupation_cards

    def discard_goods(self, good_type: GoodsType, number: int) -> None:
        """Player action that can be called at any time to discard unwanted goods."""

    def grains_or_veg_to_food(self, good_type: GoodsType, number: int) -> None:
        """Player action that can be called at any time turning crops into food."""

    def get_goods_from_future_action_spaces(self, round_num: int) -> None:
        """If player has items on future action spaces, this add them to player's inventory."""
        if self.__has_future_goods_on_action_spaces:
            for future_good in self.__future_goods:
                if future_good[0] == round_num:
                    self.__supply.add(
                        {
                            "goods_type": future_good[1],
                            "location": "inventory",
                            "coordinate": (-1,-1)
                        }
                    )

    def place_player_on_action_space(
            self,
            destination_coord: Coordinate,
            source_coord: Coordinate
        ) -> None:
        """Player public method to place a 'person' on the action spaces board."""
        if destination_coord not in self.__game.action_spaces.open_spaces:
            raise ValueError("Coordinate is already occupied.")
        self.__supply.move("person", 1, "action_space", destination_coord, "farmyard", source_coord)
        self.__farmyard.move(
            "person", 1, "action_space", destination_coord, "farmyard", source_coord
        )
        self.__game.action_spaces.move(
            "person", 1, "action_space", destination_coord, "farmyard", source_coord
        )

    def move_items(self, move_request: MoveRequest) -> None:
        """Player call to move selected item(s) around player controlled spaces."""
        self.__supply.move(**move_request)
        self.__farmyard.move(**move_request)
        self.__game.action_spaces.move(**move_request)

    def _init_persons(self) -> None:
        """Move a person piece from one coordinate & board to another."""
        self.__supply.move("person", 1, "farmyard", (1,0), "inventory", (-1,-1))
        self.__supply.move("person", 1, "farmyard", (2,0), "inventory", (-1,-1))
        self.__farmyard.move("person", 1, "farmyard", (1,0), "inventory", (-1,-1))
        self.__farmyard.move("person", 1, "farmyard", (2,0), "inventory", (-1,-1))


class Players:
    """
    Combination/convenience class that unifies all 4 possible players 
    for easy '.' access to player methods as well as iterable collection.
    """

    __one: Player
    __two: Player
    __three: Player
    __four: Player
    __num_players: int
    __players_tup: tuple[Player, ...]

    def __new__(cls, players_tup: tuple[Player, ...]) -> Self:
        self = super().__new__(cls)
        self.__players_tup = players_tup
        self.__num_players = len(players_tup)
        if self.num_players == 1:
            self.__one = players_tup[0]
        elif self.num_players == 2:
            self.__one = players_tup[0]
            self.__two = players_tup[1]
        elif self.num_players == 3:
            self.__one = players_tup[0]
            self.__two = players_tup[1]
            self.__three = players_tup[2]
        elif self.num_players == 4:
            self.__one = players_tup[0]
            self.__two = players_tup[1]
            self.__three = players_tup[2]
            self.__four = players_tup[3]
        return self

    @property
    def one(self) -> Player:
        """Returns player one & their methods."""
        return self.__one

    @property
    def two(self) -> Player:
        """Returns player two & their methods."""
        return self.__two

    @property
    def three(self) -> Player:
        """Returns player three & their methods."""
        return self.__three

    @property
    def four(self) -> Player:
        """Returns player four & their methods."""
        return self.__four

    @property
    def num_players(self) -> int:
        """Returns number of players in current game."""
        return self.__num_players

    @property
    def players_tup(self) -> tuple[Player, ...]:
        """Returns iterable collection of players for easier batch ops."""
# FIXME! Need to make sure read only
        return self.__players_tup
