# Author: Bryce Van Camp
# Project: MateFinder
# File: chess_piece.py
# Description: ChessPiece classes


import copy


_ICONS = (
    ('♚', '♔'),
    ('♛', '♕'),
    ('♜', '♖'),
    ('♝', '♗'),
    ('♞', '♘'),
    ('♟', '♙')
)


def on_chess_board(file, rank):
    '''
    Returns if the file and rank exist on an 8x8 board.

    Valid params range from ('A', 1) to ('H', 8)
    '''
    return ord('A') <= ord(file) <= ord('H') and 1 <= rank <= 8


def file_add(file, j):
    '''
    Simplifies adding to a chess file.

    e.g. returns 'B' for input ('A', 1)
    '''
    return chr(ord(file) + j)


def get_new_piece(piece_type, color, pos, board, moved=False):
    '''
    Returns a new chess piece of specified type and color with attributes.
    '''
    new_piece = None
    if piece_type == KING:
        new_piece = King(color, pos, board, moved)
    elif piece_type == QUEEN:
        new_piece = Queen(color, pos, board, moved)
    elif piece_type == ROOK:
        new_piece = Rook(color, pos, board, moved)
    elif piece_type == BISHOP:
        new_piece = Bishop(color, pos, board, moved)
    elif piece_type == KNIGHT:
        new_piece = Knight(color, pos, board, moved)
    elif piece_type == PAWN:
        new_piece = Pawn(color, pos, board, moved)
    return new_piece


def is_piece(x, color=None, piece_type=None):
    '''
    Returns if x is a ChessPiece with optional color and piece type params.
    '''
    return (
        isinstance(x, ChessPiece)
        and (True if color is None else color == x.color)
        and (True if piece_type is None else piece_type == x.piece_type)
    )


class ChessPiece:
    def __init__(self, piece_type, color, pos, board, moved=False):
        self.piece_type = piece_type
        self.color = color
        self.pos = pos
        self.board = board
        self.moved = moved

    def __str__(self):
        return _ICONS[self.piece_type][self.color]

    def get_opp_color(self):
        return not self.color

    def is_under_attack(self):
        '''
        A non-king piece is under attack if the opponent can make a move that 
        would land on the piece's position and not put their own king in check.
        '''
        # TODO: need to check for castle moves? currently only check standard 
        #       moves, pawn checks for en passant
        for _, y in self.board.yield_std_moves(color=self.get_opp_color()):
            if y == self.pos:
                return True
        return False

    def _is_open(self, pos):
        '''
        Returns if position is on chess board and not occupied by an ally piece.
        '''
        return on_chess_board(*pos) and not is_piece(self.board.getPiece(*pos), color=self.color)

    def _yield_open_pos(self):
        '''
        Yields all open positions the piece can move to from self.pos.
        
        NOTE: This method does NOT check if ally king would be in check after 
              the move and only returns the end position. yield_std_moves calls
              this method and does do the aforementioned.
        '''
        raise Exception('Instance of abstract-like class ChessPiece')

    def would_put_king_in_check(self, pos):
        '''
        Returns if the move from self.pos to pos would put the ally king in 
        check.
        '''
        # TODO: make move, store if king under attack, then reverse the move
        # TODO: might be a faster way? Could I check if king would be under 
        #       attack without moving and without checking all opponent moves?
        pass

    def yield_std_moves(self):
        '''
        Yields all standard (i.e. everything except castle and en passant) 
        moves that can be made by this piece at self.pos.
        '''
        for cur_pos in self._yield_open_pos():
            if not self.would_put_king_in_check(cur_pos):
                yield (self.pos, cur_pos)


class King(ChessPiece):
    def __init__(self, color, pos, board, moved=False):
        super().__init__(KING, color, pos, board, moved)

    def is_under_attack(self):
        '''
        A king piece is under attack (in check) if any opponent piece targets it.
        
        NOTE: It's still a check even if the targeting move would put the 
              opponent's king in check, so we do not verify that.
        '''
        for cur_piece in self.board.yield_pieces(color=self.get_opp_color()):
            for open_pos in cur_piece._yield_open_pos():
                if open_pos == self.pos:
                    return True
        return False

    def _yield_open_pos(self):
        # TODO: Don't we need to check if king would land too close to opponent king?
        my_file, my_rank = self.pos

        cur_pos = (my_file, my_rank - 1)
        if self._is_open(cur_pos):
            yield cur_pos
        cur_pos = (my_file, my_rank + 1)
        if self._is_open(cur_pos):
            yield cur_pos

        left_file = file_add(my_file, -1)
        right_file = file_add(my_file, 1)
        for i in range(-1, 1 + 1):
            cur_pos = (left_file, my_rank + i)
            if self._is_open(cur_pos):
                yield cur_pos
            cur_pos = (right_file, my_rank + i)
            if self._is_open(cur_pos):
                yield cur_pos

    def can_castle(self, pos):
        '''
        Returns if it is legal to castle with the alleged rook at position pos.
        '''
        if self.moved or self.is_under_attack():
            return False

        my_file, my_rank = self.pos
        if pos not in {('A', my_rank), ('H', my_rank)}:
            return False

        rook = self.board.get_piece(*pos)
        if (
            not is_piece(rook, color=self.color, piece_type=ROOK)
            or rook.moved
            or 

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
