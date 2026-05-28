# Author: Bryce Van Camp
# Project: MateFinder
# File: pieces.py
# Description: Piece classes


import itertools

from enums import PieceType, Color, MoveType, File
from move import Move
from peekable import Peekable
import coordinates


TYPE_MAP = {
    'K': King, 'k': King,
    'Q': Queen, 'q': Queen,
    'R': Rook, 'r': Rook,
    'B': Bishop, 'b': Bishop,
    'N': Knight, 'n': Knight,
    'P': Pawn, 'p': Pawn
}


INDEX_MAP = {
    'K': PieceType.KING, 'k': PieceType.KING,
    'Q': PieceType.QUEEN, 'q': PieceType.QUEEN,
    'R': PieceType.ROOK, 'r': PieceType.ROOK,
    'B': PieceType.BISHOP, 'b': PieceType.BISHOP,
    'N': PieceType.KNIGHT, 'n': PieceType.KNIGHT,
    'P': PieceType.PAWN, 'p': PieceType.PAWN
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
        self.type_index = INDEX_MAP[letter]

    def __str__(self):
        return self.letter

    def _is_open(self, square):
        '''
        Returns if square is on board and not occupied by an ally piece.
        '''
        return coordinates.on_board(*square) and not self.board.has_piece(square, color=self.color)

    def iter_psuedo_legal_end_squares(self):
        '''
        Iterates all pseudo-legal (doesn't verify if ally king would be in
        check after move), standard (i.e. non-castle, non-en passant) end
        squares for this piece from its current square.
        '''
        raise Exception('Instance of abstract-like class Piece')

    def get_standard_move(self, end_square):
        '''
        Returns a standard (non-castle, non-en passant) move given the end square.
        '''
        return Move(self.board, MoveType.STD, self.square, end_square, tgt_piece=self.board.get_piece(end_square))

    def iter_my_standard_moves(self):
        '''
        Iterates all legal standard (i.e. non-castle, non-en passant) moves for
        this piece from its current square.
        '''
        for end_square in self.iter_psuedo_legal_end_squares():
            m = self.get_standard_move(end_square)
            if not self.board.would_put_king_in_check(m):
                yield m

    def is_being_attacked(self):
        '''
        A non-king piece is being attacked if the opponent can make a move that 
        would land on the piece's square and not put their own king in check.
        
        NOTE: O(n*m)
        '''
        return Peekable(filter(lambda m: m.tgt_piece is self, self.board.iter_moves(move_type=MoveType.STD))).has_next()


class King(Piece):
    file_steps = [-1, 0, 1, -1, 1, -1, 0, 1]
    rank_steps = [1, 1, 1, 0, 0, -1, -1, -1]

    def iter_psuedo_legal_end_squares(self):
        st_file, st_rank = self.square
        for file_step, rank_step in zip(King.file_steps, King.rank_steps):
            end_square = st_file + file_step, st_rank + rank_step
            if self._is_open(end_square):
                yield end_square

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
            for square in piece.iter_psuedo_legal_end_squares():
                if square == tgt_square:
                    return True
        return False

    def is_checkmated(self):
        '''
        Returns if this king is checkmated, i.e. it is in check, and there
        are no standard moves or en passants that the player can make.
        '''
        return self.is_being_attacked() and not Peekable(self.board.iter_moves(move_type=MoveType.STD | MoveType.EN_PASSANT)).has_next()


class MajorPiece(Piece):
    pass


class Queen(MajorPiece):
    def __init__(self, letter, square, board):
        super().__init__(letter, square, board)
        self.rook = Rook(letter, None, board)
        self.bishop = Bishop(letter, None, board)

    def iter_psuedo_legal_end_squares(self):
        self.rook.square = self.square
        self.bishop.square = self.square
        return itertools.chain(self.rook.iter_psuedo_legal_end_squares(), self.bishop.iter_psuedo_legal_end_squares())


class Rook(MajorPiece):
    def iter_psuedo_legal_end_squares(self):
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
    def iter_psuedo_legal_end_squares(self):
        '''
        For each ordinal direction, yields squares until the first obstruction.

        If the first obstruction is a piece of the opposing color, also 
        yield that square.
        '''
        st_file, st_rank = self.square

        def iter_diagonal(end_file, end_rank):
            '''
            NOTE: This func is essentially rook's iter_horizontal and iter_vertical combined.
            '''
            # Base case
            if st_file == end_file or st_rank == end_rank:
                return

            # Traverse right if st_file < end_file else left, and up if st_rank < end_rank else down
            file_step = 1 if st_file < end_file else -1
            rank_step = 1 if st_rank < end_rank else -1
            cur_file = st_file + file_step
            cur_rank = st_rank + rank_step
            cur_square = cur_file, cur_rank

            # Iterate until we reach an end of the board or until a piece is encountered
            while cur_file != end_file and cur_rank != end_rank and not self.board.has_piece(cur_square):
                yield cur_square
                cur_file += file_step
                cur_rank += rank_step
                cur_square = cur_file, cur_rank

            # We have reached an end of the board and/or a piece; yield if not ally piece
            if not self.board.has_piece(cur_square, color=self.color):
                yield cur_square

        # Up-left, up-right, down-left, down-right
        for end_square in itertools.chain(iter_diagonal(File.A, 8), iter_diagonal(File.H, 8), iter_diagonal(File.A, 1), iter_diagonal(File.H, 1)):
            yield end_square


class Knight(MinorPiece):
    file_steps = [-2, -1, 1, 2, 2, 1, -1, -2]
    rank_steps = [1, 2, 2, 1, -1, -2, -2, -1]

    def iter_psuedo_legal_end_squares(self):
        st_file, st_rank = self.square
        for file_step, rank_step in zip(Knight.file_steps, Knight.rank_steps):
            end_square = st_file + file_step, st_rank + rank_step
            if self._is_open(end_square):
                yield end_square


class Pawn(Piece):
    def __init__(self, letter, square, board):
        super().__init__(letter, square, board)
        self.promotion_letters = ['Q', 'R', 'B', 'N'] if self.color == Color.WHITE else ['q', 'r', 'b', 'n']

    @property
    def has_moved(self):
        '''
        A pawn has moved if and only if it is not on its starting rank.
        '''
        _, rank = self.square
        return rank == 2 if self.color == Color.WHITE else rank == 7

    def is_promotion_square(self, square):
        _, rank = self.square
        return rank == 8 if self.color == Color.WHITE else rank == 1

    def is_capture_square(self, square):
        return coordinates.on_board(*square) and self.board.has_piece(square, color=self.opp_color)

    def iter_psuedo_legal_end_squares(self):
        '''
        NOTE: Does not yield possible en passant moves. Go to Board.iter_en_passant_moves
        '''
        st_file, st_rank = self.square
        rank_step = 1 if self.color == Color.WHITE else -1
        end_rank = st_rank + rank_step

        # Capture left
        end_square = st_file - 1, end_rank
        if self.is_capture_square(end_square):
            yield end_square

        # Capture right
        end_square = st_file + 1, end_rank
        if self.is_capture_square(end_square):
            yield end_square

        # Advance 1
        end_square = st_file, end_rank
        if not self.board.has_piece(end_square):
            yield end_square

            # Advance 2
            if not self.has_moved:
                end_rank += rank_step
                end_square = st_file, end_rank
                if not self.board.has_piece(end_square):
                    yield end_square

    def iter_my_standard_moves(self):
        '''
        Iterates all legal standard (i.e. non-castle, non-en passant) moves for
        this pawn from its current square.

        If the move triggers a pawn promotion, 4 moves (1 for each possible promotion) will be generated.
        '''
        for end_square in self.iter_psuedo_legal_end_squares():
            # If pawn promotion triggered
            if self.is_promotion_square(end_square):
                # Yield 4 moves, 1 for each possible promotion
                for pl in self.promotion_letters:
                    m = self.get_standard_move(end_square)
                    m.promotion_letter = pl
                    if not self.board.would_put_king_in_check(m):
                        yield m
            # Else yield 1 move as usual
            else:
                m = self.get_standard_move(end_square)
                if not self.board.would_put_king_in_check(m):
                    yield m

    def is_being_attacked(self):
        '''
        A pawn can also be attacked by en passant if it just made a
        two-step move.
        '''
        return Peekable(filter(lambda m: m.tgt_piece is self, self.board.iter_moves(move_type=MoveType.EN_PASSANT))).has_next() or super().is_being_attacked()
