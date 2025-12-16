import pygame
import os

# Inicjalizacja pygame
pygame.init()

# Parametry sprite sheet (MUSZĄ zgadzać się z CELL_SIZE w config.py!)
CELL_SIZE = 20
NUM_FRAMES = 4

# Wymiary całego sprite sheet: 4 klatki obok siebie
sheet_width = CELL_SIZE * NUM_FRAMES  # 80 pikseli
sheet_height = CELL_SIZE  # 20 pikseli

# Stwórz powierzchnię z obsługą przezroczystości
sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
sheet.fill((0, 0, 0, 0))  # Wypełnij przezroczystym kolorem

# Definicje 4 klatek animacji - różne kolory i rozmiary
frames = [
    {"color": (255, 50, 50), "radius": 7},  # Klatka 0: Jasna czerwień
    {"color": (200, 0, 0), "radius": 6},  # Klatka 1: Ciemniejsza, mniejsza
    {"color": (255, 100, 100), "radius": 8},  # Klatka 2: Różowa, większa
    {"color": (180, 0, 0), "radius": 7},  # Klatka 3: Ciemna czerwień
]

print("🎨 Tworzenie sprite sheet...")
print(f"   Wymiary: {sheet_width}x{sheet_height} px")
print(f"   Liczba klatek: {NUM_FRAMES}")
print(f"   Rozmiar klatki: {CELL_SIZE}x{CELL_SIZE} px")

# Rysuj każdą klatkę
for i, frame_data in enumerate(frames):
    # Pozycja środka kółka w tej klatce
    center_x = i * CELL_SIZE + CELL_SIZE // 2
    center_y = CELL_SIZE // 2

    # Rysuj wypełnione kółko
    pygame.draw.circle(
        sheet,
        frame_data["color"],
        (center_x, center_y),
        frame_data["radius"]
    )

    # Dodaj białą obwódkę dla lepszego wyglądu
    pygame.draw.circle(
        sheet,
        (255, 255, 255),
        (center_x, center_y),
        frame_data["radius"],
        1  # grubość obwódki
    )

    print(f"   ✓ Klatka {i}: kolor={frame_data['color']}, promień={frame_data['radius']}")

# Upewnij się, że folder assets istnieje
os.makedirs("assets", exist_ok=True)

# Zapisz sprite sheet
output_path = "assets/cell_sprites.png"
pygame.image.save(sheet, output_path)

print(f"\n✅ SUKCES!")
print(f"   Plik zapisany: {output_path}")
print(f"   Możesz go otworzyć i sprawdzić!")

# Sprawdź czy plik rzeczywiście istnieje
if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print(f"   Rozmiar pliku: {size} bajtów")
else:
    print(f"   ⚠️ OSTRZEŻENIE: Plik nie został utworzony!")

pygame.quit()

print("\n🎮 Teraz możesz uruchomić grę: python main.py")