# Author: Bryce Van Camp
# Project: chess player
# Files: chess_game.py, chess_start.py, chess_player.py


import math
import random

import chess_game


ctos = {c.lower(): s for s, c in chess_game.black_stoc.items()}
piece_values = {
    'queen': 9,
    'rook': 5,
    'bishop': 3,
    'knight': 3,
    'pawn': 1
}

WIN = math.inf
LOSS = -math.inf


def get_piece_value(c):
    '''
    Returns the standard piece values for each non-king piece.
    
    See https://www.chess.com/terms/chess-piece-value
    '''
    return piece_values[ctos[c.lower()]]


def get_max_depth(n):
    '''
    Return the maximum depth for the current recursion given the number of 
    moves.
    '''
    return 0 if n <= 0 else max(2, math.ceil(5 / (2 * math.log(n + 1))))


class ChessPlayer:
    '''
    Plays chess.
    '''
    def __init__(self, board, color):
        '''
        Init player.
        '''
        self.board = board
        self.color = color
    
    def get_opponent_color(self):
        return 'w' if self.color == 'b' else 'b'
    
    def get_move(self, cur_turn, last_move=None, cur_board=None):
        '''
        Chooses a legal and (hopefully) competitive move for the given board and returns it.
        '''
        best = {
            'move': None,
            'score': -math.inf
        }
        
        moves = list(self.board.yield_moves(color=self.color, board=cur_board))
        en_passant_positions = list(self.board.yield_en_passant_positions(self.color, last_move, board=cur_board))
        castle_positions = list(self.board.yield_castle_positions(self.color, board=cur_board))
        n = len(moves) + len(en_passant_positions) + len(castle_positions)
        max_depth = get_max_depth(n)
        for m in random.sample(moves + en_passant_positions + castle_positions, k=n):
            future_board = self.board.get_copy(board=cur_board)
            if m in en_passant_positions:
                self.board.en_passant(*m, board=future_board)
                score = self.mini(cur_turn, cur_board, future_board, max_depth, en_passant=True)
            elif m in castle_positions:
                self.board.castle(*m, board=future_board)
                score = self.mini(cur_turn, cur_board, future_board, max_depth, castle=True)
            else:
                self.board.make_move(*m, board=future_board)
                score = self.mini(cur_turn, cur_board, future_board, max_depth, last_move=m)
            
            if score > best['score']:
                best['move'] = m
                best['score'] = score
                
                print(best)
            
            if best['score'] == WIN:
                break
        
        return best['move']
        
    def win_condition(self, cur_color, last_move, cur_board=None):
        '''
        Returns -1 for AI loss, 0 for no checkmate, 1 for opponent loss.
        '''
        king = self.board.get_king(cur_color, board=cur_board)
        if king.checkmate(last_move, cur_board=cur_board):
            return LOSS if cur_color == self.color else WIN
        else:
            return 0
    
    def heuristic(self, cur_color, cur_turn, prev_board, cur_board, cur_depth, last_move, en_passant, castle):
        h = 0
        if en_passant:
            h += piece_values['pawn']
        elif castle:
            h += 0.1
        elif last_move is not None:
            if self.board.pawn_promotion_eligible(last_move, board=cur_board):
                h += piece_values[self.choose_pawn_promotion(cur_board=cur_board)] - piece_values['pawn']
            
            x, y = last_move
            
            old_x = self.board.get_piece(*x, board=prev_board)
            if not old_x.moved:
                h += 0.01
            
            old_y = self.board.get_piece(*y, board=prev_board)
            if chess_game.is_piece(old_y):
                h += get_piece_value(str(old_y))
        
        h *= 0.8**cur_depth
        
        return h if cur_color == self.get_opponent_color() else -h
    
    def maxi(self, cur_turn, prev_board, cur_board, max_depth, cur_depth=0, h=0, last_move=None, en_passant=False, castle=False):
        cond = self.win_condition(self.color, last_move, cur_board=cur_board)
        if cond != 0:
            return cond
        
        h += self.heuristic(self.color, cur_turn, prev_board, cur_board, cur_depth, last_move, en_passant, castle)
        if cur_depth >= max_depth:
            return h
        
        if self.board.pawn_promotion_eligible(last_move, board=cur_board):
            _, x = last_move
            self.board.promote_pawn(x, s=self.choose_pawn_promotion(cur_board=cur_board), board=cur_board)
        
        moves = list(self.board.yield_moves(color=self.color, board=cur_board))
        en_passant_positions = list(self.board.yield_en_passant_positions(self.color, last_move, board=cur_board))
        castle_positions = list(self.board.yield_castle_positions(self.color, board=cur_board))
        
        a = -math.inf
        
        n = len(moves) + len(en_passant_positions) + len(castle_positions)
        max_depth = get_max_depth(n)
        for m in random.sample(moves + en_passant_positions + castle_positions, k=n):
            future_board = self.board.get_copy(board=cur_board)
            if m in en_passant_positions:
                self.board.en_passant(*m, board=future_board)
                score = self.mini(cur_turn, cur_board, future_board, max_depth, cur_depth=cur_depth+1, h=h, en_passant=True)
            elif m in castle_positions:
                self.board.castle(*m, board=future_board)
                score = self.mini(cur_turn, cur_board, future_board, max_depth, cur_depth=cur_depth+1, h=h, castle=True)
            else:
                self.board.make_move(*m, board=future_board)
                score = self.mini(cur_turn, cur_board, future_board, max_depth, cur_depth=cur_depth+1, h=h, last_move=m)
            
            a = max(a, score)
            
            if a == WIN:
                break
        
        return a
    
    def mini(self, cur_turn, prev_board, cur_board, max_depth, cur_depth=0, h=0, last_move=None, en_passant=False, castle=False):
        cond = self.win_condition(self.get_opponent_color(), last_move, cur_board=cur_board)
        if cond != 0:
            return cond
        
        h += self.heuristic(self.get_opponent_color(), cur_turn, prev_board, cur_board, cur_depth, last_move, en_passant, castle)
        if cur_depth >= max_depth:
            return h
        
        if self.board.pawn_promotion_eligible(last_move, board=cur_board):
            _, x = last_move
            self.board.promote_pawn(x, s=self.choose_pawn_promotion(cur_board=cur_board), board=cur_board)
        
        moves = list(self.board.yield_moves(color=self.get_opponent_color(), board=cur_board))
        en_passant_positions = list(self.board.yield_en_passant_positions(self.get_opponent_color(), last_move, board=cur_board))
        castle_positions = list(self.board.yield_castle_positions(self.get_opponent_color(), board=cur_board))
        
        b = math.inf
        
        n = len(moves) + len(en_passant_positions) + len(castle_positions)
        max_depth = get_max_depth(n)
        for m in random.sample(moves + en_passant_positions + castle_positions, k=n):
            future_board = self.board.get_copy(board=cur_board)
            if m in en_passant_positions:
                self.board.en_passant(*m, board=future_board)
                score = self.maxi(cur_turn, cur_board, future_board, max_depth, cur_depth=cur_depth+1, h=h, en_passant=True)
            elif m in castle_positions:
                self.board.castle(*m, board=future_board)
                score = self.maxi(cur_turn, cur_board, future_board, max_depth, cur_depth=cur_depth+1, h=h, castle=True)
            else:
                self.board.make_move(*m, board=future_board)
                score = self.maxi(cur_turn, cur_board, future_board, max_depth, cur_depth=cur_depth+1, h=h, last_move=m)
            
            b = min(b, score)
            
            if b == LOSS:
                break
        
        return b
    
    def choose_pawn_promotion(self, cur_board=None):
        # TODO: implement
        
        return 'queen'