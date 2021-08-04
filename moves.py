from itertools import product

"""
Calculates the potential legal moves for any clicked piece.
"""


def is_in_range(x: tuple) -> bool:
    return 0 <= x[0] < 8 and 0 <= x[1] < 8


def moves_pawn(position, board, piece_array, is_white):
    x, y = position
    if is_white:                            # If player is white:
        x_move = (x - 1)                    # Set chess_board movement
        start_row = 6                       # Set start row
    else:                                   # If player is black
        x_move = (x + 1)                    # Set chess_board movement
        start_row = 1                       # Set start row

    move_list = [(x_move, y)]               # Add one square forwards as standard Pawn movement.

    # If pawn has not moved, add additional move forward:
    if x == start_row:
        if is_white:
            if board[x - 2][y] == 0:
                move_list.append((x - 2, y))
        else:
            if board[x + 2][y] == 0:
                move_list.append((x + 2, y))    # Add two squares forwards
    if board[x_move][y] != 0:               # If the square in front of the pawn is occupied:
        move_list = []                      # Clear the list, as the Pawn cannot attack forwards

    # Check for diagonal attack moves:
    if is_in_range((x_move, (y + 1))):      # Check the move is within chess_board bounds
        move = board[x_move][y+1]           # Get move in x,y format.
        if move not in piece_array and move != 0:
            move_list.append((x_move, y + 1))

    if is_in_range((x_move, (y - 1))):
        move = board[x_move][y-1]
        if move not in piece_array and move != 0:
            move_list.append((x_move, y - 1))

    return move_list


def moves_rook(position, board, piece_array):
    origin_x, origin_y = position
    move_list = list()                                            # Create list to store squares
    for (di_x, di_y) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        for i in range(1, 8):
            (x, y) = (origin_x + i * di_x, origin_y + i * di_y)
            if is_in_range((x, y)):                              # Keep search within board
                if board[x][y] == 0:                             # If square is empty:
                    move_list.append((x, y))                     # Add sq to be highlighted
                elif board[x][y] not in piece_array:             # If occupied:
                    move_list.append((x, y))                     # Add sq, then exit:
                    break                                        # Stop search for current direction
                else:
                    break                                        # Stop search for current direction

    return move_list


def moves_knight(position):
    x, y = position
    move_list = list(product([x-1, x+1], [y-2, y+2])) + list(product([x-2, x+2], [y-1, y+1]))
    return move_list


def moves_bishop(position, board, piece_array):
    origin_x, origin_y = position
    move_list = list()                                           # Create list to store squares
    for (di_x, di_y) in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        for i in range(1, 8):
            (x, y) = (origin_x + i * di_x, origin_y + i * di_y)
            if is_in_range((x, y)):                              # Keep search within board
                if board[x][y] == 0:                             # If square is empty:
                    move_list.append((x, y))                     # Add sq to be highlighted
                elif board[x][y] not in piece_array:             # If occupied:
                    move_list.append((x, y))                     # Add sq, then exit:
                    break                                        # Stop search for current direction
                else:
                    break                                        # Stop search for current direction

    return move_list


def moves_queen(position, board, piece_array):
    b_moves = moves_bishop(position, board, piece_array)
    r_moves = moves_rook(position, board, piece_array)
    move_list = b_moves + r_moves
    return move_list


def moves_king(position):
    x, y = position
    move_list = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1),
                 (x - 1, y - 1), (x + 1, y - 1), (x + 1, y + 1), (x - 1, y + 1)]
    return move_list


def moves_controller(piece_array, piece, position, board, is_white):
    """
    Controller for the move generator. It determines which piece has been clicked and calls the corresponding function.
    :param piece_array: array of pieces.
    :param piece: piece clicked.
    :param position: current board position.
    :param board: board state.
    :param is_white: is player white or black team.
    :return: return the list of legal moves for highlighting, if any.
    """
    if piece == piece_array[0]:                                           # Check if clicked piece is PAWN
        move_list = moves_pawn(position, board, piece_array, is_white)    # Get list of possible PAWN moves
    elif piece == piece_array[1]:                                         # Check if clicked piece is ROOK
        move_list = moves_rook(position, board, piece_array)              # Get list of possible ROOK moves
    elif piece == piece_array[2]:                                         # Check if clicked piece is KNIGHT
        move_list = moves_knight(position)                                # Get list of possible KNIGHT moves
    elif piece == piece_array[3]:                                         # Check if clicked piece is BISHOP
        move_list = moves_bishop(position, board, piece_array)            # Get list of possible BISHOP moves
    elif piece == piece_array[4]:                                         # Check if clicked piece is QUEEN
        move_list = moves_queen(position, board, piece_array)             # Get list of possible QUEEN moves
    elif piece == piece_array[5]:                                         # Check if clicked piece is KING
        move_list = moves_king(position)                                  # Get list of possible KING moves
    else:                                                                 # If the piece is on the opposite team:
        return None                                                       # Return None - to exit the move_handler

    move_list = {(x, y) for x, y in move_list if is_in_range((x, y))}     # Remove any out of bounds list items

    return move_list
