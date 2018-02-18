import unittest
import jaipur
import players

class jaipurTest(unittest.TestCase):
    def test_check_hands(self):
        j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())
        j.initial_setup()
        self.assertEqual(len(j.market),5)
        # Check players hand at most 5 cards
        self.assertTrue(len(j.hands[j.player1]) <= 5)
        self.assertTrue(len(j.hands[j.player2]) <= 5)
        # No camels in hands
        self.assertTrue('Camel' not in j.hands[j.player1] + j.hands[j.player2])

    def test_camel_taking(self):
        j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())
        j.initial_setup()j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())

        # At least 3 camels in the player's herd and no camels in the hands
        j.take_camels()
        self.assertTrue(len(j.herds[j.player1]) >= 3)
        self.assertTrue('Camel' not in j.hands[j.player1])

    def test_card_taking(self):
        j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())
        j.initial_setup()

        # Arbitrary card from the market
        card = j.market[0]
        j.take_card(card)

        # Check if the card moves into the appropriate pile
        if card == 'Camel':
            self.assertTrue(card in j.herds[j.player1])
        else:
            self.assertTrue(card in j.hands[j.player1])

        # Create arbitrary hand to test the hand limit
        j.hands[j.player1] = [1,1,1,1,1,1,1]
        card = j.market[0]
        self.assertRaises(Exception, j.take_card(card))

    def test_card_exchange(self):
        j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())
        j.initial_setup()

        # Manual setup
        j.market = ['Camel', 'Diamond', 'Silver', 'Gold', 'Gold']
        j.hands[j.player1] = ['Cloth', 'Spice', 'Leather'] 

        # Invalid actions
        self.assertRaises(Exception, j.exchange_cards, [['Gold'], ['Spice']]) # Card not in the market
        self.assertRaises(Exception, j.exchange_cards,[['Cloth', 'Spice', 'Leather'], ['Gold', 'Gold', 'Gold']]) # Too many golds
        self.assertRaises(Exception, j.exchange_cards,[['Cloth'], ['Diamond', 'Silver', 'Gold']]) # Exchange doesn't match

        # Try a valid exchange and see if the effects work
        j.exchange_cards(['Cloth', 'Spice'], ['Gold', 'Gold'])
        self.assertEqual(len([card for card in j.hands[j.player1] if card == 'Gold']), 2)
        self.assertTrue('Cloth' not in j.hands[j.player1] and 'Spice' not in j.hands[j.player1])

    def test_sell_cards(self):
        j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())
        j.initial_setup()

        # Manual setup
        j.hands[j.player1] = ['Diamond', 'Gold', 'Cloth', 'Cloth', 'Cloth']

        # Invalid sell actions
        self.assertRaises(Exception, j.sell_cards,['Gold', 1]) # Can't sell 1 gold only
        self.assertRaises(Exception, j.sell_cards,['Cloth', 4]) # Not enough cloth to sell

        # Check cards and tokens
        start_cloth_tokens = int(len(j.goods_tokens['Cloth']))
        start_triple_tokens = int(len(j.bonus_tokens[3]))

        j.sell_cards('Cloth', 3)
        self.assertTrue('Cloth' in j.discard_pile)
        self.assertTrue('Cloth' not in j.hands[j.player1])
        self.assertEqual(len(j.tokens[j.player1]), 4) # 3 goods tokens and 1 bonus token for p1
        self.assertEqual(len(j.goods_tokens['Cloth']), start_cloth_tokens - 3) # 3 less cloth tokens
        self.assertEqual(len(j.bonus_tokens[3]), start_triple_tokens - 1) # 1 less triple token

    # Test if the market is being refreshed after actions
    def test_board_replenish(self):
        j = jaipur.Jaipur(players.RandomPlayer(), players.RandomPlayer())
        j.initial_setup()

        # Arbitrary card from the market
        card = j.market[0]
        j.take_card(card)

        # Check the market has been restored
        self.assertEqual(len(j.market), 5)
        # Swap players around
        j.active_player , j.inactive_player = j.inactive_player, j.active_player

        # Take a card
        card2 = j.market[0]
        j.take_card(card2)
        if card2 == 'Camel':
            self.assertTrue(card in j.herds[j.player2])
        else:
            self.assertTrue(card in j.hands[j.player2])

        self.assertEqual(len(j.market), 5) 

if __name__=="__main__":
    unittest.main()

