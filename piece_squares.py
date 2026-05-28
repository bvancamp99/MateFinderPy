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
        elif isinstance(key, int):
            # Key is color
            return self._squares[key]
        else:
            raise ValueError(f'PieceSquares.__getitem__ received invalid key {key} !')

    def __len__(self):
        return len(self[0]) + len(self[1])

    def add(self, square, color, type_index):
        self[color].add(square)
        self[color, type_index].add(square)

    def remove(self, square, color, type_index):
        self[color].remove(square)
        self[color, type_index].remove(square)
