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
from graphics import GraphicsManager


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

        # 3 poziomy prędkości: normal, fast, fastest
        self.speed_levels = [400, 200, 80]  # ms pomiędzy generacjami
        self.speed_labels = ["NORMAL", "FAST", "FASTEST"]
        self.speed_index = 0  # startujemy od NORMAL
        self.step_interval = self.speed_levels[self.speed_index]
        self.time_since_last_step = 0

        # Animacja komórek (klatki sprite'a)
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 120  # co ile ms zmienia się klatka animacji

        # Dźwięki
        self.sounds = SoundManager()

        # Grafika (tło + sprite'y komórek)
        self.graphics = GraphicsManager(
            screen_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            cell_size=CELL_SIZE,
        )

        # Czcionka
        self.font = pygame.font.SysFont("consolas", 18)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # OBSŁUGA ZDARZEŃ
    # ------------------------------------------------------------------

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

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    # zwiększamy prędkość
                    if self.speed_index < len(self.speed_levels) - 1:
                        self.speed_index += 1
                        self.step_interval = self.speed_levels[self.speed_index]
                        self.sounds.play("click")

                elif event.key == pygame.K_MINUS:
                    # zmniejszamy prędkość
                    if self.speed_index > 0:
                        self.speed_index -= 1
                        self.step_interval = self.speed_levels[self.speed_index]
                        self.sounds.play("click")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    self.grid.toggle_cell(col, row)
                    self.sounds.play("click")

    # ------------------------------------------------------------------
    # LOGIKA
    # ------------------------------------------------------------------

    def update(self, dt):
        """Aktualizacja logiki gry z użyciem timera + animacja sprite'ów."""
        # Animacja klatek komórek (niezależna od stanu symulacji)
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame += 1

        if not self.simulation_running:
            return

        self.time_since_last_step += dt
        if self.time_since_last_step >= self.step_interval:
            self.time_since_last_step = 0
            self.grid.step()
            self.sounds.play("step")

    # ------------------------------------------------------------------
    # RYSOWANIE
    # ------------------------------------------------------------------

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

    def draw_cells(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid.grid[row][col] == 1:
                    # rysujemy komórkę przez GraphicsManager (sprite/fallback)
                    self.graphics.draw_cell(
                        screen=self.screen,
                        col=col,
                        row=row,
                        frame_index=self.animation_frame,
                        fallback_color=(0, 200, 0),
                    )

    def draw_hud(self):
        status = "RUNNING" if self.simulation_running else "PAUSED"
        speed_label = self.speed_labels[self.speed_index]
        text = (
            f"Generation: {self.grid.generation}  "
            f"Alive: {self.grid.alive_count()}  "
            f"[{status}]  Speed: {speed_label}"
        )
        surf = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(surf, (10, 10))

    def draw(self):
        # TŁO
        self.graphics.draw_background(self.screen)
        # KOMÓRKI
        self.draw_cells()
        # SIATKA
        self.draw_grid()
        # HUD
        self.draw_hud()
        pygame.display.flip()
