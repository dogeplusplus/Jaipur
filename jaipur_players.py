from jaipur import Jaipur
import random
import numpy as np

# Pick best move based off a value function   
class GreedyPlayer():
    def __init__(self, name, score=None):
        self.name = name
        self.score_fn = score

    def get_move(self, name, time_left):
        moves = game.get_legal_moves()
        return np.argmax(moves, key = self.score_fn)

# Random moves
class RandomPlayer():
    def __init__(self, name, score=None):
        self.name = name

    def get_move(self, game, time_left=0):
        return random.sample(game.get_legal_moves(),1)[0]

        
