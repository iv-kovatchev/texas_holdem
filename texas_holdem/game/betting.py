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
        return self.bet(player, self.current_bet)
    
    def raise_bet(self, player, amount):
        if amount <= self.current_bet:
            print(f"{player.name} needs to raise more than the current bet.")
            return False
        else:
            self.pot += amount - self.current_bet
            self.current_bet = amount
            player.chips -= amount
            print(f"{player.name} raises the bet to {amount} chips.")
            return True
        
    def fold(self, player):
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