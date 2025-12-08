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
    COLOR_CELL,
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

        # Stan aplikacji:
        # menu -> controls -> setup -> running <-> paused -> game_over
        self.state = "menu"

        # 3 poziomy prędkości
        self.speed_levels = [400, 200, 80]
        self.speed_labels = ["NORMAL", "FAST", "FASTEST"]
        self.speed_index = 0
        self.step_interval = self.speed_levels[self.speed_index]
        self.time_since_last_step = 0

        # Dźwięki
        self.sounds = SoundManager()

        # Czcionki
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)

        # Logika stagnacji (zostawione, ale nie używane do GAME OVER)
        self.stagnant_generations = 0
        self.stagnation_threshold = 10

        # Wyniki
        self.current_score = 0
        self.best_score = 0

        # Historia liczby żywych komórek
        self.alive_history = []  # przechowuje ostatnie wartości alive_count

        # Efekt przejścia (fade na starcie)
        self.fade_alpha = 255
        self.fade_direction = -5

    # ------------------------------------------------------------------
    # GŁÓWNA PĘTLA
    # ------------------------------------------------------------------

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
                    # obsługa różnych ekranów
                    if self.state == "menu":
                        # z menu → ekran z kontrolkami
                        self.state = "controls"
                        self.sounds.play("click")

                    elif self.state == "controls":
                        # po kontrolkach → SETUP (plansza stoi, można klikać)
                        self.state = "setup"
                        self.alive_history.clear()
                        self.sounds.play("click")

                    elif self.state == "setup":
                        # start symulacji z ustawioną planszą
                        self.state = "running"
                        # resetujemy licznik generacji i wyniku na start rozgrywki
                        self.grid.generation = 0
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.sounds.play("click")

                    elif self.state == "running":
                        # pauza w trakcie gry
                        self.state = "paused"
                        self.sounds.play("click")

                    elif self.state == "paused":
                        # powrót do gry
                        self.state = "running"
                        self.sounds.play("click")

                    elif self.state == "game_over":
                        # restart: przechodzimy do SETUP, planszę zostawiamy
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.state = "setup"
                        self.sounds.play("click")

                # Sterowanie R/C/+/- dostępne w running, setup i paused
                elif self.state in ("running", "setup", "paused"):
                    if event.key == pygame.K_r:
                        # losowa plansza
                        self.grid.randomize()
                        self.grid.generation = 0
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.sounds.play("click")

                    elif event.key == pygame.K_c:
                        # wyczyszczenie planszy
                        self.grid.clear()
                        self.grid.generation = 0
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.sounds.play("clear")

                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        if self.speed_index < len(self.speed_levels) - 1:
                            self.speed_index += 1
                            self.step_interval = self.speed_levels[self.speed_index]
                            self.sounds.play("click")

                    elif event.key == pygame.K_MINUS:
                        if self.speed_index > 0:
                            self.speed_index -= 1
                            self.step_interval = self.speed_levels[self.speed_index]
                            self.sounds.play("click")

            # Klikanie myszą dostępne w setup, running i paused
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and self.state in ("setup", "running", "paused")
            ):
                if event.button == 1:
                    x, y = event.pos
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    self.grid.toggle_cell(col, row)
                    self.stagnant_generations = 0
                    self.alive_history.clear()
                    self.sounds.play("click")

    # ------------------------------------------------------------------
    # LOGIKA
    # ------------------------------------------------------------------

    def update(self, dt):
        # Fade na starcie
        if self.fade_alpha > 0:
            self.fade_alpha += self.fade_direction
            if self.fade_alpha < 0:
                self.fade_alpha = 0

        # Symulacja Game of Life działa TYLKO w stanie running
        if self.state != "running":
            return

        self.time_since_last_step += dt
        if self.time_since_last_step >= self.step_interval:
            self.time_since_last_step = 0
            changed = self.grid.step()
            self.sounds.play("step")

            # score = liczba generacji w tej rozgrywce
            self.current_score = self.grid.generation

            # --- LOGIKA GAME OVER NA PODSTAWIE LICZBY ŻYWYCH KOMÓREK --- #
            alive_now = self.grid.alive_count()
            self.alive_history.append(alive_now)
            if len(self.alive_history) > 5:
                self.alive_history.pop(0)

            if (
                len(self.alive_history) == 5
                and all(a == self.alive_history[0] for a in self.alive_history)
            ):
                # przez 5 generacji z rzędu tyle samo żywych → GAME OVER
                if self.current_score > self.best_score:
                    self.best_score = self.current_score

                self.state = "game_over"
                self.sounds.play("clear")

            # stara logika stagnacji możesz zostawić jako ciekawostkę, ale nie używać
            if changed:
                self.stagnant_generations = 0
            else:
                self.stagnant_generations += 1

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
                    x = col * CELL_SIZE + CELL_SIZE // 2
                    y = row * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, COLOR_CELL, (x, y), CELL_SIZE // 3)

    def draw_hud(self):
        if self.state in ("setup", "running", "paused", "game_over"):
            if self.state == "running":
                status = "RUNNING"
            elif self.state == "paused":
                status = "PAUSED"
            elif self.state == "setup":
                status = "SETUP"
            else:
                status = "GAME OVER"

            speed_label = self.speed_labels[self.speed_index]
            text_main = (
                f"Generation: {self.grid.generation}  "
                f"Alive: {self.grid.alive_count()}  "
                f"[{status}]  Speed: {speed_label}  "
                f"Score: {self.current_score}  Best: {self.best_score}"
            )
            surf_main = self.font.render(text_main, True, COLOR_TEXT)
            self.screen.blit(surf_main, (10, 10))

    def draw_menu(self):
        title = self.title_font.render("Conway's Game of Life", True, (255, 0, 0))
        msg = self.font.render("Press SPACE to view controls", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        self.screen.blit(msg, (WINDOW_WIDTH // 2 - msg.get_width() // 2, 280))

    def draw_controls(self):
        title = self.title_font.render("Controls", True, (255, 0, 0))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))

        controls = [
            "SPACE - Menu -> Controls -> Setup -> Run -> Pause -> Run / Game Over",
            "R - Randomize board (SETUP / RUNNING / PAUSED)",
            "C - Clear board (SETUP / RUNNING / PAUSED)",
            "Mouse Left - Toggle cell (SETUP / RUNNING / PAUSED)",
            "+ / - - Adjust speed (in RUNNING)",
            "ESC - Exit",
            "",
            "Press SPACE to go to board setup",
        ]

        for i, text in enumerate(controls):
            surf = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(
                surf,
                (WINDOW_WIDTH // 2 - surf.get_width() // 2, 200 + i * 30),
            )

    def draw_setup_overlay(self):
        text = self.font.render(
            "SETUP - Click to toggle cells, or press R for random. SPACE to start.",
            True,
            COLOR_TEXT,
        )
        self.screen.blit(
            text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT - 40)
        )

    def draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        text = self.font.render(
            "PAUSED - Edit board, use R/C, or press SPACE to resume",
            True,
            COLOR_TEXT,
        )
        self.screen.blit(
            text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2)
        )

    def draw_game_over_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(
            f"Score: {self.current_score}   Best score: {self.best_score}",
            True,
            COLOR_TEXT,
        )
        msg = self.font.render(
            "Press SPACE to return to setup with this board",
            True,
            COLOR_TEXT,
        )

        self.screen.blit(
            title,
            (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 60),
        )
        self.screen.blit(
            score_text,
            (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2),
        )
        self.screen.blit(
            msg,
            (WINDOW_WIDTH // 2 - msg.get_width() // 2, WINDOW_HEIGHT // 2 + 40),
        )

    def draw(self):
        self.screen.fill(COLOR_BG)

        # plansza widoczna w setup, running, paused, game_over
        if self.state in ("setup", "running", "paused", "game_over"):
            self.draw_cells()
            self.draw_grid()
            self.draw_hud()

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "controls":
            self.draw_controls()
        elif self.state == "setup":
            self.draw_setup_overlay()
        elif self.state == "paused":
            self.draw_pause_overlay()
        elif self.state == "game_over":
            self.draw_game_over_overlay()

        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surf, (0, 0))

        pygame.display.flip()
