# Author: Bryce Van Camp
# Project: MateFinder
# File: chess_board.py
# Description: ChessBoard data structure


import numpy as np

import chess_piece.py
from const import *


EMPTY_ICON = '•'

_STD_TEMPLATE = np.array([
    [(ROOK, BLACK), (KNIGHT, BLACK), (BISHOP, BLACK), (QUEEN, BLACK), (KING, BLACK), (BISHOP, BLACK), (KNIGHT, BLACK), (ROOK, BLACK)],
    [(PAWN, BLACK)] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [(ROOK, WHITE), (KNIGHT, WHITE), (BISHOP, WHITE), (QUEEN, WHITE), (KING, WHITE), (BISHOP, WHITE), (KNIGHT, WHITE), (ROOK, WHITE)]
])


def _is_valid_piece_type(piece_type):
    return KING <= piece_type <= PAWN


def _is_valid_color(color):
    return color == BLACK or color == WHITE


def _is_valid_template_piece(cell):
    '''
    Returns if template cell represents a valid piece, i.e. it is a tuple of 
    (piece_type, color) format.
    '''
    if not isinstance(cell, tuple) or len(cell) != 2:
        return False

    piece_type, color = cell
    return _is_valid_piece_type(piece_type) and _is_valid_color(color)


def _test_template(template):
    '''
    Raises exception if there exists an invalid template entry or if there 
    isn't exactly one of each king.
    '''
    kings_exist = [False, False]
    for i in range(8):
        for j in range(8):
            cell = template[i,j]
            if cell is None:
                continue
            elif not _is_valid_template_piece(cell):
                raise Exception('Non-valid template entry', cell)
            elif cell == (KING, BLACK):
                if kings_exist[BLACK]:
                    raise Exception('More than one black king in template!')
                else:
                    kings_exist[BLACK] = True
            elif cell == (KING, WHITE):
                if kings_exist[WHITE]:
                    raise Exception('More than one white king in template!')
                else:
                    kings_exist[WHITE] = True

    if not kings_exist[BLACK]:
        raise Exception('No black king in template!')
    elif not kings_exist[WHITE]:
        raise Exception('No white king in template!')


class ChessBoard:
    def __init__(self, user_color, template=None):
        self._user_color = user_color

        if template is None:
            template = _STD_TEMPLATE
        _test_template(template)
        if user_color == BLACK:
            template = np.flip(template)

        self._board_arr = np.array([[None] * 8 for _ in range(8)])
        self._piece_pos = ({}, {})
        self._king_pos = [None, None]
        for i in range(8):
            for j in range(8):
                cell = template[i,j]
                if cell is None:
                    self._board_arr[i,j] = None
                else:
                    piece_type, color = cell
                    cur_pos = self.get_chess_pos(i, j)
                    cur_piece = chess_piece.get_new_piece(piece_type, color, cur_pos, self)
                    self._board_arr[i,j] = cur_piece
                    self._piece_pos[color].add(cur_pos)
                    if piece_type == KING:
                        self._king_pos[color] = cur_pos

    def get_chess_file(self, j):
        return chess_piece.file_add('A', j) if self._user_color == WHITE else chess_piece.file_add('H', -j)

    def get_chess_rank(self, i):
        return 8 - i if self._user_color == WHITE else i + 1

    def get_chess_pos(self, i, j):
        '''
        Returns tuple of chess file and rank given row i and column j of board 
        2D array.

        e.g. returns ('D', '6') for input (2, 3) when user color is white
        '''
        return (self.get_chess_file(j), self.get_chess_rank(i))

    def get_arr_row(self, rank):
        return 8 - rank if self._user_color == WHITE else rank - 1

    def get_arr_col(self, file):
        return ord(file) - ord('A') if self._user_color == WHITE else ord('H') - ord(file)

    def get_arr_index(self, file, rank):
        '''
        Returns corresponding row and column in board 2D array given chess 
        file and rank.

        e.g. returns (2, 3) for input ('D', 6) when user color is white
        '''
        return (self.get_arr_row(rank), self.get_arr_col(file))

    def get_piece(self, file, rank):
        return self._board_arr[self.get_arr_index(file, rank)]

    def get_king(self, color):
        return self.get_piece(self._king_pos[color])

    def yield_pieces(self, color=None):
        '''
        Yields all pieces on the board with optional color param.
        '''
        if color != WHITE:
            for cur_pos in self._piece_pos[BLACK]:
                yield self.get_piece(*cur_pos)
        
        if color != BLACK:
            for cur_pos in self._piece_pos[WHITE]:
                yield self.get_piece(*cur_pos)

    def yield_std_moves(self, color=None):
        '''
        Yields all standard (i.e. everything except castle and en passant) 
        moves that can be made by all pieces with optional color param.
        '''
        for cur_piece in self.yield_pieces(color=color):
            for std_move in cur_piece.yield_std_moves():
                yield std_move
