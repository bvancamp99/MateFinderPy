# Author: Bryce Van Camp
# Project: MateFinder
# File: coordinates.py
# Description: Functions that handle square/index conversion and file/rank math


from collections import namedtuple

from enums import File


Square = namedtuple('Square', ['file', 'rank'])


def on_board(square):
    '''
    Returns if square exists on an 8x8 board.

    Valid params range from (File.A, 1) to (File.H, 8)
    '''
    return File.A <= square.file <= File.H and 1 <= square.rank <= 8


def index_to_square(i, j):
    '''
    Given index row i and column j, return chess square.
    
    e.g. returns (File.D, 6) for input (2, 3)
    '''
    return Square(File.A + j, 8 - i)


def square_to_index(square):
    '''
    Given file and rank, return array index.

    e.g. returns (2, 3) for input (File.D, 6)
    '''
    return 8 - square.rank, square.file - File.A


def minmax(i, j):
    '''
    Returns min, max tuple of i and j.
    '''
    return (i, j) if i < j else (j, i)
