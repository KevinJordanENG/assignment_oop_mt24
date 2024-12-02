"""
Main class / API for the agricola game pkg.

Implements the facade pattern allowing full playing of the game through main 'Game' class.
"""
# Standard lib imports.
from __future__ import annotations
from contextlib import contextmanager
import os
import random
from types import MappingProxyType
from uuid import uuid4
from typing import ClassVar, Iterator, Mapping, Self, cast, final
from weakref import WeakValueDictionary
# Relative imports from `agricola` package.
from .players import Player, Players
from .gameboards import ActionSpaces, Tiles, MoveRequest
from .state_server import GameState
from .cards import Deck
from .type_defs import SpaceType, Coordinate, GameStates, GoodsType, Location


DATA_DIR_PATH: str = os.path.join(os.getcwd(), "agricola", "data", "")
"""
This global is the path to the CSV's containing card & action data.
It is not meant to be set by the `user`, rather, set once by the `operator`
when installing the game on target machine the 1st time.
"""


@final # No subclasses allowed (Optional Agricola expansion packs would just add to Decks' CSVs).
class Game:
    """
    Agricola Game API instance class.
    """

    __game_instances: ClassVar[WeakValueDictionary[str, Game]] = WeakValueDictionary()
    # ^^^^^^^^^^^^^^ --> Flyweight pattern.
    __is_constructing_state_server: ClassVar[bool] = False  # ⌉
    __is_constructing_action_spaces: ClassVar[bool] = False # |  Cool pattern of context managers for instantiation
    __is_constructing_tiles: ClassVar[bool] = False         # |- control borrowed from Dr. Stefano Gogioso's
    __is_constructing_decks: ClassVar[bool] = False         # |  'marketplace' implementation in OOP-MT2024.
    __is_constructing_players: ClassVar[bool] = False       # ⌋

    @staticmethod
    def _is_constructing_state_server() -> bool:
        """Class wide flag ensuring GameState is only instantiated by Game via context manager."""
        return Game.__is_constructing_state_server

    @staticmethod
    def _is_constructing_action_spaces() -> bool:
        """Class wide flag ensuring ActionSpaces is only instantiated by Game via context manager."""
        return Game.__is_constructing_action_spaces

    @staticmethod
    def _is_constructing_tiles() -> bool:
        """Class wide flag ensuring Tiles are only instantiated by Game via context manager."""
        return Game.__is_constructing_tiles

    @staticmethod
    def _is_constructing_decks() -> bool:
        """Class wide flag ensuring Decks are only instantiated by Game via context manager."""
        return Game.__is_constructing_decks

    @staticmethod
    def _is_constructing_players() -> bool:
        """Class wide flag ensuring Players are only instantiated by Game via context manager."""
        return Game.__is_constructing_players

    @staticmethod
    @contextmanager
    def __constructing_state_server() -> Iterator[None]:
        """
        Context manager helping ensure objects are only instantiated by 'Game' not Agricola user directly.
        Pattern & idea borrowed from Dr. Stefano Gogioso's 'marketplace' implementation in OOP-MT2024.
        Pattern used throughout the project, and only cited here for brevity/conciseness.
        """
        # Confirm not already in context.
        assert not Game.__is_constructing_state_server
        # Set context ClassVar to 'is constructing'.
        Game.__is_constructing_state_server = True
        try:
            # Pass control back TO caller.
            yield None
        finally:
            # Cleanup and set 'is constructing' back to False once control passed back FROM caller.
            Game.__is_constructing_state_server = False
        # Advanced Language Feature: Generator / Context Manager - When this structure of try -> yield -> finally
        # is found, Python interpreter generates a context manager invoked using `with` syntax.

    @staticmethod
    @contextmanager
    def __constructing_action_spaces() -> Iterator[None]:
        """
        Context manager helping ensure objects are only instantiated by 'Game' not Agricola user directly.
        """
        assert not Game.__is_constructing_action_spaces
        Game.__is_constructing_action_spaces = True
        try:
            yield None
        finally:
            Game.__is_constructing_action_spaces = False

    @staticmethod
    @contextmanager
    def __constructing_tiles() -> Iterator[None]:
        """
        Context manager helping ensure objects are only instantiated by 'Game' not Agricola user directly.
        """
        assert not Game.__is_constructing_tiles
        Game.__is_constructing_tiles = True
        try:
            yield None
        finally:
            Game.__is_constructing_tiles = False

    @staticmethod
    @contextmanager
    def __constructing_decks() -> Iterator[None]:
        """
        Context manager helping ensure objects are not instantiated by Agricola user directly.
        Decks are a special case where both 'Game' and 'Player' objects are valid creators of Major Imp. Decks.
        """
        assert not Game.__is_constructing_decks
        Game.__is_constructing_decks = True
        try:
            yield None
        finally:
            Game.__is_constructing_decks = False

    @staticmethod
    @contextmanager
    def __constructing_players() -> Iterator[None]:
        """
        Context manager helping ensure objects are only instantiated by 'Game' not Agricola user directly.
        """
        assert not Game.__is_constructing_players
        Game.__is_constructing_players = True
        try:
            yield None
        finally:
            Game.__is_constructing_players = False

    __instance_uuid: str
    __state: GameState
    __action_spaces: ActionSpaces
    __tiles: dict[tuple[SpaceType, SpaceType], Tiles]
    __major_imp_cards: Deck
    __player: Players

    def __new__(
            cls,
            *,
            num_players: int,
            instance_uuid: str = str(uuid4())
        ) -> Self:
        """
        Game class constructor.

        Uses flyweight pattern to enforce that each Game object is fully unique,
        but equally allowing multiple different instances.
        """
        # Early reject if invalid num_players.
        if (num_players < 1) or (num_players > 4):
            raise ValueError("Number of players must be between 1 and 4.")
        # Check if game instance (with same uuid) already exists.
        self = Game.__game_instances.get(instance_uuid)
        if self is None:
            # If game not found, create/init it.
            self = super().__new__(cls)
            self.__instance_uuid = instance_uuid
            # Init game state (also flyweight) within proper managed context.
            with Game.__constructing_state_server():
          # ^^^^ Advanced Language Feature: Context Manager - special way of handling setup/teardown
            # of contextual / situational control / logic.
                self.__state = GameState(num_players, instance_uuid)
            # Init game controlled objects within proper managed context(s).
            with Game.__constructing_action_spaces():
                self.__init_action_spaces(num_players, path=DATA_DIR_PATH)
            with Game.__constructing_tiles():
                self.__init_tiles()
            with Game.__constructing_decks():
                self.__init_major_imp_cards(path=DATA_DIR_PATH)
                # Init both full decks of minor impr. & occupation cards.
                minor_imps_full = self.__init_minor_imp_cards(path=DATA_DIR_PATH)
                occups_full = self.__init_occup_cards(path=DATA_DIR_PATH, num_players=num_players)
                # Init players in proper context. Needs to be within constructing_decks context as creating
                # players' hands of 7 cards of minor imps. & occupations also calls 'Deck' constructor.
                with Game.__constructing_players():
                    self.__player = self.__init_players(num_players, minor_imps_full, occups_full)
            # Delete leftovers from these decks as remaining cards not needed after game init.
            del minor_imps_full, occups_full
            # Store instance as otherwise flyweight doesn't work.
            Game.__game_instances[instance_uuid] = self
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
    def state(self) -> GameState:
        """Returns access to the GameState server."""
        return self.__state

    @property
    def player(self) -> Players:
        """Returns access to all players currently in the game."""
        return self.__player

    @property
    def action_spaces(self) -> ActionSpaces:
        """Returns access to gameboard/action spaces."""
        return self.__action_spaces

    @property
    def major_imp_cards(self) -> Deck:
        """Returns access to major improvement cards available."""
        return self.__major_imp_cards

    @property
    def tiles(self) -> Mapping[tuple[SpaceType, SpaceType], Tiles]:
        """Returns read only view of current store of tiles in game."""
        return MappingProxyType(self.__tiles)

    def start_game(self) -> None:
        """Public method to start the game after init/setup."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        self.__state._start()

    def start_next_round(self) -> None:
        """Public method to start the next round of game play (of 14 total)."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_game", "running_round_return_home", "running_round_harvest"
        }
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        self.__state._start_round(self.__action_spaces, self.__player)

    def play_next_player_work_actions(self) -> None:
        """Public method to play the next player action in the work step of round."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        self.__state._play_next_player_actions()

    def place_person_on_action_space(
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
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        self.__player.players_tup[player_id-1].place_person_on_action_space(
            destination_coord, source_coord
        )

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
            "running_work_player_4",
            "current_player_decision"
        }
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        self.__state._stop()

    def score_game(self) -> None:
        """Scores game for all players upon completion."""
        valid_states: set[GameStates] = {"finished"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        raise NotImplementedError()

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
        # Helper func so valid in any state as no modification to game data.
        move_request: MoveRequest = {
            "goods_type": cast(GoodsType, goods_type),
            "num_goods": num_goods,
            "destination_board": cast(Location, destination_board),
            "destination_coord": cast(Coordinate, destination_coord),
            "source_board": cast(Location, source_board),
            "source_coord": cast(Coordinate, source_coord)
        }
        return move_request
    
    def _move_item(self, move_request: MoveRequest, *, player_id: int) -> None:
        """Unified move routine from 'game' directly that changes all necessary data."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {
            "running_game",
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
            "running_round_return_home",
            "running_round_harvest"
        }
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        self.__player.players_tup[player_id-1]._move_items(move_request)

    def __init_action_spaces(self, num_players: int, *, path: str) -> None:
        """Sets up the action spaces board depending on number of players."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        # Call instantiation.
        self.__action_spaces = ActionSpaces(self, num_players, path)

    def __init_tiles(self) -> None:
        """Initializes game store of limited 2 sided tiles."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
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

    def __init_major_imp_cards(self, *, path: str) -> None:
        """Sets up the major improvements card deck."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        # Build & return.
        self.__major_imp_cards = Deck(self, "major", path=path)

    def __init_minor_imp_cards(self, *, path: str) -> Deck:
        """Loads full minor improvements card deck, used in player init, then extras dropped."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        # Build & return.
        return Deck(self, "minor", path=path)

    def __init_occup_cards(self, *, path: str, num_players: int) -> Deck:
        """Loads occupation card deck per num_players, used in player init, then extras dropped."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        # Build & return.
        return Deck(self, "occupation", path=path, num_players=num_players)

    def __init_players(self, num_players: int, minor: Deck, occup: Deck) -> Players:
        """Creates player instances for the game."""
        # Check game is in valid state.
        valid_states: set[GameStates] = {"not_started"}
        self.__state._is_valid_state_for_func(self.game_state, valid_states)
        # Initially list so append works / iterative init for varied num_players.
        players_list: list[Player] = []
        # Generate random int to assign initial 'starting player' token based on num_players.
        rnd = random.randint(1, num_players)
        for player in range(num_players):
            # Call Deck's method of returning 7 random cards to pass to Player init.
            set_of_seven_minor = minor._get_seven_rand_cards()
            set_of_seven_occup = occup._get_seven_rand_cards()
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
