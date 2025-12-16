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
    HUD_HEIGHT,  # ← DODANE
    COLOR_HUD_BG,  # ← DODANE
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

        # ========== ZMIENIONE: Plansza bez paska HUD ========== #
        # Plansza zajmuje okno MINUS pasek HUD na dole
        self.game_height = WINDOW_HEIGHT - HUD_HEIGHT  # 600px na planszę
        self.cols = WINDOW_WIDTH // CELL_SIZE
        self.rows = self.game_height // CELL_SIZE  # ← używamy game_height!
        # ====================================================== #

        self.grid = CellGrid(self.cols, self.rows)

        # GraphicsManager dla planszy (bez HUD)
        self.graphics = GraphicsManager(
            (WINDOW_WIDTH, self.game_height),  # ← ZMIENIONE!
            CELL_SIZE
        )

        # Animacja klatek
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 15

        # Stan aplikacji
        self.state = "menu"

        # Prędkość
        self.speed_levels = [400, 200, 80]
        self.speed_labels = ["NORMAL", "FAST", "FASTEST"]
        self.speed_index = 0
        self.step_interval = self.speed_levels[self.speed_index]
        self.time_since_last_step = 0

        # Dźwięki
        self.sounds = SoundManager()

        # Czcionki
        self.font = pygame.font.SysFont("consolas", 16)  # ← mniejsza dla HUD
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)

        # Logika
        self.stagnant_generations = 0
        self.stagnation_threshold = 10

        # Wyniki
        self.current_score = 0
        self.best_score = 0
        self.alive_history = []

        # Fade
        self.fade_alpha = 255
        self.fade_direction = -5

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()

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
                    if self.state == "menu":
                        self.state = "controls"
                        self.sounds.play("click")
                    elif self.state == "controls":
                        self.state = "setup"
                        self.alive_history.clear()
                        self.sounds.play("click")
                    elif self.state == "setup":
                        self.state = "running"
                        self.grid.generation = 0
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.sounds.play("click")
                    elif self.state == "running":
                        self.state = "paused"
                        self.sounds.play("click")
                    elif self.state == "paused":
                        self.state = "running"
                        self.sounds.play("click")
                    elif self.state == "game_over":
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.state = "setup"
                        self.sounds.play("click")

                elif self.state in ("running", "setup", "paused"):
                    if event.key == pygame.K_r:
                        self.grid.randomize()
                        self.grid.generation = 0
                        self.current_score = 0
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.sounds.play("click")
                    elif event.key == pygame.K_c:
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

            elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and self.state in ("setup", "running", "paused")
            ):
                if event.button == 1:
                    x, y = event.pos
                    # ========== ZMIENIONE: Sprawdź czy klik jest NA PLANSZY ========== #
                    if y < self.game_height:  # ← tylko jeśli NIE w HUD
                        col = x // CELL_SIZE
                        row = y // CELL_SIZE
                        self.grid.toggle_cell(col, row)
                        self.stagnant_generations = 0
                        self.alive_history.clear()
                        self.sounds.play("click")
                    # ================================================================= #

    def update(self, dt):
        if self.fade_alpha > 0:
            self.fade_alpha += self.fade_direction
            if self.fade_alpha < 0:
                self.fade_alpha = 0

        # Animacja
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        if self.state != "running":
            return

        self.time_since_last_step += dt
        if self.time_since_last_step >= self.step_interval:
            self.time_since_last_step = 0
            changed = self.grid.step()
            self.sounds.play("step")

            self.current_score = self.grid.generation

            alive_now = self.grid.alive_count()
            self.alive_history.append(alive_now)
            if len(self.alive_history) > 5:
                self.alive_history.pop(0)

            if (
                    len(self.alive_history) == 5
                    and all(a == self.alive_history[0] for a in self.alive_history)
            ):
                if self.current_score > self.best_score:
                    self.best_score = self.current_score
                self.state = "game_over"
                self.sounds.play("clear")

            if changed:
                self.stagnant_generations = 0
            else:
                self.stagnant_generations += 1

    # ========== RYSOWANIE ========== #

    def draw_grid(self):
        # Siatka tylko na planszy (bez HUD)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, self.game_height))
        for y in range(0, self.game_height, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

    def draw_cells(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid.grid[row][col] == 1:
                    self.graphics.draw_cell(
                        self.screen,
                        col,
                        row,
                        frame_index=self.animation_frame,
                        fallback_color=COLOR_CELL
                    )

    def draw_hud(self):
        # ========== NOWY HUD - PASEK NA DOLE ========== #
        if self.state in ("setup", "running", "paused", "game_over"):
            # Tło HUD
            hud_rect = pygame.Rect(0, self.game_height, WINDOW_WIDTH, HUD_HEIGHT)
            pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (0, self.game_height),
                (WINDOW_WIDTH, self.game_height),
                2
            )

            # Status
            if self.state == "running":
                status = "RUNNING"
                status_color = (0, 255, 0)
            elif self.state == "paused":
                status = "PAUSED"
                status_color = (255, 255, 0)
            elif self.state == "setup":
                status = "SETUP"
                status_color = (100, 100, 255)
            else:
                status = "GAME OVER"
                status_color = (255, 0, 0)

            speed_label = self.speed_labels[self.speed_index]

            # Tekst
            text = (
                f"Gen: {self.grid.generation} | "
                f"Alive: {self.grid.alive_count()} | "
                f"[{status}] | "
                f"Speed: {speed_label} | "
                f"Score: {self.current_score} | "
                f"Best: {self.best_score}"
            )

            surf = self.font.render(text, True, COLOR_TEXT)

            # Wycentruj w pasku HUD
            text_y = self.game_height + (HUD_HEIGHT - surf.get_height()) // 2
            self.screen.blit(surf, (10, text_y))
        # ============================================== #

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
                (WINDOW_WIDTH // 2 - surf.get_width() // 2, 200 + i * 25),
            )

    def draw_setup_overlay(self):
        text = self.font.render(
            "SETUP - Click cells, press R for random, SPACE to start",
            True,
            (255, 255, 0),
        )
        # Wyświetl NA PLANSZY (tuż nad HUD)
        self.screen.blit(
            text,
            (WINDOW_WIDTH // 2 - text.get_width() // 2, self.game_height - 30)
        )

    def draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, self.game_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        text = self.font.render(
            "PAUSED - Edit board, use R/C, or press SPACE to resume",
            True,
            (255, 255, 0),
        )
        self.screen.blit(
            text,
            (WINDOW_WIDTH // 2 - text.get_width() // 2, self.game_height // 2)
        )

    def draw_game_over_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, self.game_height))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(
            f"Score: {self.current_score}   Best: {self.best_score}",
            True,
            COLOR_TEXT,
        )
        msg = self.font.render(
            "Press SPACE to return to setup",
            True,
            COLOR_TEXT,
        )

        y_center = self.game_height // 2
        self.screen.blit(
            title,
            (WINDOW_WIDTH // 2 - title.get_width() // 2, y_center - 60),
        )
        self.screen.blit(
            score_text,
            (WINDOW_WIDTH // 2 - score_text.get_width() // 2, y_center),
        )
        self.screen.blit(
            msg,
            (WINDOW_WIDTH // 2 - msg.get_width() // 2, y_center + 40),
        )

    def draw(self):
        # Wypełnij całe okno czarnym
        self.screen.fill(COLOR_BG)

        # TŁO planszy (tylko górna część)
        bg_cropped = pygame.Surface((WINDOW_WIDTH, self.game_height))
        bg_cropped.blit(self.graphics.background, (0, 0))
        self.screen.blit(bg_cropped, (0, 0))

        # PLANSZA
        if self.state in ("setup", "running", "paused", "game_over"):
            self.draw_cells()
            self.draw_grid()

        # MENU/CONTROLS
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "controls":
            self.draw_controls()

        # OVERLAYS
        if self.state == "setup":
            self.draw_setup_overlay()
        elif self.state == "paused":
            self.draw_pause_overlay()
        elif self.state == "game_over":
            self.draw_game_over_overlay()

        # HUD (ZAWSZE na dole)
        self.draw_hud()

        # FADE
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surf, (0, 0))

        pygame.display.flip()