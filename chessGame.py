# Author: Bryce Van Camp
# Project: MateFinder
# File: chessGame.py
# Description:


import numpy as np
import copy
import itertools

from const import *


def getCustomBoardTemplate():
    '''
    You can start the game with a custom board state using this function.

    NOTE: This function assumes that the board state you supply is viewed
          from the white piece player's perspective.
    '''
    return np.array([
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY], ICONS[KING][BLACK], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY]],
        [ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[KING][WHITE], ICONS[EMPTY], ICONS[EMPTY]],
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[EMPTY], ICONS[ROOK][BLACK], ICONS[QUEEN][BLACK], ICONS[EMPTY]]
    ])


def getStandardBoardTemplate():
    return np.array([
        [ICONS[ROOK][BLACK], ICONS[KNIGHT][BLACK], ICONS[BISHOP][BLACK], ICONS[QUEEN][BLACK], ICONS[KING][BLACK], ICONS[BISHOP][BLACK], ICONS[KNIGHT][BLACK], ICONS[ROOK][BLACK]],
        [ICONS[PAWN][BLACK]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[EMPTY]] * 8,
        [ICONS[PAWN][WHITE]] * 8,
        [ICONS[ROOK][WHITE], ICONS[KNIGHT][WHITE], ICONS[BISHOP][WHITE], ICONS[QUEEN][WHITE], ICONS[KING][WHITE], ICONS[BISHOP][WHITE], ICONS[KNIGHT][WHITE], ICONS[ROOK][WHITE]]
    ])


def isPiece(x, colour=None, pieceType=None):
    '''
    Returns if x is a ChessPiece (i.e. is non-empty) and, optionally,
    if it is a specified colour and/or piece type.
    '''
    return (
        x != ICONS[EMPTY]
        and (True if colour is None else colour == x.colour)
        and (True if pieceType is None else pieceType == x.pieceType)
    )


def onBoard(chessCol, chessRow):
    '''
    Returns if the column and row fit in an 8x8 board.

    Valid params range from ('A', 1) to ('H', 8)
    '''
    return ord('A') <= ord(chessCol) <= ord('H') and 1 <= chessRow <= 8


def colSum(chessCol, j):
    '''
    Simplifies adding to a chess column.

    e.g. returns 'B' for input ('A', 1)
    '''
    return chr(ord(chessCol) + j)


class ChessBoard:
    def __init__(self, userColour, template=None):
        self._userColour = userColour

        if template is None:
            template = getStandardBoardTemplate()
        if userColour == BLACK:
            template = np.flip(template)

        self.iconToObject = {
            ICONS[KING][BLACK]: King(BLACK, None, self),
            ICONS[QUEEN][BLACK]: Queen(BLACK, None, self),
            ICONS[ROOK][BLACK]: Rook(BLACK, None, self),
            ICONS[BISHOP][BLACK]: Bishop(BLACK, None, self),
            ICONS[KNIGHT][BLACK]: Knight(BLACK, None, self),
            ICONS[PAWN][BLACK]: Pawn(BLACK, None, self),
            ICONS[KING][WHITE]: King(WHITE, None, self),
            ICONS[QUEEN][WHITE]: Queen(WHITE, None, self),
            ICONS[ROOK][WHITE]: Rook(WHITE, None, self),
            ICONS[BISHOP][WHITE]: Bishop(WHITE, None, self),
            ICONS[KNIGHT][WHITE]: Knight(WHITE, None, self),
            ICONS[PAWN][WHITE]: Pawn(WHITE, None, self)
        }

        self._board = np.array([[None] * 8 for _ in range(8)])
        for i in range(8):
            for j in range(8):
                c = template[i,j]
                if c == ICONS[EMPTY]:
                    self._board[i,j] = c
                elif c in ICON_SET:
                    curPiece = copy.copy(self.iconToObject[c])
                    curPiece.position = (self.getChessCol(j), self.getChessRow(i))
                    self._board[i,j] = curPiece
                else:
                    raise Exception('Non-valid piece char', c)

    def getChessRow(self, i):
        return 8 - i if self._userColour == WHITE else i + 1

    def getChessCol(self, j):
        return colSum('A', j) if self._userColour == WHITE else colSum('H', -j)

    # TODO: unused?
    def getChessPosition(self, i, j):
        '''
        Returns a string representing the chess position given the board indices.

        e.g. returns 'D6' for input (2,3) when user colour is white
        '''
        return (self.getChessCol(j), self.getChessRow(i))

    def getArrayRow(self, chessRow):
        return 8 - chessRow if self._userColour == WHITE else chessRow - 1

    def getArrayCol(self, chessCol):
        return ord(chessCol) - ord('A') if self._userColour == WHITE else ord('H') - ord(chessCol)

    def getArrayIndexing(self, chessCol, chessRow):
        '''
        Returns a tuple representing the indices of the back-end board
        corresponding with the chess_pos.

        e.g. returns (2,3) for input 'D', 6 when user colour is white
        '''
        return (self.getArrayRow(chessRow), self.getArrayCol(chessCol))

    def getPiece(self, chessCol, chessRow, board=None):
        if board is None:
            board = self._board

        return board[self.getArrayIndexing(chessCol, chessRow)]

    def _yieldVerticalBetween(self, x, y):
        xCol, xRow = x
        yCol, yRow = y

        startRow = min(xRow, yRow)
        endRow = max(xRow, yRow)

        for i in range(startRow + 1, endRow):
            yield (xCol, i)

    def _yieldHorizontalBetween(self, x, y):
        xCol, xRow = x
        yCol, yRow = y

        start_col = ord(min(xCol, yCol))
        end_col = ord(max(xCol, yCol))

        for i in range(start_col + 1, end_col):
            yield (chr(i), xRow)

    def _yieldDiagonalBetween(self, x, y):
        xCol, xRow = x
        yCol, yRow = y

        col_dif = ord(xCol) - ord(yCol)
        row_dif = xRow - yRow

        sign_match = 1 if col_dif == row_dif else -1

        start_col = ord(min(xCol, yCol))
        end_col = ord(max(xCol, yCol))

        startRow = min(xRow, yRow) if sign_match == 1 else max(xRow, yRow)
        endRow = max(xRow, yRow) if sign_match == 1 else min(xRow, yRow)

        for i in range(1, abs(col_dif)):
            yield (chr(start_col + i), startRow + i*sign_match)

    def yieldPositionsBetween(self, x, y):
        xCol, xRow = x
        yCol, yRow = y

        if xCol == yCol:
            return self._yieldVerticalBetween(x, y)
        elif xRow == yRow:
            return self._yieldHorizontalBetween(x, y)
        elif abs(ord(xCol) - ord(yCol)) == abs(xRow - yRow):
            return self._yieldDiagonalBetween(x, y)
        else:
            raise Exception('Positions {} and {} not on same vertical, horizontal, or diagonal path.'.format(x, y))

    def arePiecesBetween(self, x, y, board=None):
        '''
        Returns if at least one piece lies between positions x and y.
        Very useful in e.g. checking castle legality.

        NOTE: This function runs in linear time (checks each piece between x and y).
              This is very slow in the context of an exponentially large search tree,
              so avoid using if not necessary.
        '''
        if board is None:
            board = self._board

        for x in self.yieldPositionsBetween(x, y):
            if self.getPiece(*x, board=board) != ICONS[EMPTY]:
                return True
        return False

    def yieldPieces(self, colour=None, pieceType=None, board=None):
        '''
        Yields pieces on the board with the optionally specified colour and
        piece type.
        '''
        if board is None:
            board = self._board

        for i in range(8):
            for j in range(8):
                curPiece = board[i,j]
                if isPiece(curPiece, colour=colour, pieceType=pieceType):
                    yield curPiece

    def getKing(self, colour, board=None):
        '''
        Returns king piece of specified colour and optional different board state.
        '''
        # TODO: maybe hyper-optimize to check most likely positions first
        #       based on king's start position
        #       Better soln would be to store king object in a struct format with board state
        if board is None:
            board = self._board

        for i in range(8):
            for j in range(8):
                curPiece = board[i,j]
                if isPiece(curPiece, colour=colour, pieceType=KING):
                    return curPiece

        self.board.prettyPrint(board=board)
        raise Exception('No king of colour {} on the board!'.format(colour))

    def getCopy(self, board=None):
        if board is None:
            board = self._board

        return np.copy(board)

    def prettyPrint(self, board=None):
        if board is None:
            board = self._board

        rowOrder = list(range(1, 8 + 1))
        if self._userColour == WHITE:
            rowOrder.reverse()

        colOrder = [colSum('A', j) for j in range(8)]
        if self._userColour == BLACK:
            colOrder.reverse()

        print()
        for i in range(8):
            print(rowOrder[i], end=' '*2)
            for j in range(8):
                print(board[i,j], end=' ')
            print()
        print(end='\n' + ' '*3)
        for j in range(8):
            print(colOrder[j], end=' ')
        print()
        print()

    def makeMove(self, x, y, board=None):
        if board is None:
            board = self._board

        pieceCopy = copy.copy(self.getPiece(*x, board=board))
        pieceCopy.position = y
        pieceCopy.moved = True

        board[self.getArrayIndexing(*x)] = ICONS[EMPTY]
        board[self.getArrayIndexing(*y)] = pieceCopy

    def makeMoves(self, *moves, board=None):
        for m in moves:
            self.makeMove(*m, board=board)

    def yieldMoves(self, colour=None, pieceType=None, board=None):
        '''
        Yields all standard moves that can be made with the optionally
        specified board state.

        Default parameters can be used to filter by colour and/or piece type.
        '''
        if board is None:
            board = self._board

        for x in self.yieldPieces(colour=colour, pieceType=pieceType, board=board):
            for move in x.yieldMoves(curBoard=board):
                yield move

    def enPassant(self, x, y, board=None):
        '''
        Performs en passant for the pawn at position x against the pawn at
        position y.

        NOTE: Assumes that self.yieldEnPassantPositions has been called
              to verify.
        '''
        yPieceObj = self.getPiece(*y, board=board)
        i = 1 if yPieceObj.colour == WHITE else -1
        yCol, yRow = y

        self.setEmpty(y, board=board)
        self.makeMove(x, (yCol, yRow - i), board=board)

    def yieldEnPassantPositions(self, colour, lastMove, board=None):
        '''
        Yields (attacking pawn position, defending pawn position) for all
        pawns that can en passant against the alleged pawn at the end
        position of lastMove that just moved two steps.

        There are a maximum of two positions but typically zero for an
        arbitrary lastMove.
        '''
        if lastMove is None:
            return

        if board is None:
            board = self._board

        x, y = lastMove
        yCol, yRow = y

        leftCol = colSum(yCol, -1)
        if ord(leftCol) >= ord('A'):
            z_left = (leftCol, yRow)
            if self.isEnPassantEligible(z_left, colour, lastMove, board=board):
                yield (z_left, y)

        rightCol = colSum(yCol, 1)
        if ord(rightCol) <= ord('H'):
            z_right = (rightCol, yRow)
            if self.isEnPassantEligible(z_right, colour, lastMove, board=board):
                yield (z_right, y)

    def isEnPassantEligible(self, x, colour, lastMove, board=None):
        '''
        Returns if position x holds a pawn that can en passant given the last move.
        '''
        if board is None:
            board = self._board

        xPieceObj = self.getPiece(*x, board=board)

        return (
            isPiece(xPieceObj, colour=colour, pieceType=PAWN)
            and xPieceObj.canEnPassant(lastMove, curBoard=board)
        )

    def castle(self, x, y, board=None):
        '''
        Performs a castle for the king at position x with the rook at
        position y.

        NOTE: Assumes that self.yieldCastlePositions has been called
              to verify.
        '''
        king_move, rook_move = self.getPiece(*x, board=board).get_castle(y, curBoard=board)
        self.makeMoves(king_move, rook_move, board=board)

    def yieldCastlePositions(self, colour, board=None):
        '''
        Yields (king position, rook position) for all rooks with which the
        king with the specified colour can castle.

        There are a maximum of two positions but typically zero.
        '''
        if board is None:
            board = self._board

        king = self.getKing(colour, board=board)
        king_col, king_row = king.position
        for x in [('A', king_row), ('H', king_row)]:
            if king.canCastle(x, curBoard=board):
                yield (king.position, x)

    # TODO: unused?
    def isCastleEligible(self, x, y, board=None):
        '''
        Returns if position x holds a king that can castle with an alleged
        ally rook at position y.
        '''
        if board is None:
            board = self._board

        xPieceObj = self.getPiece(*x, board=board)

        return (
            isPiece(xPieceObj, pieceType=KING)
            and xPieceObj.canCastle(y, curBoard=board)
        )

    def promotePawn(self, x, pieceType=QUEEN, board=None):
        '''
        Promotes the pawn at position x to a new ChessPiece, by default a queen.

        NOTE: Assumes that isPawnPromotionEligible was called to verify.
        '''
        pawn = self.getPiece(*x, board=board)
        self.setPiece(x, pawn.colour, pieceType, pawn.moved, board=board)

    def isPawnPromotionEligible(self, lastMove, board=None):
        '''
        Returns if the last move was from a pawn now eligible for promotion.
        '''
        if lastMove is None:
            return False

        if board is None:
            board = self._board

        _, x = lastMove
        xPieceObj = self.getPiece(*x, board=board)
        _, xRow = x

        return (
            isPiece(xPieceObj, pieceType=PAWN)
            and (xRow == 8 if xPieceObj.colour == WHITE else xRow == 1)
        )

    def setPiece(self, x, colour, pieceType, moved, board=None):
        '''
        Sets the piece at position x to a new chess piece object with the specified
        colour, piece type, and moved state.
        '''
        if board is None:
            board = self._board

        newPieceObj = copy.copy(self.iconToObject[ICONS[pieceType][colour]])
        newPieceObj.position = x
        newPieceObj.moved = moved
        board[self.getArrayIndexing(*x)] = newPieceObj

    def setEmpty(self, x, board=None):
        '''
        Sets the piece at position x to an empty char for the given board.
        '''
        if board is None:
            board = self._board

        board[self.getArrayIndexing(*x)] = ICONS[EMPTY]


class ChessPiece:
    def __init__(self, pieceType, colour, position, board, moved=False):
        self.pieceType = pieceType
        self.colour = colour
        self.position = position
        self.board = board
        self.moved = moved

    def __str__(self):
        return ICONS[self.pieceType][self.colour]

    def getOpponentColour(self):
        return not self.colour

    def isUnderAttack(self, curBoard=None):
        '''
        A piece other than the king is under attack if there are any standard
        moves from the opponent that land on the piece's position.
        '''
        for _, x in self.board.yieldMoves(colour=self.getOpponentColour(), board=curBoard):
            if x == self.position:
                return True
        return False

    def _yieldUnobstructedEndPositions(self, curBoard=None):
        '''
        For each unobstructed, standard move from self.position, yields the
        end position.

        This differs from yieldMoves in that it only returns the end position
        and doesn't check if the move would put the ally king in check.
        '''
        raise Exception('Instance of abstract-like class ChessPiece')

    def _isObstructed(self, pos, curBoard=None):
        '''
        Returns if the move from self.position to pos is obstructed, i.e. there
        is something other than a check consideration that is preventing the
        move from being made.

        e.g. pos isn't on the board, pos is the position of an ally piece, etc.
        '''
        return (
            not onBoard(*pos)
            or isPiece(self.board.getPiece(*pos, board=curBoard), colour=self.colour)
        )

    def yieldMoves(self, curBoard=None):
        '''
        Yields all standard moves from self.position.
        '''
        for pos in self._yieldUnobstructedEndPositions(curBoard=curBoard):
            if not self.wouldKingBeInCheck(pos, curBoard=curBoard):
                yield (self.position, pos)

    def wouldKingBeInCheck(self, pos, curBoard=None):
        '''
        Returns if the unobstructed move from self.position to pos would
        put the ally king in check.
        '''
        futureBoard = self.board.getCopy(board=curBoard)
        self.board.makeMove(self.position, pos, board=futureBoard)
        allyKing = self.board.getKing(colour=self.colour, board=futureBoard)

        return allyKing.isUnderAttack(curBoard=futureBoard)


class King(ChessPiece):
    def __init__(self, colour, position, board, moved=False):
        super().__init__(KING, colour, position, board, moved)

    def isUnderAttack(self, curBoard=None):
        '''
        A king is under attack (in check) if there are any unobstructed moves
        from the opponent that land on the king's position.
        '''
        for x in self.board.yieldPieces(colour=self.getOpponentColour(), board=curBoard):
            for end in x._yieldUnobstructedEndPositions(curBoard=curBoard):
                if end == self.position:
                    return True
        return False

    def _yieldUnobstructedEndPositions(self, curBoard=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions
        for a king.
        '''
        myCol, myRow = self.position

        leftCol = colSum(myCol, -1)
        for i in range(-1, 1 + 1):
            x = (leftCol, myRow + i)
            if not self._isObstructed(x, curBoard=curBoard):
                yield x

        x = (myCol, myRow - 1)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x
        x = (myCol, myRow + 1)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x

        rightCol = colSum(myCol, 1)
        for i in range(-1, 1 + 1):
            x = (rightCol, myRow + i)
            if not self._isObstructed(x, curBoard=curBoard):
                yield x

    def canCastle(self, x, curBoard=None):
        '''
        Returns if it is legal to castle with the alleged rook at position x.
        '''
        if self.moved or self.isUnderAttack(curBoard=curBoard):
            return False

        myCol, myRow = self.position
        if x not in {('A', myRow), ('H', myRow)}:
            return False

        xPieceObj = self.board.getPiece(*x, board=curBoard)
        if (
            not isPiece(xPieceObj, colour=self.colour, pieceType=ROOK)
            or xPieceObj.moved
            or self.board.arePiecesBetween(self.position, x, board=curBoard)
        ):
            return False

        xCol, xRow = x
        pass_through = [('D', myRow), ('C', myRow)] if xCol == 'A' else [('F', myRow), ('G', myRow)]
        for y in pass_through:
            if self.wouldKingBeInCheck(y, curBoard=curBoard):
                return False

        return True

    def get_castle(self, x, curBoard=None):
        '''
        Gets the moves that perform a castle with the rook at position x.

        NOTE: Assumes that canCastle has been called to verify.
        '''
        myCol, myRow = self.position
        xCol, xRow = x

        my_new_pos = ('C', myRow) if xCol < myCol else ('G', myRow)
        x_new = ('D', xRow) if xCol < myCol else ('F', xRow)

        my_move = (self.position, my_new_pos)
        rook_move = (x, x_new)

        return (my_move, rook_move)

    def isCheckmated(self, lastMove, curBoard=None):
        '''
        Returns if this king is checkmated, i.e. it is in check, and there
        are no standard moves or en passants that the player can make.
        '''
        for m in self.board.yieldMoves(colour=self.colour, board=curBoard):
            if m is not None:
                return False

        for m in self.board.yieldEnPassantPositions(self.colour, lastMove, board=curBoard):
            if m is not None:
                return False

        return self.isUnderAttack(curBoard=curBoard)


class Queen(ChessPiece):
    def __init__(self, colour, position, board, moved=False):
        super().__init__(QUEEN, colour, position, board, moved)
        self.rook = Rook(colour, None, board, moved=None)
        self.bishop = Bishop(colour, None, board, moved=None)

    def _yieldUnobstructedEndPositions(self, curBoard=None):
        return itertools.chain(
            self.rook._yieldUnobstructedEndPositions(curBoard=curBoard, myPos=self.position),
            self.bishop._yieldUnobstructedEndPositions(curBoard=curBoard, myPos=self.position)
        )


class Rook(ChessPiece):
    def __init__(self, colour, position, board, moved=False):
        super().__init__(ROOK, colour, position, board, moved)

    def _yieldUnobstructedEndPositions(self, curBoard=None, myPos=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions
        for a rook.

        For each direction, yields positions until the first obstruction, then
        yields the obstructing piece if it is of an opposing colour.
        '''
        if myPos is None:
            myPos = self.position

        myCol, myRow = myPos

        i = myRow + 1
        while i <= 8 and not isPiece(self.board.getPiece(myCol, i, board=curBoard)):
            yield (myCol, i)
            i += 1
        if i <= 8 and isPiece(self.board.getPiece(myCol, i, board=curBoard), colour=self.getOpponentColour()):
            yield (myCol, i)

        i = myRow - 1
        while i >= 1 and not isPiece(self.board.getPiece(myCol, i, board=curBoard)):
            yield (myCol, i)
            i -= 1
        if i >= 1 and isPiece(self.board.getPiece(myCol, i, board=curBoard), colour=self.getOpponentColour()):
            yield (myCol, i)

        j = colSum(myCol, -1)
        while ord(j) >= ord('A') and not isPiece(self.board.getPiece(j, myRow, board=curBoard)):
            yield (j, myRow)
            j = colSum(j, -1)
        if ord(j) >= ord('A') and isPiece(self.board.getPiece(j, myRow, board=curBoard), colour=self.getOpponentColour()):
            yield (j, myRow)

        j = colSum(myCol, 1)
        while ord(j) <= ord('H') and not isPiece(self.board.getPiece(j, myRow, board=curBoard)):
            yield (j, myRow)
            j = colSum(j, 1)
        if ord(j) <= ord('H') and isPiece(self.board.getPiece(j, myRow, board=curBoard), colour=self.getOpponentColour()):
            yield (j, myRow)


class Bishop(ChessPiece):
    def __init__(self, colour, position, board, moved=False):
        super().__init__(BISHOP, colour, position, board, moved)

    def _yieldUnobstructedEndPositions(self, curBoard=None, myPos=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions
        for a bishop.

        For each diagonal direction, yields positions until the first
        obstruction, then yields the obstructing piece if it is of an
        opposing colour.
        '''
        if myPos is None:
            myPos = self.position

        myCol, myRow = myPos

        j_left = ord(myCol) - ord('A')
        j_right = ord('H') - ord(myCol)
        i_bottom = myRow - 1
        i_top = 8 - myRow

        i = 1
        while (
            i <= min(j_left, i_top)
            and not isPiece(self.board.getPiece(colSum(myCol, -i), myRow + i, board=curBoard))
        ):
            yield (colSum(myCol, -i), myRow + i)
            i += 1
        if (
            i <= min(j_left, i_top)
            and isPiece(self.board.getPiece(colSum(myCol, -i), myRow + i, board=curBoard), colour=self.getOpponentColour())
        ):
            yield (colSum(myCol, -i), myRow + i)

        i = 1
        while (
            i <= min(j_left, i_bottom)
            and not isPiece(self.board.getPiece(colSum(myCol, -i), myRow - i, board=curBoard))
        ):
            yield (colSum(myCol, -i), myRow - i)
            i += 1
        if (
            i <= min(j_left, i_bottom)
            and isPiece(self.board.getPiece(colSum(myCol, -i), myRow - i, board=curBoard), colour=self.getOpponentColour())
        ):
            yield (colSum(myCol, -i), myRow - i)

        i = 1
        while (
            i <= min(j_right, i_top)
            and not isPiece(self.board.getPiece(colSum(myCol, i), myRow + i, board=curBoard))
        ):
            yield (colSum(myCol, i), myRow + i)
            i += 1
        if (
            i <= min(j_right, i_top)
            and isPiece(self.board.getPiece(colSum(myCol, i), myRow + i, board=curBoard), colour=self.getOpponentColour())
        ):
            yield (colSum(myCol, i), myRow + i)

        i = 1
        while (
            i <= min(j_right, i_bottom)
            and not isPiece(self.board.getPiece(colSum(myCol, i), myRow - i, board=curBoard))
        ):
            yield (colSum(myCol, i), myRow - i)
            i += 1
        if (
            i <= min(j_right, i_bottom)
            and isPiece(self.board.getPiece(colSum(myCol, i), myRow - i, board=curBoard), colour=self.getOpponentColour())
        ):
            yield (colSum(myCol, i), myRow - i)


class Knight(ChessPiece):
    def __init__(self, colour, position, board, moved=False):
        super().__init__(KNIGHT, colour, position, board, moved)

    def _yieldUnobstructedEndPositions(self, curBoard=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions
        for a knight.
        '''
        myCol, myRow = self.position

        i = myRow + 2
        j = colSum(myCol, -1)
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x
        j = colSum(myCol, 1)
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x

        i = myRow - 2
        j = colSum(myCol, -1)
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x
        j = colSum(myCol, 1)
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x

        j = colSum(myCol, -2)
        i = myRow - 1
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x
        i = myRow + 1
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x

        j = colSum(myCol, 2)
        i = myRow - 1
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x
        i = myRow + 1
        x = (j, i)
        if not self._isObstructed(x, curBoard=curBoard):
            yield x


class Pawn(ChessPiece):
    def __init__(self, colour, position, board, moved=False):
        super().__init__(PAWN, colour, position, board, moved)

    def isUnderAttack(self, lastMove, curBoard=None):
        '''
        A pawn can also be under attack by en passant if it just made a
        two-step move.
        '''
        _, x = lastMove

        if x != self.position:
            return False

        for m in self.board.yieldEnPassantPositions(self.getOpponentColour(), lastMove, board=curBoard):
            if m is not None:
                return True

        return super().isUnderAttack(curBoard=curBoard)

    def _yieldUnobstructedEndPositions(self, curBoard=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions
        for a pawn due to how many pawns there are in an exponentially large
        search tree.
        '''
        myCol, myRow = self.position
        i_step = 1 if self.colour == WHITE else -1

        i = myRow + i_step

        j = colSum(myCol, -1)
        x = (j, i)
        if onBoard(*x) and isPiece(self.board.getPiece(*x, board=curBoard), colour=self.getOpponentColour()):
            yield x

        j = colSum(myCol, 1)
        x = (j, i)
        if onBoard(*x) and isPiece(self.board.getPiece(*x, board=curBoard), colour=self.getOpponentColour()):
            yield x

        x = (myCol, i)
        if onBoard(*x) and not isPiece(self.board.getPiece(*x, board=curBoard)):
            yield x

            if not self.moved:
                i_2 = i + i_step
                x = (myCol, i_2)
                if not isPiece(self.board.getPiece(*x, board=curBoard)):
                    yield x

    def canEnPassant(self, lastMove, curBoard=None):
        '''
        Returns if en passant is legal for this piece given the opponent's
        last move.
        '''
        x, y = lastMove
        xCol, xRow = x
        yCol, yRow = y

        myCol, myRow = self.position
        yPieceObj = self.board.getPiece(*y, board=curBoard)

        if not (
            isPiece(yPieceObj, colour=self.getOpponentColour(), pieceType=PAWN)
            and abs(xRow - yRow) == 2
            and myRow == yRow
            and abs(ord(myCol) - ord(yCol)) == 1
        ):
            return False

        futureBoard = self.board.getCopy(board=curBoard)
        self.board.enPassant(self.position, y, board=futureBoard)
        allyKing = self.board.getKing(colour=self.colour, board=futureBoard)

        return not allyKing.isUnderAttack(curBoard=futureBoard)
