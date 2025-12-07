import sys
import pygame
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    CELL_SIZE,
    FPS,
    COLOR_BG,
    COLOR_GRID,
    COLOR_TEXT,
)
from grid import CellGrid
from sound_manager import SoundManager


class GameApp:
    """Główna klasa aplikacji."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game of Life - pygame")
        self.clock = pygame.time.Clock()
        self.running = True

        # Tworzymy siatkę
        self.cols = WINDOW_WIDTH // CELL_SIZE
        self.rows = WINDOW_HEIGHT // CELL_SIZE
        self.grid = CellGrid(self.cols, self.rows)

        # Stan symulacji
        self.simulation_running = False

        # Dźwięki
        self.sounds = SoundManager()

        # Czcionka
        self.font = pygame.font.SysFont("consolas", 18)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    # start/pauza symulacji
                    self.simulation_running = not self.simulation_running
                    self.sounds.play("click")

                elif event.key == pygame.K_r:
                    # losowa plansza
                    self.grid.randomize()
                    self.sounds.play("click")

                elif event.key == pygame.K_c:
                    # wyczyszczenie planszy
                    self.grid.clear()
                    self.sounds.play("clear")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    self.grid.toggle_cell(col, row)
                    self.sounds.play("click")

    def update(self):
        if self.simulation_running:
            self.grid.step()

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

    def draw_cells(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid.grid[row][col] == 1:
                    pygame.draw.rect(
                        self.screen,
                        (0, 200, 0),
                        (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    )

    def draw_hud(self):
        status = "RUNNING" if self.simulation_running else "PAUSED"
        text = (
            f"Generation: {self.grid.generation}  "
            f"Alive: {self.grid.alive_count()}  "
            f"[{status}]"
        )
        surf = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(surf, (10, 10))

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_cells()
        self.draw_grid()
        self.draw_hud()
        pygame.display.flip()
