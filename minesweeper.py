import random
from collections import deque

MINE = -1

class MinesweeperGame:
    def __init__(self, width, height, mines):
        if width < 1 or height < 1:
            raise ValueError("A pálya mérete legyen legalább 1x1.")
        if mines < 0:
            raise ValueError("Az aknák száma nem lehet negatív.")
        if mines >= width * height:
            raise ValueError("Túl sok akna a pályához.")

        self.width = width
        self.height = height
        self.mines = mines

        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False] * width for _ in range(height)]
        self.flags = [[False] * width for _ in range(height)]
        self.mines_pos = set()

        self.game_over = False
        self.victory = False
        self.exploded_at = None

        self._place_mines()
        self._calculate_numbers()

    @classmethod
    def from_difficulty(cls, difficulty: str):
        if difficulty == "könnyű":
            return cls(9, 9, 10)
        if difficulty == "normális":
            return cls(16, 16, 40)
        if difficulty == "nehéz":
            return cls(30, 16, 99)
        raise ValueError("Ismeretlen nehézség.")

    def _place_mines(self):
        positions = random.sample(
            [(x, y) for x in range(self.width) for y in range(self.height)],
            self.mines
        )
        for x, y in positions:
            self.mines_pos.add((x, y))
            self.board[y][x] = MINE

    def _neighbors(self, x, y):
        for nx in range(x - 1, x + 2):
            for ny in range(y - 1, y + 2):
                if (nx, ny) == (x, y):
                    continue
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield nx, ny

    def _calculate_numbers(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == MINE:
                    continue
                count = 0
                for nx, ny in self._neighbors(x, y):
                    if self.board[ny][nx] == MINE:
                        count += 1
                self.board[y][x] = count

    def dig(self, x, y):
        if self.game_over:
            return
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.flags[y][x] or self.revealed[y][x]:
            return

        if self.board[y][x] == MINE:
            self.revealed[y][x] = True
            self.game_over = True
            self.victory = False
            self.exploded_at = (x, y)
            return

        self._flood_reveal(x, y)
        self._check_victory()

    def _flood_reveal(self, x, y):
        q = deque()
        q.append((x, y))
        while q:
            cx, cy = q.popleft()
            if self.revealed[cy][cx] or self.flags[cy][cx]:
                continue
            self.revealed[cy][cx] = True
            if self.board[cy][cx] == 0:
                for nx, ny in self._neighbors(cx, cy):
                    if not self.revealed[ny][nx] and not self.flags[ny][nx]:
                        q.append((nx, ny))

    def toggle_flag(self, x, y):
        if self.game_over:
            return
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.revealed[y][x]:
            return
        self.flags[y][x] = not self.flags[y][x]
        self._check_victory()

    def _check_victory(self):
        # Győzelem, ha minden nem aknás mező fel van fedve
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != MINE and not self.revealed[y][x]:
                    return
        self.victory = True
        self.game_over = True