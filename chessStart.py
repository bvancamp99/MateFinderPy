# Author: Bryce Van Camp
# Project: MateFinder
# File: chessStart.py
# Description:


import numpy as np
import random

import chessGame
import chessPlayer
from const import *

def pos(pos_str):
    col, row = pos_str
    return (col, int(row))


def main(template=None):
    userColour = None
    while userColour not in {'1', '2', '3'}:
        userColour = input('Choose colour (1: black, 2: white, 3: random): ')

    userColour = int(userColour) - 1
    if userColour == RANDOM:
        userColour = random.randint(BLACK, WHITE)

    board = chessGame.ChessBoard(userColour, template=template)

    aiColour = BLACK if userColour == WHITE else WHITE
    ai = chessPlayer.ChessPlayer(board, aiColour)

    curColour = WHITE
    curTurn = 1
    lastMove = None
    moves = set(board.yieldMoves(colour=curColour))
    enPassantPositions = set()
    castlePositions = set()
    while moves or enPassantPositions or castlePositions:
        board.prettyPrint()

        num_pieces = 0
        for _ in board.yieldPieces():
            num_pieces += 1
            if num_pieces > 2:
                break
        if num_pieces == 2:
            print('Game ends in a draw.')
            return

        curKing = board.getKing(curColour)
        if curKing.isUnderAttack():
            print('King is in check.')

        print('Turn', curTurn)

        if curColour == userColour:
            print('Your turn...')

            print('Standard moves:', moves)
            print('En passant positions:', enPassantPositions)
            print('Castle positions:', castlePositions)
            lastMove = None
            while True:
                try:
                    x = pos(input('Move from (e.g. A5): '))
                    y = pos(input('Move to (e.g. A4): '))
                except ValueError:
                    continue

                if (x, y) in moves:
                    board.makeMove(x, y)
                    lastMove = (x, y)
                    break
                elif (x, y) in enPassantPositions and input('En passant? (y/n): ') == 'y':
                    board.enPassant(x, y)
                    break
                elif (x, y) in castlePositions and input('Castle? (y/n): ') == 'y':
                    board.castle(x, y)
                    break

            if board.isPawnPromotionEligible(lastMove):
                print('Pawn promotion!', end=' ')

                promotion = None
                while promotion not in chessGame.pawn_promotion_choices:
                    promotion = input('Choose your piece type (queen, rook, bishop, or knight): ')

                _, x = lastMove
                board.promotePawn(x, s=promotion)
        else:
            print('AI\'s turn...')

            m = ai.getMove(curTurn, lastMove=lastMove)
            lastMove = None
            if m in moves:
                board.makeMove(*m)
                lastMove = m
                print('AI moves', m)
            elif m in enPassantPositions:
                m = board.enPassant(*m)
                print('AI en passants')
            elif m in castlePositions:
                m = board.castle(*m)
                print('AI castles')
            else:
                raise Exception('AI chose illegal move {}'.format(m))

            if board.isPawnPromotionEligible(lastMove):
                print('Pawn promotion!', end=' ')

                promotion = ai.choosePawnPromotion()
                if promotion not in chessGame.pawn_promotion_choices:
                    raise Exception('AI cannot choose {} for promotion piece type'.format(promotion))

                print('AI chooses', promotion)
                _, x = lastMove
                board.promotePawn(x, s=promotion)

        curColour = BLACK if curColour == WHITE else WHITE
        curTurn += 1

        moves = set(board.yieldMoves(colour=curColour))
        enPassantPositions = set(board.yieldEnPassantPositions(curColour, lastMove))
        castlePositions = set(board.yieldCastlePositions(curColour))

    board.prettyPrint()

    curKing = board.getKing(curColour)
    if curKing.isCheckmated(lastMove):
        if curColour == userColour:
            print('AI wins!')
        else:
            print('You win!')
    else:
        print('Game ends in a stalemate.')


if __name__ == '__main__':
    template = None
    #template = chessGame.getCustomBoardTemplate()
    main(template=template)
