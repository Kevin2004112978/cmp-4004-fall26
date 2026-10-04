"""Week 5 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_alphabeta.py`` passes when this module is imported in place
of ``starter``. Verify with ``studios/_verify_solutions.py`` (which aliases this
file to the name ``starter`` and runs the unmodified test).

DO NOT ship this to students — it is excluded via ``studios/.gitignore``. The
teaching walkthrough lives in ``solution.ipynb`` (which imports this file rather
than re-pasting it, so the two never drift).

The whole trick of the tournament agent is *iterative deepening*: search depth 1,
then 2, then 3, ..., always keeping the best move from the last COMPLETED depth,
and stopping when the clock runs out. That is what turns α-β into a time-bounded
anytime agent — the single thing that most often decides the bracket.
"""
import time
from math import inf

from connect4 import Connect4, alphabeta, MAX, CENTER_FIRST


def order_moves(board):
    """Return this board's legal columns in the order α-β should try them.

    Center-first (``CENTER_FIRST``) is a strong *static* order for Connect-4 —
    central columns take part in more winning lines — so we simply filter the
    static priority list down to the columns that are actually playable. This
    is a legal permutation of ``board.legal_moves()``.
    """
    return [c for c in CENTER_FIRST if c in board.legal_moves()]


def choose_move(board, time_budget_ms) -> int:
    """Return the column MAX should play, using iterative deepening + α-β.

    Contract (the tournament relies on all three):
      1. ALWAYS return a legal column, even if the budget is tiny — seed `best`
         with a legal move before the loop so you never return None.
      2. Never exceed `time_budget_ms` by much — check the clock between depths
         and stop; do not start a depth you cannot afford.
      3. Keep the best move from the last COMPLETED depth.

    We also apply the cheap dynamic-ordering trick the README recommends: after
    each completed depth, move the best column to the front of the order so the
    next (deeper) iteration examines it first and prunes harder.
    """
    deadline = time.perf_counter() + time_budget_ms / 1000.0
    order = order_moves(board)
    best = order[0]                       # rule 1: always have a legal move
    for depth in range(1, 43):
        if time.perf_counter() >= deadline:
            break
        value, move = alphabeta(board, depth, MAX, -inf, inf, [0], order)
        if move is not None:
            best = move                   # rule 3: last completed depth wins
            # dynamic ordering: try last iteration's best move first next time
            order = [best] + [c for c in order if c != best]
    return best


if __name__ == "__main__":
    # Quick smoke test: choose a move on the opening position under a 500 ms budget.
    b = Connect4()
    b.push(3, MAX)          # suppose MIN opened center; MAX replies
    t0 = time.perf_counter()
    move = choose_move(b, 500)
    dt = (time.perf_counter() - t0) * 1000
    print(f"choose_move -> col {move}  ({dt:.0f} ms, budget 500)")
    assert move in b.legal_moves(), "returned an illegal column!"
    print("legal:", b.legal_moves())
