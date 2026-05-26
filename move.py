# Author: Bryce Van Camp
# Project: MateFinder
# File: move.py
# Description: Move class


class Move:
    def __init__(self, board, m_type, st_square, end_square, tgt_piece=None, promotion_letter=''):
        self.m_type = m_type
        self.st_square = st_square
        self.end_square = end_square
        self.tgt_piece = tgt_piece
        self.promotion_letter = promotion_letter

        self.moving_piece = board.get_piece(st_square)
        self.algebraic_notation = board.get_pseudo_algebraic_notation(self)

    def __str__(self):
        # TODO: Add algebraic notation class field
        return self.algebraic_notation
