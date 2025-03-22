import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.game import PokerGame

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Texas Hold'em Poker")
    clock = pygame.time.Clock()

     # Create and start the game
    poker_game = PokerGame()

    poker_game.show_player_hands()

    running = True
    while running:
        screen.fill((0, 100, 0)) # Fill the screen with green (poker table color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.flip() # Update the display with what was drawn

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()