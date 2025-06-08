from deck.deck import Deck
from game.player import Player
from game.betting import Betting
from game.engine.ai_logic import decide_action
from game.hand_evaluator import compare_hands
from config import player_positions
from client.player_data import update_player
import pygame

TABLE_COLOR = (34, 139, 34)

class PokerGame:
    def __init__(self, human_player=None):
        self.deck = None
        self.community_cards = []
        self.betting = Betting()
        self.dealer_index = 0
        self.small_blind = 10
        self.big_blind = 20
        self.display_events = []
        self.showdown_active = False
        
        # Game state machine
        self.game_phase = "waiting"  # waiting, pre_flop, flop, turn, river, showdown
        self.betting_phase = "inactive"  # inactive, active, waiting_human, complete
        self.current_betting_player = 0
        self.waiting_for_human = False
        
        # Use provided human player or default
        if human_player is None:
            human_player = Player(name="Player 1")

        # Create players: 1 human player and 5 AI players
        self.players = [human_player, Player(name="AI 1", is_ai=True),
                        Player(name="AI 2", is_ai=True), Player(name="AI 3", is_ai=True),
                        Player(name="AI 4", is_ai=True), Player(name="AI 5", is_ai=True)]
        
        for player in self.players:
            print(f"{player.name}: {player.chips} chips")

    def setup_new_round(self, table):
        print("\n=== New Round Starting ===")
        table.add_log("=== New Round Starting ===")

        # Reset everything
        self.deck = Deck()
        self.betting.pot = 0
        self.betting.current_bet = 0
        self.community_cards = []
        self.game_phase = "pre_flop"
        self.betting_phase = "inactive"
        self.current_betting_player = 0
        self.waiting_for_human = False
        self.skip_remaining_rounds = False
        self.showdown_active = False

        for player in self.players:
            player.hand = []
            player.has_folded = False

        self.dealer_index = (self.dealer_index + 1) % len(self.players)

        # Deal cards and apply blinds
        self.deal_cards(table)
        self.apply_blinds(table)
        
        # Start pre-flop betting
        self.start_betting_round()

    def update_game_state(self, table):
        """Call this from main loop to update game state"""
        
        if self.betting_phase == "active":
            self.process_current_player(table)
        elif self.betting_phase == "complete":
            self.advance_to_next_phase(table)

    def start_betting_round(self):
        """Start a new betting round"""
        print(f"Starting {self.game_phase} betting round...")
        self.betting_phase = "active"
        self.current_betting_player = 0
        
        # For pre-flop, start after big blind
        if self.game_phase == "pre_flop":
            bb_index = (self.dealer_index + 2) % len(self.players)
            self.current_betting_player = (bb_index + 1) % len(self.players)

    def process_current_player(self, table):
        """Process the current player's action"""
        if self.waiting_for_human:
            return  # Stop here until human acts
            
        # Find next active player
        attempts = 0
        while attempts < len(self.players):
            if self.current_betting_player >= len(self.players):
                # All players have acted
                self.betting_phase = "complete"
                return
                
            player = self.players[self.current_betting_player]
            
            if not player.has_folded:
                if player.is_ai:
                    # AI acts immediately
                    action = decide_action(player, self)

                    table.add_log(f"{player.name} chooses to {action}")
                    print(f"{player.name} chooses to {action}")

                    self.current_betting_player += 1
                    
                    # Check if only one player remains
                    if self.check_for_early_winner():
                        return
                    break
                else:
                    # Human player - pause and wait
                    self.waiting_for_human = True
                    table.waiting_for_human_action = True

                    table.add_log(f"{player.name}'s turn - waiting for input...")
                    print(f"{player.name}'s turn - waiting for input...")
                    return
            else:
                # Player folded, skip
                self.current_betting_player += 1
                
            attempts += 1

    def handle_human_action(self, action, raise_amount=None):
        """Handle human player action"""
        if not self.waiting_for_human:
            return False
            
        human_player = self.players[self.current_betting_player]
        
        # Execute action
        if action == "fold":
            self.betting.fold(human_player)
        elif action == "call" and not human_player.is_called:
            self.betting.call(human_player)
        elif action == "raise" and raise_amount:
            self.betting.raise_bet(human_player, raise_amount, self.players)
        elif action == "check":
            self.betting.check()
        elif action == "quit":
            self.handle_quit_and_save()
        else:
            return False
            
        # Move to next player
        self.current_betting_player += 1
        self.waiting_for_human = False
        
        # Check if only one player remains
        self.check_for_early_winner()
        
        return True

    def check_for_early_winner(self):
        """Check if only one player remains (everyone else folded)"""
        active_players = [p for p in self.players if not p.has_folded]
        if len(active_players) <= 1:
            winner = active_players[0] if active_players else None
            if winner:
                print(f"\n🃏 Everyone else folded. {winner.name} wins the pot of {self.betting.pot} chips!")
                winner.chips += self.betting.pot
                self.betting.pot = 0
                self.skip_remaining_rounds = True
                self.game_phase = "showdown"
                self.betting_phase = "complete"
            return True
        return False

    def advance_to_next_phase(self, table):
        """Move to next phase of the game"""
        if self.skip_remaining_rounds:
            self.game_phase = "waiting"  # Round over
            return
            
        if self.game_phase == "pre_flop":
            self.deal_flop(table)
            self.game_phase = "flop"
            self.start_betting_round()
        elif self.game_phase == "flop":
            self.deal_turn(table)
            self.game_phase = "turn"
            self.start_betting_round()
        elif self.game_phase == "turn":
            self.deal_river(table)
            self.game_phase = "river"
            self.start_betting_round()
        elif self.game_phase == "river":
            self.evaluate_winner(table)
            self.game_phase = "waiting"  # Round complete

    def deal_cards(self, table):
        for player in self.players:
            player.receive_cards(self.deck.deal(2))
        table.draw_player_cards()

    def deal_flop(self, table):
        self.deck.deal(1)  # Burn card
        self.community_cards.extend(self.deck.deal(3))
        table.add_log(f"Flop: {self.community_cards[:3]}")
        print(f"Flop: {self.community_cards[:3]}")
        table.draw_community_cards()

    def deal_turn(self, table):
        self.deck.deal(1)  # Burn card
        self.community_cards.extend(self.deck.deal(1))
        table.add_log(f"Turn: {self.community_cards[3]}")
        print(f"Turn: {self.community_cards[3]}")
        table.draw_community_cards()

    def deal_river(self, table):
        self.deck.deal(1)  # Burn card
        self.community_cards.extend(self.deck.deal(1))
        table.add_log(f"River: {self.community_cards[4]}")
        print(f"River: {self.community_cards[4]}")
        table.draw_community_cards()

    def apply_blinds(self, table):
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players)

        small_blind_player = self.players[sb_index]
        big_blind_player = self.players[bb_index]

        sb_amount = min(self.small_blind, small_blind_player.chips)
        bb_amount = min(self.big_blind, big_blind_player.chips)

        small_blind_player.chips -= sb_amount
        big_blind_player.chips -= bb_amount
        big_blind_player.is_called = True

        self.betting.pot += sb_amount + bb_amount
        self.betting.current_bet = bb_amount

        print(f"{small_blind_player.name} posts small blind: {sb_amount}")
        print(f"{big_blind_player.name} posts big blind: {bb_amount}")

        table.add_log(f"{small_blind_player.name} posts small blind: {sb_amount}")
        table.add_log(f"{big_blind_player.name} posts big blind: {bb_amount}")

        # Update display
        for i in [sb_index, bb_index]:
            x, y = player_positions[i]
            name_bg = pygame.Rect(x, y - 35, 200, 25)
            pygame.draw.rect(table.screen, TABLE_COLOR, name_bg)
            table.draw_player(self.players[i], x, y)

    def evaluate_winner(self, table):
        active_players = [p for p in self.players if not p.has_folded]

        if len(active_players) == 1:
            winner = active_players[0]
        else:
            best_player = active_players[0]
            for player in active_players[1:]:
                result = compare_hands(best_player.hand, player.hand, self.community_cards)
                if result == -1:
                    best_player = player
            winner = best_player

        # Flag to show all cards
        self.showdown_active = True

        table.add_log(f"Winner: {winner.name} with {winner.hand}")
        table.add_log(f"Pot of {self.betting.pot} chips goes to {winner.name}")
        
        print(f"\n🏆 Winner: {winner.name} with {winner.hand}")
        print(f"Pot of {self.betting.pot} chips goes to {winner.name}")
        winner.chips += self.betting.pot
        self.betting.pot = 0

    def handle_quit_and_save(self):
        # Save human player's chips and quit the game
        # Find the human player
        human_player = next(p for p in self.players if not p.is_ai)

        # Save the player's current chips
        update_player(human_player.name, human_player.chips)

        print(f"Saved {human_player.name} with {human_player.chips} chips to players.json")

    def get_current_player(self):
        """Get current player for display"""
        if self.betting_phase == "active" and self.current_betting_player < len(self.players):
            return self.players[self.current_betting_player]
        return None