# Author: Bryce Van Camp
# Project: MateFinder
# File: enums.py
# Description: Enums to be used throughout the project.


import enum


class PieceType(enum.IntEnum):
    KING = 0
    QUEEN = 1
    ROOK = 2
    BISHOP = 3
    KNIGHT = 4
    PAWN = 5


class Color(enum.IntEnum):
    BLACK = 0
    WHITE = 1


class MoveType(enum.IntEnum):
    STD = 1
    CASTLE = 2
    EN_PASSANT = 4
    ALL = STD + CASTLE + EN_PASSANT


class File(enum.IntEnum):
    '''
    Decimal ascii values of 'a' through 'h'
    '''
    A = ord('a')
    B = ord('b')
    C = ord('c')
    D = ord('d')
    E = ord('e')
    F = ord('f')
    G = ord('g')
    H = ord('h')
