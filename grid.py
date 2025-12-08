# grid.py

import random


class CellGrid:
    """Reprezentuje siatkę komórek Game of Life."""

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.generation = 0

    def clear(self):
        """Czyści siatkę (wszystkie komórki martwe)."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.generation = 0

    def randomize(self, probability=0.25):
        """Losowo wypełnia siatkę żywymi komórkami."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() < probability else 0
        self.generation = 0

    def toggle_cell(self, col, row):
        """Przełącza stan komórki (żywa/martwa)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1 - self.grid[row][col]

    def count_alive_neighbors(self, col, row):
        """Liczy liczbę żywych sąsiadów wokół komórki."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    count += self.grid[nr][nc]
        return count

    def step(self) -> bool:
        """
        Oblicza kolejne pokolenie według zasad Conwaya.
        Zwraca True, jeśli stan planszy się zmienił, inaczej False.
        """
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        changed = False

        for r in range(self.rows):
            for c in range(self.cols):
                alive = self.grid[r][c] == 1
                neighbors = self.count_alive_neighbors(c, r)
                if alive and neighbors in (2, 3):
                    new_grid[r][c] = 1
                elif not alive and neighbors == 3:
                    new_grid[r][c] = 1
                else:
                    new_grid[r][c] = 0

                if new_grid[r][c] != self.grid[r][c]:
                    changed = True

        self.grid = new_grid
        self.generation += 1
        return changed

    def alive_count(self):
        """Zwraca liczbę żywych komórek."""
        return sum(sum(row) for row in self.grid)
