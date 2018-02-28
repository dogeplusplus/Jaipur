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

########### VALUE HEURISTIC ################################
'''
For each move in the history append a label saying 1 if the player who executed the move is 1 else 0 otherwise.
This will be the target labels and we can use standard supervised learning to predict the probability of win
given move at time t.
The only trouble will be how to capture the interdependencies of moves within the same game.
'''
############################################################