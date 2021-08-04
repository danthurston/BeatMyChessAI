import gui


def main():
    """
    imports book.bin file and calls the GUI controller.
    """
    book_moves = 'Book/book.bin'

    bmcai = gui.Controller(book_moves)
    bmcai.main_loop()


if __name__ == "__main__":
    main()
