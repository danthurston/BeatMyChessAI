import chess.svg
import chess.polyglot
import chess.pgn
import chess.engine
import piece_tables


class NegamaxEngine:
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

    def negamax(self, depth_left):
        """
        Searches the best move using NegaMax implementation of Minimax.
        :param depth_left: search depth remaining.
        :return: best score found.
        """
        if depth_left == 0:                        # If max depth or terminal node reached:
            return self.evaluation()               # Return current leaf eval.

        best_score = -9999
        for move in self.board.legal_moves:        # For every position:
            self.board.push(move)                  # Get current move
            score = -self.negamax(depth_left - 1)  # Call opponent, switching sign of return value
            self.board.pop()                       # Undo move

            best_score = max(score, best_score)    # Compare returned and existing score values, storing highest

        return best_score

    def search_controller(self):
        """
        Controls the NegaMax search.
        :return: best move found.
        """
        best_move = chess.Move.null()
        best_value = -99999                         # Set as INF (essentially)

        for move in self.board.legal_moves:
            self.board.push(move)
            board_value = -self.negamax(self.depth - 1)

            if board_value > best_value:
                best_value = board_value
                best_move = move

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