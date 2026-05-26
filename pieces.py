# Author: Bryce Van Camp
# Project: MateFinder
# File: pieces.py
# Description: Piece classes


import itertools

from enums import Color, MoveType, File
from move import Move
from peekable import Peekable
import coordinates


TYPE_MAP = {
    'K': King
    'Q': Queen
    'R': Rook
    'B': Bishop
    'N': Knight
    'P': Pawn
}


INDEX_MAP = {
    'K': 0,
    'Q': 1,
    'R': 2,
    'B': 3,
    'N': 4,
    'P': 5
}


def get_color(letter):
    return Color.WHITE if letter.isupper() else Color.BLACK


class Piece:
    def __init__(self, letter, square, board):
        self.letter = letter
        self.square = square
        self.board = board
        self.color = get_color(letter)
        self.opp_color = self.color ^ 1

    def __str__(self):
        return self.letter

    def _is_open(self, square):
        '''
        Returns if square is on board and not occupied by an ally piece.
        '''
        return coordinates.on_board(*square) and not self.board.has_piece(square, color=self.color)

    def is_being_attacked(self):
        '''
        A non-king piece is being attacked if the opponent can make a move that 
        would land on the piece's square and not put their own king in check.
        
        NOTE: O(n*m)
        '''
        return Peekable(filter(lambda m: m.tgt_piece is self, self.board.iter_moves(self.opp_color, move_type=MoveType.STD))).has_next()

    def _iter_psuedo_legal_end_squares(self):
        '''
        Iterates all pseudo-legal (doesn't verify if ally king would be in
        check after move), standard (i.e. non-castle, non-en passant) end
        squares for this piece from its current square.
        '''
        raise Exception('Instance of abstract-like class Piece')

    def iter_my_standard_moves(self):
        '''
        Iterates all legal standard (i.e. non-castle, non-en passant) moves for
        this piece from its current square.
        '''
        for end_square in self._iter_psuedo_legal_end_squares():
            m = Move(self.board, MoveType.STD, self.square, end_square, tgt_piece=self.board.get_piece(end_square))
            if not self.board.would_put_king_in_check(m):
                yield m


class King(Piece):
    def is_being_attacked(self, tgt_square=None):
        '''
        A king piece is being attacked (in check) if any opponent piece targets it.

        NOTE: Same as super class except we do not call would_king_be_in_check.
        
        square: Optional param used for checking if king would be in check at any 
             point in castling.
        '''
        if tgt_square is None:
            tgt_square = self.square

        for piece in self.board.iter_pieces(self.opp_color):
            for square in piece._iter_psuedo_legal_end_squares():
                if square == tgt_square:
                    return True
        return False

    def _iter_psuedo_legal_end_squares(self):
        st_file, st_rank = self.square

        if self._is_open(st_file, st_rank - 1):
            yield st_file, st_rank - 1
        if self._is_open(st_file, st_rank + 1):
            yield st_file, st_rank + 1

        left_file = coordinates.shift_file(st_file, -1)
        right_file = coordinates.shift_file(st_file, 1)
        for i in range(-1, 1 + 1):
            if self._is_open(left_file, st_rank + i):
                yield (left_file, st_rank + i)
            if self._is_open(right_file, st_rank + i):
                yield (right_file, st_rank + i)

    def is_checkmated(self):
        '''
        Returns if this king is checkmated, i.e. it is in check, and there
        are no standard moves or en passants that the player can make.
        '''
        if not self.is_being_attacked():
            return False

        return not Peekable(self.board.iter_moves(self.color, move_type=MoveType.STD | MoveType.EN_PASSANT)).has_next()


class MajorPiece(Piece):
    pass


class Queen(MajorPiece):
    def __init__(self, letter, square):
        super().__init__(letter, square)
        self.rook = Rook(letter, None)
        self.bishop = Bishop(letter, None)

    def _iter_psuedo_legal_end_squares(self):
        self.rook.square = self.square
        self.bishop.square = self.square
        return itertools.chain(self.rook._iter_psuedo_legal_end_squares(), self.bishop._iter_psuedo_legal_end_squares())


class Rook(MajorPiece):
    def _iter_psuedo_legal_end_squares(self):
        '''
        TODO: test

        For each cardinal direction, yields squares until the first obstruction.

        If the first obstruction is a piece of the opposing color, also 
        yield that square.
        '''
        st_file, st_rank = self.square

        # ←→
        def iter_horizontal(end_file):
            # Base case
            if st_file == end_file:
                return

            # Traverse right if st_file < end_file else left
            step = 1 if st_file < end_file else -1
            cur_file = st_file + step
            cur_square = cur_file, st_rank

            # Iterate until end_file or until a piece is encountered
            while cur_file != end_file and not self.board.has_piece(cur_square):
                yield cur_square
                cur_file += step
                cur_square = cur_file, st_rank

            # We have reached end_file and/or a piece; yield if not ally piece
            if not self.board.has_piece(cur_square, color=self.color):
                yield cur_square

        # ↓↑
        def iter_vertical(end_rank):
            # Base case
            if st_rank == end_rank:
                return

            # Traverse up if st_rank < end_rank else down
            step = 1 if st_rank < end_rank else -1
            cur_rank = st_rank + step
            cur_square = st_file, cur_rank

            # Iterate until end_rank or until a piece is encountered
            while cur_rank != end_rank and not self.board.has_piece(cur_square):
                yield cur_square
                cur_rank += step
                cur_square = st_file, cur_rank

            # We have reached end_rank and/or a piece; yield if not ally piece
            if not self.board.has_piece(cur_square, color=self.color):
                yield cur_square

        # ← → ↓ ↑
        for end_square in itertools.chain(iter_horizontal(File.A), iter_horizontal(File.H), iter_vertical(1), iter_vertical(8)):
            yield end_square


class MinorPiece(Piece):
    pass


class Bishop(MinorPiece):
    def _iter_psuedo_legal_end_squares(self):
        '''
        For each ordinal direction, yields squares until the first obstruction.
        
        If the first obstruction is a piece of the opposing color, also 
        yield that square.
        '''
        st_file, st_rank = self.square

        def iter_diagonal(max_dist, file_sign=1, rank_sign=1):
            for cur_dist in range(1, max_dist):
                end_square = coordinates.shift_file(st_file, file_sign * cur_dist), st_rank + rank_sign * cur_dist
                tgt_piece = self.board.get_piece(end_square)
                if tgt_piece is None:
                    yield end_square
                else:
                    if tgt_piece.color == self.opp_color:
                        yield end_square
                    break

        # max number of open squares in each cardinal direction
        max_left = ord(st_file) - ord(File.A)
        max_right = ord(File.H) - ord(st_file)
        max_up = 8 - st_rank
        max_down = st_rank - 1

        # up-left, up-right, down-left, down-right
        for end_square in itertools.chain(
            iter_diagonal(min(max_left, max_up), file_sign=-1),
            iter_diagonal(min(max_right, max_up)),
            iter_diagonal(min(max_left, max_down), file_sign=-1, rank_sign=-1),
            iter_diagonal(min(max_right, max_down), rank_sign=-1)
        ):
            yield end_square


class Knight(MinorPiece):
    def _iter_psuedo_legal_end_squares(self):
        st_file, st_rank = self.square

        def get_L(long_rank=True, file_sign=1, rank_sign=1):
            file_dist = 1 if long_rank else 2
            rank_dist = 2 if long_rank else 1
            end_file = coordinates.shift_file(st_file, file_sign * file_dist)
            end_rank = st_rank + (rank_sign * rank_dist)
            if self._is_open(end_file, end_rank):
                return (end_file, end_rank)

        def yield_all_L():
            # up-LEFT
            yield get_L(long_rank=False, file_sign=-1)
            # UP-left
            yield get_L(long_rank=True, file_sign=-1)
            # UP-right
            yield get_L(long_rank=True)
            # up-RIGHT
            yield get_L(long_rank=False)
            # down-RIGHT
            yield get_L(long_rank=False, rank_sign=-1)
            # DOWN-right
            yield get_L(long_rank=True, rank_sign=-1)
            # DOWN-left
            yield get_L(long_rank=True, file_sign=-1, rank_sign=-1)
            # down-LEFT
            yield get_L(long_rank=False, file_sign=-1, rank_sign=-1)

        # TODO: have to do this to avoid yielding None, but I don't like it
        for L in yield_all_L():
            if L: yield L


class Pawn(Piece):
    @property
    def has_moved(self):
        '''
        A pawn has moved if and only if it is not on its starting rank.
        '''
        _, rank = self.square
        if self.color == Color.WHITE:
            return rank == 2
        else:
            return rank == 7

    def is_promotion_square(self, square):
        _, rank = self.square
        if self.color == Color.WHITE:
            return rank == 8
        else:
            return rank == 1

    def is_being_attacked(self):
        '''
        A pawn can also be being attacked by en passant if it just made a
        two-step move.
        '''
        for m in self.board.iter_moves(self.opp_color, move_type=MoveType.EN_PASSANT):
            if m.tgt_piece is self:
                return True

        return super().is_being_attacked()

    def _iter_psuedo_legal_end_squares(self):
        '''
        NOTE: Does not yield possible en passant moves. Go to Board.iter_en_passant_moves
        '''
        st_file, st_rank = self.square
        rank_step = 1 if self.color == Color.WHITE else -1
        end_rank = st_rank + rank_step

        def get_capture_square(file_step):
            capture_file = coordinates.shift_file(st_file, file_step)
            capture_square = (capture_file, end_rank)
            if coordinates.on_board(*capture_square) and self.board.has_piece(capture_square, color=self.opp_color):
                return capture_square

        # capture left
        capture_square = get_capture_square(file_step=-1)
        if capture_square is not None:
            yield capture_square

        # capture right
        capture_square = get_capture_square(file_step=1)
        if capture_square is not None:
            yield capture_square

        # move up 1
        end_square = (st_file, end_rank)
        if not self.board.has_piece(end_square):
            yield end_square

            # move up 2
            if not self.has_moved:
                end_rank += rank_step
                end_square = (st_file, end_rank)
                if not self.board.has_piece(end_square):
                    yield end_square

    def iter_my_standard_moves(self):
        '''
        Iterates all legal standard (i.e. non-castle, non-en passant) moves for
        this pawn from its current square.

        If the move triggers a pawn promotion, 4 moves (1 for each possible promotion) will be generated.
        '''
        for end_square in self._iter_psuedo_legal_end_squares():
            # If pawn promotion triggered
            if self.is_promotion_square(end_square):
                # Yield 4 moves, 1 for each possible promotion
                promotion_letters = ['Q', 'R', 'B', 'N'] if self.color == Color.WHITE else ['q', 'r', 'b', 'n']
                for pl in promotion_letters:
                    m = Move(self.board, MoveType.STD, self.square, end_square, tgt_piece=self.board.get_piece(end_square), promotion_letter=pl)
                    if not self.board.would_put_king_in_check(m):
                        yield m
            # Else yield 1 move as usual
            else:
                m = Move(self.board, MoveType.STD, self.square, end_square, tgt_piece=self.board.get_piece(end_square))
                if not self.board.would_put_king_in_check(m):
                    yield m
