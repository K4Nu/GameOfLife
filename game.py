import sys
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    COLOR_BG,
)


class GameApp:
    """Główna klasa aplikacji – odpowiada za pętlę gry i ogólny flow."""

    def __init__(self):
        # Inicjalizacja pygame
        pygame.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game of Life - pygame (skeleton)")

        self.clock = pygame.time.Clock()

        self.running = True

    def run(self):
        """Główna pętla gry."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


    def handle_events(self):
        """Obsługa zdarzeń (klawiatura, mysz, zamykanie okna)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Aktualizacja logiki gry.
        """
        pass

    def draw(self):
        """Rysowanie na ekran."""
        self.screen.fill(COLOR_BG)

        pygame.display.flip()
