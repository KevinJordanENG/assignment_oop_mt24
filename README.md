# Agricola - Implementation for OOP MT24

This file contains listed and described features of the implementation such as advanced type features, object oriented patterns, and reusable data structures. A short notes section addressing limitations, assumptions, and implementation choices is also included. A list & description of advanced language features were not requested in this document and therefore reported as inline comments throughout the package where present.

## Advanced Type Features

1. Inheritance - Used specifically in the project as listed below.
    - AbstractBaseClass (A.B.C.) of `BaseBoard` providing common gameboard functionality inherited/concrete-ized by `Farmyard` and `ActionSpaces` classes.
    - A.B.C. of `Card` providing functions common to all card types inherited by `MajorImprovement`, `MinorImprovement`, & `Occupation` classes.
2. Composition - While a few select placed merited inheritance, composition was favored for its flexibility and implemented as listed below.
    - `Deck` class is a composition of a various number of all card types (`MajorImprovement`, `MinorImprovement`, & `Occupation`). This allowed batch operations.
    - `Players` is a composition of up to 4 `Player` objects allowing "dot"/written access to each player object.
    - `Player` object composes `Supply`, `Farmyard`, & `Deck`s supporting "Player" scope control of game actions.
    - `Game` object composes `GameState`, `ActionSpaces`, `Tiles`, `Deck`, & `Players` supporting "Game" scope control of actions.
3. Generics - TODO, revisit what counts here...
4. Structural Types - Used in numerous places such as:
    - TypedDicts - used to define lightweight/fixed data packets such as `Good` (with `NotRequired` args), `PerimeterData`, `MoveRequest`, & `SpaceData`.
    - Iterator - used in context manager based object instantiation control.
5. Type Aliases - These were used heavily such as:
    - used to define sets of valid string literals (globally useful ones in `type_defs.py`) via `Literal["a", "b", ..., "z"]`.
    - tuples such as `Coordinate` for [row][col] access.
    - sets (including `Final[]`) such as `START_COORDS` & `FuncNoEval` for specific membership structuring & parsing.
6. Others - Various other machinery used that seems to be type features that were used are listed below.
    - `ContextVar`s - used to maintain game state globally (within `GameState`) via verified setters/getters.
    - `ClassVar`s - used for flyweight pattern for instance cache & context manager based instantiation control.
    - `MappingProxyType` - used to return read only view of objects' data via `@property`s.
    - `__slots__()` - to switch from Dict type to selected pointer store of sub-object references.

## Object Oriented Patterns

1. Facade Pattern - Implemented in the `Game` class, the entry point for this single entry point / API style package. All complexities and submodules/subclasses/data structures are hidden from the user/client yet all functionality are accessible.
2. Flyweight Pattern - Implemented in `Game` & `GameState` classes where based on provided UUID (same for both objects as tightly coupled, one/unique state server per game) new instances are only created if one matching the given UUID is not present in class' instance cache. If new instance is created, it is added to the class' global instance cache.
3. Factory Pattern - Implemented in `Deck`'s `__load_csv()` method which is called uniformly but constructs `Deck`s of different objects based on factory call signature.
4. Global Object Pattern - Implemented by `GameState`, this object is singular, unique, & global providing state based validation, control, & rejection from "one source of truth" across entire `agricola` package.
5. Proxy Pattern - Implemented where `dict` are returned by `@property`s via `MappingProxyType` to enforce read-only access to object data.
6. Command Pattern - Implemented in `Player` as the `decision()` method relying on caching of functions & their args to allow encapsulation of player's "decision request" to be invoked as needed "under the hood" with uniform typed input parameters. Supports automatic cleanup & unlimited decision command chaining as needed with uniform "decision" command.
7. Prototype Pattern - Implemented in `Supply` when creating initial player goods, creates one example `Good` & replicates instances from this initial prototype as needed.
8. State Pattern - Also from the `GameState` object, various methods become available / blocked (raises error) depending on previous chain of `Game` API calls, changing the behavior of all objects throughout the package.

## Reusable Data Structures

1. Decision Caches - Implemented as part of the `decision()` automatic function evaluation & command pattern, these caches of function signature (`str`), function required args (`list[str]`), & pending payment (`tuple[tuple[int,str], ...]`) allowed reusable, uniform structures for all player evaluatable effects.
2. `MoveRequest` - A uniform-ized data packet of all required data fields to execute a move request across all game objects.
3. CSVs - Many game components (action spaces plus major improvement, minor improvement, & occupation cards) have extensive unique data, and their storing, loading, and usage were built in a reusable & highly structured manner.

## Notes

- The main `Game` instance defines methods that control the state of the game enabling the functionality required for each of the games phases. If some direct object methods are tried to be invoked directly before properly advancing the game state they will fail until the proper game state has been reached.
    - An example is the `game.player.two.place_player()` method which will error unless it is player two's turn.
    - All public (and protected) methods of all classes/objects include state based checks.
    - While this adds some less than pretty STATE literals to the beginning of each function, it assures encapsulation is not broken.
- Alongside the `agricola` package is a test script `agricola_test.py`. This script demonstrates most major game functions and represents a sample playing of the game.
- Protected vs Private methods are used in the following way in the project:
    - Protected: These are used between objects that need to access "friend" objects' data or methods (as the 'friend' class idea works in C++) but are not intended to be used by a game player/user. Encapsulation is maintained to the outside user, but the many needed tightly coupled interactions between game components is allowed.
        - It is noted that many game components / subclasses do not expose many public methods if any. This is intentional as Agricola is only intended to allow actions either in "Game" scope (updates affecting everything such as adding goods to all accumulation action spaces) or in "Player" scope (such as actions / decisions to move player to specific action space or choose farmyard space for development). Actions such as modifying board spaces directly, moving a player's goods without being that player, or attempting to get a new hand of 7 cards are illegal moves for a user/player to make and therefore only exposed via unified & legal "Game" or "Player" scope public methods.
    - Private: These methods are truly only to be used within the object where they are implemented.
- As actions and cards contain lots of data/instructions/options, they are cached/loaded in/from CSV files.
    - Default is to use the current working directory of where the `Game` class is instantiated to build appropriate filepaths (portable, os agnostic) using the pkg module tree and a global variable.
        - This assumes that the `Game` class is instantiated in the same directory that contains the `agricola` pkg and its related file tree.
    - The `DATA_DIR_PATH` global variable in `Game` constructor can be used to specify path to CSV files (directory only, without the filenames as they are appended to this path) if needed.
    - A decision was made to evaluate the CSV data as it is read in changing it to be stored in its proper functional type. This however necessitates the use of `Any` as each value in the dict now has a varied type, and the required union type to support proper typing would be unmanageable. Wherever possible standardization of value types was done to ensure functions using these `Any` values from dict DO properly type check.
    - A brittle & potentially dangerous decision was made in that space & card action/functions were saved in str form, cached in the CSV and `eval()`'d upon interaction with the space/card. A big no-no usually but seen to allow dynamic execution of very large number of unique combinations of functions / parameters / flags in centralized way.
- As noted in the "Number of Components" section (pg. 12 of game rules) there is no intended/inherent limit on general goods.
    - Sheep, boar, cattle, wood, clay, reed, stone, grain, vegetable, and food are part of general goods and a global inventory is not maintained (no counters as 'unlimited' supply). Only on a legitimate player request are they created and added to that player's inventory.
    - Inherently limited & player supplies such as people, stables, fences, plus the 'starting player' token are initialized for each player with the maximum defined in pg. 2 of the rule book.
    - Wood-room/field and clay/stone room tiles are also limited as specified but not initialized to any one player.
- Gameboard coordinates are represented in row major [row][col] 2D array format.
- Seeing the cool pattern of using context managers to ensure sub-objects are only instantiated by their proper caller object implemented by Dr. Stefano Gogioso in his 'marketplace' package, the idea and pattern was implemented throughout the project (citing sources here).
- As physical space is not a concern, the 2 food denominations (1 & 5) have not been implemented separately, instead just an int value is used to represent a food token.
- In functions deemed equally likely to be executed by either `game` or `player` the same functions are available to provide UI/UX simplicity.
    - E.g. `game.player.one.place_person_on_action_space(*args)` is the same as `game.place_person_on_action_space(*args, player_id=1)`.
- Age checking for players was omitted as it was considered that playing an API based game implied age of at least 12 years.
- "side_job" and other 2 variant tiles are not used in base game, and therefore omitted.
- 3 yellow "suggestion" tiles are only intended as support for extra young/inexperienced players so were omitted.
- It was difficult to confirm if 2 food per person is consumed at the end of *each* round or exclusively on *harvest* rounds. It seemed most well described in the harvest sections so food consumption was only implemented at the end of harvest rounds.



# TODOs for project tidy up:

DONE---    1. Hide path (make global in game to be manually set)
DONE---    2. Build patterns (flyweight etc) from notes around
DONE---    3. Join all state action in GameState
DONE---    4. Add state checking to all funcs
DONE---    5. Enforce methods are called only by appropriate object
DONE---    6. Make sure all private data can't be mod'ed
DONE---    7. Verify error checking throughout
DONE---    8. Add type checking to decision()
DONE---    9. Document three categories here (type features, patterns, reusable structs)
DONE---    10. Add comments as needed to all funcs
DONE---    11. Change all TODOs into raise NotImplementedError
DONE---    12. Remove `bag` if not used
DONE---    13. Rename rounds_server -> state_server
DONE---    14. Try to refactor away all `Any`s
DONE---    15. Clean CSV data & update with all now present funcs
16. Make test script more verbose/complete
    - Try to add functionality for full player turns / round change
17. Test all decision funcs
18. Surface player methods in `Game`
19. Finish "left off here" funcs