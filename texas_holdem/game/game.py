from deck.deck import Deck
from game.player import Player

class PokerGame:
    def __init__(self):
        self.deck = Deck()
        # Create players: 1 human player and 5 AI players
        self.players = [Player(name="Player 1"), Player(name="AI 1", is_ai=True),
                        Player(name="AI 2", is_ai=True), Player(name="AI 3", is_ai=True),
                        Player(name="AI 4", is_ai=True), Player(name="AI 5", is_ai=True)]
        self.deal_cards()

    def deal_cards(self):
        for player in self.players:
            player.receive_cards(self.deck.deal(2))

    def show_player_hands(self):
        for player in self.players:
            print(player)