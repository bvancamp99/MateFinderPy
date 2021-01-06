# Author: Bryce Van Camp
# Project: chess player
# Files: chess_game.py, chess_start.py, chess_player.py

import numpy as np
import threading

import chess_game
import chess_player


def pos(pos_str):
    col, row = pos_str
    return (col, int(row))


def main(template=None):
    user_color = None
    while user_color not in {'w', 'b'}:
        user_color = input('Choose your piece color (w or b): ')
    
    board = chess_game.ChessBoard(user_color, template=template)
    
    ai_color = 'b' if user_color == 'w' else 'w'
    ai = chess_player.ChessPlayer(board, ai_color)
    
    minimax_thread = threading.Thread(target=ai.get_move, args=())
    minimax_thread.start()
    
    cur_color = 'w'
    cur_turn = 1
    last_move = None
    moves = set(board.yield_moves(color=cur_color))
    en_passant_positions = set()
    castle_positions = set()
    while moves or en_passant_positions or castle_positions:
        board.pretty_print()
        
        num_pieces = 0
        for _ in board.yield_pieces():
            num_pieces += 1
            if num_pieces > 2:
                break
        if num_pieces == 2:
            print('Game ends in a draw.')
            return
        
        cur_king = board.get_king(cur_color)
        if cur_king.under_attack():
            print('King is in check.')
        
        print('Turn', cur_turn)
        
        if cur_color == user_color:
            print('Your turn...')
            
            print('Standard moves:', moves)
            print('En passant positions:', en_passant_positions)
            print('Castle positions:', castle_positions)
            last_move = None
            while True:
                try:
                    x = pos(input('Move from (e.g. A5): '))
                    y = pos(input('Move to (e.g. A4): '))
                except ValueError:
                    continue
                
                if (x, y) in moves:
                    board.make_move(x, y)
                    last_move = (x, y)
                    break
                elif (x, y) in en_passant_positions and input('En passant? (y/n): ') == 'y':
                    board.en_passant(x, y)
                    break
                elif (x, y) in castle_positions and input('Castle? (y/n): ') == 'y':
                    board.castle(x, y)
                    break
            
            if board.pawn_promotion_eligible(last_move):
                print('Pawn promotion!', end=' ')
                
                promotion = None
                while promotion not in chess_game.pawn_promotion_choices:
                    promotion = input('Choose your piece (queen, rook, bishop, or knight): ')
                
                _, x = last_move
                board.promote_pawn(x, s=promotion)
        else:
            print('AI\'s turn...')
            
            if not minimax_thread.is_alive():
                minimax_thread = threading.Thread(target=ai.get_move, args=(cur_turn, last_move))
                minimax_thread.start()
            
            minimax_thread.join()
            
            print(len(ai.scores))
            m, score = ai.scores[chess_player.get_hashable_board(board.get_copy())][last_move]
            last_move = None
            if m in moves:
                board.make_move(*m)
                last_move = m
                print('AI moves', m)
            elif m in en_passant_positions:
                m = board.en_passant(*m)
                print('AI en passants')
            elif m in castle_positions:
                m = board.castle(*m)
                print('AI castles')
            else:
                raise Exception('AI chose illegal move {}'.format(m))
            
            if board.pawn_promotion_eligible(last_move):
                print('Pawn promotion!', end=' ')
                
                promotion = ai.choose_pawn_promotion()
                if promotion not in chess_game.pawn_promotion_choices:
                    raise Exception('AI cannot choose {} for promotion piece'.format(promotion))
                
                print('AI chooses', promotion)
                _, x = last_move
                board.promote_pawn(x, s=promotion)
        
        cur_color = 'b' if cur_color == 'w' else 'w'
        cur_turn += 1
        
        moves = set(board.yield_moves(color=cur_color))
        en_passant_positions = set(board.yield_en_passant_positions(cur_color, last_move))
        castle_positions = set(board.yield_castle_positions(cur_color))
    
    board.pretty_print()
    
    cur_king = board.get_king(cur_color)
    if cur_king.checkmate(last_move):
        if cur_color == user_color:
            print('AI wins!')
        else:
            print('You win!')
    else:
        print('Game ends in a stalemate.')


if __name__ == '__main__':
    template = None
    #template = chess_game.get_custom_board_template()
    main(template=template)