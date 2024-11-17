"""
Main class / API for the agricola game pkg.

Implements the facade pattern allowing full playing of the game through main 'Game' class.
"""

import os
import random
from uuid import uuid4
from typing import Self, cast

from .players import Player
from .gameboards import ActionSpaces, Tiles
from .rounds_server import GameState
from .cards import Deck
from .type_defs import SpaceType, GoodsType, Location, Coordinate


class Game:
    """
    Agricola Game API instance class.
    """

# TODO: Implement flyweight cuz why not!
    __instance_uuid: str
    __players: tuple[Player, ...]
    __action_spaces: ActionSpaces
    __tiles: dict[tuple[SpaceType, SpaceType], Tiles]
    __major_imp_cards: Deck
    __state: GameState

    def __new__(
            cls,
            *,
            num_players: int,
            data_dir_path: str = os.path.join(os.getcwd(), "agricola", "data", ""),
            instance_uuid: str = str(uuid4())
        ) -> Self:
        """
        Game class constructor.
        """
        self = super().__new__(cls)
        if (num_players < 1) or (num_players > 4):
            raise ValueError("Number of players must be between 1 and 4.")
        self.__instance_uuid = instance_uuid
        self.__state = GameState()
        self._init_action_spaces(num_players, path=data_dir_path)
        self._init_tiles()
        self._init_major_imp_cards(path=data_dir_path)
        # Init both full decks of minor impr. & occupation cards.
        minor_imps_full = self._init_minor_imp_cards(path=data_dir_path)
        occups_full = self._init_occup_cards(path=data_dir_path, num_players=num_players)
        # Init players.
        self.__players = self._init_players(num_players, minor_imps_full, occups_full)
        # Delete leftovers from these decks as remaining cards not needed after game init.
        del minor_imps_full, occups_full
        return self

    @property
    def instance_uuid(self) -> str:
        """Returns uuid str of game instance."""
        return self.__instance_uuid

    @property
    def round(self) -> int:
        """Returns the current round number from game's GameState instance."""
        return self.__state.round_number

    @property
    def phase(self) -> int:
        """Returns the current phase number from game's GameState instance."""
        return self.__state.phase_number

    @property
    def players(self) -> tuple[Player, ...]:
        """Returns read only view of players currently in the game."""
# FIXME! Need to make sure return is ACTUALLY read only.
        return self.__players

    @property
    def action_spaces(self) -> ActionSpaces:
        """Returns read only view of gameboard/action spaces."""
# FIXME! Need to make sure return is ACTUALLY read only.
        return self.__action_spaces

    @property
    def major_imp_cards(self) -> Deck:
        """Returns read only view of major improvement cards available."""
# FIXME! Need to make sure return is ACTUALLY read only.
        return self.__major_imp_cards

    @property
    def tiles(self) -> dict[tuple[SpaceType, SpaceType], Tiles]:
        """Returns view of current store of tiles in game."""
# FIXME! Need to make sure return is ACTUALLY read only.
        return self.__tiles

    def start_game(self) -> None:
        """"""

    def quit_game_early(self) -> None:
        """"""

    def score_game(self) -> None:
        """"""

    def move_item(
            self,
            player: Player,
            good: GoodsType,
            num_goods: int,
            new_board: Location,
            new_coords: Coordinate,
            prev_board: Location,
            prev_coord: Coordinate
        ) -> None:
        """Unified move routine that changes all necessary data."""
# TODO: Add some SERIOUS error checking here via subroutine!
        self._check_valid_move()
        player.move_items(good, num_goods, new_board, new_coords, prev_board, prev_coord)
        self.__action_spaces.move(good, num_goods, new_board, new_coords, prev_board, prev_coord)

    def _init_action_spaces(self, num_players: int, *, path: str) -> None:
        """Sets up the action spaces board depending on number of players."""
        self.__action_spaces = ActionSpaces(num_players, path)

    def _init_tiles(self) -> None:
        """Initializes game store of limited 2 sided tiles."""
        # Init empty.
        self.__tiles = {}
        # Make sure we know they really are SpaceTypes.
        wf: tuple[SpaceType, SpaceType] = (
            cast(SpaceType, "wood_room"), cast(SpaceType, "field")
        )
        cs: tuple[SpaceType, SpaceType] = (
            cast(SpaceType, "clay_room"), cast(SpaceType, "stone_room")
        )
        # Initialize / add to game store.
        self.__tiles[wf] = Tiles(wf)
        self.__tiles[cs] = Tiles(cs)

    def _init_major_imp_cards(self, *, path: str) -> None:
        """Sets up the major improvements card deck."""
        self.__major_imp_cards = Deck("major", path=path)

    def _init_minor_imp_cards(self, *, path: str) -> Deck:
        """Loads full minor improvements card deck, used in player init, then extras dropped."""
        return Deck("minor", path=path)

    def _init_occup_cards(self, *, path: str, num_players: int) -> Deck:
        """Loads occupation card deck per num_players, used in player init, then extras dropped."""
        return Deck("occupation", path=path, num_players=num_players)

    def _init_players(self, num_players: int, minor: Deck, occup: Deck) -> tuple[Player, ...]:
        """Creates player instances for the game."""
        # Initially list so append works / iterative init for num_players.
        players_list: list[Player] = []
        # Generate random int to assign initial 'starting player' token based on num_players.
        rnd = random.randint(1, num_players)
        for player in range(num_players):
            # Call Deck's method of returning 7 random cards to pass to Player init.
            set_of_seven_minor = minor.get_seven_rand_cards()
            set_of_seven_occup = occup.get_seven_rand_cards()
            # Init next player & append to our players list.
            players_list.append(
                Player(
                    self,
                    set_of_seven_minor,
                    set_of_seven_occup,
                    num_players,
                    player_id=player+1,
                    starting=(player+1 == rnd)
                )
            )
        # Cast to tuple for return making it immutable.
        return tuple(players_list)

    def _check_valid_move(self) -> None:
        """
        Error checking logic for if move requested is valid.
        Extensive and uses many subroutines as well as turn/round/stage server/state-machine.
        """
# TODO: Build this!
