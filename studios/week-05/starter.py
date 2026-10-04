"""Week 5 studio — your tournament agent.

The engine (board, ``minimax``, ``alphabeta``, the static orderings, ``play``)
is GIVEN in ``connect4.py`` and must not be modified. Your job is the one thing
the tournament actually enforces: a **time-bounded, anytime** agent.

    def choose_move(board, time_budget_ms) -> int

Hard tournament rules (from the plan): 500 ms per move, no external processes,
no network, no opening book larger than 20 positions. The reference bracket runs
a plain α-β agent at depth 6 — beat it with *depth*, not cleverness.

Fill in the two functions below. Then run ``python3 test_alphabeta.py``; the
starter-dependent tests must pass and the two *guarantee* tests (which use the
given engine) show you what α-β and the horizon effect actually buy you.

Why iterative deepening rather than a fixed depth? Because a fixed depth either
finishes early (wasting budget) or blows the 500 ms limit and forfeits. Iterative
deepening searches depth 1, then 2, then 3, ... keeping the best move from the
last COMPLETED depth, and stops when the clock runs out. It is what turns α-β
into a time-bounded anytime agent — the single most important thing in the
tournament, per the plan.
"""
import time
from math import inf

from connect4 import Connect4, alphabeta, MAX, CENTER_FIRST


def order_moves(board):
    """Return this board's legal columns in the order α-β should try them.

    α-β's best case (O(b^(m/2)) — double the reachable depth) requires examining
    strong moves first. A good *static* order for Connect-4 is center-first
    (``CENTER_FIRST`` in connect4.py). Fast-finishing pairs: try a *dynamic*
    order that puts last iteration's best move first (see ``choose_move``).
    """
    # TODO: return the legal moves of `board`, best-first.
    #   Minimum: [c for c in CENTER_FIRST if c in board.legal_moves()]
    raise NotImplementedError


def choose_move(board, time_budget_ms) -> int:
    """Return the column MAX should play, using iterative deepening + α-β.

    Contract (the tournament relies on all three):
      1. ALWAYS return a legal column, even if the budget is tiny — seed `best`
         with a legal move before the loop so you never return None.
      2. Never exceed `time_budget_ms` by much — check the clock between depths
         and stop; do not start a depth you cannot afford to be interrupted in.
      3. Keep the best move from the last COMPLETED depth (a half-finished depth
         can return a worse move than the one below it).

    You call the GIVEN ``alphabeta(board, depth, MAX, -inf, inf, counter, order)``
    at increasing depths. Pass ``order=order_moves(board)`` so pruning bites.
    """
    # TODO: implement iterative deepening.
    #   deadline = time.perf_counter() + time_budget_ms / 1000.0
    #   order = order_moves(board)
    #   best = order[0]                       # rule 1: always have a legal move
    #   for depth in range(1, 43):
    #       if time.perf_counter() >= deadline:
    #           break
    #       value, move = alphabeta(board, depth, MAX, -inf, inf, [0], order)
    #       if move is not None:
    #           best = move                   # rule 3: last completed depth wins
    #   return best
    raise NotImplementedError


if __name__ == "__main__":
    # Quick smoke test: choose a move on the opening position under a 500 ms budget.
    b = Connect4()
    b.push(3, MAX)          # suppose MIN opened center; MAX replies
    try:
        t0 = time.perf_counter()
        move = choose_move(b, 500)
        dt = (time.perf_counter() - t0) * 1000
        print(f"choose_move -> col {move}  ({dt:.0f} ms, budget 500)")
        assert move in b.legal_moves(), "returned an illegal column!"
        print("legal:", b.legal_moves())
    except NotImplementedError:
        print("choose_move / order_moves not implemented yet — fill them in.")
