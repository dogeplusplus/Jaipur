from jaipur import Jaipur
import random
import numpy as np

# Pick best move based off a value function   
class GreedyPlayer():
    def __init__(self, name, score=None):
        self.name = name
        self.score_fn = score

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
    def __init__(self, name, score=None):
        self.name = name

    def get_move(self, game, time_left=0):
        return random.sample(game.get_legal_moves(),1)[0]

# Prioritises moves that involve the taking and selling of Jewel goods, as these have the most value in the game
class JewelPlayer():
    def __init__(self, name, score=None):
        self.name = name

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

########### VALUE HEURISTIC ##############################
'''
For each move in the history append a label saying 1 if the player who executed the move is 1 else 0 otherwise.
This will be the target labels and we can use standard supervised learning to predict the probability of win
given move at time t.
The only trouble will be how to capture the interdependencies of moves within the same game.
'''
##########################################################

# can do alpha beta pruning if the game history is shown

class SearchTimeout(Exception):
    pass

class JaipurPlayer:
    def __init__(self, search_depth=3, score_fn = None, timeout=10.):
        self.search_depth = search_depth
        self.score_fn = score_fn
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
        argmax_fn = lambda x: min_value(game.forecast_move(x), 1)

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

        def max_value(game, alpha, beta, current_depth):
            if self.time_left() <  self.TIMER_THRESHOLD:
                raise SearchTimeout
            if not state.get_legal_moves() or current_depth >= depth:
                return self.score(state, self)

            v = float("inf")

