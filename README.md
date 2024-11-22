# Agricola - Implementation for OOP MT24

This file contains listed and described features of the implementation such as advanced type features, object oriented patterns, and reusable data structures. A short notes section addressing limitations, assumptions, and implementation choices is also included.

## Advanced Type Features

{list only}

## Object Oriented Patterns

{list, explain where, justify}

1. Facade Pattern - Implemented in the 'Game' class, the entry point for this single entry point / API style package. All complexities and submodules/subclasses/data structures are hidden from the user/client yet all functionality are accessible.

## Reusable Data Structures

{list, explain where, justify}

## Notes

- Age checking for players was omitted as it was considered that playing an API based game implied age of at least 12 years.
- "side_job" and other 2 variant tiles are not used in base game, and therefore omitted.
- 3 yellow "suggestion" tiles are only intended as support for extra young/inexperienced players so were omitted.
- As physical space is not a concern, the 2 food denominations (1 & 5) have not been implemented separately, instead just an int value is used to represent a food token.
- As noted in the "Number of Components" section (pg. 12 of game rules) there is no intended/inherent limit on general goods.
    - Sheep, boar, cattle, wood, clay, reed, stone, grain, vegetable, and food are part of general goods and a global inventory is not maintained (no counters as 'unlimited' supply). Only on a legitimate player request are they created and added to that player's inventory.
    - Inherently limited & player supplies such as people, stables, fences, plus the 'starting player' token are initialized for each player with the maximum defined in pg. 2 of the rule book.
    - Wood-room/field and clay/stone room tiles are also limited as specified but not initialized to any one player.
- Gameboard coordinates are represented in row major [row][col] 2D array format.
- As actions and cards contain lots of data/instructions/options, they are cached/loaded in/from CSV files.
    - Default is to use the current working directory of where the `Game` class is instantiated to build appropriate filepaths (portable, os agnostic) using the pkg module tree.
        - This assumes that the `Game` class is instantiated in the same directory that contains the `agricola` pkg and its related file tree.
    - Optional `data_dir_path` argument in `Game` constructor can be used to specify path to CSV files (directory only, without the filenames as they are appended to this path) if needed.
- It was difficult to confirm if 2 food per person is consumed at the end of *each* round or exclusively on *harvest* rounds. It seemed most well described in the harvest sections so food consumption was only implemented at the end of harvest rounds.
- The main `Game` instance defines methods that control the state of the game enabling the functionality required for each of the games phases. If some direct object methods are tried to be invoked directly before properly advancing the game state they will fail until the proper game state has been reached.
    - An example is the `game.player.two.place_player()` method which will error unless it is the proper player's turn specifically within the 'round work' phase.
- In functions deemed equally likely to be executed by either `game` or `player` the same functions are available to provide UI/UX simplicity.
    - E.g. `game.player.one.move_item(move_request)` is the same as `game.move_item(move_request, player_id=1)`
- The fundamental logic/valid move checking is implemented in the board ABC '_move...' functions.
    - These functions are longer than normal as the if/else/error tree of validating move paths, object type, and space type are extensive.