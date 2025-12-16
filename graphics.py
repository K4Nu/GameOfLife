import pygame
from utils import resource_path
import os

class SpriteSheet:
    """
    Prosty komponent do pracy ze sprite sheetem.
    Umożliwia wycinanie klatek (kopiowanie fragmentów obrazu).
    """

    def __init__(self, filename: str, frame_width: int, frame_height: int):
        image_path = resource_path(filename)
        self.sheet = pygame.image.load(image_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.columns = self.sheet.get_width() // frame_width
        self.rows = self.sheet.get_height() // frame_height
        self.total_frames = self.columns * self.rows

    def get_frame(self, index: int) -> pygame.Surface:
        """Zwraca wyciętą klatkę o danym indeksie."""
        index = index % self.total_frames
        col = index % self.columns
        row = index // self.columns

        rect = pygame.Rect(
            col * self.frame_width,
            row * self.frame_height,
            self.frame_width,
            self.frame_height,
        )

        frame_surf = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surf.blit(self.sheet, (0, 0), rect)
        return frame_surf


class GraphicsManager:
    """
    Odpowiada za zasoby graficzne:
    - tło
    - sprite'y komórek
    """

    def __init__(self, screen_size: tuple[int, int], cell_size: int):
        self.width, self.height = screen_size
        self.cell_size = cell_size

        # Ładowanie tła
        self.background = self._load_background()

        # Ładowanie sprite sheet komórek
        self.cell_sprite_sheet, self.use_sprites = self._load_cell_sprites()

    # ----------------- ŁADOWANIE ZASOBÓW ----------------- #

    def _load_background(self) -> pygame.Surface:
        try:
            path = resource_path("background.png")
            print(f"🔍 Trying to load background from: {path}")
            print(f"📁 File exists: {os.path.exists(path)}")

            bg_image = pygame.image.load(path).convert()
            bg_image = pygame.transform.scale(bg_image, (self.width, self.height))
            print("✅ Background loaded successfully!")
            return bg_image
        except Exception as e:
            print(f"❌ Failed to load background: {e}")
            # awaryjne tło
            fallback = pygame.Surface((self.width, self.height))
            fallback.fill((10, 10, 40))
            return fallback

    def _load_cell_sprites(self) -> tuple[SpriteSheet | None, bool]:
        try:
            sheet = SpriteSheet("cell_sprites.png", self.cell_size, self.cell_size)
            return sheet, True
        except Exception:
            # jeśli brak pliku / problem – rysujemy prostokąty zamiast sprite'ów
            return None, False

    # ----------------- RYSOWANIE ----------------- #

    def draw_background(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))

    def draw_cell(
        self,
        screen: pygame.Surface,
        col: int,
        row: int,
        frame_index: int,
        fallback_color: tuple[int, int, int],
    ) -> None:
        x = col * self.cell_size
        y = row * self.cell_size

        if self.use_sprites and self.cell_sprite_sheet is not None:
            frame = self.cell_sprite_sheet.get_frame(frame_index)
            screen.blit(frame, (x, y))
        else:
            # fallback – prostokąt
            pygame.draw.rect(
                screen,
                fallback_color,
                pygame.Rect(x, y, self.cell_size, self.cell_size),
            )
