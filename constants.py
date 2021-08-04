import os

"""
Stores all the constants throughout the software.
"""

WINDOW_TITLE = 'Beat My Chess AI'
LOGO = 'Images/logo.ico'

ALGORITHM_LIST = ['NegaMax', 'NegaMax & Alpha-Beta', 'NegaScout & Quiesce', 'MTD(f) - Main']
DEPTH_LIST = [2, 3, 4, 5]

# State 1: Pre-Game. GUI elements outside of in-game.
PREGAME_MENU_BAR = [['Menu', ['Start Game', ['Play as White', 'Play as Black'], 'Close Application']],
                    ['Algorithm Info. && Settings', ['Select Algorithm', 'Default Algorithm', 'Change Search Depth',
                                                     'Algorithm Information']],
                    ['Display Settings', ['Preview Themes', 'Default Theme', 'Select Theme', 'Select Board Colours']],
                    ['Timer Settings', ['Timer Settings']],
                    ['Help && Info', ['Help && Info']]]
STATE_PREGAME = "Pre-Game - Ready!"

# State 2: In-Game. GUI elements for during gameplay
IN_GAME_MENU_BAR = [['&Menu', ['End Game']],
                    ['Algorithm Information', ['Algorithm Info.']],
                    ['Help && Info', ['Help && Info']]]

STATE_PLAYER_MOVE = "In-Game - Your Move!"
STATE_ENGINE_MOVE = "In-Game - Thinking..."
START_PIECES_NUM = 16

COLOUR_LIST = ['Green', 'Wood']

EXACT_SCORE = 0
LOWER_BOUND_SCORE = 1
UPPER_BOUND_SCORE = 2

# Identifiers for each chess piece
BLANK = 0
PAWN_B = 1
KNIGHT_B = 2
BISHOP_B = 3
ROOK_B = 4
KING_B = 5
QUEEN_B = 6
PAWN_W = 7
KNIGHT_W = 8
BISHOP_W = 9
ROOK_W = 10
KING_W = 11
QUEEN_W = 12

# Layout for chess_board
INIT_BOARD = [[ROOK_B, KNIGHT_B, BISHOP_B, QUEEN_B, KING_B, BISHOP_B, KNIGHT_B, ROOK_B],
              [PAWN_B, ] * 8,
              [BLANK, ] * 8,
              [BLANK, ] * 8,
              [BLANK, ] * 8,
              [BLANK, ] * 8,
              [PAWN_W, ] * 8,
              [ROOK_W, KNIGHT_W, BISHOP_W, QUEEN_W, KING_W, BISHOP_W, KNIGHT_W, ROOK_W]]

# Import chess piece images
IMG_PATH = 'Images'  # Path to images
IMG_BLANK = os.path.join(IMG_PATH, 'blank.png')
IMG_PAWN_B = os.path.join(IMG_PATH, 'b_pawn.png')
IMG_PAWN_W = os.path.join(IMG_PATH, 'w_pawn.png')
IMG_ROOK_B = os.path.join(IMG_PATH, 'b_rook.png')
IMG_ROOK_W = os.path.join(IMG_PATH, 'w_rook.png')
IMG_KNIGHT_B = os.path.join(IMG_PATH, 'b_knight.png')
IMG_KNIGHT_W = os.path.join(IMG_PATH, 'w_knight.png')
IMG_BISHOP_B = os.path.join(IMG_PATH, 'b_bishop.png')
IMG_BISHOP_W = os.path.join(IMG_PATH, 'w_bishop.png')
IMG_QUEEN_B = os.path.join(IMG_PATH, 'b_queen.png')
IMG_QUEEN_W = os.path.join(IMG_PATH, 'w_queen.png')
IMG_KING_B = os.path.join(IMG_PATH, 'b_king.png')
IMG_KING_W = os.path.join(IMG_PATH, 'w_king.png')

PIECE_IMAGES = {BISHOP_B: IMG_BISHOP_B, BISHOP_W: IMG_BISHOP_W, PAWN_B: IMG_PAWN_B, PAWN_W: IMG_PAWN_W,
                KNIGHT_B: IMG_KNIGHT_B, KNIGHT_W: IMG_KNIGHT_W, ROOK_B: IMG_ROOK_B, ROOK_W: IMG_ROOK_W,
                KING_B: IMG_KING_B, KING_W: IMG_KING_W, QUEEN_B: IMG_QUEEN_B, QUEEN_W: IMG_QUEEN_W, BLANK: IMG_BLANK}

CLICKED_LIGHT_COLOUR = '#00A35A'                # Colour if light square clicked
CLICKED_DARK_COLOUR = '#008148'                 # Colour if dark square clicked

"""game Constants"""
HIGHLIGHT_LIGHT = '#80DED9'                     # Colour to highlight potential moves - light sq
HIGHLIGHT_DARK = '#3CCDC6'                      # Colour to highlight potential moves - dark sq
STARTER_PGN = {'Event': 'Player vs Engine',   # Starting PGN tags
               'White': 'Player',
               'Black': 'Engine'}

"""evaluator Constants"""
PAWN_SCORE = 100                # Piece value a pawn
MAX_SCORE = PAWN_SCORE * 100    # Maximum score awarded in static evaluation
"""Value of each piece: (old vals shown to side)"""
PIECE_VALUE = [100,             # PAWN:   100
               300,             # KNIGHT: 400
               330,             # BISHOP: 410
               550,             # ROOK: 600
               1000,            # QUEEN: 1200
               0]               # KING: 0
PHASE_POINTS = [0, 1, 1, 2, 4, 0]

"""Information Windows Text"""
INFO_STR = 'This software provides four search algorithms to select from, in increasing complexity: ' \
           '\nNegaMax, NegaMax with Alpha-Beta Pruning, NegaScout with Quiesce Search, and finally, MTD(f).' \
           '\n\nAll of these methods are based around the MiniMax algorithm. In chess, each player ' \
           'can be thought of as having\na numerical score denoting the likelihood of winning. The system wants to ' \
           'maximise this score, whilst the opponent wants to minimise it.\n\nMinimax works by simulating this ' \
           'situation through a depth-first search, iterating over all potential moves to find the maximum and ' \
           'minimum\nscores, respectively. This mimics each players optimal move during a game, and the process ' \
           'builds a Search Tree\ncontaining all potential moves for each player.' \
           '\n\nAs the search through the tree progresses, the number of potential game-states increases ' \
           'drastically. Whilst a brute-force approach,\nsearching all states, would return the perfect move, this ' \
           'is not computationally feasible, and the search-space must be limited. ' \
           '\n\nThe search depth for the algorithms can be set with this software. The deeper the search, the ' \
           'greater the effectiveness, however,\nefficiency decreases dramatically. ' \
           '\n\nAs the algorithms become more complex, the deeper search depth they ' \
           'are able to reach.\nFor example, MTD(f) functions efficiently at depth 4, however to match that speed ' \
           'NegaMax, ' \
           '\n\nNegaMax: The most basic of the algorithms provided, this is a implementation variation of ' \
           'the Minimax algorithm. It iterates over a\nsearch-tree, calling alternating functions that return ' \
           'the minimum and maximum scores, respectively.\nThis simulates the alternating moves of players.' \
           '\n\nNegaMax with Alpha-Beta Pruning: This enhancement to NegaMax aims to reduce the width of the ' \
           'search-tree by not calculating\nareas of the tree it has determined to be redundant.' \
           '\n\nNegaScout with Quiesce Search: Building on the previous algorithm, NegaScout involves further ' \
           'narrowing of the search-tree by\n performing minimal-window searches. ' \
           'The other addition is Quiescence, which combats the horizon-effect, by performing additional,\n' \
           'limited searches on moves in the next layer of the tree that involve captures or check-moves.' \
           '\n\nMTD(f): This algorithm enhances the former methods by using new upperbound and lowerbound ' \
           'values to converge on the\ntrue value. It also incorporates transposition tables, that reduce ' \
           'calculations by providing a mechanism for storing and retrieving\nchess_board states and their evaluations.'

HELP_STR_INIT = 'Welcome to ''BeatMyChessAI'', a software designed to allow you to compete against a selection of ' \
              'prolific and powerful search algorithms.' \
              '\n\nTo quickly begin a game, simply click the Menu button in the header, followed by Start Game, ' \
              'and then choose a colour.' \
              '\n\nTo alter the application colours, themes can be previewed to quickly find the ideal ' \
              'colour-scheme. It can then be selected from the vast selection in Themes Options.' \
              '\n\nIf the game is too difficult, there are two mechanisms to alter the difficulty:' \
              '\n    Depth: The lower the search depth, the less calculations the engine is able to complete, ' \
              'thus lowering its effectiveness.' \
              '\n    Algorithm: The algorithms are provided in increasing levels of difficulty, with NegaMax ' \
              'being the most simple and MTD(f) the most complex.' \
              '\n\n The timer can also be turned off, for a less stressful game, through the Timer Settings.'

HELP_STR_INGAME = 'Welcome to ''BeatMyChessAI'', a software designed to allow you to compete against a selection of ' \
              'prolific and powerful search algorithms.' \
              '\n\nYou are now in a game against one of the algorithms!' \
              '\nTo make a move, simply click on a piece and all of the moves it can make will be highlighted. ' \
              'Click any of these squares to make a move.' \
                  '\n\n\nThe Move History output contains a breakdown of each move. The initial code is Chess ' \
                  'Notation, from this code, all the other information is extrapolated. ' \
                  '\n\nThe code for Chess Notation is as follows:' \
                  '\nMovement: The movement for each piece is represented in alphanumerical format (IE e4, d5).' \
                  '\n\nPieces: The piece moved is denoted by a letter.\nK = King, Q = Queen, B = Bishop, N = Knight, ' \
                  'and R = Rook. If there is no letter then it means a Pawn was moved.' \
                  '\n\nEvents: There are symbols that represent different move types in the game, similar to pieces:' \
                  '\nx = Capture, ' \
                  '\nO-O/O-O-O = Castling,' \
                  '\n+ = In-Check,' \
                  '\n# = Checkmate.' \
                  '' \
              '\n\nGood Luck!' \
              '\n\nIf you would like to end the game, to change theme, algorithm settings or colour, just click ' \
              'the menu and then End Game and you will be returned to the home screen'

