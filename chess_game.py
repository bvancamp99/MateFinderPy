# Author: Bryce Van Camp
# Project: chess player
# Files: chess_game.py, chess_start.py, chess_player.py


import numpy as np
import copy
import itertools


empty_char = ' '
black_stoc = {
    'king': 'K',
    'queen': 'Q',
    'rook': 'R',
    'bishop': 'B',
    'knight': 'N',
    'pawn': 'P'
}
black_chars = {c for c in black_stoc.values()}
white_stoc = {s: c.lower() for s, c in black_stoc.items()}
white_chars = {c for c in white_stoc.values()}

pawn_promotion_choices = {
    'queen',
    'rook',
    'bishop',
    'knight'
}


def get_custom_board_template():
    '''
    You can start the game with a custom board state using this function.
    
    NOTE: This function assumes that the board state you supply is viewed 
          from the white piece player's perspective.
    '''
    return np.array([
        [empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char],
        [empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char],
        [empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char],
        [empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char],
        [empty_char, black_stoc['king'], empty_char, empty_char, empty_char, empty_char, empty_char, empty_char],
        [empty_char, empty_char, empty_char, empty_char, empty_char, white_stoc['king'], empty_char, empty_char],
        [empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char, empty_char],
        [empty_char, empty_char, empty_char, empty_char, empty_char, black_stoc['rook'], black_stoc['queen'], empty_char]
    ])


def get_standard_board_template():
    return np.array([
        [black_stoc['rook'], black_stoc['knight'], black_stoc['bishop'], black_stoc['queen'], black_stoc['king'], black_stoc['bishop'], black_stoc['knight'], black_stoc['rook']],
        [black_stoc['pawn']] * 8,
        [empty_char] * 8,
        [empty_char] * 8,
        [empty_char] * 8,
        [empty_char] * 8,
        [white_stoc['pawn']] * 8,
        [white_stoc['rook'], white_stoc['knight'], white_stoc['bishop'], white_stoc['queen'], white_stoc['king'], white_stoc['bishop'], white_stoc['knight'], white_stoc['rook']]
    ])


def is_piece(x, color=None, s=None):
    '''
    Returns if x is a ChessPiece (i.e. is non-empty) and has the optionally 
    specified color and type s.
    '''
    return (
        x != empty_char 
        and (True if color is None else x.color == color)
        and (True if s is None else str(x).upper() == x.get_allyc(s).upper())
    )


def on_board(chess_col, chess_row):
    '''
    Returns if the column and row fit in an 8x8 board.
    
    Valid params range from ('A', 1) to ('H', 8)
    '''
    return ord('A') <= ord(chess_col) <= ord('H') and 1 <= chess_row <= 8


def col_sum(chess_col, j):
    '''
    Simplifies adding to a chess column.
    
    e.g. returns 'B' for input ('A', 1)
    '''
    return chr(ord(chess_col) + j)


class ChessBoard:
    def __init__(self, user_color, template=None):
        self._user_color = user_color
        
        if template is None:
            template = get_standard_board_template()
        if user_color == 'b':
            template = np.flip(template)
        
        self.black_ctopt = {
            black_stoc['king']: King('b', None, self),
            black_stoc['queen']: Queen('b', None, self),
            black_stoc['rook']: Rook('b', None, self),
            black_stoc['bishop']: Bishop('b', None, self),
            black_stoc['knight']: Knight('b', None, self),
            black_stoc['pawn']: Pawn('b', None, self)
        }
        self.white_ctopt = {
            white_stoc['king']: King('w', None, self),
            white_stoc['queen']: Queen('w', None, self),
            white_stoc['rook']: Rook('w', None, self),
            white_stoc['bishop']: Bishop('w', None, self),
            white_stoc['knight']: Knight('w', None, self),
            white_stoc['pawn']: Pawn('w', None, self)
        }
        
        self._board = np.array([[None] * 8 for _ in range(8)])
        for i in range(8):
            for j in range(8):
                c = template[i,j]
                if c == empty_char:
                    self._board[i,j] = c
                elif c in black_chars:
                    piece = copy.copy(self.black_ctopt[c])
                    piece.position = (self.get_chess_col(j), self.get_chess_row(i))
                    self._board[i,j] = piece
                elif c in white_chars:
                    piece = copy.copy(self.white_ctopt[c])
                    piece.position = (self.get_chess_col(j), self.get_chess_row(i))
                    self._board[i,j] = piece
                else:
                    raise Exception('Non-valid piece char', c)
    
    def get_chess_row(self, i):
        return 8 - i if self._user_color == 'w' else i + 1
    
    def get_chess_col(self, j):
        return col_sum('A', j) if self._user_color == 'w' else col_sum('H', -j)
    
    def get_chess_position(self, i, j):
        '''
        Returns a string representing the chess position given the board indices.
        
        e.g. returns 'D6' for input (2,3) when user color is white
        '''
        return (self.get_chess_col(j), self.get_chess_row(i))
    
    def get_i(self, chess_row):
        return 8 - chess_row if self._user_color == 'w' else chess_row - 1
    
    def get_j(self, chess_col):
        return ord(chess_col) - ord('A') if self._user_color == 'w' else ord('H') - ord(chess_col)
    
    def get_indices(self, chess_col, chess_row):
        '''
        Returns a tuple representing the indices of the back-end board 
        corresponding with the chess_pos.
        
        e.g. returns (2,3) for input 'D', 6 when user color is white
        '''
        return (self.get_i(chess_row), self.get_j(chess_col))
    
    def get_piece(self, chess_col, chess_row, board=None):
        if board is None:
            board = self._board
        
        return board[self.get_indices(chess_col, chess_row)]
    
    def _yield_vertical_between(self, x, y):
        x_col, x_row = x
        y_col, y_row = y
        
        start_row = min(x_row, y_row)
        end_row = max(x_row, y_row)
        
        for i in range(start_row + 1, end_row):
            yield (x_col, i)
    
    def _yield_horizontal_between(self, x, y):
        x_col, x_row = x
        y_col, y_row = y
        
        start_col = ord(min(x_col, y_col))
        end_col = ord(max(x_col, y_col))
        
        for i in range(start_col + 1, end_col):
            yield (chr(i), x_row)
    
    def _yield_diagonal_between(self, x, y):
        x_col, x_row = x
        y_col, y_row = y
        
        col_dif = ord(x_col) - ord(y_col)
        row_dif = x_row - y_row
        
        sign_match = 1 if col_dif == row_dif else -1
        
        start_col = ord(min(x_col, y_col))
        end_col = ord(max(x_col, y_col))
        
        start_row = min(x_row, y_row) if sign_match == 1 else max(x_row, y_row)
        end_row = max(x_row, y_row) if sign_match == 1 else min(x_row, y_row)
        
        for i in range(1, abs(col_dif)):
            yield (chr(start_col + i), start_row + i*sign_match)
    
    def yield_positions_between(self, x, y):
        x_col, x_row = x
        y_col, y_row = y
        
        if x_col == y_col:
            return self._yield_vertical_between(x, y)
        elif x_row == y_row:
            return self._yield_horizontal_between(x, y)
        elif abs(ord(x_col) - ord(y_col)) == abs(x_row - y_row):
            return self._yield_diagonal_between(x, y)
        else:
            raise Exception('Positions {} and {} not on same vertical, horizontal, or diagonal path.'.format(x, y))
    
    def are_pieces_between(self, x, y, board=None):
        '''
        Returns if at least one piece lies between positions x and y.
        Very useful in e.g. checking castle legality.
        
        NOTE: This function runs in linear time (checks each piece between x and y).
              This is very slow in the context of an exponentially large search tree,
              so avoid using if not necessary.
        '''
        if board is None:
            board = self._board
        
        for x in self.yield_positions_between(x, y):
            if self.get_piece(*x, board=board) != empty_char:
                return True
        return False
    
    def yield_pieces(self, color=None, s=None, board=None):
        '''
        Yields pieces on the board with the optionally specified color and 
        type s.
        '''
        if board is None:
            board = self._board
        
        for i in range(8):
            for j in range(8):
                piece = board[i,j]
                if is_piece(piece, color=color, s=s):
                    yield piece
    
    def get_king(self, color, board=None):
        # TODO: maybe hyper-optimize to check most likely positions first 
        #       based on king's start position
        #       Better soln would be to store king object in a struct format with board state
        if board is None:
            board = self._board
        
        for i in range(8):
            for j in range(8):
                piece = board[i,j]
                if is_piece(piece, color=color, s='king'):
                    return piece
        
        self.board.pretty_print(board=board)
        raise Exception('No king of color {} on the board!'.format(color))
    
    def get_copy(self, board=None):
        if board is None:
            board = self._board
        
        return np.copy(board)
    
    def pretty_print(self, board=None):
        if board is None:
            board = self._board
        
        row_order = list(range(1, 8 + 1))
        if self._user_color == 'w':
            row_order.reverse()
        
        col_order = [col_sum('A', j) for j in range(8)]
        if self._user_color == 'b':
            col_order.reverse()
        
        print()
        for i in range(8):
            print(row_order[i], end=' '*2)
            for j in range(8):
                print(board[i,j], end=' ')
            print()
        print(end='\n' + ' '*3)
        for j in range(8):
            print(col_order[j], end=' ')
        print()
        print()
    
    def make_move(self, x, y, board=None):
        if board is None:
            board = self._board
        
        piece_copy = copy.copy(self.get_piece(*x, board=board))
        piece_copy.position = y
        piece_copy.moved = True
        
        board[self.get_indices(*x)] = empty_char
        board[self.get_indices(*y)] = piece_copy
    
    def make_moves(self, *moves, board=None):
        for m in moves:
            self.make_move(*m, board=board)
    
    def yield_moves(self, color=None, s=None, board=None):
        '''
        Yields all standard moves that can be made with the optionally 
        specified board state.
        
        Default parameters can be used to filter color and type s.
        '''
        if board is None:
            board = self._board
        
        for x in self.yield_pieces(color=color, s=s, board=board):
            for move in x.yield_moves(cur_board=board):
                yield move
    
    def en_passant(self, x, y, board=None):
        '''
        Performs en passant for the pawn at position x against the pawn at 
        position y.
        
        NOTE: Assumes that self.yield_en_passant_positions has been called 
              to verify.
        '''
        y_piece = self.get_piece(*y, board=board)
        i = 1 if y_piece.color == 'w' else -1
        y_col, y_row = y
        
        self.set_empty(y, board=board)
        self.make_move(x, (y_col, y_row - i), board=board)
    
    def yield_en_passant_positions(self, color, last_move, board=None):
        '''
        Yields (attacking pawn position, defending pawn position) for all 
        pawns that can en passant against the alleged pawn at the end 
        position of last_move that just moved two steps.
        
        There are a maximum of two positions but typically zero for an 
        arbitrary last_move.
        '''
        if last_move is None:
            return
        
        if board is None:
            board = self._board
        
        x, y = last_move
        y_col, y_row = y
        
        left_col = col_sum(y_col, -1)
        if ord(left_col) >= ord('A'):
            z_left = (left_col, y_row)
            if self.en_passant_eligible(z_left, color, last_move, board=board):
                yield (z_left, y)
        
        right_col = col_sum(y_col, 1)
        if ord(right_col) <= ord('H'):
            z_right = (right_col, y_row)
            if self.en_passant_eligible(z_right, color, last_move, board=board):
                yield (z_right, y)
    
    def en_passant_eligible(self, x, color, last_move, board=None):
        '''
        Returns if position x holds a pawn that can en passant given the last move.
        '''
        if board is None:
            board = self._board
        
        x_piece = self.get_piece(*x, board=board)
        
        return (
            is_piece(x_piece, color=color, s='pawn')
            and x_piece.can_en_passant(last_move, cur_board=board)
        )
    
    def castle(self, x, y, board=None):
        '''
        Performs a castle for the king at position x with the rook at 
        position y.
        
        NOTE: Assumes that self.yield_castle_positions has been called 
              to verify.
        '''
        king_move, rook_move = self.get_piece(*x, board=board).get_castle(y, cur_board=board)
        self.make_moves(king_move, rook_move, board=board)
    
    def yield_castle_positions(self, color, board=None):
        '''
        Yields (king position, rook position) for all rooks with which the 
        king with the specified color can castle.
        
        There are a maximum of two positions but typically zero.
        '''
        if board is None:
            board = self._board
        
        king = self.get_king(color, board=board)
        king_col, king_row = king.position
        for x in [('A', king_row), ('H', king_row)]:
            if king.can_castle(x, cur_board=board):
                yield (king.position, x)
    
    def castle_eligible(self, x, y, board=None):
        '''
        Returns if position x holds a king that can castle with an alleged 
        ally rook at position y.
        '''
        if board is None:
            board = self._board
        
        x_piece = self.get_piece(*x, board=board)
        
        return (
            is_piece(x_piece, s='king')
            and x_piece.can_castle(y, cur_board=board)
        )
    
    def promote_pawn(self, x, s='queen', board=None):
        '''
        Promotes the pawn at position x to a new ChessPiece of type s.
        
        NOTE: Assumes that pawn_promotion_eligible was called to verify.
        '''
        pawn = self.get_piece(*x, board=board)
        self.set_piece(x, pawn.color, s, pawn.moved, board=board)
    
    def pawn_promotion_eligible(self, last_move, board=None):
        '''
        Returns if the last move was from a pawn now eligible for promotion.
        '''
        if last_move is None:
            return False
        
        if board is None:
            board = self._board
        
        _, x = last_move
        x_piece = self.get_piece(*x, board=board)
        _, x_row = x
        
        return (
            is_piece(x_piece, s='pawn')
            and (x_row == 8 if x_piece.color == 'w' else x_row == 1)
        )
    
    def set_piece(self, x, color, s, moved, board=None):
        '''
        Sets the piece at position x to a new chess piece with the specified 
        color, type s, and moved state.
        '''
        if board is None:
            board = self._board
        
        new_piece = copy.copy(self.black_ctopt[black_stoc[s]] if color == 'b' else self.white_ctopt[white_stoc[s]])
        new_piece.position = x
        new_piece.moved = moved
        board[self.get_indices(*x)] = new_piece
    
    def set_empty(self, x, board=None):
        '''
        Sets the piece at position x to an empty char for the given board.
        '''
        if board is None:
            board = self._board
        
        board[self.get_indices(*x)] = empty_char


class ChessPiece:
    def __init__(self, color, position, board, moved=False):
        self.color = color
        self.position = position
        self.board = board
        self.moved = moved
    
    def get_opponent_color(self):
        return 'w' if self.color == 'b' else 'b'
    
    def get_allyc(self, s):
        return black_stoc[s] if self.color == 'b' else white_stoc[s]
    
    def get_opponentc(self, s):
        return black_stoc[s] if self.color == 'w' else white_stoc[s]
    
    def under_attack(self, cur_board=None):
        '''
        A piece other than the king is under attack if there are any standard 
        moves from the opponent that land on the piece's position.
        '''
        for _, x in self.board.yield_moves(color=self.get_opponent_color(), board=cur_board):
            if x == self.position:
                return True
        return False
    
    def _yield_unobstructed_end_positions(self, cur_board=None):
        '''
        For each unobstructed, standard move from self.position, yields the 
        end position.
        
        This differs from get_moves in that it only returns the end position 
        and doesn't check if the move would put the ally king in check.
        '''
        raise Exception('Instance of abstract-like class ChessPiece')
    
    def _is_obstructed(self, x, cur_board=None):
        '''
        Returns if the move from self.position to x is obstructed, i.e. there 
        is something other than a check consideration that is preventing the 
        move from being made.
        
        e.g. x isn't on the board, x is the position of an ally piece, etc.
        '''
        return (
            not on_board(*x) 
            or is_piece(self.board.get_piece(*x, board=cur_board), color=self.color)
        )
    
    def yield_moves(self, cur_board=None):
        '''
        Yields all standard moves from self.position.
        '''
        for x in self._yield_unobstructed_end_positions(cur_board=cur_board):
            if not self.check_whatif(x, cur_board=cur_board):
                yield (self.position, x)
    
    def check_whatif(self, x, cur_board=None):
        '''
        Returns if the unobstructed move from self.position to x would put 
        the ally king in check.
        '''
        future_board = self.board.get_copy(board=cur_board)
        self.board.make_move(self.position, x, board=future_board)
        ally_king = self.board.get_king(color=self.color, board=future_board)
        
        return ally_king.under_attack(cur_board=future_board)


class King(ChessPiece):
    def __str__(self):
        return self.get_allyc('king')
    
    def under_attack(self, cur_board=None):
        '''
        A king is under attack (in check) if there are any unobstructed moves 
        from the opponent that land on the king's position.
        '''
        for x in self.board.yield_pieces(color=self.get_opponent_color(), board=cur_board):
            for end in x._yield_unobstructed_end_positions(cur_board=cur_board):
                if end == self.position:
                    return True
        return False
    
    def _yield_unobstructed_end_positions(self, cur_board=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions 
        for a king.
        '''
        my_col, my_row = self.position
        
        left_col = col_sum(my_col, -1)
        for i in range(-1, 1 + 1):
            x = (left_col, my_row + i)
            if not self._is_obstructed(x, cur_board=cur_board):
                yield x
        
        x = (my_col, my_row - 1)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        x = (my_col, my_row + 1)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        
        right_col = col_sum(my_col, 1)
        for i in range(-1, 1 + 1):
            x = (right_col, my_row + i)
            if not self._is_obstructed(x, cur_board=cur_board):
                yield x
    
    def can_castle(self, x, cur_board=None):
        '''
        Returns if it is legal to castle with the alleged rook at position x.
        '''
        if self.moved or self.under_attack(cur_board=cur_board):
            return False
        
        my_col, my_row = self.position
        if x not in {('A', my_row), ('H', my_row)}:
            return False
        
        x_piece = self.board.get_piece(*x, board=cur_board)
        if (
            not is_piece(x_piece, color=self.color, s='rook')
            or x_piece.moved 
            or self.board.are_pieces_between(self.position, x, board=cur_board)
        ):
            return False
        
        x_col, x_row = x
        pass_through = [('D', my_row), ('C', my_row)] if x_col == 'A' else [('F', my_row), ('G', my_row)]
        for y in pass_through:
            if self.check_whatif(y, cur_board=cur_board):
                return False
        
        return True
    
    def get_castle(self, x, cur_board=None):
        '''
        Gets the moves that perform a castle with the rook at position x.
        
        NOTE: Assumes that can_castle has been called to verify.
        '''
        my_col, my_row = self.position
        x_col, x_row = x
        
        my_new_pos = ('C', my_row) if x_col < my_col else ('G', my_row)
        x_new = ('D', x_row) if x_col < my_col else ('F', x_row)
        
        my_move = (self.position, my_new_pos)
        rook_move = (x, x_new)
        
        return (my_move, rook_move)
    
    def checkmate(self, last_move, cur_board=None):
        '''
        Returns if this king is checkmated, i.e. it is in check, and there 
        are no standard moves or en passants that the player can make.
        '''
        for m in self.board.yield_moves(color=self.color, board=cur_board):
            if m is not None:
                return False
        
        for m in self.board.yield_en_passant_positions(self.color, last_move, board=cur_board):
            if m is not None:
                return False
        
        return self.under_attack(cur_board=cur_board)


class Queen(ChessPiece):
    def __init__(self, color, position, board, moved=False):
        super().__init__(color, position, board, moved)
        self.rook = Rook(color, None, board, moved=None)
        self.bishop = Bishop(color, None, board, moved=None)
    
    def __str__(self):
        return self.get_allyc('queen')
    
    def _yield_unobstructed_end_positions(self, cur_board=None):
        return itertools.chain(
            self.rook._yield_unobstructed_end_positions(cur_board=cur_board, my_pos=self.position),
            self.bishop._yield_unobstructed_end_positions(cur_board=cur_board, my_pos=self.position)
        )


class Rook(ChessPiece):
    def __str__(self):
        return self.get_allyc('rook')
    
    def _yield_unobstructed_end_positions(self, cur_board=None, my_pos=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions 
        for a rook.
        
        For each direction, yields positions until the first obstruction, then 
        yields the obstructing piece if it is of an opposing color.
        '''
        if my_pos is None:
            my_pos = self.position
        
        my_col, my_row = my_pos
        
        i = my_row + 1
        while i <= 8 and not is_piece(self.board.get_piece(my_col, i, board=cur_board)):
            yield (my_col, i)
            i += 1
        if i <= 8 and is_piece(self.board.get_piece(my_col, i, board=cur_board), color=self.get_opponent_color()):
            yield (my_col, i)
        
        i = my_row - 1
        while i >= 1 and not is_piece(self.board.get_piece(my_col, i, board=cur_board)):
            yield (my_col, i)
            i -= 1
        if i >= 1 and is_piece(self.board.get_piece(my_col, i, board=cur_board), color=self.get_opponent_color()):
            yield (my_col, i)
        
        j = col_sum(my_col, -1)
        while ord(j) >= ord('A') and not is_piece(self.board.get_piece(j, my_row, board=cur_board)):
            yield (j, my_row)
            j = col_sum(j, -1)
        if ord(j) >= ord('A') and is_piece(self.board.get_piece(j, my_row, board=cur_board), color=self.get_opponent_color()):
            yield (j, my_row)
        
        j = col_sum(my_col, 1)
        while ord(j) <= ord('H') and not is_piece(self.board.get_piece(j, my_row, board=cur_board)):
            yield (j, my_row)
            j = col_sum(j, 1)
        if ord(j) <= ord('H') and is_piece(self.board.get_piece(j, my_row, board=cur_board), color=self.get_opponent_color()):
            yield (j, my_row)


class Bishop(ChessPiece):
    def __str__(self):
        return self.get_allyc('bishop')
    
    def _yield_unobstructed_end_positions(self, cur_board=None, my_pos=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions 
        for a bishop.
        
        For each diagonal direction, yields positions until the first 
        obstruction, then yields the obstructing piece if it is of an 
        opposing color.
        '''
        if my_pos is None:
            my_pos = self.position
        
        my_col, my_row = my_pos
        
        j_left = ord(my_col) - ord('A')
        j_right = ord('H') - ord(my_col)
        i_bottom = my_row - 1
        i_top = 8 - my_row
        
        i = 1
        while (
            i <= min(j_left, i_top) 
            and not is_piece(self.board.get_piece(col_sum(my_col, -i), my_row + i, board=cur_board))
        ):
            yield (col_sum(my_col, -i), my_row + i)
            i += 1
        if (
            i <= min(j_left, i_top) 
            and is_piece(self.board.get_piece(col_sum(my_col, -i), my_row + i, board=cur_board), color=self.get_opponent_color())
        ):
            yield (col_sum(my_col, -i), my_row + i)
        
        i = 1
        while (
            i <= min(j_left, i_bottom) 
            and not is_piece(self.board.get_piece(col_sum(my_col, -i), my_row - i, board=cur_board))
        ):
            yield (col_sum(my_col, -i), my_row - i)
            i += 1
        if (
            i <= min(j_left, i_bottom) 
            and is_piece(self.board.get_piece(col_sum(my_col, -i), my_row - i, board=cur_board), color=self.get_opponent_color())
        ):
            yield (col_sum(my_col, -i), my_row - i)
        
        i = 1
        while (
            i <= min(j_right, i_top)
            and not is_piece(self.board.get_piece(col_sum(my_col, i), my_row + i, board=cur_board))
        ):
            yield (col_sum(my_col, i), my_row + i)
            i += 1
        if (
            i <= min(j_right, i_top)
            and is_piece(self.board.get_piece(col_sum(my_col, i), my_row + i, board=cur_board), color=self.get_opponent_color())
        ):
            yield (col_sum(my_col, i), my_row + i)
        
        i = 1
        while (
            i <= min(j_right, i_bottom)
            and not is_piece(self.board.get_piece(col_sum(my_col, i), my_row - i, board=cur_board))
        ):
            yield (col_sum(my_col, i), my_row - i)
            i += 1
        if (
            i <= min(j_right, i_bottom)
            and is_piece(self.board.get_piece(col_sum(my_col, i), my_row - i, board=cur_board), color=self.get_opponent_color())
        ):
            yield (col_sum(my_col, i), my_row - i)


class Knight(ChessPiece):
    def __str__(self):
        return self.get_allyc('knight')
    
    def _yield_unobstructed_end_positions(self, cur_board=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions 
        for a knight.
        '''
        my_col, my_row = self.position
        
        i = my_row + 2
        j = col_sum(my_col, -1)
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        j = col_sum(my_col, 1)
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        
        i = my_row - 2
        j = col_sum(my_col, -1)
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        j = col_sum(my_col, 1)
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        
        j = col_sum(my_col, -2)
        i = my_row - 1
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        i = my_row + 1
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        
        j = col_sum(my_col, 2)
        i = my_row - 1
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x
        i = my_row + 1
        x = (j, i)
        if not self._is_obstructed(x, cur_board=cur_board):
            yield x


class Pawn(ChessPiece):
    def __str__(self):
        return self.get_allyc('pawn')
    
    def under_attack(self, last_move, cur_board=None):
        '''
        A pawn can also be under attack by en passant if it just made a 
        two-step move.
        '''
        _, x = last_move
        
        if x != self.position:
            return False
        
        for m in self.board.yield_en_passant_positions(self.get_opponent_color(), last_move, board=cur_board):
            if m is not None:
                return True
        
        return super().under_attack(cur_board=cur_board)
    
    def _yield_unobstructed_end_positions(self, cur_board=None):
        '''
        Attempts to hyper-optimize yielding the unobstructed end positions 
        for a pawn due to how many pawns there are in an exponentially large 
        search tree.
        '''
        my_col, my_row = self.position
        i_step = 1 if self.color == 'w' else -1
        
        i = my_row + i_step
        
        j = col_sum(my_col, -1)
        x = (j, i)
        if on_board(*x) and is_piece(self.board.get_piece(*x, board=cur_board), color=self.get_opponent_color()):
            yield x
        
        j = col_sum(my_col, 1)
        x = (j, i)
        if on_board(*x) and is_piece(self.board.get_piece(*x, board=cur_board), color=self.get_opponent_color()):
            yield x
        
        x = (my_col, i)
        if on_board(*x) and not is_piece(self.board.get_piece(*x, board=cur_board)):
            yield x
            
            if not self.moved:
                i_2 = i + i_step
                x = (my_col, i_2)
                if not is_piece(self.board.get_piece(*x, board=cur_board)):
                    yield x
    
    def can_en_passant(self, last_move, cur_board=None):
        '''
        Returns if en passant is legal for this piece given the opponent's 
        last move.
        '''
        x, y = last_move
        x_col, x_row = x
        y_col, y_row = y
        
        my_col, my_row = self.position
        y_piece = self.board.get_piece(*y, board=cur_board)
        
        if not (
            is_piece(y_piece, color=self.get_opponent_color(), s='pawn')
            and abs(x_row - y_row) == 2
            and my_row == y_row
            and abs(ord(my_col) - ord(y_col)) == 1
        ):
            return False
        
        future_board = self.board.get_copy(board=cur_board)
        self.board.en_passant(self.position, y, board=future_board)
        ally_king = self.board.get_king(color=self.color, board=future_board)
        
        return not ally_king.under_attack(cur_board=future_board)