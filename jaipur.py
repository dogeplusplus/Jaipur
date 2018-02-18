import random
import copy
from collections import Counter
from itertools import combinations
import timeit
from jaipur_players import *

cards = {
    'Diamond': 6,
    'Gold': 6,
    'Silver': 6,
    'Cloth': 8,
    'Spice': 8,
    'Leather': 10,
    'Camel': 8 # 11 total camels but 3 are in the initial setup
}

class Jaipur:
    def __init__(self, player1, player2):
        # Board objects
        self.deck = []
        self.market = []
        self.discard_pile = []
        self.goods_tokens = {
            'Diamond': [7,7,5,5,5],
            'Gold': [6,6,5,5,5],
            'Silver': [5,5,5,5,5],
            'Cloth': [5,3,3,2,2,1,1],
            'Spice': [5,3,3,2,2,1,1],
            'Leather': [4,3,2,1,1,1,1,1,1]
        }
        self.bonus_tokens = {
            3: [1,1,2,2,2,3,3],
            4: [4,4,5,5,6,6],
            5: [8,8,9,10,10]
        }

        # Player objects
        self.player1 = player1
        self.player2 = player2
        self.active_player = player1
        self.inactive_player = player2

        # Store generic cards
        self.hands = {
            player1: [],
            player2: []
        }

        # Store camels here
        self.herds = {
            player1: [],
            player2: []
        }

        # Goods tokens and bonus tokens
        self.tokens = {
            player1: [[],[]],
            player2: [[],[]]
        }

        self.camel_token = None

    # Determine which player has the most camels
    def camel_token_allocate(self):
        if len(self.herds[self.player1]) > len(self.herds[self.player2]):
            self.camel_token = self.player1
        elif len(self.herds[self.player2]) > len(self.herds[self.player1]):
            self.camel_token = self.player2
        else:
            self.camel_token = None

    # Initial board set up of players, market
    def initial_setup(self):

        # Shuffle the deck
        for k, v in cards.items():
            self.deck += [k] * cards[k]
        random.shuffle(self.deck)

        # Get 3 camels and 2 cards into the market
        self.market = ['Camel' for _ in range(3)]
        for _ in range(2):
            self.market.append(self.draw())

        # Add cards to player hands
        self.hands[self.player1] = [self.draw() for _ in range(5)]
        self.hands[self.player2] = [self.draw() for _ in range(5)]

        # Add camels from the player hands to the herds
        # Check change herds before changing the player hands otherwise camels get deleted
        self.herds[self.player1] = [card for card in self.hands[self.player1] if card == 'Camel']
        self.herds[self.player2] = [card for card in self.hands[self.player2] if card == 'Camel']
        self.hands[self.player1] = [card for card in self.hands[self.player1] if card != 'Camel']
        self.hands[self.player2] = [card for card in self.hands[self.player2] if card != 'Camel']

        # Shuffle bonus tokens
        for k in self.bonus_tokens:
            random.shuffle(self.bonus_tokens[k])

    # Create copy of game for move forecasting
    def copy(self):
        new_board = Jaipur(self.player1, self.player2)
        new_board.deck = self.deck
        new_board.market = self.market
        new_board.discard_pile = self.discard_pile

        new_board.active_player = self.active_player
        new_board.inactive_player = self.inactive_player

        new_board.goods_tokens = self.goods_tokens
        new_board.bonus_tokens = self.bonus_tokens

        new_board.hands = self.hands
        new_board.herds = self.herds
        new_board.tokens = self.tokens

        return new_board

    @property
    # Return the active player
    def _active_player(self):
        return self.active_player

    @property
    # Return the inactive player
    def _inactive_player(self):
        return self.inactive_player

    # Draw a card from the deck
    def draw(self):
        return self.deck.pop()

    # Shuffle the deck if required
    def shuffle(self):
        random.shuffle(self.deck)

    # Fill any missing cards from the market
    def replenish_board(self):
        while len(self.market) < 5:
            try:
                self.market.append(self.draw())
            except IndexError:
                print("No more cards in the deck.")

    # Return the score of the players good's tokens
    def visible_score(self, player=None):
        if not player:
            player = self.active_player

        bonus_camel = 5 if self.camel_token == player else 0
        return sum(self.tokens[player][0]) + bonus_camel

    # Return the total score of the player including hidden bonus tokens
    def total_score(self, player=None):
        if not player:
            player = self.active_player

        bonus_camel = 5 if self.camel_token == player else 0
        return sum(self.tokens[player][0]) + sum(self.tokens[player][1]) + bonus_camel

    # Take all the camels from the market into the active player's hand
    def take_camels(self):
        self.herds[self.active_player] += [card for card in self.market if card == 'Camel']
        self.market = [card for card in self.market if card != 'Camel']
        self.replenish_board()

    # Take a single card from the market without exchanging
    def take_card(self, card):
        if card not in self.market:
            raise Exception("Card is not in the market")
        else:
            self.market.remove(card)

            # Add camel to herd if it's a camel
            if card == 'Camel':
                self.herds[self.active_player].append(card)
            # Add the card into the hand otherwise
            else:
                self.hands[self.active_player].append(card)

            # Replace the missing card
            self.replenish_board()

    # Exchange 1 or more cards from the market into the player's hand
    def exchange_cards(self, give_cards, take_cards):
        # Check if the cards to give is a subset of the player's hand
        if len(give_cards) != len(take_cards):
            raise Exception("Number of cards to exchange don't match.")
            
        give_card_count = Counter(give_cards)
        hand_count = Counter(self.hands[self.active_player])
        if any(give_card_count[c] > hand_count[c] for c, _ in give_card_count.items()):
            raise Exception("Not enough cards to give.")

        # Check if there are enough cards to take from the market
        take_card_count = Counter(take_cards)
        market_count = Counter(self.market)
        if any(take_card_count[c] > market_count[c] for c, _ in take_card_count.items()):
            raise Exception("Not enough cards in the market.")

        # Swap cards between the hand and market
        for card in give_cards:
            self.hands[self.active_player].remove(card)
        self.hands[self.active_player] += take_cards

        for card in take_cards:
            self.market.remove(card)
        self.market += give_cards

        # Move any camels to the herd
        combined_hand = self.hands[self.active_player] + self.herds[self.active_player]
        self.hands[self.active_player] = [card for card in combined_hand if card != 'Camel']
        self.herds[self.active_player] = [card for card in combined_hand if card == 'Camel']

    # Sell cards into the discard pile
    def sell_cards(self, card, n):

        hand_count = Counter(self.hands[self.active_player])
        if n > hand_count[card]:
            raise Exception("Not enough cards to sell.")
        else:
            for _ in range(n):
                self.hands[self.active_player].remove(card)
                self.discard_pile.append(card)

            # Give the player goods tokens
            for _ in range(n):
                try:
                    tk = self.goods_tokens[card].pop(0)
                    self.tokens[self.active_player][0].append(tk)
                # No more tokens to take from this pile
                except IndexError:
                    print("No more %s tokens." % card)

            # If 3 or more sold give them a bonus token
            if n >= 3:
                try:
                    bt = self.bonus_tokens[n].pop()
                    self.tokens[self.active_player][1].append(bt)
                # No more bonus tokens for this amount
                except IndexError:
                    print("No more %d bonus tokens" % n)

    # Apply move based on arguments                
    def apply_move(self, args):
        print(args)

        if args == 'Camels':
            self.take_camels()
        elif args[0] == 'Take':
            self.take_card(args[1])
        elif args[0] == 'Exchange':
            self.exchange_cards(args[1][0], args[1][1])
        elif args[0] == 'Sell':
            self.sell_cards(args[1][0],int(args[1][1]))
        else:
            raise Exception("Option is not valid.")

        # Check who has the most camels
        self.camel_token_allocate()

        # Swap players around
        self.active_player, self.inactive_player = self.inactive_player, self.active_player

    def print_board(self):
        for good in self.goods_tokens:
            print(good, '|', ' '.join(map(str,self.goods_tokens[good])))
            print('-'*20)

        hand_1 = ' ' if not self.hands[self.player1] else ' '.join(self.hands[self.player1])
        herd_1 = ' ' if not self.herds[self.player1] else ' '.join(self.herds[self.player1])
        hand_2 = ' ' if not self.hands[self.player2] else ' '.join(self.hands[self.player2])
        herd_2 = ' ' if not self.herds[self.player2] else ' '.join(self.herds[self.player2])

        print('%s''s hand: %s' % (self.player1.name, hand_1), end=' ')
        print('%s''s herd: %s' % (self.player1.name, herd_1))
        print('%s''s hand: %s' % (self.player2.name, hand_2), end=' ')
        print('%s''s herd: %s' % (self.player2.name, herd_2))
        print('Market: %s' % ' '.join(self.market))

    # A player can either take cards or sell, but not both
    def get_legal_moves(self, player=None):
        possible_moves = []

        if not player:
            player = self.active_player

        # Take all camels from the market
        if 'Camel' in self.market:
            possible_moves.append(('Camels'))

        # Actions involving taking 1 card from the market
        if len(self.hands[player]) < 7:
            for card in self.market:
                possible_moves.append(('Take', (card)))

        # All possible actions for exchanging n cards between the hand and market
        if len(self.hands[player]) > 0:
            for i in range(1, min(len(self.hands[player]), 5) + 1):
                give_card_combos = combinations(self.hands[player] + self.herds[player], i)
                take_card_combos = combinations(self.market, i)
                # Add all combinations of cards to swap and remove any redundant swaps, as these can be done using fewer cards
                possible_moves += [('Exchange', (gc, tc)) for gc in give_card_combos for tc in take_card_combos if not set(gc).intersection(set(tc))]

        # Selling actions
        card_counter = Counter(self.hands[player])
        for k in card_counter:
            
            # Determine the minimum number of cards to sell, 2 if it's a Jewel
            min_k = 1 if k not in ['Diamond', 'Gold', 'Silver'] else 2

            # Add all the possible selling combinations to the list of moves
            for i in range(min_k, card_counter[k]+1):
                possible_moves.append(('Sell', (k, i)))

        # De-duplicate moves for repeated card
        possible_moves = set(possible_moves)
        return possible_moves

    def play(self, time_limit = 1000):
        self.initial_setup()

        move_history = []
        time_millis = lambda: 1000 * timeit.default_timer()

        # While the deck isn't empty or 3 good piles haven't been depleted yet
        while self.deck != [] and len([good for good in self.goods_tokens if self.goods_tokens[good] == []]) < 3:
            legal_moves = self.get_legal_moves()
            game_copy = self.copy()

            move_start = time_millis()
            time_left = lambda : time_limit - (time_millis() - move_start)
            curr_move = self._active_player.get_move(game_copy, time_left)

            move_end = time_left()

            if move_end < 0:
                return self._inactive_player, move_history, "timeout"

            if curr_move not in legal_moves:
                if len(legal_moves) > 0:
                    return self._inactive_player, move_history, "forfeit"
                return self._inactive_player, move_history, "illegal move"

            move_history.append(list(curr_move))

            self.apply_move(curr_move)
            self.print_board()

        if self.total_score(self.player1) > self.total_score(self.player2):
            return self.player1.name, move_history, "player 1 wins"
        elif self.total_score(self.player1) < self.total_score(self.player2):
            return self.player2.name, move_history, "player 2 wins"
        else:
            return self.player1.name, move_history, "draw"

if __name__ == "__main__":
    my_deck = Jaipur(RandomPlayer("Albert"),RandomPlayer("Rohit"))
    a, b, c = my_deck.play()
    print(a)
    print(my_deck.total_score(my_deck.player1))
    print(my_deck.total_score(my_deck.player2))
    print(c)