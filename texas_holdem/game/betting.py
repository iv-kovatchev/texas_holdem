class Betting:
    def __init__(self):
        self.pot = 0
        self.current_bet = 0

    def bet(self, player, amount):
        if amount > player.chips:
            print(f"{player.name} doesn't have enough chips to bet.")
            return False
        else:
            player.chips -= amount
            self.pot += amount
            self.current_bet = amount
            print(f"{player.name} bets {amount} chips.")
            return True
        
    def call(self, player):
        player.is_called = True
        return self.bet(player, self.current_bet)
    
    def raise_bet(self, current_player, amount, players):
        if amount <= self.current_bet:
            print(f"{current_player.name} needs to raise more than the current bet.")
            return False
        else:
            self.pot += amount - self.current_bet
            self.current_bet = amount
            current_player.chips -= amount
            print(f"{current_player.name} raises the bet to {amount} chips.")
            
            # Reset all players' is_called to False except the one who raised
            for p in players:
                if p != current_player:
                    p.is_called = False
            
            return True
        
    def check(self):
        return True
        
    def fold(self, player):
        player.has_folded = True
        print(f"{player.name} folds.")
        return True
    
    def human_input(self, player):
        print(f"\n{player.name}, it's your turn!")
        action = input(f"Choose action: (C)all, (R)aise, (F)old: ").lower()
        
        if action == 'c':
            return self.call(player)
        elif action == 'r':
            raise_amount = int(input(f"Enter raise amount (current bet is {self.current_bet}): "))
            return self.raise_bet(player, raise_amount)
        elif action == 'f':
            return self.fold(player)
        else:
            print("Invalid input, please try again.")
            return self.human_input(player)