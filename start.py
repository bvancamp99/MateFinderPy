# Author: Bryce Van Camp
# Project: MateFinder
# File: start.py
# Description: Run this file to start the game loop


import random
import sys
import timeit

from board import Board
from engine import Engine
from enums import Color
from peekable import Peekable
import fen


def get_user_color():
    user_color = None
    while user_color not in {'1', '2', '3'}:
        user_color = input('Choose colour (1: black, 2: white, 3: random): ')

    user_color = int(user_color) - 1
    if user_color == 2:
        user_color = random.randint(Color.BLACK, Color.WHITE)

    return user_color


def get_user_move(notation_dict):
    notation = None
    while notation not in notation_dict:
        notation = input('Please enter the notation for your next move: ')

    return notation_dict[notation]


def main(fen_str):
    fen_class = fen.FenClass(fen_str)
    user_color = get_user_color()
    engine = Engine(user_color)
    board = Board(fen_class, user_color)

    board.pretty_print()
    while board.move_it.has_next():
        if board.insufficient_material():
            print('Insufficient material. Game ends in a draw.')
            return

        if board.get_active_king().is_being_attacked():
            print('King is in check.')

        # User's turn
        if fen_class.active_color == user_color:
            print('Your turn...')

            notation_dict = {str(m): m for m in list(board.move_it)}
            print('Legal moves:', end=' ')
            for notation in notation_dict.keys():
                print(notation, end='  ')

            user_move = get_user_move(notation_dict)
            board.make_move(user_move)
        # Engine's turn
        else:
            print('Engine\'s turn...')

            engine_move = engine.get_move(board)
            board.make_move(engine_move)

            print('Engine move:', engine_move)

        board.pretty_print()

    if board.get_active_king().is_being_attacked():
        if fen_class.active_color == user_color:
            print('Engine wins!')
        else:
            print('You win!')
    else:
        print('Game ends in a stalemate.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fen_str = sys.argv[1]
    else:
        fen_str = fen.START_FEN

    main(fen_str)
