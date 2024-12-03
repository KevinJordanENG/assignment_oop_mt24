"""
Module providing the state machine/management for game turn based logic.
"""

from __future__ import annotations
from contextvars import ContextVar
from typing import ClassVar, Self, TYPE_CHECKING, cast, final
from weakref import WeakValueDictionary
from .type_defs import GameStates
from .gameboards import ActionSpaces

if TYPE_CHECKING:
    from .players import Players


class StateError(Exception):
    """Error for trying to perform illegal game moves based on current game state."""


PhaseChangeRounds: set[int] = set([4, 7, 9, 11, 13, 14])
"""Set of predefined rounds where game 'phase' changes. Also when harvest happens."""


# Advanced Language Feature: Decorators (Final) - Modifies without need of code change.
@final  # Final blocks subclassing / inheritance supporting flyweight pattern.
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

    __state_servers: ClassVar[WeakValueDictionary[str, GameState]] = (
        WeakValueDictionary()
    )
    # Advanced Language Feature: WeakRef & Garbage Collection
    # Allows management of how garbage collection clears unused data.
    __round_number: int
    __phase_number: int
    __num_players: int
    __active_player_id: int
    __persons_left_to_place: list[int]

    STATE: ContextVar[GameStates] = ContextVar("STATE", default="not_started")
    """Context variable allowing all server state managers to update/read game state."""

    def __new__(cls, num_players: int, game_uuid: str) -> Self:
        """Constructor using flyweight pattern & context manager validation for init only by 'Game'."""
        # Dynamic to avoid circular imports, and error if not being built in proper context.
        from .game import Game

        if not Game._is_constructing_state_server():
            raise TypeError(
                "GameState can only be instantiated by 'Game', not directly."
            )
        # Try to get state by game uuid if cached by flyweight pattern instance cache.
        self = GameState.__state_servers.get(game_uuid)
        if self is None:
            # Create instance if not already existent.
            self = super().__new__(cls)
            self.__round_number = 0
            self.__phase_number = 0
            self.__num_players = num_players
            self.__active_player_id = 1
            # All players start with 2 'person's to play, so use Pythons array building `['xyz'] * int_len` syntax.
            self.__persons_left_to_place = [2] * num_players
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

    def _play_next_player_actions(self, players: Players | None = None) -> None:
        """
        Sets state to next player for them to take actions.
        As some players have more/less 'person's via having kids, function
        recurses until finds a player with people to play left, or base case
        no player does, in which case will advance to 'return home' stage.
        Optionally takes in `Players` for 'return home' & 'harvest' stages.
        """
        # Check valid state.
        valid_states: set[GameStates] = {
            "running_round_prep",
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
            "current_player_decision",
        }
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        # Only option.
        if self.STATE.get() == "running_round_prep":
            self.STATE.set("running_work_player_1")
            return
        # If current player decision, we want to increment so set back to current player.
        if self.STATE.get() == "current_player_decision":
            state_val = cast(
                GameStates, "running_work_player_" + str(self.active_player_id)
            )
            self.STATE.set(state_val)
        # Base case where all players have no persons left to place.
        if all(i == 0 for i in self.__persons_left_to_place):
            self.STATE.set("running_round_return_home")
            if players is None:
                raise ValueError(
                    "Expected 'Player' to be provided in called context."
                )
            self.__returning_home(players)
            return
        # If not base case, do checks if simple increment or loop around.
        # Last player, loop around.
        if self.active_player_id == self.__num_players:
            self.STATE.set("running_work_player_1")
            self.__active_player_id = 1
        # Otherwise simple increment.
        else:
            state_val = cast(
                GameStates,
                "running_work_player_" + str(self.active_player_id + 1),
            )
            self.STATE.set(state_val)
            self.__active_player_id += 1
        # Now that we've updated to possible next player, confirm they have 'person' to place still.
        # Check.
        if self.__persons_left_to_place[self.__active_player_id - 1] != 0:
            # If yes, do nothing.
            return
        else:
            # If no, recursive call that will update to next skipping current player.
            if players is None:
                raise ValueError(
                    "Expected 'Player' to be provided in called context."
                )
            self._play_next_player_actions(players)

    def _update_persons_left(
        self, *, add: bool = False, remove: bool = False
    ) -> None:
        """Updates GameState with player's number of 'person's left, delegating add/remove."""
        if add and remove:
            raise ValueError(
                "Ambiguous request to add AND remove person left for player in round."
            )
        elif not add and not remove:
            raise ValueError(
                "Ambiguous request to neither add nor remove player's persons left."
            )
        elif not add and remove:
            # Removing.
            self.__remove_person_left()
        elif add and not remove:
            # Adding, only when 'having kids'.
            self.__add_person_left()

    def _set_current_player_decision(self) -> None:
        """Sets state to decision mode if current player decision is required."""
        # Check valid state.
        valid_states: set[GameStates] = {
            "running_work_player_1",
            "running_work_player_2",
            "running_work_player_3",
            "running_work_player_4",
        }
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        self.STATE.set("current_player_decision")

    def _start_round(
        self, action_spaces: ActionSpaces, players: Players
    ) -> None:
        """Method to start the round."""
        # Check valid state.
        valid_states: set[GameStates] = {
            "running_game",
            "running_round_return_home",
            "running_round_harvest",
        }
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        # Increment round & phase.
        self.__round_number += 1
        if self.__round_number in PhaseChangeRounds:
            self.__phase_number += 1
        # Set state as appropriate.
        self.STATE.set("running_round_prep")
        # Perform preparation actions.
        action_spaces._add_action_space(self.round_number, self.phase_number)
        action_spaces._accumulate_all()
        for player in players.players_tup:
            player._get_goods_from_future_action_spaces(self.round_number)

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
            "current_player_decision",
        }
        self._is_valid_state_for_func(self.STATE.get(), valid_states)
        self.STATE.set("stopped_early")
        self.__round_number = 0
        self.__phase_number = 0

    def _is_valid_state_for_func(
        self, current_state: GameStates, valid_states: set[GameStates]
    ) -> bool:
        """
        Takes in current state & set of valid states,
        returns True if current state is valid for function where called.
        """
        subset_valid_states = self.__filter_valid_states_by_num_players(
            valid_states
        )
        if current_state in subset_valid_states:
            return True
        raise StateError("Illegal move attempted.")

    def __filter_valid_states_by_num_players(
        self, valid_states: set[GameStates]
    ) -> set[GameStates]:
        """Takes in set of normally valid states and returns subset based on num_players."""
        if self.__num_players == 1:
            if "running_work_player_2" in valid_states:
                valid_states.remove("running_work_player_2")
            if "running_work_player_3" in valid_states:
                valid_states.remove("running_work_player_3")
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        if self.__num_players == 2:
            if "running_work_player_3" in valid_states:
                valid_states.remove("running_work_player_3")
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        if self.__num_players == 3:
            if "running_work_player_4" in valid_states:
                valid_states.remove("running_work_player_4")
        return valid_states

    def __remove_person_left(self) -> None:
        """Decrements active players remaining 'person' count."""
        self.__persons_left_to_place[self.__active_player_id - 1] -= 1

    def __add_person_left(self) -> None:
        """Adds a person to the remaining count of persons to play when 'having kids'."""
        self.__persons_left_to_place[self.__active_player_id - 1] += 1

    def __check_if_harvest_round(self) -> bool:
        """Check for if we're in a harvest round to do harvest actions as required."""
        # Uses PhaseChangeRounds.
        return self.round_number in PhaseChangeRounds

    def __returning_home(self, players: Players) -> None:
        """Runs the if/else cases & states for if there is harvest or just straight home."""
        if self.__check_if_harvest_round():
            # Harvest, set accordingly.
            self.STATE.set("running_round_harvest")
            # Perform all harvest steps.
            self.__harvest_crops(players)
            self.__feed_your_people(players)
            self.__animal_breeding(players)
        else:
            # Return all players people home.
            self.__return_people_home(players)
        # No state changed needed as next round start expects either "return home" or "harvest" states.

    def __return_people_home(self, players: Players) -> None:
        """Takes 'person's of all players and moves them back to inventory at end on round."""
        for player in players.players_tup:
            person_locations = player.supply._count_person()
            for i in range(person_locations[0]):
                if person_locations[1][i] == "action_space":
                    # Get an open farmyard room to return person to.
                    open_room = player.farmyard._get_open_room()
                    # Move in all required places.
                    player.supply._move(
                        "person",
                        1,
                        "farmyard",
                        open_room,
                        "action_space",
                        person_locations[2][i],
                    )
                    player.farmyard._move(
                        "person",
                        1,
                        "farmyard",
                        open_room,
                        "action_space",
                        person_locations[2][i],
                    )
                    player.game.action_spaces._move(
                        "person",
                        1,
                        "farmyard",
                        open_room,
                        "action_space",
                        person_locations[2][i],
                    )

    def __harvest_crops(self, players: Players) -> None:
        """Gets crops from fields & moves to inventory for all players."""
        for player in players.players_tup:
            for coord in player.farmyard.board.keys():
                space_type = player.farmyard.get_space_type(coord)
                num_present = player.farmyard.get_num_goods_present(coord)
                goods_type = player.farmyard.get_goods_type(coord)
                if (
                    (space_type == "field")
                    and (num_present > 0)
                    and (goods_type is not None)
                ):
                    # Get crop from field and add to inventory.
                    player.supply._move(
                        goods_type, 1, "inventory", (-1, -1), "farmyard", coord
                    )
                    player.farmyard._move(
                        goods_type, 1, "inventory", (-1, -1), "farmyard", coord
                    )

    def __feed_your_people(self, players: Players) -> None:
        """Consumes required food from inventory for all players during harvest."""
        # TODO: 2 food per person 2-4 players but 3 food per person 1 player.
        raise NotImplementedError()

    def __set_begging_marker(self) -> None:
        """Sets begging marker(s) on player if not enough food for their people."""
        raise NotImplementedError()

    def __animal_breeding(self, players: Players) -> None:
        """Final step of harvest where pastures containing enough animals breed."""
        raise NotImplementedError()
