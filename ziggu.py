"""Ziggu maze logic."""
from __future__ import annotations
from collections import deque

DEFAULT_PATH: list[tuple[int, int]] = [
    (0, 3), (0, 2), (0, 1), (0, 0),
    (1, 0), (1, 1), (1, 2), (1, 3),
    (2, 3), (2, 2), (2, 1), (2, 0),
    (3, 3),
]
DEFAULT_START = (0, 0)


class ZigguPuzzle:
    def __init__(self, m: int = 4, path: list[tuple[int, int]] | None = None,
                 start_pos: tuple[int, int] | None = None):
        self.m = m
        self.path = list(path) if path is not None else DEFAULT_PATH
        self.valid_cells = set(self.path)
        self.pos_index = {p: i for i, p in enumerate(self.path)}
        if start_pos is not None:
            self.start_pos = start_pos
        elif path is None:
            self.start_pos = DEFAULT_START
        else:
            self.start_pos = self.path[0]
        self.reset()

    def reset(self):
        self.positions: list[tuple[int, int]] = [self.start_pos for _ in range(self.m)]
        self.moves: int = 0

    def state_string(self) -> str:
        c1 = self.positions[-1][1]
        rs = [self.positions[-(i + 1)][0] for i in range(self.m)]
        return str(c1) + "".join(str(r) for r in rs)

    def _apply_move(self, maze_idx: int, direction: int,
                    positions: list | None = None) -> list[tuple[int, int]] | None:
        pos = positions if positions is not None else self.positions
        cur = pos[maze_idx]
        i = self.pos_index[cur]
        ni = i + direction
        if ni < 0 or ni >= len(self.path):
            return None
        new_pos = self.path[ni]
        new_positions = list(pos)
        new_positions[maze_idx] = new_pos

        dr = new_pos[0] - cur[0]
        dc = new_pos[1] - cur[1]

        if dr != 0 and maze_idx > 0:
            left = new_positions[maze_idx - 1]
            new_left = (left[0], new_pos[0])
            if new_left not in self.valid_cells:
                return None
            if abs(self.pos_index[new_left] - self.pos_index[left]) != 1:
                return None
            if new_left[0] != left[0]:
                return None
            new_positions[maze_idx - 1] = new_left

        if dc != 0 and maze_idx < self.m - 1:
            right = new_positions[maze_idx + 1]
            new_right = (new_pos[1], right[1])
            if new_right not in self.valid_cells:
                return None
            if abs(self.pos_index[new_right] - self.pos_index[right]) != 1:
                return None
            if new_right[1] != right[1]:
                return None
            new_positions[maze_idx + 1] = new_right

        for k in range(self.m - 1):
            if new_positions[k][1] != new_positions[k + 1][0]:
                return None
        return new_positions

    def can_move(self, maze_idx: int, direction: int) -> bool:
        return self._apply_move(maze_idx, direction) is not None

    def move(self, maze_idx: int, direction: int) -> bool:
        result = self._apply_move(maze_idx, direction)
        if result is None:
            return False
        self.positions = result
        self.moves += 1
        return True

    def is_solved(self) -> bool:
        exit_cell = self.path[-1]
        return all(p == exit_cell for p in self.positions)

    def solve(self) -> list[tuple[int, int]] | None:
        """BFS shortest solution. Returns list of (maze_idx, direction) or None."""
        start = tuple(self.positions)
        goal = tuple(self.path[-1] for _ in range(self.m))
        if start == goal:
            return []
        queue: deque[tuple[tuple, list]] = deque([(start, [])])
        visited: set = {start}
        while queue:
            state, moves = queue.popleft()
            pos_list = list(state)
            for maze_idx in range(self.m):
                for direction in (-1, +1):
                    result = self._apply_move(maze_idx, direction, pos_list)
                    if result is not None:
                        new_state = tuple(result)
                        if new_state not in visited:
                            new_moves = moves + [(maze_idx, direction)]
                            if new_state == goal:
                                return new_moves
                            visited.add(new_state)
                            queue.append((new_state, new_moves))
        return None
