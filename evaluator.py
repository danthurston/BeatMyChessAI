import piece_tables
import constants
import chess


def evaluator(board, result):
    """
    Evaluate movement.
    :param board: board state.
    :param result: transposition table result.
    :return:
    """
    if not result == "*":                 # If entry exists and is determined:
        if result[0] == "1":              # If entry begins with 1 (player win or draw (1/2-1/2)):
            evaluation = 0 if result[1] == "/" else constants.MAX_SCORE  # If result is '1/2-1/2', eval. = 0, else MAX
        else:                             # If result doesn't begin with 1 (opponent win)
            evaluation = -constants.MAX_SCORE  # Set evaluation as negative of max_score -(100*100)
        if not board.turn:                # If not turn turn:
            evaluation = -evaluation      # Reverse evaluation
        return evaluation

    # Quantity of remaining pieces:
    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    material = 100 * (wp - bp) + 300 * (wn - bn) + 330 * (wb - bb) + 550 * (wr - br) + 1000 * (wq - bq)

    pawn_sq = sum([piece_tables.TABLE_PAWN_MAIN[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    pawn_sq += sum([-piece_tables.TABLE_PAWN_MAIN[chess.square_mirror(i)]
                    for i in board.pieces(chess.PAWN, chess.BLACK)])
    knight_sq = sum([piece_tables.TABLE_KNIGHT_MAIN[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    knight_sq += sum([-piece_tables.TABLE_KNIGHT_MAIN[chess.square_mirror(i)]
                      for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    bishop_sq = sum([piece_tables.TABLE_BISHOP_MAIN[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
    bishop_sq += sum([-piece_tables.TABLE_BISHOP_MAIN[chess.square_mirror(i)]
                      for i in board.pieces(chess.BISHOP, chess.BLACK)])
    rook_sq = sum([piece_tables.TABLE_ROOK_MAIN[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
    rook_sq += sum([-piece_tables.TABLE_ROOK_MAIN[chess.square_mirror(i)]
                    for i in board.pieces(chess.ROOK, chess.BLACK)])
    queen_sq = sum([piece_tables.TABLE_QUEEN_MAIN[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
    queen_sq += sum([-piece_tables.TABLE_QUEEN_MAIN[chess.square_mirror(i)]
                     for i in board.pieces(chess.QUEEN, chess.BLACK)])
    king_sq = sum([piece_tables.TABLE_KING_MAIN[i] for i in board.pieces(chess.KING, chess.WHITE)])
    king_sq += sum([-piece_tables.TABLE_KING_MAIN[chess.square_mirror(i)]
                    for i in board.pieces(chess.KING, chess.BLACK)])

    evaluation = material + pawn_sq + knight_sq + bishop_sq + rook_sq + queen_sq + king_sq

    return evaluation if board.turn else -evaluation


"""
Gaikwad, A. (2020). Let’s create a Chess AI. [ONLINE] Medium.
Available at: https://medium.com/dscvitpune/lets-create-a-chess-ai-8542a12afef. [Accessed 25 May. 2021].
This source provided the basis for the evaluation functions.
This was an area where only a basic evaluator was required that could function across multiple algorithms,
with this being an ideal example to use as a foundation.
"""
