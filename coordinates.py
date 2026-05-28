# Author: Bryce Van Camp
# Project: MateFinder
# File: coordinates.py
# Description: Functions that handle square/index conversion and file/rank math


from enums import *


def on_board(file, rank):
    '''
    Returns if file and rank exist on an 8x8 board.

    Valid params range from (File.A, 1) to (File.H, 8)
    '''
    return File.A <= file <= File.H and 1 <= rank <= 8


def index_to_square(i, j):
    '''
    Given index row i and column j, return chess square.
    
    e.g. returns (File.D, 6) for input (2, 3)
    '''
    return File.A + j, 8 - i


def square_to_index(file, rank):
    '''
    Given file and rank, return array index.

    e.g. returns (2, 3) for input (File.D, 6)
    '''
    return 8 - rank, file - File.A


def minmax(i, j):
    '''
    Returns min, max tuple of i and j.
    '''
    return (i, j) if i < j else (j, i)


def iter_between(i, j):
    '''
    Iterates values between i and j, exclusive.
    '''
    step = 1 if i < j else - 1
    return (btwn for btwn in range(i + step, j, step))


def iter_rook_squares_between(x_file, x_rank, y_file, y_rank):
    '''
    Iterates squares between two squares that have the same rank or file.
    '''
    # Horizontal
    if x_rank == y_rank:
        for btwn_file in iter_between(x_file, y_file):
            yield btwn_file, x_rank
    # Vertical
    elif x_file == y_file:
        for btwn_rank in iter_between(x_rank, y_rank):
            yield x_file, btwn_rank
    else:
        raise ValueError(f'iter_rook_squares_between called with squares not on same rank or file! {x_file}{x_rank}, {y_file}{y_rank}')


def iter_bishop_squares_between(x_file, x_rank, y_file, y_rank):
    '''
    Iterates squares between two squares that are facing diagonally.
    '''
    # Diagonal
    if abs(x_file - y_file) == abs(x_rank - y_rank):
        for btwn_file, btwn_rank in zip(iter_between(x_file, y_file), iter_between(x_rank, y_rank)):
            yield btwn_file, btwn_rank
    else:
        raise ValueError(f'iter_bishop_squares_between called with squares not on same diagonal path! {x_file}{x_rank}, {y_file}{y_rank}')
