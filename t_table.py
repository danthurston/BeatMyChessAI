class TransTableEntry:
    """
    Each entry, representing a board state in the transposition table.
    """
    z_key = 0          # Zobrist hash key.
    score = 0          # Node score.
    depth = 0          # Current depth. Increases til max_depth reached.
    finalBoard = None  # Board state
    flag = 0           # 0 true value; 1 lower bound; 2 upper bound
    move = ''          # Optimal move
    result = ''        # Python-Chess formatted result of entry


class TransTable:
    """
    Transposition table. Holds all transposition table entries.
    """
    table = {}             # Table entry array
    size = 0               # Table initial size
    maxSize = 10 ** 7      # Maximum transposition table size
