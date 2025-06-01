class Player:
    def __init__(self, name, chips=1000, is_ai=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_ai = is_ai
        self.has_folded = False
        self.bet_this_round = 0
        self.is_called = False

    def receive_cards(self, cards):
        self.hand = cards

    def __repr__(self):
        return f"{self.name}: {self.hand}"
    
    