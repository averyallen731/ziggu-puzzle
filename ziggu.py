"""Ziggu maze logic: S-shaped maze and m-Ziggu puzzle state."""
from __future__ import annotations


VALID_CELLS: set[tuple[int, int]] = {
    (r, c) for r in (0, 1, 2) for c in (0, 1, 2, 3)
} | {(3, 3)}


S_PATH: list[tuple[int, int]] = [
    (0, 3), (0, 2), (0, 1), (0, 0),
    (1, 0), (1, 1), (1, 2), (1, 3),
    (2, 3), (2, 2), (2, 1), (2, 0),
    (3, 3),
]

POS_INDEX: dict[tuple[int, int], int] = {p: i for i, p in enumerate(S_PATH)}


def neighbors(pos: tuple[int, int]) -> list[tuple[int, int]]:
    i = POS_INDEX[pos]
    result = []
    if i > 0:
        result.append(S_PATH[i - 1])
    if i < len(S_PATH) - 1:
        result.append(S_PATH[i + 1])
    return result


class ZigguPuzzle:
    """m connected Ziggu mazes.

    State: list of (row, col) — one per maze, mazes[0] is leftmost (Maze m in
    slides), mazes[-1] is rightmost (Maze 1, the one with the free column).
    Coupling: row of maze i equals col of maze i+1 (where i+1 is to the right).
    """

    def __init__(self, m: int = 4):
        self.m = m
        self.reset()

    def reset(self):
        self.positions: list[tuple[int, int]] = [(0, 0) for _ in range(self.m)]
        self.moves: int = 0

    def state_string(self) -> str:
        # c_1 r_1 r_2 ... r_m where maze 1 is rightmost.
        rightmost = self.positions[-1]
        c1 = rightmost[1]
        rs = [self.positions[-(i + 1)][0] for i in range(self.m)]
        return str(c1) + "".join(str(r) for r in rs)

    def can_move(self, maze_idx: int, direction: int) -> bool:
        """direction: +1 forward along S-path, -1 backward.

        Moving maze_idx changes its (r, c). Constraint: row(i) == col(i+1) for
        all i (where i+1 is the maze to the right). Adjusting maze_idx's row
        forces the maze to its LEFT (idx-1) to change its column — and its new
        (row, col) must still be a valid cell on the S-path. Changing column
        forces the maze to the RIGHT (idx+1) to change its row similarly.
        """
        new_positions = self._apply_move(maze_idx, direction)
        return new_positions is not None

    def _apply_move(self, maze_idx: int, direction: int) -> list[tuple[int, int]] | None:
        cur = self.positions[maze_idx]
        i = POS_INDEX[cur]
        ni = i + direction
        if ni < 0 or ni >= len(S_PATH):
            return None
        new_pos = S_PATH[ni]
        new_positions = list(self.positions)
        new_positions[maze_idx] = new_pos

        # Propagate coupling. Mazes are indexed 0..m-1 left-to-right.
        # Maze indices in slide labels: maze_idx 0 -> "Maze m", maze_idx m-1 -> "Maze 1".
        # Coupling (slide 33): "current row of maze i equals current column of maze i+1"
        # where "maze i+1" is TO THE RIGHT of "maze i" in slide numbering.
        # In our left-to-right list, "to the right" means higher index.
        # So: positions[k].row == positions[k+1].col for all k in 0..m-2.

        dr = new_pos[0] - cur[0]
        dc = new_pos[1] - cur[1]

        # Propagate row change leftward: positions[k-1].col must equal positions[k].row
        if dr != 0 and maze_idx > 0:
            left = new_positions[maze_idx - 1]
            new_left = (left[0], new_pos[0])
            if new_left not in VALID_CELLS:
                return None
            # must be a legal step on S-path from old left
            if abs(POS_INDEX[new_left] - POS_INDEX[left]) != 1:
                return None
            new_positions[maze_idx - 1] = new_left
            # Further leftward propagation only happens if left's row also changed.
            if new_left[0] != left[0]:
                return None  # changing two rows at once not allowed in one move

        # Propagate column change rightward: positions[k+1].row must equal positions[k].col
        if dc != 0 and maze_idx < self.m - 1:
            right = new_positions[maze_idx + 1]
            new_right = (new_pos[1], right[1])
            if new_right not in VALID_CELLS:
                return None
            if abs(POS_INDEX[new_right] - POS_INDEX[right]) != 1:
                return None
            new_positions[maze_idx + 1] = new_right
            if new_right[1] != right[1]:
                return None

        # Verify coupling holds: positions[k].col == positions[k+1].row
        for k in range(self.m - 1):
            if new_positions[k][1] != new_positions[k + 1][0]:
                return None

        return new_positions

    def move(self, maze_idx: int, direction: int) -> bool:
        new_positions = self._apply_move(maze_idx, direction)
        if new_positions is None:
            return False
        self.positions = new_positions
        self.moves += 1
        return True

    def is_solved(self) -> bool:
        # Rightmost (Maze 1) has reached its exit (3, 3) and all others at (3, 3) too?
        # Per paper: puzzle solved when last maze exits from (3,3).
        # Actually, start is all (0,0); target is all (3,3). Let's treat solved as all at (3,3).
        return all(p == (3, 3) for p in self.positions)
