"""
Module providing the state machine(s) for game turn based logic.
"""
from __future__ import annotations
from contextvars import ContextVar
from typing import Self, TYPE_CHECKING

from .type_defs import GameStates
from .gameboards import ActionSpaces
if TYPE_CHECKING:
    from .players import Players


class StateError(Exception):
    """Error for trying to perform illegal game moves based on current game state."""

PhaseChangeRounds: set[int] = set([4, 7, 9, 11, 13, 14])
"""Set of predefined rounds where game 'phase' changes. Also when harvest happens."""

class PlayerActionServer:
    """Smallest sub state machine governing actions available to player who's turn it is."""

    __game_state: GameState
    __active_player_id: int

    def __new__(cls, game_state: GameState) -> Self:
        self = super().__new__(cls)
        self.__game_state = game_state
        self.__active_player_id = 1
        return self

    @property
    def active_player_id(self) -> int:
        """Returns the id of the currently active player."""
        return self.__active_player_id

    def play_next_player_actions(self) -> None:
        """Sets state to next player for them to take actions."""
        # Set state as appropriate.
        if (self.__game_state.STATE.get() == "running_round_prep"
            or self.__game_state.STATE.get() == "running_work_player_4"):
            self.__game_state.STATE.set("running_work_player_1")
        elif self.__game_state.STATE.get() == "running_work_player_1":
            self.__game_state.STATE.set("running_work_player_2")
        elif self.__game_state.STATE.get() == "running_work_player_2":
            self.__game_state.STATE.set("running_work_player_3")
        elif self.__game_state.STATE.get() == "running_work_player_3":
            self.__game_state.STATE.set("running_work_player_4")

    def set_current_player_decision(self) -> None:
        """Sets state to decision mode if current player decision is required."""
        self.__game_state.STATE.set("current_player_decision")


class RoundServer:
    """Medium sub state machine handling state actions within a round."""

    __game_state: GameState
    __player_action_server: PlayerActionServer

    def __new__(cls, game_state: GameState) -> Self:
        self = super().__new__(cls)
        self.__game_state = game_state
        self.__player_action_server = PlayerActionServer(game_state)
        return self

    @property
    def player_action_server(self) -> PlayerActionServer:
# FIXME! Need to make sure read only or switch to getter/setter
        """Returns player action server object."""
        return self.__player_action_server

    def start_round(self, action_spaces: ActionSpaces, players: Players) -> None:
        """Method to start the round."""
        # Set state as appropriate.
        self.__game_state.STATE.set("running_round_prep")
        # Perform preparation actions.
        action_spaces.add_action_space(
            self.__game_state.round_number,
            self.__game_state.phase_number
        )
        action_spaces.accumulate_all()
        for player in players.players_tup:
            player.get_goods_from_future_action_spaces(self.__game_state.round_number)

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


class GameState:
    """Main state class that controls all sub-state components."""

# TODO: Consider joining RoundServer & PlayerActionServer into main GameState
    # Not currently clear why separate classes are beneficial...

    __round_number: int
    __phase_number: int
    __num_players: int
    __round_server: RoundServer

    STATE: ContextVar[GameStates] = ContextVar('STATE', default="not_started")
    """Context variable allowing all server state managers to update/read game state."""

    def __new__(cls, num_players: int) -> Self:
        self = super().__new__(cls)
        self.__round_number = 0
        self.__phase_number = 0
        self.__num_players = num_players
        self.__round_server = RoundServer(self)
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
    def round_server(self) -> RoundServer:
        """Returns round server object."""
# FIXME! Need to make sure read only or switch to getter/setter
        return self.__round_server

    def start(self) -> None:
        """Starts game & changes game state."""
        self.STATE.set("running_game")
        self.__phase_number = 1

    def stop(self) -> None:
        """Stops the game early."""
        self.STATE.set("stopped_early")
        self.__round_number = 0
        self.__phase_number = 0

    def play_round(self) -> None:
        """Starts the next round."""
        self.__round_number += 1
        if self.__round_number in PhaseChangeRounds:
            self.__phase_number += 1

    def is_valid_state_for_func(
            self,
            current_state: GameStates,
            valid_states: set[GameStates]
        ) -> bool:
        """
        Takes in current state & set of valid states,
        returns True if current state is valid for function where called.
        """
        subset_valid_states = self._filter_valid_states_by_num_players(valid_states)
        if current_state in subset_valid_states:
            return True
        raise StateError("Illegal move attempted.")

    def _filter_valid_states_by_num_players(self, valid_states: set[GameStates]) -> set[GameStates]:
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
