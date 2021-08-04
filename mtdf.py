from chess.polyglot import zobrist_hash
import evaluator
import t_table
import constants


class MTDfEngine(object):
    def __init__(self, board, depth):
        self._max_depth = depth
        self._max_score = constants.MAX_SCORE
        self._transTable = t_table.TransTable()

    def quiesce(self, alpha, beta, board, entry, final_board):
        """ Apply a Quiescence Search, which aids combat the horizon effect.
        """
        move = None
        stand_pat = evaluator.evaluator(board, entry.result)
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)

        q_moves = (move for move in board.legal_moves if (board.is_check or board.is_capture(move)))
        for move in q_moves:
            if board.is_capture(move):
                board.push(move)
                move, score, entry.finalBoard = -self.quiesce(-beta, -alpha, board, entry, final_board)
                board.pop()

                if score >= beta:
                    return beta
                alpha = max(alpha, score)

        return move, alpha, entry.finalBoard

    def update_t_table(self, entry, new_entry):
        if self._transTable.size == self._transTable.maxSize and new_entry:  # If the entry is new and table is full
            self._transTable.table.popitem()                                 # Remove the last entry
            self._transTable.size = self._transTable.size - 1                # -1 from the table size
        self._transTable.table[entry.z_key] = entry                          # Add new entry to the table
        self._transTable.size = self._transTable.size + 1                    # +1 to the table size

    def _abwm_negamax(self, board, max_depth, depth, alpha, beta):          # NegaMax with Alpha-BetaWithMemory function
        """
        NegaMax with AlphaBetaWithMemory implementation.
        """
        alpha_original = alpha                                               # Set holder for original alpha value
        new_entry = False
        z_hash = zobrist_hash(board)                      # Get Zobrist hash for current chess_board state from Polyglot
        entry = self._transTable.table.get(z_hash)              # Get table entry for current hash key

        if entry and entry.depth >= max_depth - depth:  # If entry exists and...
            if entry.flag == constants.EXACT_SCORE:          # If entry is flagged as an exact score (0):
                return entry.move, entry.score, entry.finalBoard    # Return entry
            elif entry.flag == constants.LOWER_BOUND_SCORE:  # If entry is flagged as an lower bound score (1):
                alpha = max(alpha, entry.score)                     # Get max
            else:                                                   # If entry is flagged as an upper bound score (2):
                beta = min(beta, entry.score)                       # Get min
            if alpha >= beta:                                       # AB test
                return entry.move, entry.score, entry.finalBoard    # Prune or return entry?

        """ Create new entry and initialize values """
        if not entry:                                               # If state is not in the transposition table:
            entry = t_table.TransTableEntry()                       # Create new entry. Set class variables:
            entry.z_key = z_hash                                    # Set Zobrist hash key
            new_entry = True                                        # Set entry state to True
            entry.result = board.result()      # Get python-chess entry result (1-0, 0-1, 1/2-1/2, or * (undetermined))
        entry.depth = max_depth - depth                             # Set entry depth (max depth - current depth)
        entry.move = None                                           # Set entry move to None

        if depth == max_depth or entry.result != "*":  # if max_depth is reached, or if result is determined (not '*'):
            entry.score = evaluator.evaluator(board, entry.result)  # Get utility evaluation of current entry
            entry.finalBoard = board                                # Set final chess_board (to be stored in t. table)
            self.update_t_table(entry, new_entry)                   # Update table with entry
            return '', entry.score, board                           # Return values

        best_score = -(1 << 64)
        best_move = None
        final_board = None                                          # Set values to None
        """ Main negamax loop - Recursively loops through all possible moves """
        for move in board.legal_moves:
            board.push(move)
            _, score, final_board = self._abwm_negamax(board, max_depth, depth + 1, -beta, -alpha)

            # NegaScout implementation
            score_a = score
            if alpha < score < beta:
                _, score_b, final_board = self._abwm_negamax(board, max_depth, depth + 1, -beta, -alpha)
                score = max(score_a, score_b)
            else:
                score = score_a

            score = -score
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        entry.score = best_score
        entry.move = best_move
        entry.finalBoard = final_board

        if best_score <= alpha_original:
            entry.flag = constants.UPPER_BOUND_SCORE
        elif best_score >= beta:
            entry.flag = constants.LOWER_BOUND_SCORE
        else:
            entry.flag = constants.EXACT_SCORE
        self.update_t_table(entry, new_entry)

        return best_move, best_score, final_board

    # MTD(f)
    def _mtd(self, board, max_depth, first_guess):
        """
        MTD(f) function. Converges bounds on true minimax value.
        :param board: board state.
        :param max_depth: maximum search depth.
        :param first_guess: initial search guess.
        """
        move = None
        final_board = None
        guess = first_guess
        upper_bound = self._max_score
        lower_bound = -self._max_score

        while lower_bound < upper_bound:   # Loop until the bounds converge
            if guess == lower_bound:
                beta = guess + 1
            else:
                beta = guess
            move, guess, final_board = self._abwm_negamax(board, max_depth, 0, beta - 1, beta)
            if guess < beta:
                upper_bound = guess
            else:
                lower_bound = guess

        return move, guess, final_board

    def search_controller(self, board):               # Iterative Deepening Implementation
        """
        Iterative deepening framework and controller for the MTD(f) engine.
        :param board: board state.
        :return: chosen move.
        """
        move = None                                   # Initialize chess move, for return
        guess1 = 1 << 64                              # First guess is of high importance
        guess2 = 1 << 64

        for depth in range(2, self._max_depth + 1):
            if depth % 2 == 0:
                move, guess1, final_board1 = self._mtd(board, depth, guess1)
            else:
                move, guess2, final_board2 = self._mtd(board, depth, guess2)

        return move


"""
Ramachandran, A. (2020). JHurricane96/chessai. [ONLINE] GitHub.
Available at: https://github.com/JHurricane96/chessai [Accessed 13 Apr. 2021].
This source provided working examples of several of the desired
functionalities for the MTD(f) algorithm, including Transposition Tables.

Elnaggar, A., Aziem, M., Gadallah, M., and El-Deeb, H., (2014).
A Comparative Study of Game Tree Searching Methods.
International Journal of Advanced Computer Science and Applications, 5(5). [ONLINE]
Available at: https://www.researchgate.net/publication/262672371_A_Comparative_Study_of_Game_Tree_Searching_Methods.
[Accessed 21 Feb. 2021].
This research paper provided excellent resources for all the algorithms used in the software.
The pseudocode provided formed the basis of all four chess algorithms.
"""

