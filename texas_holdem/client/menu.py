import pygame
from client.player_data import get_valid_players, update_player
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

pygame.init()

FONT = pygame.font.SysFont(None, 32)
BG_COLOR = (34, 139, 34)

class MenuUI:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Texas Hold'em - Player Select")
        self.clock = pygame.time.Clock()
        self.input_active = False
        self.input_box = pygame.Rect(50, 60, 300, 32)
        self.input_text = ""
        self.selected_index = None
        self.players = get_valid_players()
        self.running = True

    def draw_text(self, text, x, y, color=(255,255,255)):
        self.screen.blit(FONT.render(text, True, color), (x, y))

    def run(self):
        while self.running:
            self.screen.fill(BG_COLOR)
            self.handle_events()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)

    def draw_ui(self):
        self.draw_text("Create New Player:", 50, 30)
        # Highlight input box if active
        box_color = (255, 255, 0) if self.input_active else (255, 255, 255)
        pygame.draw.rect(self.screen, box_color, self.input_box, 2)
        
        # Draw the typed text
        self.draw_text(self.input_text, self.input_box.x + 5, self.input_box.y + 5, (0, 0, 0))

        self.draw_text("Select Existing Player:", 50, 120)
        for idx, player in enumerate(self.players):
            y = 160 + idx * 35
            color = (255, 215, 0) if idx == self.selected_index else (255, 255, 255)
            self.draw_text(f"{player['name']} ({player['chips']} chips)", 60, y, color)

        # Buttons
        self.draw_text("[Enter] Start Game", 50, SCREEN_HEIGHT - 80)
        self.draw_text("[Esc] Quit", 1040, SCREEN_HEIGHT - 80)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        update_player(self.input_text.strip(), 1000)
                        self.players = get_valid_players()
                        self.selected_index = len(self.players) - 1
                        self.input_text = ""
                    elif self.selected_index is not None:
                        player = self.players[self.selected_index]
                        print(f"Start game with: {player['name']} ({player['chips']} chips)")
                        self.running = False
                        self.selected_player = player

                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]

                elif event.key == pygame.K_UP:
                    if self.selected_index is not None:
                        self.selected_index = max(0, self.selected_index - 1)

                elif event.key == pygame.K_DOWN:
                    if self.selected_index is not None:
                        self.selected_index = min(len(self.players) - 1, self.selected_index + 1)
                    elif self.players:
                        self.selected_index = 0

                else:
                    if len(self.input_text) < 15 and self.input_active:
                        self.input_text += event.unicode
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_box.collidepoint(event.pos):
                    self.input_active = True
                else:
                    self.input_active = False

    def get_selected_player(self):
        return getattr(self, "selected_player", None)