import chess
import chess.svg
import chess.polyglot
import chess.pgn
import chess.engine
import piece_tables


class NegaScoutEngine:
    def __init__(self, board, depth):
        self.board = board
        self.depth = depth

    def evaluation(self):
        """
        evaluate current position.
        :return: node score.
        """
        if self.board.is_checkmate():
            if self.board.turn:
                return -9999
            else:
                return 9999
        if self.board.is_stalemate():
            return 0
        if self.board.is_insufficient_material():
            return 0

        # Quantity of remaining pieces:
        wp = len(self.board.pieces(chess.PAWN, chess.WHITE))
        bp = len(self.board.pieces(chess.PAWN, chess.BLACK))
        wn = len(self.board.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(self.board.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(self.board.pieces(chess.BISHOP, chess.WHITE))
        bb = len(self.board.pieces(chess.BISHOP, chess.BLACK))
        wr = len(self.board.pieces(chess.ROOK, chess.WHITE))
        br = len(self.board.pieces(chess.ROOK, chess.BLACK))
        wq = len(self.board.pieces(chess.QUEEN, chess.WHITE))
        bq = len(self.board.pieces(chess.QUEEN, chess.BLACK))
        # Piece val was: 100, 320, 330, 500, 900

        material = 100 * (wp - bp) + 300 * (wn - bn) + 330 * (wb - bb) + 550 * (wr - br) + 1000 * (wq - bq)

        pawn_sq = sum([piece_tables.TABLE_PAWN_MAIN[i] for i in self.board.pieces(chess.PAWN, chess.WHITE)])
        pawn_sq += sum([-piece_tables.TABLE_PAWN_MAIN[chess.square_mirror(i)]
                        for i in self.board.pieces(chess.PAWN, chess.BLACK)])
        knight_sq = sum([piece_tables.TABLE_KNIGHT_MAIN[i] for i in self.board.pieces(chess.KNIGHT, chess.WHITE)])
        knight_sq += sum([-piece_tables.TABLE_KNIGHT_MAIN[chess.square_mirror(i)]
                         for i in self.board.pieces(chess.KNIGHT, chess.BLACK)])
        bishop_sq = sum([piece_tables.TABLE_BISHOP_MAIN[i] for i in self.board.pieces(chess.BISHOP, chess.WHITE)])
        bishop_sq += sum([-piece_tables.TABLE_BISHOP_MAIN[chess.square_mirror(i)]
                         for i in self.board.pieces(chess.BISHOP, chess.BLACK)])
        rook_sq = sum([piece_tables.TABLE_ROOK_MAIN[i] for i in self.board.pieces(chess.ROOK, chess.WHITE)])
        rook_sq += sum([-piece_tables.TABLE_ROOK_MAIN[chess.square_mirror(i)]
                        for i in self.board.pieces(chess.ROOK, chess.BLACK)])
        queen_sq = sum([piece_tables.TABLE_QUEEN_MAIN[i] for i in self.board.pieces(chess.QUEEN, chess.WHITE)])
        queen_sq += sum([-piece_tables.TABLE_QUEEN_MAIN[chess.square_mirror(i)]
                        for i in self.board.pieces(chess.QUEEN, chess.BLACK)])
        king_sq = sum([piece_tables.TABLE_KING_MAIN[i] for i in self.board.pieces(chess.KING, chess.WHITE)])
        king_sq += sum([-piece_tables.TABLE_KING_MAIN[chess.square_mirror(i)]
                       for i in self.board.pieces(chess.KING, chess.BLACK)])

        evaluation = material + pawn_sq + knight_sq + bishop_sq + rook_sq + queen_sq + king_sq

        return evaluation if self.board.turn else -evaluation

    def quiesce(self, alpha, beta):
        """ Apply a Quiescence Search to aid combat the horizon effect """
        standing_pat = self.evaluation()
        if standing_pat >= beta:                                      # If current eval >= beta(max score)
            return beta
        alpha = max(alpha, standing_pat)                              # Set lower bound

        for move in self.board.legal_moves:                           # For each possible move:
            if self.board.is_check() or self.board.is_capture(move):
                self.board.push(move)                                 # Get Move
                score = -self.quiesce(-beta, -alpha)
                self.board.pop()                                      # Undo Move

                if score >= beta:
                    return beta                                       # Return new score
                alpha = max(alpha, score)                             # Adjust search window

        return alpha

    # Searching the best move using NegaScout Search.
    def negascout(self, alpha, beta, depth_left):
        """
        Searches the best move using NegaScout, incorporating Alpha-Beta Pruning and NegaMax but adding additional
        NegaScout search and calling the Quiesce search.
        :param alpha: current Alpha score.
        :param beta: current Beta score.
        :param depth_left: search depth remaining.
        :return: best score found.
        """
        best_score = -9999
        b = beta

        if depth_left == 0:                                      # If max depth reached:
            return self.quiesce(alpha, beta)                     # Complete Quiesce Search

        for move in self.board.legal_moves:                      # Loop over all possible moves
            self.board.push(move)                                # Get current move
            score = -self.negascout(-b, -alpha, depth_left - 1)  # Iterate

            # NegaScout Search:
            if score > best_score:
                if alpha < score < beta:                         # NegaScout condition
                    best_score = max(score, best_score)
                else:
                    best_score = -self.negascout(-beta, -score, depth_left - 1)

            self.board.pop()                                     # Undo move
            alpha = max(score, alpha)                            # Adjust search window
            if alpha >= beta:                                    # Alpha Beta Pruning condition
                return alpha                                     # Prune branch

            b = alpha + 1

        return best_score

    def search_controller(self):
        """
        Controls the NegaScout and Quiesce search.
        :return: best move found.
        """
        best_move = chess.Move.null()
        best_value = -99999  # Set as INF (essentially)
        alpha = -100000      # Set as INF (essentially)
        beta = 100000        # Set as INF (essentially)

        for move in self.board.legal_moves:
            self.board.push(move)
            board_value = -self.negascout(-beta, -alpha, self.depth - 1)

            if board_value > best_value:
                best_value = board_value
                best_move = move
            alpha = max(board_value, alpha)

            self.board.pop()

        return best_move


"""
Gaikwad, A. (2020). Let’s create a Chess AI. [ONLINE] Medium.
Available at: https://medium.com/dscvitpune/lets-create-a-chess-ai-8542a12afef. [Accessed 25 May. 2021].
This source provided the basis for the evaluation functions.
This was an area where only a basic evaluator was required that could function across multiple algorithms,
with this being an ideal example to use as a foundation.

Elnaggar, A., Aziem, M., Gadallah, M., and El-Deeb, H., (2014).
A Comparative Study of Game Tree Searching Methods.
International Journal of Advanced Computer Science and Applications, 5(5). [ONLINE]
Available at: https://www.researchgate.net/publication/262672371_A_Comparative_Study_of_Game_Tree_Searching_Methods.
[Accessed 21 Feb. 2021].
This research paper provided excellent resources for all the algorithms used in the software.
The pseudocode provided formed the basis of all four chess algorithms.
"""