# Author: Bryce Van Camp
# Project: MateFinder
# File: piece_squares.py
# Description: Piece squares class


from pieces import INDEX_MAP, get_color


'''
Board helper class that stores piece squares, organizing them by color and by type for speed of access.
'''
class PieceSquares:
    def __init__(self):
        # piece squares by color
        self._squares = (set(), set())

        # piece squares by color and piece type
        num_piece_types = 6
        black_squares_by_type = tuple(set() for _ in range(num_piece_types))
        white_squares_by_type = tuple(set() for _ in range(num_piece_types))
        self._squares_by_type = (black_squares_by_type, white_squares_by_type)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            color, type_index = key
            return self._squares_by_type[color][type_index]
        else:
            color = key
            return self._squares[color]

    def __len__(self):
        return len(self[0]) + len(self[1])

    def add(self, square, letter):
        color = get_color(letter)
        type_index = INDEX_MAP[letter.upper()]
        self[color].add(square)
        self[color, type_index].add(square)

    def remove(self, square, letter):
        color = get_color(letter)
        type_index = INDEX_MAP[letter.upper()]
        self[color].remove(square)
        self[color, type_index].remove(square)
