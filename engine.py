# Author: Bryce Van Camp
# Project: MateFinder
# File: engine.py
# Description: Decision-making logic of the chess engine


import math
import random
import time

from enums import *


class EndState:
    LOSS = -math.inf
    DRAW = 0
    WIN = math.inf
    OUT_OF_TIME = None


class Engine:
    def __init__(self, user_color):
        self.user_color = user_color
        self.engine_color = user_color ^ 1

    '''
    def get_max_depth(self, n):
        \'''
        Return the maximum depth for the current recursion given the number of
        moves n.
        
        nodes ≈ branching_factor ^ depth
        depth = log(nodes) / log(branching_factor)
        \'''
        if n == 0:
            return 0

        TARGET_NODE_COUNT = 200000
        return int(math.log(TARGET_NODE_COUNT) / math.log(n + 1))

    def game_result(self, color):
        if self.board.get_king(color).is_checkmated():
            return LOSS if color == self.color else WIN
        else:
            return 0

    def heuristic(self, color):
        # TODO: implement
        h = 0
        return h

    def maxi(self, max_depth, cur_depth, h):
        result = self.game_result(self.color)
        if result:
            return result

        h += self.heuristic(self.color)
        if cur_depth == max_depth:
            return h

        a = LOSS
        for m in self.board.iter_moves(self.color):
            self.board.make_move(m)
            if self.board.is_pawn_promotion_triggered():
                self.board.promote_pawn(self.choose_pawn_promotion())
            score = self.mini(max_depth, cur_depth+1, h)
            self.board.reverse_move()

            a = max(a, score)
            if a == WIN:
                break

        return a

    def mini(self, max_depth, cur_depth, h):
        result = self.game_result(self.board.user_color)
        if result:
            return result

        h += self.heuristic(self.board.user_color)
        if cur_depth == max_depth:
            return h

        b = WIN
        for m in self.board.iter_moves(self.board.user_color):
            self.board.make_move(m)
            if self.board.is_pawn_promotion_triggered():
                self.board.promote_pawn(self.choose_pawn_promotion())
            score = self.maxi(max_depth, cur_depth+1, h)
            self.board.reverse_move()

            b = min(b, score)
            if b == LOSS:
                break

        return b

    def get_move_slow(self):
        best_move = None
        best_score = LOSS
        moves = list(self.board.iter_moves(self.color))
        print(self.get_max_depth(len(moves)))
        for m in random.sample(moves, k=len(moves)):
            self.board.make_move(m)
            if self.board.is_pawn_promotion_triggered():
                self.board.promote_pawn(self.choose_pawn_promotion())
            score = self.mini(self.get_max_depth(len(moves)), 0, 0)
            self.board.reverse_move()

            if score > best_score:
                best_move = m
                best_score = score

            if best_score == WIN:
                break

        return best_move
    '''

    '''
    def minimax_alpha_beta(self, board, depth, end_time, alpha, beta, maximizing_player)
        # TODO: if end state
        if depth == 0:
            # return evaluation
        elif time.time() >= end_time:
            return None

        if maximizing_player:
            max_score = LOSS
            for m in board.iter_moves(self.engine_color):
                board.make_move(m)
                if board.is_pawn_promotion_triggered():
                    board.promote_pawn(self.choose_pawn_promotion(board))

                # get score for current move by continuing search
                cur_score = self.minimax_alpha_beta(board, depth-1, end_time, alpha, beta, False)

                board.reverse_move()

                max_score = max(max_score, cur_score)
                alpha = max(alpha, cur_score)
                if alpha >= beta:
                    break
            return max_score
        else:
            min_score = WIN
            for m in board.iter_moves(self.user_color):
                board.make_move(m)
                if board.is_pawn_promotion_triggered():
                    board.promote_pawn(self.choose_pawn_promotion(board))

                # get score for current move by continuing search
                cur_score = self.minimax_alpha_beta(board, depth-1, end_time, alpha, beta, True)

                board.reverse_move()

                # store optimal evaluation for opponent
                min_score = min(min_score, cur_score)

                # prune if bet
                alpha = min(alpha, cur_score)
                if beta <= alpha:
                    break
            return min_score

    def initial_search(self, board):
        # TODO: need to check if insufficient material/game end?
        # maybe check that stuff in evaluation
        initial_nodes = {}

        # evaluate positions after engine 1st move
        for m in board.iter_moves(self.color):
            board.make_move(m)
            if board.is_pawn_promotion_triggered():
                board.promote_pawn(self.choose_pawn_promotion(board))
            score = self.evaluate_position(board)
            board.reverse_move()
            initial_nodes[m] = score

        return initial_nodes

    def iterative_deepening(self, board, time_limit):
        end_time = time.time() + time_limit
        cur_depth = 2 # begin after initial search
        initial_nodes = initial_search(board)
        sorted_initial = sorted(initial_nodes.items(), key=lambda item: item[1], reverse=True)
        best_move, best_score = initial_nodes[0]
        if abs(best_score) == WIN:
            return 
        while time.time() < end_time:
            for m, _ in sorted_initial:
                board.make_move(m)
                if board.is_pawn_promotion_triggered():
                    board.promote_pawn(self.choose_pawn_promotion(board))

                # get score for current initial move
                m_score = minimax_alpha_beta(board, cur_depth-1, end_time, LOSS, WIN, True)

                board.reverse_move()

                # exit quickly without storing new result if time ran out
                if time.time() >= end_time:
                    break

                initial_nodes[m] = m_score
            cur_move, cur_score = minimax_alpha_beta(board, cur_depth, end_time, LOSS, WIN, True)
            # None returned if search ran out of time before depth was fully explored
            if cur_move is None:
                break
            best_move, best_score = cur_move, cur_score
            # break after assigning best vars if game result found
            if abs(cur_score) == WIN:
                break

            cur_depth += 1

        print('Iterative deepening achieved depth =', cur_depth)
        print('best move:", 
        return best_move, best_score
    '''

    def evaluate_position(self, board, color):
        # TODO: implement
        return 0

    def choose_pawn_promotion(self, board):
        # TODO: evaluate each promotion and return the best one
        return PieceType.QUEEN

    def search(self, board, depth, end_time, alpha, beta, color, move_order=None, root_children=None):
        '''
        TODO: implement all possible end states
              currently do checkmate & stalemate (no legal moves for color) and insufficient material
              https://www.chess.com/article/view/how-chess-games-can-end-8-ways-explained
        '''
        if board.insufficient_material():
            return EndState.DRAW
        elif not board.has_next_move(color):
            # checkmate
            if board.get_king(color).is_being_attacked():
                return EndState.LOSS if color == self.engine_color else EndState.WIN
            # stalemate
            else:
                return EndState.DRAW
        elif time.time() >= end_time:
            return EndState.OUT_OF_TIME
        elif depth == 0:
            return self.evaluate_position(board, color)

        if color == self.engine_color:
            max_score = EndState.LOSS

            # use sorted moves for first pass
            if move_order is None:
                move_order = board.iter_moves(self.engine_color)
            else:
                move_order = [m for m, _ in move_order]

            for m in move_order:
                board.make_move(m)
                if board.is_pawn_promotion_triggered():
                    board.promote_pawn(self.choose_pawn_promotion(board))

                # get score for current move by continuing search
                cur_score = self.search(board, depth-1, end_time, alpha, beta, self.user_color)

                board.reverse_move()

                # update score for move in root_children in first pass
                if root_children is not None:
                    root_children[m] = cur_score

                # exit if search ran out of time
                if cur_score is EndState.OUT_OF_TIME:
                    return EndState.OUT_OF_TIME

                # store best evaluation for engine
                max_score = max(max_score, cur_score)

                # alpha-beta pruning
                alpha = max(alpha, cur_score)
                if beta <= alpha:
                    break

            return max_score
        else:
            min_score = EndState.WIN

            for m in board.iter_moves(self.user_color):
                board.make_move(m)
                if board.is_pawn_promotion_triggered():
                    board.promote_pawn(self.choose_pawn_promotion(board))

                # get score for current move by continuing search
                cur_score = self.search(board, depth-1, end_time, alpha, beta, self.engine_color)

                board.reverse_move()

                # exit if search ran out of time
                if cur_score is EndState.OUT_OF_TIME:
                    return EndState.OUT_OF_TIME

                # store best evaluation for opponent
                min_score = min(min_score, cur_score)

                # alpha-beta pruning
                beta = min(alpha, cur_score)
                if beta <= alpha:
                    break

            return min_score

    def iterative_deepening(self, board, time_limit):
        end_time = time.time() + time_limit
        depth = 0
        root_children = {m: EndState.LOSS for m in board.iter_moves(self.engine_color)}
        move_order = list(root_children.items())

        while time.time() < end_time:
            # update scores for root_children in search
            self.search(board, depth+1, end_time, EndState.LOSS, EndState.WIN, self.engine_color, move_order, root_children)

            # if the search ran out of time
            if EndState.OUT_OF_TIME in root_children.values():
                break

            # sort root children in descending order by score
            move_order = sorted(root_children.items(), key=lambda child: child[1], reverse=True)

            depth += 1

        print('Depth achieved:', depth)
        print(move_order[0])

        return move_order[0][0]

    def get_move(self, board):
        time_limit = 5 # TODO: calculate based on remaining time and estimated moves remaining
        return self.iterative_deepening(board, time_limit)
