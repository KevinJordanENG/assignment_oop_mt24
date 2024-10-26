"""
Main class / API for the agricola game pkg.

Implements the facade pattern allowing full playing of the game through main 'Game' class.
"""

# TODO: different game rules for 1, 2, 3, and 4 player games! Also check permutations
# TODO: game is played over 14 rounds
    # TODO: each round has 4 phases: 1) Preparation, 2) Work, 3) Returning home, 4) Harvest

from typing import Self
from .players import Player

class Game:
    """
    Agricola Game API instance class.
    """

    __players: tuple[Player, ...]

    def __new__(cls, num_players: int) -> Self:
        """
        Game class constructor.
        """
        self = super().__new__(cls)
        match num_players:
            case 1:
                self._init_1_player()
            case 2:
                self._init_2_player()
            case 3:
                self._init_3_player()
            case 4:
                self._init_4_player()
            case _:
                raise ValueError("Number of players must be between 1 and 4.")
        return self

    @property
    def players(self) -> None:
        """Returns read only view of players currently in the game."""
        raise NotImplementedError

    def _init_1_player(self) -> None:
        raise NotImplementedError

    def _init_2_player(self) -> None:
        raise NotImplementedError

    def _init_3_player(self) -> None:
        raise NotImplementedError

    def _init_4_player(self) -> None:
        raise NotImplementedError
