from jaipur import Jaipur
import random
import numpy as np

# Pick best move based off a value function   
class GreedyPlayer():
    def __init__(self, score=None):
        pass

    def get_move(self, game, time_left):
        previous_score = game.visible_score()
        # Evaluate the moves and the scores 
        options = []
        for move in game.get_legal_moves():
            forecast = forecast_move(game, move)
            point_change =  forecast.visible_score(forecast._inactive_player) - previous_score
            if point_change > 0:
                options.append((move,point_change))

        if options:
            return max(options, key=lambda x:x[1] )[0]
        else:
            return random.sample(game.get_legal_moves(),1)[0]

# Random moves
class RandomPlayer():
    def __init__(self, score=None):
        pass

    def get_move(self, game, time_left=0):
        return random.sample(game.get_legal_moves(),1)[0]

# Prioritises moves that involve the taking and selling of Jewel goods, as these have the most value in the game
class JewelPlayer():
    def __init__(self, score=None):
        pass

    def get_move(self, game, time_left=0):
        legal_moves =  [move for move in game.get_legal_moves()
                            if move[0] in ('Take', 'Sell') and move[1] in ('Diamond', 'Silver', 'Gold') 
                            or move[0] == 'Exchange' and set(move[2]).intersection(set(['Diamond', 'Silver', 'Gold']))]
        if legal_moves:
            return random.sample(legal_moves,1)[0]
        else:
            return random.sample(game.get_legal_moves(),1)[0] 
        
# Forecast the move, to be used by the players for inference
def forecast_move(game, move):
    game_copy = game.board_copy()
    game_copy.apply_move(move)

    return game_copy

class SearchTimeout(Exception):
    pass

class JaipurPlayer:
    def __init__(self, search_depth=3, score_fn=None, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

class MinimaxPlayer(JaipurPlayer):

    # Get the best move from the minimax algorithm
    def get_move(self, game, time_left):
        self.time_left = time_left

        best_move = random.sample(game.get_legal_moves(),1)[0]

        try:
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass

    # Minimax algorithm
    def minimax(self, game, depth):

        # Best move on the current player's choice
        def max_value(state, current_depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout
            if not state.get_legal_moves() or current_depth >= depth:
                return self.score(state, self)

            v = float("-inf")

            for a in state.get_legal_moves():
                v = max(v, min_value(forecast_move(state, a), current_depth + 1))

            return v

        # Worst move on the opponent player's choice
        def min_value(state, current_depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout
            if not state.get_legal_moves() or current_depth >= depth:
                return self.score(state, self)

            v = float("inf")

            for a in state.get_legal_moves():
                v = min(v, max_value(forecast_move(state, a), current_depth + 1))

            return v

        # Return best move from root
        argmax_fn = lambda x: min_value(forecast_move(game, x), 1)

        best_action = None
        best_value = float("-inf")

        if not game.get_legal_moves():
            return best_action

        return max(game.get_legal_moves(), key = argmax_fn)

class AlphaBetaPlayer(JaipurPlayer):

    def get_move(self, game, time_left):
        best_move = random.sample(game.get_legal_moves(),1)[0]
        self.time_left = time_left

        depth = 20
        for d in range(1, depth):
            try:
                best_move = self.alphabeta(game, d)
            except SearchTimeout:
                return best_move

    def alphabeta(game, depth, alpha=float("-inf"), beta=float("inf")):

        def max_value(state, alpha=float("-inf"), beta=float("inf"), current_depth=1):
            if self.time_left() <  self.TIMER_THRESHOLD:
                raise SearchTimeout
            if not state.get_legal_moves() or current_depth >= depth:
                return self.score(state, self)

            v = float("-inf")

            for move in state.get_legal_moves():
                v = max(v, min_value(forecast_move(state, move), alpha, beta, current_depth + 1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(state, alpha=float("-inf"), beta=float("inf"), current_depth=1):
            if self.time_left < self.TIMER_THRESHOLD:
                raise SearchTimeout
            if not state.get_legal_moves() or current_depth >= depth:
                return self.score(state, self)

            v = float("inf")

            for move in state.get_legal_moves():
                v = min(v, max_value(forecast_move(state, move), alpha, beta, current_depth + 1))

                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        root_legal_moves = game.get_legal_moves()

        if not root_legal_moves:
            return None

        best_action = root_legal_moves[0]
        best_v = alpha

        for move in root_legal_moves:
            v_test = min_value(forecast_move(game, move), alpha, beta, 1)
            if v_test > best_v:
                best_action = move
                best_v = float(v_test)

        return best_action

# Return the score of the move that gives the most benefit to the player
def custom_score(game, player):

    if game.is_winner(player):
        return float("inf")
    elif game.is_loser(player):
        return float("-inf")

    moves = game.get_legal_moves(player)
    current_points = game.visible_score(player)
    point_differential = [forecast_move(game, move).visible_score(player) - current_points for move in moves]
    return max(point_differential)

# Return the number of sell actions the player has
def custom_score_2(game, player):

    if game.is_winner(player):
        return float("inf")
    elif game.is_loser(player):
        return float("-inf")

    moves = game.get_legal_moves(player)
    sell_actions = [move for move in moves if move[0] == 'Sell']
    return len(sell_actions)

# Return the number of moves the player has
def custom_score_3(game, player):

    if game.is_winner(player):
        return float("inf")
    elif game.is_loser(player):
        return float("-inf")

    return len(game.get_legal_moves(player))
