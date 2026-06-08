# Author: Bryce Van Camp
# Project: MateFinder
# File: move.py
# Description: Move class


class Move:
    def __init__(self, board, m_type, st_square, end_square, tgt_piece=None, promotion_letter=''):
        self.m_type = m_type
        self.st_file, self.st_rank = st_square
        self.end_file, self.end_rank = end_square
        self.tgt_piece = tgt_piece
        self.promotion_letter = promotion_letter

        self.moving_piece = board.get_piece(st_square)
        self.algebraic_notation = board.get_pseudo_algebraic_notation(self)

    @property
    def st_square(self):
        return self.st_file, self.st_rank

    @st_square.setter
    def st_square(self, st_square):
        self.st_file, self.st_rank = st_square

    @property
    def end_square(self):
        return self.end_file, self.end_rank

    @end_square.setter
    def end_square(self, end_square):
        self.end_file, self.end_rank = end_square

    def __str__(self):
        # TODO: Add algebraic notation class field
        return self.algebraic_notation
