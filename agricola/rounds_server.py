"""
Module providing the state machine(s) for game turn based logic.
"""

from typing import Self

from .type_defs import RoundSteps

# TODO: Maybe use context managers here!

class PlayerActionServer:
    """Smallest sub state machine governing actions available to player who's turn it is."""

    __active_player_id: int

    def __new__(cls) -> Self:
        self = super().__new__(cls)
        self.__active_player_id = 1
        return self

    @property
    def active_player_id(self) -> int:
        """Returns the id of the currently active player."""
        return self.__active_player_id

    def _block_for_player_action(self) -> None:
        """Blocks game executions outside of permitted player actions."""

    def _place_player(self) -> None:
        """"""

    def _make_decision(self) -> None:
        """"""

# TODO: Decide which order the ^ & \/ should take

    def _take_action(self) -> None:
        """"""


class TurnServer:
    """Small sub state machine governing 'person' placement turn logic."""

    __player_action_server: PlayerActionServer

    def __new__(cls) -> Self:
        self = super().__new__(cls)
        self.__player_action_server = PlayerActionServer()
        return self

    @property
    def player_action_server(self) -> PlayerActionServer:
# FIXME! Need to make sure read only or switch to getter/setter
        """Returns player action server object."""
        return self.__player_action_server

    def _block_for_turn(self) -> None:
        """Blocks game executions outside of permitted in-turn actions."""

    def _run_each_players_action_server(self) -> None:
        """"""


class RoundServer:
    """Medium sub state machine handling state actions within a round."""
# TODO: each round has 4 phases: 1) Preparation, 2) Work, 3) Returning home, 4) Harvest
    # Each round, players (clockwise/inc order) place all 'person's on action spaces one at a time.

    __round_step: RoundSteps
    __turn_server: TurnServer

    def __new__(cls) -> Self:
        self = super().__new__(cls)
        self.__round_step = "preparation"
        self.__turn_server = TurnServer()
        return self

    @property
    def round_step(self) -> RoundSteps:
        """Returns the current step/phase of the current round."""
        return self.__round_step

    @property
    def turn_server(self) -> TurnServer:
# FIXME! Need to make sure read only or switch to getter/setter
        """Returns turn server object."""
        return self.__turn_server

    def _block_for_step(self) -> None:
        """Blocks game executions outside of permitted in-step actions."""

# TODO: below relate to PREPARATION ___________________________
    def _add_new_action_space(self) -> None:
        """"""

    def _players_get_goods_from_future_action_spaces(self) -> None:
        """"""

    def _populate_accum_spaces(self) -> None:
        """"""

# TODO: below relate to WORK __________________________________
    def _run_turn_server(self) -> None:
        """"""

# TODO: below relate to RETURNING HOME ________________________
    def _return_people_home(self) -> None:
        """"""

# TODO: below relate to HARVEST _______________________________
    def _check_if_harvest_round(self) -> None:
        """"""
        # rounds 4, 7, 9, 11, 13, and 14

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
# TODO: game is played over 14 rounds, handled here

    __round_number: int
    __phase_number: int
    __round_server: RoundServer

    def __new__(cls) -> Self:
        self = super().__new__(cls)
        self.__round_number = 1
        self.__phase_number = 1
        self.__round_server = RoundServer()
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

    def _block_for_round(self) -> None:
        """Blocks game executions outside of permitted in-round actions."""

    def _run_round_server(self) -> None:
        """"""

    def _score_game_at_end(self) -> None:
        """"""
