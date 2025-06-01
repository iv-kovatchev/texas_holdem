import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from client.menu import MenuUI
from client.table import Table
from game.game import PokerGame
from game.player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Texas Hold'em Poker")
    clock = pygame.time.Clock()

    # Show player select menu
    menu = MenuUI(screen)
    menu.run()
    player_data = menu.get_selected_player()

    if not player_data:
        pygame.quit()
        sys.exit()

    # Create actual Player instance
    player = Player(name=player_data["name"], chips=player_data["chips"])

    # Create and start the game
    poker_game = PokerGame(player)
    table = Table(screen, poker_game)

    # Game timing
    round_start_time = pygame.time.get_ticks()
    countdown_seconds = 10

    running = True
    while running:
        now = pygame.time.get_ticks()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle human player actions
            if poker_game.waiting_for_human:
                action = table.handle_human_action(event, player)
                if action:
                    if action == "fold":
                        poker_game.handle_human_action("fold")
                    elif action == "call":
                        poker_game.handle_human_action("call")
                    elif action == "check":
                        poker_game.handle_human_action("check")
                    elif action == "raise":
                        current_bet = poker_game.betting.current_bet
                        raise_amount = current_bet + 50
                        poker_game.handle_human_action("raise", raise_amount)
                    elif action == "quit":
                        poker_game.handle_human_action("quit")
                        pygame.quit()
                        sys.exit()

        # Game state handling
        if poker_game.game_phase == "waiting":
            # Countdown before next round
            elapsed = (now - round_start_time) // 1000
            remaining = max(0, countdown_seconds - elapsed)

            if remaining <= 0:
                # Check if human can still play
                human_player = next(p for p in poker_game.players if not p.is_ai)
                if human_player.chips <= 0:
                    # Game over
                    pass
                else:
                    poker_game.setup_new_round(table)
                    round_start_time = pygame.time.get_ticks()
        else:
            # Game is active - update game state
            poker_game.update_game_state(table)
            
            # Check if round finished
            if poker_game.game_phase == "waiting":
                round_start_time = pygame.time.get_ticks()
                for p in poker_game.players:
                    p.is_called = False

        # Draw everything
        screen.fill((34, 139, 34))
        table.draw()
        table.draw_community_cards()

        if poker_game.showdown_active:
            table.draw_showdown_cards()  # Show all cards face up
        else:
            table.draw_player_cards()    # Normal card display

        # Show game status
        if poker_game.game_phase == "waiting":
            elapsed = (now - round_start_time) // 1000
            remaining = max(0, countdown_seconds - elapsed)
            if remaining > 0:
                font = pygame.font.SysFont(None, 48)
                countdown_text = font.render(f"Next round in: {remaining}", True, (255, 255, 255))
                screen.blit(countdown_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        else:
            # Show current player and phase
            current_player = poker_game.get_current_player()
            if current_player:
                font = pygame.font.SysFont(None, 32)
                turn_text = f"{current_player.name}'s turn"
                
                if poker_game.waiting_for_human:
                    turn_text = "YOUR TURN - choose an action!"
                    
                turn_label = font.render(turn_text, True, (255, 215, 0) if poker_game.waiting_for_human else (255, 255, 255))
                
                screen.blit(turn_label, (SCREEN_WIDTH // 2 - 100, 200))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()