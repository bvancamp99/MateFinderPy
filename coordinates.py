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


def shift_file(file, delta):
    '''
    Shifts a file by delta, e.g. returns File.B for input (File.A, 1)
    '''
    return chr(ord(file) + delta)


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


# TODO remove from here...
def on_same_rook_path(x_file, x_rank, y_file, y_rank):
    '''
    Returns if two squares are on the same horizontal or vertical path.
    - i.e. A rook could (without checking for pieces in between) move from one square to the other in a single move.
    '''
    return x_rank == y_rank or x_file == y_file


def iter_rook_squares_between(x_file, x_rank, y_file, y_rank):
    '''
    Iterates squares between two squares that are on the same horizontal or vertical path.
    '''
    if x_rank == y_rank:
        # Iter horizontal squares between, traversing right if x_file < y_file else left
        sign = 1 if x_file < y_file else -1
        for cur_dist in range(1, abs(ord(x_file) - ord(y_file)):
            yield x_file + sign * cur_dist, x_rank
    elif x_file == y_file:
        # Iter vertical squares between, traversing up if x_rank < y_rank, else down
        sign = 1 if x_rank < y_rank else -1
        for cur_dist in range(1, abs(x_rank - y_rank)):
            yield x_file, x_rank + sign * cur_dist
    else:
        raise ValueError(f'iter_rook_squares_between called with squares not on same rook path! {x_file}{x_rank}, {y_file}{y_rank}')


def on_same_diagonal_path(x_file, x_rank, y_file, y_rank):
    '''
    Returns if two squares are on the same diagonal path.
    - i.e. A bishop could (without checking for pieces in between) move from one square to the other in a single move.
    '''
    return abs(x_file - y_file) == abs(x_rank - y_rank)


def iter_bishop_squares_between(x_file, x_rank, y_file, y_rank):
    '''
    Iterates squares between two squares that are on the same diagonal path.
    '''
    if not on_same_diagonal_path(x_file, x_rank, y_file, y_rank):
        raise ValueError(f'iter_bishop_squares_between called with squares not on same bishop path! {x_file}{x_rank}, {y_file}{y_rank}')

    # Traverse right if x_file < y_file, else left
    file_sign = 1 if x_file < y_file else -1

    # Traverse up if x_rank < y_rank, else down
    rank_sign = 1 if x_rank < y_rank else -1

    for cur_dist in range(1, abs(x_rank - y_rank)):
        yield x_file + file_sign * cur_dist, x_rank + rank_sign * cur_dist
# TODO ...to here?


def iter_between(i, j):
    '''
    Iterates values between i and j, exclusive.
    '''
    step = 1 if i < j else - 1
    return (btwn for btwn in range(i + step, j, step))


def iter_squares_between(x_file, x_rank, y_file, y_rank):
    '''
    Iterates squares between two squares that are on the same rank, file, or diagonal path.
    '''
    # Horizontal - traverse right if x_file < y_file else left
    if x_rank == y_rank:
        sign = 1 if x_file < y_file else -1
        for cur_dist in range(1, abs(x_file - y_file)):
            yield x_file + sign * cur_dist, x_rank
    # Vertical - traverse up if x_rank < y_rank, else down
    elif x_file == y_file:
        sign = 1 if x_rank < y_rank else -1
        for cur_dist in range(1, abs(x_rank - y_rank)):
            yield x_file, x_rank + sign * cur_dist
    # Diagonal - traverse as above but both at the same time
    elif abs(x_file - y_file) == abs(x_rank - y_rank):
        file_sign = 1 if x_file < y_file else -1
        rank_sign = 1 if x_rank < y_rank else -1
        for cur_dist in range(1, abs(x_rank - y_rank)):
            yield x_file + file_sign * cur_dist, x_rank + rank_sign * cur_dist
    else:
        raise ValueError(f'iter_squares_between called with squares not on same rank, file, or diagonal path! {x_file}{x_rank}, {y_file}{y_rank}')


# TODO remove?
def iter_squares_between(x_file, x_rank, y_file, y_rank):
    '''
    NOTE: O(N), N = distance between x_square + 1 and y_square - 1
    '''
    def iter_horizontal_between():
        st_file, end_file = minmax(x_file, y_file)
        for file_ord in range(ord(st_file) + 1, ord(end_file)):
            yield chr(file_ord), x_rank

    def iter_vertical_between():
        st_rank, end_rank = minmax(x_rank, y_rank)
        for cur_rank in range(st_rank + 1, end_rank):
            yield x_file, cur_rank

    def iter_diagonal_between():
        file_dist = ord(x_file) - ord(y_file)
        rank_dist = x_rank - y_rank
        st_file, end_file = minmax(x_file, y_file)
        rank_sign = 1
        if file_dist == rank_dist:
            # up-right
            st_rank, end_rank = minmax(x_rank, y_rank)
        else: # file_dist == -rank_dist
            # down-right
            end_rank, st_rank = minmax(x_rank, y_rank)
            rank_sign = -rank_sign

        for cur_dist in range(1, abs(file_dist)):
            yield coordinates.shift_file(st_file, cur_dist), st_rank + (rank_sign * cur_dist)

    if x_rank == y_rank:
        return iter_horizontal_between()
    elif x_file == y_file:
        return iter_vertical_between()
    elif abs(x_file - y_file) == abs(x_rank - y_rank):
        return iter_diagonal_between()
    else:
        raise ValueError(f'Squares {x} and {y} not on same vertical, horizontal, or diagonal path.')
