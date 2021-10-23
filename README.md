# BeatMyChessAI
Main Computing Project. By Daniel Thurston.

This software provides a platform to compete against four different AI chess algorithms: NegaMax, NegaMax with Alpha-Beta Pruning, NegaScout with Quiescent Search, and MTD(f).
It comes with a GUI with various statistical outputs such as timers and move-history, as well as functionality to highlight potential moves for any selected chess piece.

The software has a goal of teaching AI concepts through the medium of chess by allowing users to adjust the search depth and experiment between algorithms.


## main:
Imports '.bin' opening book file then calls gui.

## gui:
I/O and handling of the gui creation and handling.

## concreteGUI: 
Creates the concrete layout of the application.

## game:
Handles the gameplay of the software, acting as a bridge between the algorithms and the gui.

## book:
Handler for the 'opening_book.bin' file. Called before the engine to check if board state correlates with pre-defined states for opening moves.

## moves:
Move Generator. This is used solely for highlighting moves on-click. It generates lists of legal squares for any clicked piece and returns it to the gui to highlight.

## timer:
Handles the creation and definitions of the timers. three timers are used, one for counting each move duration, total time, and remaining time, respectively.

## NegaMax, NegaMaxAB, and NegaScout:
The code for each respective algorithm.

## MTDf:
MTD(f) algorithm. It has sole use of 't_table.py' and 'evaluator.py'.

## piece_tables:
Define a score for each position on the board, for each piece.

## evaluator:
Utility evaluation function. Scores nodes of the search tree when called. Scores are based on positions (piece_tables) and values of the pieces. (I need to make this evaluation more substantial (eg killer heuristic and history heuristic)).

## t_table:
Transposition Table file. This contains two classes, one for the main table itself, and one for each entry. TTables store moves throughout the game to avoid re-calculating the same states. It is implemented through a Zobrist Hash calculated by the Python Chess library.

### piece_tables:
This was the original set of table definitions used before switching to MTD(f) method. They are much more logical, promote castling, knight centralization etc. piece_tables3 contains much more confusing tables that appear to have no logic. I replaced the init. tables with the ones from this file but have the original tables stored. Understanding how these tables relate is probably key.
