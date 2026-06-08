# Author: Bryce Van Camp
# Project: MateFinder
# File: board.py
# Description: Board data structure


import itertools
import numpy as np

from enums import *
from move import Move
from peekable import Peekable
import coordinates
import fen
import piece_squares
import pieces


class Board:
    def __init__(self, fen_class, user_color):
        self.fen_class = fen_class
        self.user_color = user_color

        self._arr = np.array([[None] * 8 for _ in range(8)])
        self.piece_squares = piece_squares.PieceSquares()
        for i in range(8):
            for j in range(8):
                letter = self.fen_class.piece_placement[i,j]
                if letter is None:
                    continue
                square = coordinates.index_to_square(i, j)
                piece = pieces.TYPE_MAP[letter](letter, square, self)
                self._arr[i,j] = piece
                self.piece_squares.add(square, piece.color, piece.type_index)

        self.move_stack = []
        self.move_it = Peekable(self.iter_moves()) # TODO: remove color param

    def get_piece(self, square):
        return self._arr[coordinates.square_to_index(square)]

    def has_piece(self, square, color=None):
        '''
        Returns if square has a piece on it, with optional color specifier.
        '''
        piece = self.get_piece(square)
        if color is None:
            return piece is not None
        else:
            return piece is not None and piece.color == color

    def get_king(self, color):
        return self.get_piece(next(iter(self.piece_squares[color, PieceType.KING)))

    def get_active_king(self):
        return self.get_piece(next(iter(self.piece_squares[self.fen_class.active_color, PieceType.KING])))

    def iter_pieces(self, color=None):
        '''
        Iterates all pieces on the board with optional color param.
        '''
        if color != Color.WHITE:
            for square in self.piece_squares[Color.BLACK]:
                yield self.get_piece(square)
        
        if color != Color.BLACK:
            for square in self.piece_squares[Color.WHITE]:
                yield self.get_piece(square)

    def insufficient_material(self):
        '''
        Returns if neither side has the sufficient material to force a checkmate.
        '''
        def has_minor_piece(color):
            return len(self.piece_squares[color, PieceType.BISHOP]) + len(self.piece_squares[color, PieceType.KNIGHT]) > 0

        def has_two_knights(color):
            return len(self.piece_squares[color, PieceType.KNIGHT]) == 2

        num_black = len(self.piece_squares[Color.BLACK])
        num_white = len(self.piece_squares[Color.WHITE])

        # exit quickly if piece count too large to possibly have insufficient material
        min_num, max_num = coordinates.minmax(num_black, num_white)
        if max_num > 3 or (max_num == 3 and min_num > 1):
            return False

        # King vs king
        elif num_black == 1 and num_white == 1:
            return True

        # King + minor piece vs king
        elif num_black == 2 and num_white == 1:
            return has_minor_piece(Color.BLACK)
        elif num_black == 1 and num_white == 2:
            return has_minor_piece(Color.WHITE)

        # King + minor piece vs king + minor piece
        elif num_black == 2 and num_white == 2:
            return has_minor_piece(Color.BLACK) and has_minor_piece(Color.WHITE)

        # King + two knights vs king
        elif num_black == 3 and num_white == 1:
            return has_two_knights(Color.BLACK)
        elif num_black == 1 and num_white == 3:
            return has_two_knights(Color.WHITE)

        else:
            raise ValueError('Insufficient material reached else statement!')

    def remove_piece(self, piece):
        '''
        Removes piece from the board and updates data structures.
        '''
        self.piece_squares.remove(piece.square, piece.letter)
        i, j = coordinates.square_to_index(piece.square)
        self.fen_class.piece_placement[i,j] = None
        self._arr[i,j] = None

    def put_piece(self, piece, square):
        '''
        Puts piece on specified board square and updates data structures.
        '''
        piece.square = square
        self.piece_squares.add(square, piece.letter)
        i, j = coordinates.square_to_index(square)
        self.fen_class.piece_placement[i,j] = piece.letter
        self._arr[i,j] = piece

    def _move_piece(self, piece, square):
        '''
        Moves piece from its current square to the specified board square.
        '''
        self.remove_piece(piece)
        self.put_piece(piece, square)

    def make_move(self, m):
        '''
        Performs a complete move of any type.

        NOTE: Assumes that the move is legal.
        '''
        # Remove target piece first if there is one
        if m.tgt_piece is not None:
            self.remove_piece(m.tgt_piece)

        # Move king if move is a castle
        elif m.m_type == MoveType.CASTLE:
            # moving_piece field is rook
            r_file, _ = m.moving_piece.square

            # Move king
            king = self.get_active_king()
            k_file, k_rank = king.square
            k_end_square = coordinates.shift_file(k_file, 2 if r_file == File.H else -2), k_rank
            self._move_piece(king, k_end_square)

        # Move piece
        if len(m.promotion_letter) == 0:
            self._move_piece(m.moving_piece, m.end_square)
        # Pawn promotion case
        else:
            self.remove_piece(m.moving_piece)
            upgrade = pieces.TYPE_MAP[m.promotion_letter](m.promotion_letter, m.end_square, self)
            self.put_piece(upgrade, m.end_square)

        # NOTE: Active color is updated here
        self.fen_class.update(m)

        self.move_it = Peekable(self.iter_moves())

        # Add check or checkmate char to algebraic notation if applicable
        if m.algebraic_notation[-1] not in ['+', '#'] and self.get_active_king().is_being_attacked:
            m.algebraic_notation += '+' if self.move_it.has_next() else '#'

        self.move_stack.append(m)

    def reverse_move(self):
        '''
        Pops and reverses the last move in the stack.

        NOTE: Assumes there is a move to reverse
        '''
        m = self.move_stack.pop()

        # Move back piece
        if len(m.promotion_letter) == 0:
            self._move_piece(m.moving_piece, m.st_square)
        # Or revert pawn promotion and put pawn on start square
        else:
            self.remove_piece(self.get_piece(m.end_square))
            self.put_piece(m.moving_piece, m.st_square)

        # If a piece was taken, place it back on its square
        if m.tgt_piece is not None:
            self.put_piece(m.tgt_piece, m.tgt_piece.square)
        # Move king back if move was a castle
        elif m.m_type == MoveType.CASTLE:
            k_st_square = File.E, m.moving_piece.square[1]
            self._move_piece(self.get_king(m.moving_piece.color), k_st_square)

        # NOTE: Active color is reverted here
        self.fen_class.revert()

        self.move_it = Peekable(self.iter_moves())

    def peek_move(self, m):
        '''
        Function decorator that makes move m, runs func, reverses move and finally returns func result.

        NOTE: Need inner decorator so that we can accept move m parameter in peek_move method.
        '''
        # Actual function decorator
        def decorate(func):
            # Wrapper to modify function behavior
            def wrap(*args, **kwargs):
                self.make_move(m)
                result = func(*args, *kwargs)
                self.reverse_move()
                return result
            return wrap
        return decorate

    def would_put_king_in_check(self, m):
        '''
        Returns if the otherwise legal move m would put the moving piece's king in check.
        '''
        @self.peek_move(m)
        def inner():
            return self.get_king(m.moving_piece.color).is_being_attacked()
        return inner()

    def get_pseudo_algebraic_notation(self, m):
        '''
        TODO: test
        Returns the complete algebraic notation of Move m, e.g. 'Nc6', EXCEPT for the check/checkmate character.
        - That character, if applicable, is added while move is being made in self.make_move(m).

        NOTE: Assumes move hasn't yet been made, i.e. the moving piece is still at m.st_square.
        - Called in Move constructor

        Order if pawn:
        1. Capture? -> start file + 'x'
        2. End square
        3. Pawn promotion? -> new piece letter
        4. Check or checkmate? -> '+' or '#'

        Order for other pieces:
        1. Piece letter
        2. Same piece type can move to that square?
            a. Different file? -> start file
            b. Else -> start rank
            c. 1 same file, 1 same rank? -> start file + start rank
        3. Capture? -> 'x'
        4. End square
        5. Check or checkmate? -> '+' or '#'
        '''
        # Base case: Castling
        if m.m_type == MoveType.CASTLE:
            r_file, _ = m.st_square
            # Kingside
            if r_file == File.H:
                return 'O-O'
            # Queenside
            else:
                return 'O-O-O'

        def get_disambiguation_str():
            '''
            Returns file and/or rank of moving piece if needed to remove ambiguity regarding which piece is moving, otherwise returns ''.
            '''
            def iter_ambiguous_pieces(piece, end_square):
                '''
                Iterates pieces of the same type and color as the moving piece that can also land on the target end square.

                NOTE: There can be 2 (very rarely), 1 (sometimes), and usually 0 ambiguous pieces.
                '''
                # Iterate non-identical pieces of same type
                for piece_square in filter(lambda sq: sq != piece.square, self.piece_squares[piece.color, piece.type_index]):
                    cur_piece = self.get_piece(piece_square)
                    # Disambiguation needed if move to end square is fully legal
                    if cur_piece.is_pseudo_legal_end_square(end_square) and not self.would_put_king_in_check(cur_piece.get_standard_move(end_square)):
                        yield cur_piece

            st_file, st_rank = m.st_square
            dif_file = False
            dif_rank = False

            # Iterate pieces of same type that can land on the same square
            for amb_piece in iter_ambiguous_pieces():
                amb_file, amb_rank = amb_piece.square
                # a. Different file (NOTE: could also be different rank but only file necessary in this case)
                if amb_file != st_file:
                    dif_file = True
                # b. Different rank
                else:
                    dif_rank = True

                # c. 1 different file and same rank, 1 different rank and same file; TODO: does this work in queen wikipedia example Qff1?
                if dif_file and dif_rank:
                    return st_file + str(st_rank)

            if dif_file:
                return st_file
            elif dif_rank:
                return str(st_rank)
            else:
                # No ambiguous pieces
                return ''

        notation_arr = []

        # Pawn
        if isinstance(m.moving_piece, pieces.Pawn):
            # 1. Capture? -> start file + 'x'
            if m.tgt_piece is not None:
                notation_arr.append(m.st_square[0] + 'x')
        # Other pieces
        else:
            # 1. Piece letter
            notation_arr.append(m.moving_piece.letter)
            # 2. Disambiguation
            notation_arr.append(get_disambiguation_str())
            # 3. Capture? -> 'x'
            if m.tgt_piece is not None:
                notation_arr.append('x')

        # 2/4. End square
        end_file, end_rank = m.end_square
        notation_arr.append(end_file + str(end_rank))

        # Pawn 3. Pawn promotion? -> new piece letter
        notation_arr.append(m.promotion_letter)

        return ''.join(notation_arr)

    def is_piece_between(self, x_square, y_square):
        '''
        Returns if at least one piece lies between squares x and y which lie on same horizontal, vertical, or diagonal path.

        TODO: test
        '''
        return Peekable(filter(lambda sq: self.has_piece(sq), coordinates.iter_squares_between(*x_square, *y_square))).has_next()

    def iter_en_passant_moves(self):
        '''
        Iterates up to two (usually zero) possible en passant moves.
        '''
        if len(self.move_stack) == 0:
            return
        last_m = self.move_stack[-1]

        # Verify last move was pawn that moved 2 spaces
        d_pawn = self.get_piece(last_m.end_square)
        if d_pawn.piece_type != PieceType.PAWN:
            return

        d_file, d_rank = d_pawn.square
        _, st_rank = last_m.st_square
        if abs(d_rank - st_rank) != 2:
            return

        def get_en_passant(file_step=1):
            # Check if there is an attacking pawn in the correct position
            st_square = (coordinates.shift_file(d_file, file_step), d_rank)
            a_pawn = self.get_piece(st_square)
            if a_pawn is None or a_pawn.piece_type != PieceType.PAWN or a_pawn.color != d_pawn.opp_color:
                return

            end_square = d_file, d_rank + (1 if a_pawn.color == Color.WHITE else -1)
            m = Move(self, MoveType.EN_PASSANT, st_square, end_square, tgt_piece=d_pawn)
            if not self.would_put_king_in_check(m):
                return m

        # from left
        if d_file > File.A:
            m = get_en_passant(file_step=-1)
            if m is not None:
                yield m
        # from right
        if d_file < File.H:
            m = get_en_passant()
            if m is not None:
                yield m

    def iter_castle_moves(self, color):
        '''
        Iterates up to two (usually zero) possible castle moves.
        
        Castling rules: (https://en.wikipedia.org/wiki/Castling)
        1. Neither the king nor the rook has previously moved. ✅
        2. There are no pieces between the king and the rook. ✅
        3. The king is not currently in check. ✅
        4. The king does not pass through or finish on a square that is attacked by an enemy piece. ✅
        
        To clarify:
        - The rook can be under attack.
        - The rook can pass through an attacked square. (Can castle queenside even if b file is attacked)
        - The king can have been in check earlier in the game.
        '''
        # TODO: Use fen_class fields instead of moved variable and other stuff

        king = self.get_king(color)
        if king.moved: return #1.1

        king_file, king_rank = king.square

        def is_valid_rook(rook):
            return rook is not None and rook.piece_type == PieceType.ROOK and rook.color == king.color and not rook.moved #1.2

        def get_castle(rook_file, rook_movement, king_file_step=1):
            rook_st_square = rook_file, king_rank
            rook = self.get_piece(rook_st_square)
            if not is_valid_rook(rook) or self.is_piece_between(king.square, rook_st_square) or king.is_being_attacked(): #2,3
                return

            rook_end_file = coordinates.shift_file(rook_file, rook_movement)
            rook_end_square = rook_end_file, king_rank
            king_end_file = coordinates.shift_file(king_file, king_file_step*2)
            king_end_square = king_end_file, king_rank
            # check if king would pass through or into check
            if king.is_being_attacked(rook_end_square) or king.is_being_attacked(king_end_square): #4
                return

            return Move(self, MoveType.CASTLE, rook_st_square, rook_end_square)

        # kingside
        m = get_castle(File.H, -2)
        if m: yield m
        # queenside
        m = get_castle(File.A, 3, -1)
        if m: yield m

    def iter_standard_moves(self, color):
        '''
        Iterates all standard (i.e. everything except castle and en passant)
        moves that can be made by all pieces with optional color param.
        '''
        for cur_piece in self.iter_pieces(color=color):
            for m in cur_piece.iter_my_standard_moves():
                yield m

    def iter_moves(self, color, move_type=MoveType.ALL):
        gen_list = []
        if move_type & MoveType.STD:
            gen_list.append(self.iter_standard_moves(color))
        if move_type & MoveType.CASTLE:
            gen_list.append(self.iter_castle_moves(color))
        if move_type & MoveType.EN_PASSANT:
            gen_list.append(self.iter_en_passant_moves())

        return itertools.chain(*gen_list)

    def has_next_move(self, color, move_type=MoveType.ALL):
        return next(self.iter_moves(color, move_type)) is not None

    def pretty_print(self):
        arr = self._arr
        if self.user_color == Color.BLACK:
            rank_order = list(range(1, 8 + 1))
            file_order = [coordinates.shift_file(File.H, -j) for j in range(8)]
            arr = np.flip(arr)
        else:
            rank_order = list(range(8, 1 - 1, -1))
            file_order = [coordinates.shift_file(File.A, j) for j in range(8)]

        print()
        for i in range(8):
            print(rank_order[i], end=' '*2)
            for j in range(8):
                piece_str = '•' if arr[i,j] is None else str(arr[i,j])
                print(piece_str, end=' ')
            print()
        print(end='\n' + ' '*3)
        for j in range(8):
            print(file_order[j], end=' ')
        print(end='\n\n')
