"""
Main class / API for the agricola game pkg.

Implements the facade pattern allowing full playing of the game through main 'Game' class.
"""

import os
import random
from uuid import uuid4
from typing import Self, cast

from .players import Player, Players
from .gameboards import ActionSpaces, Tiles, MoveRequest
from .rounds_server import GameState
from .cards import Deck
from .type_defs import SpaceType, Coordinate, GameStates, GoodsType, Location


class Game:
    """
    Agricola Game API instance class.
    """

# TODO: Implement flyweight cuz why not!
    __instance_uuid: str
    __player: Players
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
        self.__state = GameState(num_players)
        self._init_action_spaces(num_players, path=data_dir_path)
        self._init_tiles()
        self._init_major_imp_cards(path=data_dir_path)
        # Init both full decks of minor impr. & occupation cards.
        minor_imps_full = self._init_minor_imp_cards(path=data_dir_path)
        occups_full = self._init_occup_cards(path=data_dir_path, num_players=num_players)
        # Init players.
        self.__player = self._init_players(num_players, minor_imps_full, occups_full)
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
    def game_state(self) -> GameStates:
        """Returns the current state of the game from GameState server."""
        return self.__state.STATE.get()

    @property
    def player(self) -> Players:
        """Returns read only view of all players currently in the game."""
# FIXME! Need to make sure return is ACTUALLY read only.
        return self.__player

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
        """Public method to start the game after init/setup."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        self.__state.start()

    def start_next_round(self) -> None:
        """Public method to start the next round of game play (of 14 total)."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"running_game"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        self.__state.play_round()
        self.__state.round_server.start_round(self.__action_spaces, self.__player)

    def play_next_player_work_actions(self) -> None:
        """Public method to play the next player action in the work step of round."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3"
        }
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        self.__state.round_server.player_action_server.play_next_player_actions()

    def place_player_on_action_space(
            self,
            destination_coord: Coordinate,
            source_coord: Coordinate,
            *,
            player_id: int
        ) -> None:
        """
        Game public method to place a 'person' on the action spaces board for specified player.
        Method just forwards to game.player.player_id.place_player() via tuple index.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        self.__player.players_tup[player_id-1].place_player_on_action_space(
            destination_coord, source_coord
        )

    def move_item(self, move_request: MoveRequest, *, player_id: int) -> None:
        """Unified move routine from 'game' directly that changes all necessary data."""
        self.__player.players_tup[player_id-1].move_items(move_request)

    def quit_game_early(self) -> None:
        """
        Public method allowing early stopping of game.
        Method puts game in state that requires re-starting with a fresh game instance.
        """
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_game",
            "running_round_prep",
            "running_round_return_home",
            "running_round_harvest",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        self.__state.stop()

    def score_game(self) -> None:
        """Scores game for all players upon completion."""
        valid_states: set[GameStates] = {"finished"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
# TODO: build scoring logic

    def bundle_move_request(
            self,
            *,
            goods_type: str,
            num_goods: int,
            destination_board: str,
            destination_coord: tuple[int,int],
            source_board: str,
            source_coord: tuple[int,int]
        ) -> MoveRequest:
        """Helper function that bundles/casts to TypedDict needed for requesting item moves."""
        move_request: MoveRequest = {
            "goods_type": cast(GoodsType, goods_type),
            "num_goods": num_goods,
            "destination_board": cast(Location, destination_board),
            "destination_coord": cast(Coordinate, destination_coord),
            "source_board": cast(Location, source_board),
            "source_coord": cast(Coordinate, source_coord)
        }
        return move_request

    def _init_action_spaces(self, num_players: int, *, path: str) -> None:
        """Sets up the action spaces board depending on number of players."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        # Init.
        self.__action_spaces = ActionSpaces(num_players, path)

    def _init_tiles(self) -> None:
        """Initializes game store of limited 2 sided tiles."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
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
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        # Init.
        self.__major_imp_cards = Deck("major", path=path)

    def _init_minor_imp_cards(self, *, path: str) -> Deck:
        """Loads full minor improvements card deck, used in player init, then extras dropped."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        # Init.
        return Deck("minor", path=path)

    def _init_occup_cards(self, *, path: str, num_players: int) -> Deck:
        """Loads occupation card deck per num_players, used in player init, then extras dropped."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
        # Init.
        return Deck("occupation", path=path, num_players=num_players)

    def _init_players(self, num_players: int, minor: Deck, occup: Deck) -> Players:
        """Creates player instances for the game."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state.is_valid_state_for_func(self.game_state, valid_states)
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
        # Use list of player to init Players class (cast to tuple when passing in).
        return Players(tuple(players_list))
