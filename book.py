import chess
import logging
import chess.polyglot


class BookController:
    def __init__(self, book_file, board):
        """
        Handle polyglot Opening Book Moves for the engine.
        :param book_file: Polgylot book file
        :param board: provided chess_board position
        """
        self.book_file = book_file
        self.board = board
        self.__book_move = None

    def get_book_move(self):
        reader = chess.polyglot.open_reader(self.book_file)
        try:
            entry = reader.weighted_choice(self.board)            # Get move from book
            self.__book_move = entry.move                         # Store move
        except IndexError:
            logging.info('No book move. Moving to main engine.')
        except Exception():
            logging.exception('Failed to get Book.')
        finally:
            reader.close()                                        # Close polyglot reader

        return self.__book_move
