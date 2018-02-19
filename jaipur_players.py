from jaipur import Jaipur, copy, apply_move
import random
import numpy as np

# Pick best move based off a value function   
class GreedyPlayer():
    def __init__(self, name, score=None):
        self.name = name
        self.score_fn = score

    def get_move(self, game, time_left):
        moves = game.get_legal_moves()
        return np.argmax(moves, key = self.score_fn)

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
        pass

# Forecast the move, to be used by the players for inference
def forecast_move(game, move):
    game_copy = copy(game)
    game_copy.apply_move(move)

    return game_copy