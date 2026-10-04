"""Provided tests for the week-5 studio.

Run: ``python3 test_alphabeta.py``. Prints one line per test.

Two kinds of test live here:

  * STARTER tests exercise your ``choose_move`` / ``order_moves`` in
    ``starter.py``. With the starter unfilled they report "not implemented yet".

  * GUARANTEE tests use the GIVEN engine in ``connect4.py`` and always run. They
    are the point of the week:

      - ``test_alphabeta_matches_minimax_value_with_fewer_nodes`` — α-β returns
        the *identical* value minimax returns while expanding strictly fewer
        nodes. Pruning is not approximation; it discards only provably
        irrelevant branches. THIS is the guarantee that matters.

      - ``test_horizon_effect_shallow_agent_loses`` — a guarantee *failing* on
        purpose. A depth-limited agent cannot see a threat past its horizon, so
        the shallow side loses even though every move it plays is optimal WITH
        RESPECT TO ITS HORIZON. Watching a guarantee fail is how you learn where
        its edge is.
"""
import sys
import time
from math import inf

from connect4 import (Connect4, minimax, alphabeta, play,
                      MAX, MIN, CENTER_FIRST)
import starter as s


# ---- shared fixtures --------------------------------------------------------

def _fresh():
    """The notebook's demo position: MAX and MIN both opened centre."""
    b = Connect4()
    b.push(3, MAX); b.push(3, MIN)
    return b


def _immediate_win_for_max():
    """MAX has cols 0,1,2 on the bottom row and is to move. Dropping col 3
    completes four-in-a-row NOW. A searching agent must take it."""
    b = Connect4()
    for col, p in [(0, MAX), (4, MIN), (1, MAX), (5, MIN), (2, MAX), (6, MIN)]:
        b.push(col, p)
    return b            # winning move = column 3


def _immediate_threat_against_max():
    """MIN has a vertical three in column 3 and MAX is to move. If MAX does not
    play column 3, MIN wins next ply. The only saving move is column 3."""
    b = Connect4()
    for col, p in [(0, MAX), (3, MIN), (1, MAX), (3, MIN), (2, MAX), (3, MIN)]:
        b.push(col, p)
    return b            # blocking move = column 3


# ---- STARTER tests (need starter.py filled in) ------------------------------

def test_order_moves_is_a_legal_permutation():
    b = _fresh()
    order = s.order_moves(b)
    legal = b.legal_moves()
    assert sorted(order) == sorted(legal), (
        f"order_moves must return exactly the legal columns; got {order} "
        f"for legal {legal}")
    print("  ok  order_moves returns the legal columns, reordered")


def test_choose_move_returns_legal_column():
    for b in (Connect4(), _fresh(), _immediate_threat_against_max()):
        move = s.choose_move(b, 300)
        assert move in b.legal_moves(), f"choose_move returned illegal col {move}"
    print("  ok  choose_move always returns a legal column")


def test_choose_move_takes_the_immediate_win():
    b = _immediate_win_for_max()
    move = s.choose_move(b, 500)
    assert move == 3, (
        f"choose_move missed a one-move win: played {move}, should play 3. "
        "This is the exact failure the LLM challenger shows in class — do not "
        "reproduce it with a real search.")
    print("  ok  choose_move takes the immediate win (col 3)")


def test_choose_move_blocks_the_immediate_threat():
    b = _immediate_threat_against_max()
    move = s.choose_move(b, 500)
    assert move == 3, (
        f"choose_move failed to block MIN's vertical threat: played {move}, "
        "must play 3.")
    print("  ok  choose_move blocks the immediate threat (col 3)")


def test_choose_move_respects_the_time_budget():
    # An anytime agent must return promptly under a small budget and never
    # forfeit. We allow generous slack (GC, cold caches) but not a blown clock.
    b = _fresh()
    budget_ms = 300
    t0 = time.perf_counter()
    move = s.choose_move(b, budget_ms)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert move in b.legal_moves()
    assert elapsed_ms < budget_ms + 2000, (
        f"choose_move took {elapsed_ms:.0f} ms on a {budget_ms} ms budget — "
        "it is not stopping between depths. In the tournament this forfeits.")
    print(f"  ok  choose_move respected the budget ({elapsed_ms:.0f} ms / {budget_ms} ms)")


# ---- GUARANTEE tests (given engine; always run) -----------------------------

def test_alphabeta_matches_minimax_value_with_fewer_nodes():
    """The guarantee that matters: same answer, strictly fewer nodes."""
    for depth in (2, 4, 5, 6):
        b1, c1 = _fresh(), [0]
        v_mini, _ = minimax(b1, depth, MAX, c1)
        b2, c2 = _fresh(), [0]
        v_ab, _ = alphabeta(b2, depth, MAX, -inf, inf, c2, CENTER_FIRST)
        assert v_mini == v_ab, (
            f"α-β changed the ANSWER at depth {depth}: {v_mini} vs {v_ab}. "
            "That is a bug — pruning must be exact.")
        assert c2[0] < c1[0], (
            f"α-β did not expand fewer nodes at depth {depth}: "
            f"{c2[0]} !< {c1[0]}")
    print("  ok  α-β returns minimax's value while expanding fewer nodes")


def test_horizon_effect_shallow_agent_loses():
    """A guarantee failing on purpose: depth is strength, so the shallow side
    loses. play(2, 5) -> MIN (deep) wins; play(6, 4) -> MAX (deep) wins.

    Note (from the notebook): play(5, 5) -> MIN also wins, but that is an
    artifact of ``evaluate()`` at equal depth, NOT the horizon effect, so we do
    not assert on it here.
    """
    w_shallow_max, _ = play(2, 5)
    assert w_shallow_max == MIN, (
        f"expected the depth-5 side (MIN) to beat the depth-2 side; got {w_shallow_max}")
    w_deep_max, _ = play(6, 4)
    assert w_deep_max == MAX, (
        f"expected the depth-6 side (MAX) to beat the depth-4 side; got {w_deep_max}")
    print("  ok  horizon effect: the shallow agent loses to the deeper one")


TESTS = [
    test_order_moves_is_a_legal_permutation,
    test_choose_move_returns_legal_column,
    test_choose_move_takes_the_immediate_win,
    test_choose_move_blocks_the_immediate_threat,
    test_choose_move_respects_the_time_budget,
    test_alphabeta_matches_minimax_value_with_fewer_nodes,
    test_horizon_effect_shallow_agent_loses,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: starter not implemented yet")
            failed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    if failed:
        print(f"\n{failed}/{len(TESTS)} failed")
        sys.exit(1)
    print(f"\nall {len(TESTS)} tests pass")


if __name__ == "__main__":
    main()
