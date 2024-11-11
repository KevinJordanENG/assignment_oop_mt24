"""
Main class / API for the agricola game pkg.

Implements the facade pattern allowing full playing of the game through main 'Game' class.
"""
# TODO: game is played over 14 rounds
    # TODO: each round has 4 phases: 1) Preparation, 2) Work, 3) Returning home, 4) Harvest
# TODO: Maybe implement singleton pattern for phase/round/turn management for each game instance?

import os
import random
from uuid import uuid4
from typing import Self, cast

from .players import Player
from .gameboards import ActionSpaces, Tiles
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
        self._init_action_spaces(num_players, path=data_dir_path)
        self._init_tiles()
        self._init_major_imp_cards(path=data_dir_path)
# TODO: Need to init temp local minor/occup, pass to player init to pull rnd, then drop leftovers
        minor_imps_full = self._init_minor_imp_cards(path=data_dir_path)
        occups_full = self._init_occup_cards(path=data_dir_path, num_players=num_players)
        self.__players = self._init_players(num_players, minor_imps_full, occups_full)
        del minor_imps_full, occups_full # Delete leftovers as not needed after game init.
        return self

    @property
    def instance_uuid(self) -> str:
        """Returns uuid str of game instance."""
        return self.__instance_uuid

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
# TODO: Fix the card deck init! Sourcing per player!

        # Initially list so append works / iterative init for num_players.
        players_list: list[Player] = []
        # Generate random int to assign initial 'starting player' token based on num_players.
        rnd = random.randint(1, num_players)
        for player_id in range(num_players):
            players_list.append(Player(self, player_id+1, player_id+1 == rnd))
        # Cast to tuple for return making it immutable.
        return tuple(players_list)

    def _check_valid_move(self) -> None:
        """
        Error checking logic for if move requested is valid.
        Extensive and uses many subroutines as well as turn/round/stage server/state-machine.
        """
# TODO: Build this!
