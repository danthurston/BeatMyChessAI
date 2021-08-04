import PySimpleGUI as sg
import sys
import chess
import chess.pgn
import chess.engine
import chess.polyglot                                      # Polyglot is based on NumPy for speed
import logging
import game
import concretegui
import constants


def clear_elements(window):
    """
    Clear GUI fields.
    :param window: app window.
    """
    window['el_total_time']('00m:00s')                      # Reset total timer
    window['el_player_time_left']('')                       # Clear player timer
    window['el_engine_time_left']('')                       # Clear engine timer
    window['el_player_time_counter']('')                    # Clear player counter
    window['el_engine_time_counter']('')                    # Clear engine counter
    window['el_move_history']('')                           # Clear move history
    window['el_game_state'](constants.STATE_PREGAME)        # Reset game-state text
    window['el_player_pieces'](constants.START_PIECES_NUM)  # Reset player start pieces
    window['el_engine_pieces'](constants.START_PIECES_NUM)  # Reset engine start pieces


def check_for_end(window, button, value):
    """
    Checks for exit of the game or application. If the application is closed, all processes are stopped
    and window closed. If a turn resigns, the function returns True to initiate return to pre-game state.
    :param window: application window, used if turn closes whole app
    :param button: button turn clicked. Indicates exit method.
    :param value: read value of window, used to 'check for exit'.
    :return: True if turn resigns. False if no exit requested.
    """
    is_exit_game = False                            # Initialize return var.
    if button == sg.WIN_CLOSED or value == 'Exit':  # If app is closed (X).
        logging.info('Window Closed')               # Log event.
        window.Close()                              # Close app window.
        sys.exit(0)                                 # Stop program.
    if button == 'End Game':                        # If turn resigns from game.
        logging.info('User Resigns')                # Log event.
        is_exit_game = True                         # Set return val to True to initiate return to home state.

    return is_exit_game                             # Return True if turn resigns. False if no exit requested.


def check_ingame_buttons(button):
    """
    Check for in-game button clicks.
    :param button: button clicked.
    """
    if button == 'Algorithm Info.':
        sg.Window('Search Algorithms',
                  [[sg.Text(constants.INFO_STR)],
                   [sg.Ok()]],
                  size=(980, 670), finalize=True, font=('Helvetica', 12),
                  icon=constants.LOGO).read(close=True)
    if button == 'Help & Info':
        sg.Popup(constants.HELP_STR_INGAME, title='Help and Information', font=('Helvetica', 12), icon=constants.LOGO)


def update_move_timer(window, name, counter, elapse_str):
    counter.update_base()
    if name == 'player':
        window['el_player_time_counter'](elapse_str)
    else:
        window['el_engine_time_counter'](elapse_str)


def update_board_colours(x, y, dark, light):
    """
    Determines the required colour.
    :param x: x axis.
    :param y: y axis.
    :param dark: dark square colour.
    :param light: light sq colour.
    :return: colour to update to.
    """
    if (x + y) % 2:      # Check if light or dark square
        colour = dark    # Dark square
    else:
        colour = light   # Light square

    return colour


def change_sq_colour(window, sq):                           # change colour of squares on-click
    row, col = sq[0], sq[1]
    square = window.FindElement(key=(row, col))
    colour = update_board_colours(row, col, constants.CLICKED_DARK_COLOUR, constants.CLICKED_LIGHT_COLOUR)
    square.Update(button_color=('black', colour))


def reset_clicked_sq(move_from, button_square, light, dark):
    if (move_from[0] + move_from[1]) % 2:
        colour = dark
    else:
        colour = light
    button_square.Update(button_color=('black', colour))


def update_board(window, dark, light, game_board):
    """
    Update board with alterations.
    :param window: app window.
    :param dark: dark square colour.
    :param light: light square colour.
    :param game_board: board state.
    """
    for x in range(8):
        for y in range(8):
            colour = update_board_colours(x, y, dark, light)
            img = constants.PIECE_IMAGES[game_board[x][y]]
            element = window.FindElement(key=(x, y))
            element.Update(button_color=('black', colour), image_filename=img)


class Controller:
    def __init__(self, opening_book):
        # Default chess_board colours and theme
        self.depth = 4
        self.is_timer_on = True
        self.is_player_white = True
        self.pregame = True
        self.menu_element, self.board_array = None, None
        # accessibility - add one or two colour options for the BOARD !!!
        self.theme = 'DarkBlue2'               # Application theme and default
        self.light_sq_colour = '#D7CAC1'       # Colour for light squares
        self.dark_sq_colour = '#769656'        # Colour for dark squares - Start as Green
        self.opening_book = opening_book       # Opening Book File
        self.algorithm = 'MTD(f) - Main'

    def set_labels(self, window):
        """
        Set GUI labels for player sides at the beginning of each game.
        :param window: app window.
        """
        if self.is_player_white or self.pregame:  # Check if the turn is white or in pre-game state
            window['el_user_colour']('White')     # Swap GUI 'White' and 'Black' text
            window['el_engine_colour']('Black')
        else:  # Else, if turn is black:
            window['el_user_colour']('Black')
            window['el_engine_colour']('White')  # Swap GUI 'White' and 'Black' text

    def check_menu_buttons(self, button, window):
        """
        Check all menu buttons for input.
        :param button: clicked button.
        :param window: app window.
        :return: window (in case updated)
        """
        if button == 'Close Application':                          # If turn clicks 'Preview Themes'
            logging.info('Window Closed')                          # Log event.
            window.Close()                                         # Close app window.
            sys.exit(0)                                            # Stop program.

        if button == 'Preview Themes':                          # If turn clicks 'Preview Themes'
            sg.theme_previewer(columns=7, scrollable=True)      # Open dialog to display theme previewer

        if button == 'Timer Settings':                          # If turn selects the timer settings menu option:
            buttons, values = sg.Window('Timer Settings',       # Create popup window for timer settings
                                        [[sg.Checkbox('Enable Timer?', default=self.is_timer_on,
                                                      key='timer_enable'), sg.OK(), sg.Cancel()]],
                                        finalize=True, font=('Helvetica', 12), icon=constants.LOGO).read(close=True)

            if buttons == 'OK':                                 # If OK clicked: set timer state:
                self.is_timer_on = True if values['timer_enable'] else False
                value = '05m:00s' if self.is_timer_on else u"\u221E"
                window['el_player_time_left'](value)
                window['el_engine_time_left'](value)

        if button == 'Change Search Depth':
            buttons, values = sg.Window('Select Search Depth',  # Create popup window for depth selection
                                        [[sg.Combo(constants.DEPTH_LIST, size=(10, 15), readonly=True,
                                                   k='depth_select'), sg.OK(), sg.Cancel()]],
                                        finalize=True, font=('Helvetica', 12), icon=constants.LOGO).read(close=True)
            if buttons == 'OK':
                self.depth = values['depth_select']
                window['el_depth'](self.depth)

        if button == 'Select Board Colours':
            buttons, values = sg.Window('Select Board Colour:',  # Create popup window for depth selection
                                        [[sg.Combo(constants.COLOUR_LIST, size=(10, 15), readonly=True,
                                                   k='colour_select'), sg.OK(), sg.Cancel()]],
                                        finalize=True, font=('Helvetica', 12), icon=constants.LOGO).read(close=True)
            if buttons == 'OK':
                new_col = values['colour_select']
                if new_col == 'Green':
                    self.dark_sq_colour = '#769656'
                if new_col == 'Wood':
                    self.dark_sq_colour = '#9D7E68'
                update_board(window, self.dark_sq_colour, self.light_sq_colour, self.board_array)

        if button == 'Select Algorithm':
            buttons, values = sg.Window('Select Algorithm',  # Create popup window for algorithm selection
                                        [[sg.Combo(constants.ALGORITHM_LIST, size=(20, 16), readonly=True,
                                                   k='algorithm_select'), sg.OK(), sg.Cancel()]],
                                        finalize=True, font=('Helvetica', 12), icon=constants.LOGO).read(close=True)
            if buttons == 'OK':
                self.algorithm = values['algorithm_select']
                window['el_algorithm'](self.algorithm)

        if button == 'Default Algorithm':
            self.algorithm = 'MTD(f) - Main'
            window['el_algorithm'](self.algorithm)

        if button == 'Algorithm Information':
            sg.Window('Search Algorithms',
                      [[sg.Text(constants.INFO_STR)],
                       [sg.Ok()]],
                      size=(980, 670), finalize=True, font=('Helvetica', 12),
                      icon=constants.LOGO).read(close=True)

        if button == 'Help & Info':
            sg.Popup(constants.HELP_STR_INIT, title='Help and Information',
                     font=('Helvetica', 12), icon=constants.LOGO)

        if button == 'Default Theme':  # If turn reverts to original theme
            self.theme = 'DarkBlue2'   # Set original theme
            window = self.update_new_window(window)  # Update window with alterations

        if button == 'Select Theme':  # If turn clicks 'Select Theme': Get window
            buttons, values = sg.Window('Select Theme',  # Create window for theme selection
                                        [[sg.Combo(sg.theme_list(), size=(20, 16), readonly=True, k='theme_select'),
                                          sg.OK(), sg.Cancel()]],
                                        finalize=True, font=('Helvetica', 12), icon=constants.LOGO).read(close=True)
            if buttons == 'OK':
                self.theme = values['theme_select']
                window = self.update_new_window(window)

        return window

    def update_new_window(self, old_win):
        """
        Creates a new app window.
        :param old_win: old/current window to be replaced.
        :return: new window.
        """
        old_win.Disable()                                                        # Disable the current (old) window
        dec = concretegui.ConcreteGUI(self.algorithm, self.depth, self.theme, self.is_timer_on, self.dark_sq_colour)
        new_win, self.menu_element, self.board_array = dec.get_gui_layout(self.is_player_white)  # Get initial layout
        old_win.Close()                                                          # Close old window

        return new_win                                                           # Return new window

    def main_loop(self):
        """
        Main pre-game loop for the application. Builds the GUI and sets the initial element values.
        It waits for turn to select a button from the menu and responds accordingly. It also resets
        the game and all elements once the game_loop returns.
        """
        layout = concretegui.ConcreteGUI(self.algorithm, self.depth, self.theme, self.is_timer_on, self.dark_sq_colour)
        window, self.menu_element, self.board_array = layout.get_gui_layout()       # Get Initial GUI layout
        self.set_labels(window)                                         # Set labels for the app window

        while True:                                                     # PRE-GAME - Start main game loop
            button, value = window.Read(timeout=60)
            check_for_end(window, button, value)                        # Check for exit
            window = self.check_menu_buttons(button, window)            # Check for menu button selections not new game

            # Begin Game:
            if button == 'Play as White' or button == 'Play as Black':  # If turn selects a begin-game button:
                self.pregame = False                                    # Set state to in-game
                chess_board = chess.Board(chess960=False)                     # Create chessboard

                if button == 'Play as White':                           # If turn is playing as white
                    self.is_player_white = True                         # Set var to show player colour
                else:                                                   # If turn playing as black
                    self.is_player_white = False                        # Set var to show player colour
                    window = self.update_new_window(window)
                    self.set_labels(window)                             # Swap GUI labels to show colour change
                    update_board(window, self.dark_sq_colour, self.light_sq_colour, self.board_array)

                self.menu_element.Update(constants.IN_GAME_MENU_BAR)    # Change menu to 'In-Game' options
                new_game = game.Game(chess_board, window, self.is_player_white, self.opening_book,
                                     self.algorithm, self.board_array, self.depth, self.is_timer_on,
                                     self.dark_sq_colour, self.light_sq_colour)  # initialize game
                new_game.game_controller()                                       # Begin game loop

                # Reset elements after game
                self.is_player_white, self.pregame = True, True         # Reset colours and game state
                window = self.update_new_window(window)
                self.set_labels(window)                                 # Reset labels to pre-game state
                continue

        window.Close()  # Close window when exiting system


"""
fsmosca (2021). fsmosca/Python-Easy-Chess-GUI. [ONLINE] GitHub.
Available at: https://github.com/fsmosca/Python-Easy-Chess-GUI [Accessed 13 Apr. 2021].
This source provided detailed information for the implementation of a simple chess GUI
utilizing PySimpleGUI that links to python chess for gameplay.
This aligned perfectly with the desired requirements for this software and so formed a good foundation and resource.
"""