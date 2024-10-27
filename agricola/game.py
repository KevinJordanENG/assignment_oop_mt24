"""
Main class / API for the agricola game pkg.

Implements the facade pattern allowing full playing of the game through main 'Game' class.
"""

# TODO: game is played over 14 rounds
    # TODO: each round has 4 phases: 1) Preparation, 2) Work, 3) Returning home, 4) Harvest

import random
from typing import Any, Self
from .players import Player

class Game:
    """
    Agricola Game API instance class.
    """

    __game_instance_uuid: str
    __players: tuple[Player, ...]
    __action_spaces: Any # FIXME!!! Need to setup this once built

    def __new__(cls, num_players: int) -> Self:
        """
        Game class constructor.
        """
        self = super().__new__(cls)
        if (num_players < 1) or (num_players > 4):
            raise ValueError("Number of players must be between 1 and 4.")
        self.__players = self._init_players(num_players)
        return self

    @property
    def players(self) -> tuple[Player, ...]:
        """Returns read only view of players currently in the game."""
        return self.__players

    def _init_action_spaces(self, num_players: int):
        """Sets up the action spaces board depending on number of players."""

    def _init_card_decks(self, num_players: int):
        """Sets up the decks according to num_players."""
        # TODO: decide if this should be internal to init players logic
    
    def _init_players(self, num_players: int) -> tuple[Player, ...]:
        """Creates player instances for the game."""
# TODO: build out the various num_player init logic here!
        # Initially list so append works / iterative init for num_players.
        players_list: list[Player] = []
        # Generate random int to assign initial 'starting player' token based on num_players.
        rnd = random.randint(1, num_players)
        for i in range(num_players):
            players_list.append(Player(i+1, i+1 == rnd))
        # Cast to tuple for return making it immutable.
        return tuple(players_list)
