import PySimpleGUI as sg
import copy
import gui
import constants


def build_square(img, key, location, dark_sq_col):  # Returns Read-Button and image
    colour = gui.update_board_colours(location[0], location[1], dark_sq_col, '#D7CAC1')
    new_button = sg.RButton('', image_filename=img, button_color=('black', colour), size=(100, 1), border_width=0,
                            pad=(0, 0), key=key)
    return new_button


class ConcreteGUI:
    def __init__(self, alg, depth, theme, timer_on, sq_colour):
        self.algorithm = alg
        self.depth = depth
        self.theme = theme
        self.is_timer_on = timer_on
        self.game_board = None
        self.sq_colour = sq_colour

    def build_board(self, is_player_white):
        """
        Create the initial chess_board using the INIT_BOARD layout and adding images to each square of the chess_board.
        :return: board_layout: GUI chessboard as an array of read-buttons with piece images added.
        """
        self.game_board = copy.deepcopy(constants.INIT_BOARD)      # Copy layout from instance var
        board_layout = []                                   # Board layout array, for return

        if is_player_white:
            start, end, step = 0, 8, 1                      # Save chess_board with white at bottom
        else:
            start, end, step = 7, -1, -1                    # Save chess_board with black at bottom

        for x in range(start, end, step):                   # Loop through chess_board cols
            row = []                                        # Reset row array after each row
            for y in range(start, end, step):               # Loop through chess_board rows
                img = constants.PIECE_IMAGES[self.game_board[x][y]]   # Get img for chess_board location
                row.append(build_square(img, key=(x, y), location=(x, y), dark_sq_col=self.sq_colour))  # Build sq
            board_layout.append(row)                        # Add row to chess_board array

        return board_layout                                 # Return completed chess_board

    # Implement decorator Pattern?
    def get_gui_layout(self, is_player_white=True):
        sg.SetOptions(margins=(10, 12), border_width=1)
        menu_element = sg.Menu(constants.PREGAME_MENU_BAR, tearoff=False, background_color='White', text_color='black')
        board_layout = self.build_board(is_player_white)
        sg.theme(self.theme)
        timer_val = '05m:00s' if self.is_timer_on else u"\u221E"  # Set value dependent on timer settings

        # Column 1 - Y Axis
        gui_y_axis = [
            [sg.Text('8', font=('Courier', 12), size=(1, 1), pad=((0, 0), (0, 19)))],
            [sg.Text('7', font=('Courier', 12), size=(1, 1), pad=(0, 19))],
            [sg.Text('6', font=('Courier', 12), size=(1, 1), pad=(0, 19))],
            [sg.Text('5', font=('Courier', 12), size=(1, 1), pad=(0, 19))],
            [sg.Text('4', font=('Courier', 12), size=(1, 1), pad=(0, 19))],
            [sg.Text('3', font=('Courier', 12), size=(1, 1), pad=(0, 19))],
            [sg.Text('2', font=('Courier', 12), size=(1, 1), pad=(0, 19))],
            [sg.Text('1', font=('Courier', 12), size=(1, 1), pad=((0, 0), (19, 15)))]]

        # Column 2 - Chessboard and X axis
        board_and_axis = [[sg.Column(board_layout)],
                          [sg.Text('  A     B     C     D     E     F     G     H',
                                   font=('Courier', 12), size=(45, 1), pad=((6, 0), (2, 0)))]]

        # Column 3 - GUI elements, including statistics, move history and game state
        window_elements = [
            # ROW 1 - Headings
            [sg.Text(constants.STATE_PREGAME, k='el_game_state', size=(23, 1), font=('Courier', 14)),
             sg.Text('Time Left ', size=(11, 1), font=('Courier', 14)),
             sg.Text('Move Time ', size=(11, 1), font=('Courier', 14)),
             sg.Text('Pieces ', size=(7, 1), font=('Courier', 14))],
            # ROW 2 - User identifiers and elements for ROW 1 headings
            [sg.Text('Player', font=('Courier', 12), size=(9, 1)),
             sg.Text('White', k='el_user_colour', font=('Courier', 12), size=(12, 1), relief='sunken',
                     pad=((0, 45), (1, 7))),
             sg.Text(timer_val, k='el_player_time_left', font=('Courier', 12), size=(10, 1), pad=((0, 0), (1, 7)),
                     relief='sunken'),
             sg.Text('00m:00s', k='el_player_time_counter', font=('Courier', 12), size=(10, 1), pad=((30, 0), (1, 7)),
                     relief='sunken'),
             sg.Text('16', k='el_player_pieces', font=('Courier', 14), size=(5, 1), pad=((35, 0), (1, 7)),
                     relief='sunken')],
            # ROW 3 - Engine identifiers and elements for ROW 1 headings
            [sg.Text('Engine', font=('Courier', 12), size=(9, 1)),
             sg.Text('Black', k='el_engine_colour', size=(12, 1), font=('Courier', 12), relief='sunken',
                     pad=((0, 45), (1, 7))),
             sg.Text(timer_val, k='el_engine_time_left', font=('Courier', 12), size=(10, 1), pad=((0, 0), (1, 7)),
                     relief='sunken'),
             sg.Text('00m:00s', k='el_engine_time_counter', font=('Courier', 12), size=(10, 1), pad=((30, 0), (1, 7)),
                     relief='sunken'),
             sg.Text('16', k='el_engine_pieces', font=('Courier', 14), size=(5, 1), pad=((35, 0), (1, 7)),
                     relief='sunken')],
            # ROW 4 - Headings
            [sg.HorizontalSeparator()],
            [sg.Text('Algorithm:', pad=((7, 174), (5, 0)), font=('Courier', 14), size=(11, 1)),
             sg.VerticalSeparator(),
             sg.Text('Search Depth:', pad=((10, 0), (5, 0)), font=('Courier', 14), size=(14, 1)),
             sg.VerticalSeparator(),
             sg.Text('Total Time:', pad=((7, 8), (5, 0)), font=('Courier', 14), size=(11, 1))],
            # ROW 5 - Elements for ROW 5 headings
            [sg.Text(self.algorithm, k='el_algorithm', pad=((7, 15), (0, 7)), font=('Courier', 18), size=(20, 1),
                     relief='sunken'),
             sg.VerticalSeparator(),
             sg.Text(self.depth, k='el_depth', pad=((10, 100), (0, 7)), font=('Courier', 18), size=(4, 1),
                     relief='sunken'),
             sg.VerticalSeparator(),
             sg.Text('00m:00s', k='el_total_time', pad=((10, 10), (0, 7)), font=('Courier', 18), size=(8, 1),
                     relief='sunken')],
            # ROW 6 - Headings for move-history output
            [sg.HorizontalSeparator()],
            [sg.Text('Move History', pad=((7, 10), (5, 0)), font=('Courier', 14), size=(13, 1)),
             sg.VerticalSeparator(),
             sg.Text('Move', pad=((7, 10), (5, 0)), font=('Courier', 14), size=(10, 1)),
             sg.VerticalSeparator(),
             sg.Text('Move Type', pad=((7, 10), (5, 0)), font=('Courier', 14), size=(11, 1)),
             sg.VerticalSeparator(),
             sg.Text('Duration', pad=((7, 14), (5, 0)), font=('Courier', 14), size=(8, 1)),
             sg.VerticalSeparator()],
            # ROW 7 - Element for move-history output throughout game-play
            [sg.Multiline('', k='el_move_history', do_not_clear=True, autoscroll=True, size=(60, 15),
                          font=('Courier', 12), disabled=True)]]

        # Build chess_board layout
        layout = [
            [menu_element],
            [sg.Column(gui_y_axis), sg.Column(board_and_axis), sg.VerticalSeparator(),
             sg.Column(window_elements), sg.VerticalSeparator()]]

        window = sg.Window(constants.WINDOW_TITLE, layout, default_button_element_size=(100, 1),
                           auto_size_buttons=False, finalize=True, icon=constants.LOGO)  # Create application window

        return window, menu_element, self.game_board


"""
fsmosca (2021). fsmosca/Python-Easy-Chess-GUI. [ONLINE] GitHub.
Available at: https://github.com/fsmosca/Python-Easy-Chess-GUI [Accessed 13 Apr. 2021].
This source provided detailed information for the implementation of a simple chess GUI
utilizing PySimpleGUI that links to python chess for gameplay.
This aligned perfectly with the desired requirements for this software and so formed a good foundation and resource.
"""