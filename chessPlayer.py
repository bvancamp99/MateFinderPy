# Author: Bryce Van Camp
# Project: MateFinder
# File: chessPlayer.py
# Description:


import math
import random

import chessGame
from const import *


pieceValues = {
    QUEEN: 9,
    ROOK: 5,
    BISHOP: 3, # TODO: 3.25?
    KNIGHT: 3,
    PAWN: 1
}

WIN = math.inf
LOSS = -math.inf


def getPieceValue(pieceType):
    '''
    Returns the value of the given piece type.

    See https://www.chess.com/terms/chess-piece-value
    '''
    return pieceValues[pieceType]


def getMaxDepth(n):
    '''
    Return the maximum depth for the current recursion given the number of
    moves n.
    '''
    return 0 if n <= 0 else max(2, math.ceil(5 / (2 * math.log(n + 1))))


class ChessPlayer:
    '''
    Plays chess.
    '''
    def __init__(self, board, colour):
        '''
        Init player.
        '''
        self.board = board
        self.colour = colour

    def getOpponentColour(self):
        return not self.colour

    def getMove(self, curTurn, lastMove=None, curBoard=None):
        '''
        Chooses a legal and (hopefully) competitive move for the given board and returns it.
        '''
        best = {
            'move': None,
            'score': -math.inf
        }

        moves = list(self.board.yieldMoves(colour=self.colour, board=curBoard))
        enPassantPositions = list(self.board.yieldEnPassantPositions(self.colour, lastMove, board=curBoard))
        castlePositions = list(self.board.yieldCastlePositions(self.colour, board=curBoard))
        n = len(moves) + len(enPassantPositions) + len(castlePositions)
        maxDepth = getMaxDepth(n)
        for m in random.sample(moves + enPassantPositions + castlePositions, k=n):
            futureBoard = self.board.getCopy(board=curBoard)
            if m in enPassantPositions:
                self.board.enPassant(*m, board=futureBoard)
                score = self.mini(curTurn, curBoard, futureBoard, maxDepth, enPassant=True)
            elif m in castlePositions:
                self.board.castle(*m, board=futureBoard)
                score = self.mini(curTurn, curBoard, futureBoard, maxDepth, castle=True)
            else:
                self.board.makeMove(*m, board=futureBoard)
                score = self.mini(curTurn, curBoard, futureBoard, maxDepth, lastMove=m)

            if score > best['score']:
                best['move'] = m
                best['score'] = score

                print(best)

            if best['score'] == WIN:
                break

        return best['move']

    def winCondition(self, cur_colour, lastMove, curBoard=None):
        '''
        Returns -1 for AI loss, 0 for no checkmate, 1 for opponent loss.
        '''
        king = self.board.getKing(cur_colour, board=curBoard)
        if king.isCheckmated(lastMove, curBoard=curBoard):
            return LOSS if cur_colour == self.colour else WIN
        else:
            return 0

    def heuristic(self, cur_colour, curTurn, prev_board, curBoard, curDepth, lastMove, enPassant, castle):
        h = 0
        if enPassant:
            h += pieceValues[PAWN]
        elif castle:
            h += 0.1
        elif lastMove is not None:
            if self.board.isPawnPromotionEligible(lastMove, board=curBoard):
                h += pieceValues[self.choosePawnPromotion(curBoard=curBoard)] - pieceValues[PAWN]

            x, y = lastMove

            oldX = self.board.getPiece(*x, board=prev_board)
            if not oldX.moved:
                h += 0.01

            oldY = self.board.getPiece(*y, board=prev_board)
            if chessGame.isPiece(oldY):
                h += getPieceValue(oldY.pieceType)

        h *= 0.8**curDepth

        return h if cur_colour == self.getOpponentColour() else -h

    def maxi(self, curTurn, prev_board, curBoard, maxDepth, curDepth=0, h=0, lastMove=None, enPassant=False, castle=False):
        cond = self.winCondition(self.colour, lastMove, curBoard=curBoard)
        if cond != 0:
            return cond

        h += self.heuristic(self.colour, curTurn, prev_board, curBoard, curDepth, lastMove, enPassant, castle)
        if curDepth >= maxDepth:
            return h

        if self.board.isPawnPromotionEligible(lastMove, board=curBoard):
            _, x = lastMove
            self.board.promotePawn(x, pieceType=self.choosePawnPromotion(curBoard=curBoard), board=curBoard)

        moves = list(self.board.yieldMoves(colour=self.colour, board=curBoard))
        enPassantPositions = list(self.board.yieldEnPassantPositions(self.colour, lastMove, board=curBoard))
        castlePositions = list(self.board.yieldCastlePositions(self.colour, board=curBoard))

        a = -math.inf

        n = len(moves) + len(enPassantPositions) + len(castlePositions)
        maxDepth = getMaxDepth(n)
        for m in random.sample(moves + enPassantPositions + castlePositions, k=n):
            futureBoard = self.board.getCopy(board=curBoard)
            if m in enPassantPositions:
                self.board.enPassant(*m, board=futureBoard)
                score = self.mini(curTurn, curBoard, futureBoard, maxDepth, curDepth=curDepth+1, h=h, enPassant=True)
            elif m in castlePositions:
                self.board.castle(*m, board=futureBoard)
                score = self.mini(curTurn, curBoard, futureBoard, maxDepth, curDepth=curDepth+1, h=h, castle=True)
            else:
                self.board.makeMove(*m, board=futureBoard)
                score = self.mini(curTurn, curBoard, futureBoard, maxDepth, curDepth=curDepth+1, h=h, lastMove=m)

            a = max(a, score)

            if a == WIN:
                break

        return a

    def mini(self, curTurn, prev_board, curBoard, maxDepth, curDepth=0, h=0, lastMove=None, enPassant=False, castle=False):
        cond = self.winCondition(self.getOpponentColour(), lastMove, curBoard=curBoard)
        if cond != 0:
            return cond

        h += self.heuristic(self.getOpponentColour(), curTurn, prev_board, curBoard, curDepth, lastMove, enPassant, castle)
        if curDepth >= maxDepth:
            return h

        if self.board.isPawnPromotionEligible(lastMove, board=curBoard):
            _, x = lastMove
            self.board.promotePawn(x, pieceType=self.choosePawnPromotion(curBoard=curBoard), board=curBoard)

        moves = list(self.board.yieldMoves(colour=self.getOpponentColour(), board=curBoard))
        enPassantPositions = list(self.board.yieldEnPassantPositions(self.getOpponentColour(), lastMove, board=curBoard))
        castlePositions = list(self.board.yieldCastlePositions(self.getOpponentColour(), board=curBoard))

        b = math.inf

        n = len(moves) + len(enPassantPositions) + len(castlePositions)
        maxDepth = getMaxDepth(n)
        for m in random.sample(moves + enPassantPositions + castlePositions, k=n):
            futureBoard = self.board.getCopy(board=curBoard)
            if m in enPassantPositions:
                self.board.enPassant(*m, board=futureBoard)
                score = self.maxi(curTurn, curBoard, futureBoard, maxDepth, curDepth=curDepth+1, h=h, enPassant=True)
            elif m in castlePositions:
                self.board.castle(*m, board=futureBoard)
                score = self.maxi(curTurn, curBoard, futureBoard, maxDepth, curDepth=curDepth+1, h=h, castle=True)
            else:
                self.board.makeMove(*m, board=futureBoard)
                score = self.maxi(curTurn, curBoard, futureBoard, maxDepth, curDepth=curDepth+1, h=h, lastMove=m)

            b = min(b, score)

            if b == LOSS:
                break

        return b

    def choosePawnPromotion(self, curBoard=None):
        # TODO: implement

        return QUEEN
