import PySimpleGUI as sg
import os
import chess
import chess.pgn
import chess.engine
import chess.polyglot  # Polyglot is based on NumPy for speed
import logging
import gui
import timer
import book
import negamax
import negascout
import negamaxab
import mtdf
import moves
import constants


def get_col(sq):
    """
    Gets the current column of a given square.
    :param sq: current square
    :return: Return column of given square 'sq'
    """
    return chess.square_file(sq)


def get_row(sq):
    """
    Gets the current row of a given square.
    :param sq: current square
    :return: Return row of given square 'sq'
    """
    return 7 - chess.square_rank(sq)


def update_move_counters(counter_player, counter_engine, window, is_player):
    """
    Update counters that time the duration of each move.
    :param is_player: True if players turn else false.
    :param counter_player: Time counter for player move.
    :param counter_engine: Time counter for engine move.
    :param window: Application window.
    """
    if is_player:
        elapse_hum = timer.get_timer(counter_player.elapsed)  # Get elapsed time for player
        window['el_player_time_counter'](elapse_hum)  # Update GUI with new player time
    else:
        elapse_eng = timer.get_timer(counter_engine.elapsed)  # Get elapsed time for engine
        window['el_engine_time_counter'](elapse_eng)  # Update GUI with new engine time


class Game:
    def __init__(self, board, window, is_player_white, open_book, alg, game_board, depth, timer_state, dark_sq,
                 light_sq):
        self.chess_board = board
        self.board_array = game_board
        self.window = window
        self.is_player_white = is_player_white
        self.opening_book = open_book
        self.algorithm = alg
        self.moves_per_side = 0
        self.depth = depth
        self.is_timer_on = timer_state
        self.dark_sq = dark_sq
        self.light_sq = light_sq
        self.node, self.game, self.timer_total = None, None, None
        self.piece_left_player, self.piece_left_engine = 16, 16

    def setup_game(self):
        """
        Setup PGN headers, game and total timer.
        :return:
        """
        self.timer_total = timer.Timer()  # Reset main timer
        self.game = chess.pgn.Game()  # Set/Reset pgn game
        self.node = None  # Set/Reset node to None
        self.moves_per_side = 0
        self.game.headers['White'] = constants.STARTER_PGN['White']
        self.game.headers['Black'] = constants.STARTER_PGN['Black']
        self.game.headers['Event'] = constants.STARTER_PGN['Event']
        if self.is_player_white:  # Check if the turn is white or in pre-game state
            self.game.headers['White'] = 'Player'    # Set PGN headers
            self.game.headers['Black'] = 'Computer'  # Set PGN headers
        else:                                        # Else, if turn is black:
            self.game.headers['White'] = 'Computer'
            self.game.headers['Black'] = 'Player'    # Swap the PGN headers

    def update_game(self, window, move_count, move, elapse_str, origin_sq, new_sq, user):
        """
        update search nodes and GUI after each move.
        """
        if move_count == 1:                                        # Update game nodes:
            self.node = self.game.add_variation(move)
        else:
            self.node = self.node.add_variation(move)
        self.update_gui_elements(window, user, elapse_str)         # Update GUI elements
        gui.change_sq_colour(window, origin_sq)                    # Update original square colour
        gui.change_sq_colour(window, new_sq)                       # Update new sq colour

    def update_total_time(self, window):
        elapse_str = timer.get_timer(self.timer_total.elapsed)      # Get timer
        window['el_total_time'](elapse_str)                        # Update GUI
        self.timer_total.elapsed += 100                             # Elapse timer

    def get_output_string(self, colour, game_moves, move_time):
        """
        Format string for GUI move-history element output. Move type extrapolated from game_moves chess notation.
        :param colour: Which colour turn it is
        :param game_moves: Array of current game move history
        :param move_time: Time taken per move.
        :return: Formatted string for output to GUI
        """
        result = ''
        for game_move in game_moves:                                   # Loop through each move in game_moves list
            move_types = {'#': 'Checkmate!', '+': 'In-Check!',         # Create dict. match keys to move types
                          '-': 'Castling', 'x': 'Capture', '=': 'Promotion'}
            move_type = 'Normal Move'                                  # Set type to Normal Move as default
            for m_type in move_types:                         # Loop through keys in dict to check if in game_move
                if m_type in game_move:                                # If key is present:
                    move_type = move_types[m_type]                     # Set move type

            # Get piece name
            piece_types = {'R': 'Rook', 'N': 'Knight', 'B': 'Bishop',  # Create dict to match keys to piece names
                           'Q': 'Queen', 'K': 'King', 'O': 'King'}     # ("'O': King" represents Castling)
            if game_move[0] in piece_types:                            # Check first char of move for piece key
                piece = piece_types[game_move[0]]                      # If present, set piece
            else:
                piece = 'Pawn'                                         # If no letter present, set as pawn move

            move_str = str(game_move[-2:]) if '+' not in game_move else str(game_move[-3:-1])  # Get move as string
            piece = piece + ':' + (' ' * (7 - len(piece))) + move_str + '  | '
            space_one = ' ' * (6 - len(game_move)) + '| '              # Set spacing by text length
            space_two = ' ' * (12 - len(move_type))
            counter = str(self.moves_per_side)
            num_align = ' 0' if self.moves_per_side < 10 else ' '

            new_move_arr = colour + num_align + counter + ': ' + game_move + space_one + piece + move_type + space_two \
                           + '  | ' + move_time + '   | \n'
            result = ''.join(new_move_arr)

        return result

    def update_gui_elements(self, window, turn, move_time):
        """
        Updates the statistical elements of the GUI.
        :param window: App window
        :param turn: Engine or Player turn
        :param move_time: duration of move
        """
        variation_str = str(self.game.variations[0])  # Get game moves as string
        game_moves = variation_str.split()            # Split the string into components

        if turn == 'player' and self.is_player_white:
            colour = 'White'
            self.moves_per_side += 1                  # As white starts, +1 to counter if white move
        elif turn == 'engine' and not self.is_player_white:
            colour = 'White'
            self.moves_per_side += 1
        else:
            colour = 'Black'

        # Update 'Move History' Element
        result = self.get_output_string(colour, game_moves, move_time)
        window['el_move_history'](result, append=True)

        # Update 'Remaining Pieces' Elements
        if 'x' in game_moves[-1]:
            if turn == 'player':
                self.piece_left_player -= 1
            elif turn == 'engine':
                self.piece_left_engine -= 1
        window['el_player_pieces'](self.piece_left_player)
        window['el_engine_pieces'](self.piece_left_engine)

    def highlight_possible_moves(self, window, current_piece, move_from):
        """
        Gets all possible moves, including capturing, for any piece clicked on the chess_board by calling move-generator
        :param window: Application window
        :param current_piece: Current location in format used to check which piece is at location.
        :param move_from: Current location in x/y format.
        :return: return without effect if no piece is on selected square.
        """
        if self.is_player_white:  # If turn is playing as white:
            piece_array = [constants.PAWN_W, constants.ROOK_W, constants.KNIGHT_W,
                           constants.BISHOP_W, constants.QUEEN_W, constants.KING_W]
        else:                     # If turn is playing as black:
            piece_array = [constants.PAWN_B, constants.ROOK_B, constants.KNIGHT_B,
                           constants.BISHOP_B, constants.QUEEN_B, constants.KING_B]

        if current_piece != constants.BLANK:  # If clicked square is not empty
            move_list = moves.moves_controller(piece_array, current_piece, move_from,
                                               self.board_array, self.is_player_white)  # Get moves list
        else:                                                               # If piece on opposite team
            return

        if move_list is None:                                               # If the list is empty:
            return

        for sq in move_list:                                                # Loop each square in move_list
            new_elem = window.FindElement(key=sq)                           # Get current square element
            curr_sq = self.board_array[sq[0]][sq[1]]                         # Get current square in x/y
            if curr_sq not in piece_array:                                  # Check array for own pieces
                colour = gui.update_board_colours(sq[0], sq[1], constants.HIGHLIGHT_DARK,
                                                  constants.HIGHLIGHT_LIGHT)  # Get colour
                new_elem.Update(button_color=('black', colour))             # Update colour of button

    def move_castling(self, window, current_move, turn):
        """
        Implements front-end Castling.
        :param window: app window.
        :param current_move: move made.
        :param turn: Engine or Player turn.
        """
        is_white = True if self.is_player_white and turn == 'player' else False
        if current_move == 'e1g1' or current_move == 'e1h1':                                # Player King-side
            self.board_array[7][7] = constants.BLANK                                         # Clear Rook
            self.board_array[7][4] = constants.BLANK                                         # Clear King
            self.board_array[7][5] = constants.ROOK_W if is_white else constants.ROOK_B      # Set Rook
            self.board_array[7][6] = constants.KING_W if is_white else constants.KING_B      # Set King
        elif current_move == 'e1a1' or current_move == 'e1c1':                              # Player Queen-side
            self.board_array[7][0] = constants.BLANK                                         # Clear Rook
            self.board_array[7][4] = constants.BLANK                                         # Clear King
            self.board_array[7][3] = constants.ROOK_W if is_white else constants.ROOK_B      # Set Rook
            self.board_array[7][2] = constants.KING_W if is_white else constants.KING_B      # Set King
        elif current_move == 'e8g8' or current_move == 'e8h8':                              # Engine King-side
            self.board_array[0][7] = constants.BLANK                                         # Clear Rook
            self.board_array[0][4] = constants.BLANK                                         # Clear King
            self.board_array[0][5] = constants.ROOK_B if is_white else constants.ROOK_B      # Set Rook
            self.board_array[0][6] = constants.KING_W if is_white else constants.KING_B      # Set King
        elif current_move == 'e8a8' or current_move == 'e8c8':                              # Engine Queen-side
            self.board_array[0][0] = constants.BLANK                                         # Clear Rook
            self.board_array[0][4] = constants.BLANK                                         # Clear King
            self.board_array[0][3] = constants.ROOK_W if is_white else constants.ROOK_B      # Set Rook
            self.board_array[0][2] = constants.KING_W if is_white else constants.KING_B      # Set King
        gui.update_board(window, self.dark_sq, self.light_sq, self.board_array)              # Draw Changes

    def move_handler(self, window, board, player, move, original_sq, new_sq, current_piece):
        """
        Handles the move for each competitor and acts accordingly.
        """
        if board.is_castling(move):                                              # Check if move is Castling
            move_str = str(move)
            self.move_castling(window, move_str, player)                         # Call function to implement Castling
        else:                                                                    # Else if normal move:
            self.board_array[original_sq[0]][original_sq[1]] = constants.BLANK   # Clear original square [row,col]
            self.board_array[new_sq[0]][new_sq[1]] = current_piece               # Update new square [row, col]

        gui.update_board(window, self.dark_sq, self.light_sq, self.board_array)
        board.push(move)

    def player_move(self, window, board, move_count, timer_player, timer_engine):
        """
        Handles the player game movement.
        :param window: app window.
        :param board: chess board.
        :param move_count: current move number.
        :param timer_player: player timer.
        :param timer_engine: engine timer.
        :return: turn, move_count, check for exit
        """
        window['el_game_state'](constants.STATE_PLAYER_MOVE)               # Update GUI 'game-state' text
        original_sq, new_sq = None, None
        is_exit_game, has_user_moved, is_human_turn = False, False, True

        while is_human_turn:                                                # Loop until turn has moved
            button, value = window.Read(timeout=100)                        # Read any window input
            update_move_counters(timer_player, timer_engine, window, True)  # Update move timers
            self.update_total_time(window)                                  # Update total timer
            timer_player.elapsed += 100
            is_exit_game = gui.check_for_end(window, button, value)         # Check if turn ends game / 'X'
            gui.check_ingame_buttons(button)
            if is_exit_game:                                                # Game ended, return to pre-game state
                break

            if type(button) is tuple:                                                 # If chess_board button is clicked
                if not has_user_moved:
                    original_sq = button                                              # Get the clicked button
                    current_piece = self.board_array[original_sq[0]][original_sq[1]]  # Get original board square num
                    gui.change_sq_colour(window, original_sq)                         # Change original square colour
                    self.highlight_possible_moves(window, current_piece, original_sq)  # Highlight moves
                    has_user_moved = True

                elif has_user_moved:
                    origin_row, origin_col = original_sq  # Get original-sq row and col
                    new_sq = button
                    new_row, new_col = new_sq
                    button_element = window.FindElement(key=(origin_row, origin_col))

                    if new_sq == original_sq:  # If button is double-clicked:
                        gui.reset_clicked_sq(original_sq, button_element, self.light_sq, self.dark_sq)
                        gui.update_board(window, self.dark_sq, self.light_sq, self.board_array)
                        has_user_moved = False  # Undo 'turn move' status
                        continue

                    origin_row, origin_col = original_sq                      # Get location of turn move
                    origin_square = chess.square(origin_col, 7 - origin_row)  # Make python-chess format move
                    new_square = chess.square(new_col, 7 - new_row)
                    player_move = chess.Move(origin_square, new_square)

                    if player_move in board.legal_moves:                      # Check if turn move is legal
                        self.move_handler(window, board, 'player', player_move, original_sq, new_sq, current_piece)

                        # Update Timers
                        elapse_str = timer.get_timer(timer_player.elapsed)
                        gui.update_move_timer(window, 'player', timer_player, elapse_str)  # Reset move counter
                        if self.is_timer_on:
                            elapsed_time = timer.get_timer(timer_player.base)  # Get timer
                            window['el_player_time_left'](elapsed_time)        # Update timer with elapsed time

                        # Update Game
                        move_count += 1
                        self.update_game(window, move_count, player_move, elapse_str, original_sq, new_sq, 'player')
                        is_human_turn = False                                   # End human turn

                    else:                                                       # If move is illegal:
                        has_user_moved = False                                  # Undo 'move completed' variable
                        gui.reset_clicked_sq(original_sq, button_element, self.light_sq, self.dark_sq)
                        gui.update_board(window, self.dark_sq, self.light_sq, self.board_array)
                        continue

        return is_human_turn, move_count, is_exit_game

    def engine_move(self, window, board, move_count, timer_player, timer_engine):
        """
        Handles the engine game movement.
        :param window: app window.
        :param board: chess board.
        :param move_count: current move number.
        :param timer_player: player timer.
        :param timer_engine: engine timer.
        :return: turn, move_count, check for exit
        """
        window['el_game_state'](constants.STATE_ENGINE_MOVE)                     # Update GUI game-state text
        is_exit_game = False
        engine_move = None

        # Engine turn. Get initial moves from Opening Book to initiate different strategies.
        if move_count <= 7:
            if os.path.isfile(self.opening_book):                                   # If the path to the book exists
                opening_book = book.BookController(self.opening_book, board)        # Initiate opening book
                engine_move = opening_book.get_book_move()                          # Get the optimal move from the book
            else:                                                                   # If the book doesn't exist
                logging.warning('GUI book is missing.')                             # Log missing book as warning

        if engine_move is None:                                                     # Run engine if book has no move
            if self.algorithm == 'NegaMax':
                engine_search = negamax.NegamaxEngine(board, self.depth)            # Get engine object
            elif self.algorithm == 'NegaMax & Alpha-Beta':
                engine_search = negamaxab.NegamaxAbEngine(board, self.depth)
            elif self.algorithm == 'NegaScout & Quiesce':
                engine_search = negascout.NegaScoutEngine(board, self.depth)
            else:                                                                   # Else use MTD(f)
                engine_search = mtdf.MTDfEngine(board, self.depth)

            while engine_move is None and not is_exit_game:                              # Loop until engine finds move
                button, value = window.Read(timeout=100)
                update_move_counters(timer_player, timer_engine, window, False)          # Update move timers
                self.update_total_time(window)                                           # Update total timer
                timer_engine.elapsed += 100                                               # Elapse timer
                is_exit_game = gui.check_for_end(window, button, value)           # Check for app or game exit

                if self.algorithm != 'MTD(f) - Main':
                    engine_move = engine_search.search_controller()                      # Get move from engine
                else:
                    engine_move = engine_search.search_controller(board)                 # Get move from MTF(f) engine

        if engine_move is None:                                                          # If no legal move (Null-Move):
            return                                                                       # Return to human turn

        # Update chess_board with engine move
        move_string = str(engine_move)                             # Get engine move as a string
        origin_col = ord(move_string[0]) - ord('a')                # Get column of original square
        origin_row = 8 - int(move_string[1])                       # Get row of original square
        new_col = ord(move_string[2]) - ord('a')                   # Get column of new square
        new_row = 8 - int(move_string[3])                          # Get row of new square

        new_sq = new_row, new_col
        original_sq = origin_row, origin_col                                        # Get location as x/y format
        current_piece = self.board_array[origin_row][origin_col]                    # Get location

        self.move_handler(window, board, 'engine', engine_move, original_sq, new_sq, current_piece)

        elapse_str = timer.get_timer(timer_player.elapsed)
        gui.update_move_timer(window, 'engine', timer_engine, elapse_str)           # Reset engine move counter
        if self.is_timer_on:
            elapsed_time = timer.get_timer(timer_engine.base)                       # Get timer
            window['el_engine_time_left'](elapsed_time)                             # Update timer with elapsed time

        move_count += 1
        self.update_game(window, move_count, engine_move, elapse_str, original_sq, new_sq, 'engine')

        return True, move_count, is_exit_game

    def game_controller(self):  # Begin chess game
        """
        Controls the game flow through iterating each move.
        :return: return if exit.
        """
        is_exit_game = False
        move_count = 0
        timer_player = timer.Timer()
        timer_engine = timer.Timer()
        is_human_turn = True if self.is_player_white else False
        self.setup_game()

        # Game loop
        while not self.chess_board.is_game_over(claim_draw=True) and not is_exit_game:
            if is_human_turn:        # If player turn: Get PLAYER move
                is_human_turn, move_count, is_exit_game = self.player_move(self.window, self.chess_board, move_count,
                                                                           timer_player, timer_engine)
            elif not is_human_turn:  # If engine turn: Get ENGINE move
                is_human_turn, move_count, is_exit_game = self.engine_move(self.window, self.chess_board, move_count,
                                                                           timer_player, timer_engine)

        # Final Scoreboard
        if self.chess_board.is_game_over(claim_draw=True):
            if self.is_player_white:
                if str(self.chess_board.result()) == '0-1':
                    result = 'Engine Wins!'
                elif str(self.chess_board.result()) == '1-0':
                    result = 'You Won! Congrats!'
                else:
                    result = 'Draw!'
            else:
                if str(self.chess_board.result()) == '0-1':
                    result = 'You Won! Congrats'
                elif str(self.chess_board.result()) == '1-0':
                    result = 'Engine Wins!'
                else:
                    result = 'Draw!'

            result_str = 'Game Over! Result: ' + result
            sg.Popup(result_str, font='helvetica', title=constants.WINDOW_TITLE)
        gui.clear_elements(self.window)

        return


"""
fsmosca (2021). fsmosca/Python-Easy-Chess-GUI. [ONLINE] GitHub.
Available at: https://github.com/fsmosca/Python-Easy-Chess-GUI [Accessed 13 Apr. 2021].
This source provided detailed information for the implementation of a simple chess GUI
utilizing PySimpleGUI that links to python chess for gameplay.
This aligned perfectly with the desired requirements for this software and so formed a good foundation and resource.
"""