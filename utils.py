import os


def resource_path(*parts: str) -> str:
    """
    Zwraca absolutną ścieżkę do pliku z katalogu 'assets'.

    resource_path("click.wav") ->
        <katalog_projektu>/assets/click.wav
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets", *parts)
