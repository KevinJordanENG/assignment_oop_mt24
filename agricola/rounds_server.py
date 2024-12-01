"""
Module providing the state machine(s) for game turn based logic.
"""
from __future__ import annotations
from contextvars import ContextVar
from typing import ClassVar, Self, TYPE_CHECKING, final
from weakref import WeakValueDictionary

from .type_defs import GameStates
from .gameboards import ActionSpaces
if TYPE_CHECKING:
    from .players import Players


class StateError(Exception):
    """Error for trying to perform illegal game moves based on current game state."""


PhaseChangeRounds: set[int] = set([4, 7, 9, 11, 13, 14])
"""Set of predefined rounds where game 'phase' changes. Also when harvest happens."""


@final
class GameState:
    """
    Main state class that controls all sub-state components.
    
    Implements flyweight pattern tied to same uuid as game 
    redundantly ensuring unique state machine per game.
    Contains 3 main levels of logic/state related actions:
    1. Round - Controls inter-round logic.
    2. Turn - Controls intra-round logic and turn taking.
    3. Player actions - Player's individual person placing logic.
    """

    __state_servers: ClassVar[WeakValueDictionary[str, GameState]] = WeakValueDictionary()
    __round_number: int
    __phase_number: int
    __num_players: int
    __active_player_id: int

    STATE: ContextVar[GameStates] = ContextVar('STATE', default="not_started")
    """Context variable allowing all server state managers to update/read game state."""

    def __new__(cls, num_players: int, game_uuid: str) -> Self:
        """Constructor using flyweight pattern & context manager validation for init only by 'Game'."""
        # Dynamic to avoid circular imports, and error if not being built in proper context.
        from .game import Game
        if not Game._is_constructing_state_server():
            raise TypeError("GameState can only be instantiated by 'Game', not directly.")
        # Try to get state by game uuid if cached by flyweight pattern instance cache.
        self = GameState.__state_servers.get(game_uuid)
        if self is None:
            # Create instance if not already existent.
            self = super().__new__(cls)
            self.__round_number = 0
            self.__phase_number = 0
            self.__num_players = num_players
            self.__active_player_id = 1
            GameState.__state_servers[game_uuid] = self
        return self

    @property
    def round_number(self) -> int:
        """Returns the number of the current round."""
        return self.__round_number

    @property
    def phase_number(self) -> int:
        """Returns the number of the current phase."""
        return self.__phase_number

    @property
    def active_player_id(self) -> int:
        """Returns the id of the currently active player."""
        return self.__active_player_id

    def _play_next_player_actions(self) -> None:
        """Sets state to next player for them to take actions."""
        # Set state as appropriate.
        if (self.STATE.get() == "running_round_prep"
            or self.STATE.get() == "running_work_player_4"):
            self.STATE.set("running_work_player_1")
        elif self.STATE.get() == "running_work_player_1":
            self.STATE.set("running_work_player_2")
        elif self.STATE.get() == "running_work_player_2":
            self.STATE.set("running_work_player_3")
        elif self.STATE.get() == "running_work_player_3":
            self.STATE.set("running_work_player_4")
        else:
            raise StateError("Invalid state change action requested.")

    def _set_current_player_decision(self) -> None:
        """Sets state to decision mode if current player decision is required."""
        # Check valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4"
        }
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        self.STATE.set("current_player_decision")

    def _start_round(self, action_spaces: ActionSpaces, players: Players) -> None:
        """Method to start the round."""
        # Check valid state.
        valid_states: set[GameStates] = {
            "running_game", "running_round_return_home", "running_round_harvest"
        }
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        # Increment round & phase.
        self.__round_number += 1
        if self.__round_number in PhaseChangeRounds:
            self.__phase_number += 1
        # Set state as appropriate.
        self.STATE.set("running_round_prep")
        # Perform preparation actions.
        action_spaces._add_action_space(
            self.round_number,
            self.phase_number
        )
        action_spaces._accumulate_all()
        for player in players.players_tup:
            player._get_goods_from_future_action_spaces(self.round_number)

# TODO: below relate to RETURNING HOME ________________________
    def _return_people_home(self) -> None:
        """"""

# TODO: below relate to HARVEST _______________________________
    def _check_if_harvest_round(self) -> None:
        """"""
        # Use PhaseChangeRounds to check if harvest round

    def _harvest_crops(self) -> None:
        """"""

    def _feed_your_people(self) -> None:
        """"""
# TODO: 2 food per person 2-4 players but 3 food per person 1 player

    def _set_begging_marker(self) -> None:
        """"""

    def _animal_breeding(self) -> None:
        """"""

    def _start(self) -> None:
        """Starts game & changes game state."""
        # Check valid state.
        valid_states: set[GameStates] = {"not_started"}
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        self.STATE.set("running_game")
        self.__phase_number = 1

    def _stop(self) -> None:
        """Stops the game early."""
        # Check valid state.
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
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        self.STATE.set("stopped_early")
        self.__round_number = 0
        self.__phase_number = 0

    def _is_valid_state_for_func(
            self,
            current_state: GameStates,
            valid_states: set[GameStates]
        ) -> bool:
        """
        Takes in current state & set of valid states,
        returns True if current state is valid for function where called.
        """
        subset_valid_states = self.__filter_valid_states_by_num_players(valid_states)
        if current_state in subset_valid_states:
            return True
        raise StateError("Illegal move attempted.")

    def __filter_valid_states_by_num_players(self, valid_states: set[GameStates]) -> set[GameStates]:
        """Takes in set of normally valid states and returns subset based on num_players."""
# TODO: Maybe check this logic as more funcs added.
        if self.__num_players == 1:
            if "running_work_player_1" in valid_states:
                valid_states.remove("running_work_player_1")
            if "running_work_player_2" in valid_states:
                valid_states.remove("running_work_player_2")
            if "running_work_player_3" in valid_states:
                valid_states.remove("running_work_player_3")
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        if self.__num_players == 2:
            if "running_work_player_2" in valid_states:
                valid_states.remove("running_work_player_2")
            if "running_work_player_3" in valid_states:
                valid_states.remove("running_work_player_3")
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        if self.__num_players == 3:
            if "running_work_player_3" in valid_states:
                valid_states.remove("running_work_player_3")
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        if self.__num_players == 4:
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        return valid_states
