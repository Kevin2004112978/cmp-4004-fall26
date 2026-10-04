"""Week 5 studio — the game engine (GIVEN to you; do not modify).

This is the Connect-4 board, ``minimax``, and ``alphabeta`` from the Session-A
notebook, verbatim, plus the static move orderings and the ``play`` self-play
harness used in the three live demonstrations. Week 5 is about *adversarial
search* and *move ordering*, not about re-deriving the board — so the engine is
provided. You write your tournament agent (``choose_move``) in ``starter.py``.

Key design choices carried over from the notebook:

    * ``push`` / ``pop`` MUTATE in place. At depth 7 a copying implementation
      allocates hundreds of thousands of boards and dominates the runtime.
    * ``evaluate()`` returns a value from MAX's point of view: +10_000 for a MAX
      win, -10_000 for a MIN win, and a windowed material+centre score otherwise.
    * ``alphabeta`` takes an optional ``order`` — a column priority list — which
      is the entire subject of Demonstration 2.

Interface (identical to the notebook):
    board.legal_moves()            -> list[int] of playable columns
    board.push(col, player)        -> drop a disc (player is MAX or MIN)
    board.pop(col)                 -> undo the last disc in that column
    board.winner()                 -> MAX / MIN / None
    board.full()                   -> bool
    board.evaluate()               -> int, from MAX's point of view
    minimax(board, depth, player, counter)                 -> (value, move)
    alphabeta(board, depth, player, alpha, beta, counter, order=None) -> (value, move)
"""
import time
from math import inf

ROWS, COLS, WIN = 6, 7, 4
MAX, MIN = 1, -1        # MAX is the search's own side


class Connect4:
    def __init__(self):
        self.grid = [[0] * COLS for _ in range(ROWS)]
        self.heights = [0] * COLS      # how many discs in each column
        self.last = None

    # ---- mechanics ---------------------------------------------------
    def legal_moves(self):
        return [c for c in range(COLS) if self.heights[c] < ROWS]

    def push(self, col, player):
        r = self.heights[col]
        self.grid[r][col] = player
        self.heights[col] += 1
        self.last = (r, col, player)

    def pop(self, col):
        self.heights[col] -= 1
        r = self.heights[col]
        self.grid[r][col] = 0

    def full(self):
        return all(h == ROWS for h in self.heights)

    # ---- terminal test ----------------------------------------------
    def _line(self, r, c, dr, dc):
        p = self.grid[r][c]
        if p == 0:
            return None
        for k in range(1, WIN):
            rr, cc = r + dr * k, c + dc * k
            if not (0 <= rr < ROWS and 0 <= cc < COLS) or self.grid[rr][cc] != p:
                return None
        return p

    def winner(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == 0:
                    continue
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    w = self._line(r, c, dr, dc)
                    if w:
                        return w
        return None

    # ---- evaluation --------------------------------------------------
    def _windows(self):
        for r in range(ROWS):
            for c in range(COLS):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    rr, cc = r + dr * (WIN - 1), c + dc * (WIN - 1)
                    if 0 <= rr < ROWS and 0 <= cc < COLS:
                        yield [self.grid[r + dr * k][c + dc * k] for k in range(WIN)]

    def evaluate(self):
        """Heuristic value from MAX's point of view."""
        w = self.winner()
        if w == MAX:
            return 10_000
        if w == MIN:
            return -10_000
        score = 0
        for win in self._windows():
            mx, mn = win.count(MAX), win.count(MIN)
            if mx and mn:
                continue                       # blocked, worthless to both
            if mx:
                score += {1: 1, 2: 10, 3: 50}[mx]
            elif mn:
                score -= {1: 1, 2: 10, 3: 50}[mn]
        # central columns are worth more -- classic Connect-4 domain knowledge
        for r in range(ROWS):
            if self.grid[r][COLS // 2] == MAX:
                score += 3
            elif self.grid[r][COLS // 2] == MIN:
                score -= 3
        return score

    def __str__(self):
        sym = {0: ".", MAX: "X", MIN: "O"}
        rows = ["|" + " ".join(sym[self.grid[r][c]] for c in range(COLS)) + "|"
                for r in reversed(range(ROWS))]
        return "\n".join(rows) + "\n " + " ".join(str(c) for c in range(COLS))


# ---- minimax ----------------------------------------------------------------

def minimax(board, depth, player, counter):
    counter[0] += 1
    winner = board.winner()
    if winner is not None or depth == 0 or board.full():
        return board.evaluate(), None

    best_move = None
    if player == MAX:
        best = -inf
        for move in board.legal_moves():
            board.push(move, MAX)
            value, _ = minimax(board, depth - 1, MIN, counter)
            board.pop(move)
            if value > best:
                best, best_move = value, move
        return best, best_move
    else:
        best = inf
        for move in board.legal_moves():
            board.push(move, MIN)
            value, _ = minimax(board, depth - 1, MAX, counter)
            board.pop(move)
            if value < best:
                best, best_move = value, move
        return best, best_move


# ---- alpha-beta -------------------------------------------------------------

def alphabeta(board, depth, player, alpha, beta, counter, order=None):
    counter[0] += 1
    winner = board.winner()
    if winner is not None or depth == 0 or board.full():
        return board.evaluate(), None

    moves = board.legal_moves()
    if order is not None:
        moves = [c for c in order if c in moves]

    best_move = None
    if player == MAX:
        best = -inf
        for move in moves:
            board.push(move, MAX)
            value, _ = alphabeta(board, depth - 1, MIN, alpha, beta, counter, order)
            board.pop(move)
            if value > best:
                best, best_move = value, move
            alpha = max(alpha, best)
            if alpha >= beta:
                break                      # <-- the entire optimization
        return best, best_move
    else:
        best = inf
        for move in moves:
            board.push(move, MIN)
            value, _ = alphabeta(board, depth - 1, MAX, alpha, beta, counter, order)
            board.pop(move)
            if value < best:
                best, best_move = value, move
            beta = min(beta, best)
            if alpha >= beta:
                break
        return best, best_move


# ---- static move orderings (Demonstration 2) --------------------------------
# Central columns are strong in Connect-4, so center-first is a good static
# order. These are the exact orderings from the notebook.
CENTER_FIRST = [3, 2, 4, 1, 5, 0, 6]
LEFT_TO_RIGHT = [0, 1, 2, 3, 4, 5, 6]
WORST = [0, 6, 1, 5, 2, 4, 3]


# ---- self-play harness (Demonstration 3) ------------------------------------

def play(depth_max, depth_min, order=CENTER_FIRST, max_plies=42, verbose=False):
    """MAX vs MIN, both alpha-beta, different depths. Returns (winner, board)."""
    board = Connect4()
    player = MAX
    for ply in range(max_plies):
        if board.winner() is not None or board.full():
            break
        d = depth_max if player == MAX else depth_min
        _, move = alphabeta(board, d, player, -inf, inf, [0], order)
        if move is None:
            break
        board.push(move, player)
        if verbose:
            print(f"ply {ply}: {'MAX' if player == MAX else 'MIN'} -> col {move}")
        player = -player
    return board.winner(), board


if __name__ == "__main__":
    # Demonstration 1 — same answer, far fewer nodes.
    def fresh():
        b = Connect4()
        b.push(3, MAX); b.push(3, MIN)
        return b

    print(f"  {'depth':>6}{'minimax':>12}{'alpha-beta':>13}{'speedup':>10}")
    print("  " + "-" * 45)
    for depth in (2, 4, 5, 6):
        b1, c1 = fresh(), [0]
        v1, _ = minimax(b1, depth, MAX, c1)
        b2, c2 = fresh(), [0]
        v2, _ = alphabeta(b2, depth, MAX, -inf, inf, c2)
        assert v1 == v2, f"VALUES DIFFER at depth {depth}: {v1} vs {v2}"
        print(f"  {depth:>6}{c1[0]:>12,}{c2[0]:>13,}{c1[0] / c2[0]:>9.1f}x")
    print("\nAll values identical. Pruning changed the COST, not the ANSWER.")
