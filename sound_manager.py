import pygame
from utils import resource_path

class SoundManager:
    """
    Klasa odpowiedzialna za ładowanie i odtwarzanie dźwięków.
    Dzięki temu logika gry nie musi znać szczegółów pygame.mixer.
    """

    def __init__(self):
        # Inicjalizacja modułu dźwięku
        try:
            pygame.mixer.init()
        except pygame.error:
            # Brak karty dźwiękowej / problem ze sterownikami
            # Nie rozwalamy gry, po prostu wyłączamy dźwięk.
            self.enabled = False
            self.sounds = {}
            return

        self.enabled = True
        self.sounds = {}

        self._load_sound("click", "click.wav")
        self._load_sound("step", "step.wav")
        self._load_sound("clear", "clear.wav")

    def _load_sound(self, name: str, filename: str):
        """Ładuje pojedynczy dźwięk do słownika."""
        if not self.enabled:
            return

        try:
            path = resource_path(filename)
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except Exception:
            # Jeśli nie ma pliku / problem z formatem – dźwięk będzie po prostu pominięty
            self.sounds[name] = None

    def play(self, name: str):
        """Odtwarza dźwięk o podanej nazwie (jeśli dostępny)."""
        if not self.enabled:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
