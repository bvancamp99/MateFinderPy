# Author: Bryce Van Camp
# Project: MateFinder
# File: fen.py
# Description: Logic for Forsyth–Edwards Notation with FenClass


import numpy as np

from enums import Color, MoveType, File
import pieces


START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


def get_piece_placement_arr(piece_placement_str):
    '''
    Returns 8x8 piece placement array given fen substring.

    e.g. rank 'r3kbnr' -> ['r', None, None, None, 'k', 'b', 'n', 'r']
    '''
    piece_placement_arr = np.array([[None] * 8 for _ in range(8)])
    i = 0
    j = 0
    for ch in piece_placement_str:
        if ch.isalpha():
            piece_placement_arr[i,j] = ch
            j += 1
        elif ch.isdecimal():
            # add to j by number of empty spaces
            j += int(ch)
        elif ch == '/':
            # go to beginning of next row and reset j
            i += 1
            j = 0
        else:
            raise ValueError('Invalid char in FEN board state substring!')

    return piece_placement_arr


def get_piece_placement_str(piece_placement_arr):
    '''
    Returns fen piece placement substring given 8x8 array.
    '''
    str_buffer = []
    empty_counter = 0
    for i in range(8):
        for j in range(8):
            ch = piece_placement_arr[i,j]
            if ch is None:
                empty_counter += 1
            else:
                # record then reset empty_counter if > 0
                if empty_counter > 0:
                    str_buffer.append(str(empty_counter))
                    empty_counter = 0

                # record piece letter
                str_buffer.append(ch)

        # record then reset empty_counter if > 0
        if empty_counter > 0:
            str_buffer.append(str(empty_counter))
            empty_counter = 0

        # record a slash to end the row
        str_buffer.append('/')

    # return joined string, not including last slash
    str_buffer.pop()
    return ''.join(str_buffer)


_CR_ORDER = ('K', 'Q', 'k', 'q')


def get_castling_rights_set(cr_str):
    # Base case: No castling rights
    if cr_str == '-':
        return set()
    # Else add each castling right to set
    else:
        return {cr for cr in cr_str}


def get_castling_rights_str(cr_set):
    # Base case: No castling rights
    if len(cr_set) == 0:
        return '-'
    # Else join castling rights in order
    else:
        return ''.join(filter(lambda cr: cr in cr_set, _CR_ORDER))


class FenClass:
    def __init__(self, fen_str):
        piece_placement, active_color, castling_rights, en_passant_target, halfmove_clock, fullmove_number = fen_str.split()

        self.piece_placement = get_piece_placement_arr(piece_placement)
        self.active_color = Color.BLACK if active_color == 'b' else Color.WHITE
        self.castling_rights = get_castling_rights_set(castling_rights)
        self.en_passant_target = en_passant_target
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)

        self.fen_stack = [str(self)]
        self.fen_counter = {self.get_hash_str(): 1}

    def __str__(self):
        '''
        Returns full FEN string.
        '''
        return ' '.join([
            get_piece_placement_str(self.piece_placement), 
            'b' if self.active_color == Color.BLACK else 'w',
            get_castling_rights_str(self.castling_rights), 
            self.en_passant_target, 
            str(self.halfmove_clock), 
            str(self.fullmove_number)
        ])

    def get_hash_str(self):
        '''
        Returns first four parts of FEN string, used to count identical board states for threefold repetition.
        '''
        return ' '.join([
            get_piece_placement_str(self.piece_placement), 
            'b' if self.active_color == Color.BLACK else 'w',
            get_castling_rights_str(self.castling_rights), 
            self.en_passant_target
        ])

    def update(self, m):
        '''
        Update fields using info from Move parameter that is being made.

        NOTE: Piece placement is updated in Board class at the same time as its own internal array.
              This method assumes that piece placement has been updated.
        '''
        def update_castling_rights():
            '''
            Castling rights are lost permanently if:
            1. The king has moved at any previous point in the game (all rights lost)
            2. The rook of the desired castling side has moved (kingside or queenside rights lost)
            3. The rook of the desired castling side has been captured (kingside or queenside rights lost)
            '''
            def remove_for_rook(rook, kingside, queenside):
                orig_rank = 1 if rook.color == Color.WHITE else 8
                # If still have castling rights and rook is on its original square, this is the first time it's moving.
                if kingside in self.castling_rights and rook.square == (File.A, orig_rank):
                    self.castling_rights.remove(kingside)
                elif queenside in self.castling_rights and rook.square == (File.H, orig_rank):
                    self.castling_rights.remove(queenside)

            kingside, queenside = ('K', 'Q') if m.moving_piece.color == Color.WHITE else ('k', 'q')

            # 1.
            if m.m_type == MoveType.CASTLE or isinstance(m.moving_piece, pieces.King):
                self.castling_rights.discard(kingside)
                self.castling_rights.discard(queenside)
            # 2.
            elif isinstance(m.moving_piece, pieces.Rook):
                remove_for_rook(m.moving_piece, kingside, queenside)
            # 3.
            if isinstance(m.tgt_piece, pieces.Rook):
                tgt_kingside, tgt_queenside = ('k', 'q') if kingside.isupper() else ('K', 'Q')
                remove_for_rook(m.tgt_piece, tgt_kingside, tgt_queenside)

        update_castling_rights()

        # En passant target
        if isinstance(m.moving_piece, pieces.Pawn) and abs(m.end_square[1] - m.st_square[1]) == 2:
            self.en_passant_target = m.end_square[0] + str(m.end_square[1])

        # Halfmove clock
        if m.tgt_piece is not None or is_instance(m.moving_piece, pieces.Pawn):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Fullmove number
        if self.active_color == Color.BLACK:
            self.fullmove_number += 1

        self.active_color ^= 1

        self.fen_stack.append(str(self))

        # FEN counter
        hash_str = self.get_hash_str()
        if hash_str in self.fen_counter:
            self.fen_counter[hash_str] += 1
        else:
            self.fen_counter[hash_str] = 1

    def revert(self):
        '''
        Reverts fields back to their state before the last move.

        NOTE: Piece placement is updated in Board class at the same time as its own internal array.
              This method assumes that piece placement has been updated.
        '''
        # FEN counter
        hash_str = self.get_hash_str()
        if self.fen_counter[hash_str] > 1:
            self.fen_counter[hash_str] -= 1
        else:
            del self.fen_counter[hash_str]

        # FEN stack: Pop last move's FEN and get info from the second-to-last (now last again) move
        self.fen_stack.pop()
        _, _, castling_rights, en_passant_target, halfmove_clock, fullmove_number = self.fen_stack[-1].split()

        self.active_color ^= 1
        self.castling_rights = get_castling_rights_set(castling_rights)
        self.en_passant_target = en_passant_target
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)
