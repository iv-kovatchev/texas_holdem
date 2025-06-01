import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, player_positions, TABLE_COLOR
from client.button import Button

CARD_WIDTH, CARD_HEIGHT = 80, 111
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

class Table:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 32)

        # Create action buttons for human player
        button_y = SCREEN_HEIGHT - 80
        self.fold_button = Button(50, button_y, 100, 40, "Fold", (180, 50, 50))
        self.call_button = Button(170, button_y, 100, 40, "Call", (50, 150, 50))
        self.raise_button = Button(290, button_y, 100, 40, "Raise", (50, 100, 180))
        
        self.quit_save = Button(1040, button_y, 180, 40, "Quit and Save", (180, 50, 50))

        self.waiting_for_human_action = False
        self.human_action_result = None

        try:
            self.card_back = pygame.image.load("assets/card_back.jpg")
            self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
        except:
            self.card_back = None

    def draw_card(self, x, y, text, face_up=True):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
        if face_up:
            try:
                card_image = pygame.image.load(f"assets/cards/{text}.jpg")
                card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
                self.screen.blit(card_image, (x, y))
            except:
                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                label = self.font.render(text, True, BLACK)
                self.screen.blit(label, (x + 5, y + 5))
        else:
             # Draw card back
            if self.card_back:
                self.screen.blit(self.card_back, (x, y))
            else:
                pygame.draw.rect(self.screen, (100, 100, 200), rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                # Draw card back pattern
                pygame.draw.line(self.screen, WHITE, (x + 10, y + 10), (x + 50, y + 80), 2)
                pygame.draw.line(self.screen, WHITE, (x + 50, y + 10), (x + 10, y + 80), 2)

    def draw_showdown_cards(self):
        """Draw all players' cards face up for showdown"""
        for i, player in enumerate(self.game.players):
            if player.has_folded:  # Skip players with no cards
                continue

            x, y = player_positions[i]
            for j, card in enumerate(player.hand):
                cx = x + j * (CARD_WIDTH + 10)
                cy = y

                # Show ALL cards face up during showdown
                card_label = f"{card.rank}{card.suit[0]}"
                self.draw_card(cx, cy, card_label, face_up=True)

            # Optional: Add a "WINNER" indicator if this player won
            if hasattr(self.game, 'round_winner') and self.game.round_winner == player:
                winner_text = "🏆 WINNER!"
                winner_label = self.font.render(winner_text, True, GOLD)
                self.screen.blit(winner_label, (x, y + CARD_HEIGHT + 10))

    def draw_player(self, player, x, y):
        # Draw player name
        name_color = GOLD if not player.has_folded else (128, 128, 128)
        name_text = f"{player.name}"
        if player.has_folded:
            name_text += " (FOLDED)"
            
        label = self.font.render(name_text, True, name_color)
        self.screen.blit(label, (x, y - 35))
        name_width = label.get_width()
        
        # Draw player chips
        chip_text = f"{player.chips} chips"
        chip_label = self.font.render(chip_text, True, WHITE)
        self.screen.blit(chip_label, (x + name_width + 10, y - 35))

    def draw_player_name(self, player, x, y):
        name_text = f"{player.name}"
        label = self.font.render(name_text, True, WHITE)
        self.screen.blit(label, (x, y - 35))
        return label.get_width()

    def draw_player_chips(self, player, x, y, offset_x):
        chip_text = f"{player.chips} chips"
        label = self.font.render(chip_text, True, WHITE)

        # Optional: clear previous area if needed
        chip_rect = pygame.Rect(x + offset_x + 10, y - 35, 100, 20)
        pygame.draw.rect(self.screen, TABLE_COLOR, chip_rect)

        self.screen.blit(label, (x + offset_x + 10, y - 35))
        
    def draw_player_cards(self):
        # Draw all player cards
        for i, player in enumerate(self.game.players):
            if player.has_folded:
                continue
                
            x, y = player_positions[i]
            for j, card in enumerate(player.hand):
                cx = x + j * (CARD_WIDTH + 10)
                cy = y
                
                if player.is_ai:
                    # AI cards are face down
                    self.draw_card(cx, cy, "", face_up=False)
                else:
                    # Human cards are face up
                    card_label = f"{card.rank}{card.suit[0]}"
                    self.draw_card(cx, cy, card_label, face_up=True)

    def draw_community_cards(self):
        """Draw community cards in the center"""
        if not self.game.community_cards:
            return

        y = SCREEN_HEIGHT // 2 - 120
        spacing = 10
        total_width = CARD_WIDTH * 5 + spacing * 4
        x_start = (SCREEN_WIDTH - total_width) // 2

        for i, card in enumerate(self.game.community_cards):
            text = f"{card.rank}{card.suit[0]}"
            x = x_start + i * (CARD_WIDTH + spacing)
            self.draw_card(x, y, text, face_up=True)

    def draw_pot_info(self):
        """Draw pot size and current bet info"""
        pot_text = f"Pot: {self.game.betting.pot} chips"
        bet_text = f"Current Bet: {self.game.betting.current_bet} chips"
        
        # Determine phase based on community cards count
        if not self.game.community_cards:
            phase_text = "Phase: PRE-FLOP"
        elif len(self.game.community_cards) == 3:
            phase_text = "Phase: FLOP"
        elif len(self.game.community_cards) == 4:
            phase_text = "Phase: TURN"
        elif len(self.game.community_cards) == 5:
            phase_text = "Phase: RIVER"
        else:
            phase_text = "Phase: BETTING"
        
        pot_label = self.big_font.render(pot_text, True, GOLD)
        bet_label = self.font.render(bet_text, True, WHITE)
        phase_label = self.font.render(phase_text, True, WHITE)
        
        # Draw in center area
        self.screen.blit(pot_label, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(bet_label, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(phase_label, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))

    def draw_action_buttons(self):
        """Draw action buttons for human player"""
        self.quit_save.draw(self.screen)

        if self.waiting_for_human_action:
            self.fold_button.draw(self.screen)
            
            # Update call button text based on current bet
            player = next(p for p in self.game.players if not p.is_ai)

            call_amount = max(0, self.game.betting.current_bet)
            self.call_button.text = f"Call {call_amount}" if not player.is_called else "Check"
            self.call_button.draw(self.screen)
            self.raise_button.draw(self.screen)
            
            # Draw instruction text
            instruction = "Your turn - choose an action:"
            inst_label = self.font.render(instruction, True, WHITE)
            self.screen.blit(inst_label, (50, SCREEN_HEIGHT - 120))

    def handle_human_action(self, event, player):
        """Handle human player button clicks"""
        if not self.waiting_for_human_action:
            return None
            
        if self.fold_button.handle_event(event):
            self.human_action_result = "fold"
            self.waiting_for_human_action = False
            return "fold"
            
        elif self.call_button.handle_event(event):
            action = "check" if player.is_called else "call"

            self.human_action_result = action
            self.waiting_for_human_action = False
            return action
            
        elif self.raise_button.handle_event(event):
            # For now, just do a simple raise
            self.human_action_result = "raise"
            self.waiting_for_human_action = False
            return "raise"
        
        elif self.quit_save.handle_event(event):
            self.human_action_result = "quit"
            self.waiting_for_human_action = False
            return "quit"
            
        return None

    def wait_for_human_action(self):
        """Set the table to wait for human player input"""
        self.waiting_for_human_action = True
        self.human_action_result = None

    def draw(self):
        """Draw the entire table"""
        # Clear areas that might change
        info_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 200, 200, 100)
        pygame.draw.rect(self.screen, TABLE_COLOR, info_rect)
        
        button_rect = pygame.Rect(0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
        pygame.draw.rect(self.screen, TABLE_COLOR, button_rect)
        
        # Draw all elements
        for i, player in enumerate(self.game.players):
            self.draw_player(player, *player_positions[i])

        if(self.game.game_phase != "waiting"):    
            self.draw_pot_info()
        
        self.draw_action_buttons()