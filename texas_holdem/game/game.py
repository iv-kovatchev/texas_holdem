from deck.deck import Deck
from game.player import Player
from game.betting import Betting

class PokerGame:
    def __init__(self):
        self.deck = Deck()
        self.betting = Betting() # Instantiate the Betting class

        # Create players: 1 human player and 5 AI players
        self.players = [Player(name="Player 1"), Player(name="AI 1", is_ai=True),
                        Player(name="AI 2", is_ai=True), Player(name="AI 3", is_ai=True),
                        Player(name="AI 4", is_ai=True), Player(name="AI 5", is_ai=True)]
        
        # Deal 2 cards to each player
        self.deal_cards()

        self.community_cards = []

    def deal_cards(self):
        for player in self.players:
            player.receive_cards(self.deck.deal(2))

    def deal_community_cards(self):
        # Deal the flop (3 cards)
        self.community_cards.extend(self.deck.deal(3))
        print("Flop: ", self.community_cards[:3])

        # Betting round test
        self.betting_round()

        # Deal the turn (1 card)
        self.community_cards.extend(self.deck.deal(1))
        print("Turn: ", self.community_cards[:4])

         # Betting round test
        self.betting_round()

        # Deal the river (1 card)
        self.community_cards.extend(self.deck.deal(1))
        print("River: ", self.community_cards[:5])

         # Betting round test
        self.betting_round()


    def betting_round(self):
        print("Starting betting round...")
        for player in self.players:
            if player.is_ai:
                self.betting.call(player)
            else:
                self.betting.human_input(player)

    def show_player_hands(self):
        for player in self.players:
            print(player)