"""Provided tests for the week-6 studio.

Run: ``python3 test_csp.py``. Prints one line per test. Passing means your
schedule model is a valid timetable AND you have watched two "should-help"
promises fail on the notebook's HARD Sudoku:

  * ``test_lcv_can_hurt`` -- LCV is supposed to speed search up. On HARD it makes
    things WORSE (34,478 -> 56,813 backtrack calls). Value ordering is a gamble
    you pay for on every branch; report what you measure, not what the textbook
    implies. This is the flagged result from the Session-6A notebook.
  * ``test_plain_backtracking_blows_up`` -- plain backtracking is "complete", so
    it "should" solve any solvable puzzle. On HARD it exhausts a 300k-call budget
    without finishing, while forward-checking + MRV + AC-3 solves in ~34k. Watching
    the guarantee fail once is how you learn "complete" says nothing about *when*.
"""
import sys

from csp import (sudoku_csp, backtrack_search, ac3, HARD,
                 solution_consistent, valid_sudoku)
import starter as s


# ---- Task 1: the school schedule (depends on your starter.scheduling_csp) ----

def test_scheduling_is_valid_timetable():
    csp = s.scheduling_csp()
    sol, _ = backtrack_search(csp, use_fc=True, use_mrv=True)
    assert sol not in (None, "TIMEOUT"), "scheduling CSP was unsatisfiable"
    assert set(sol) == set(s.ACTIVITIES), "not every activity was scheduled"
    assert solution_consistent(sol, csp), "two activities share a period"
    assert len(set(sol.values())) == len(s.ACTIVITIES), "periods are not all distinct"
    print(f"  ok  schedule is a complete, all-different timetable ({len(sol)} activities)")


def test_scheduling_sports_before_lunch():
    """The one domain constraint: sports may not be scheduled after lunch."""
    csp = s.scheduling_csp()
    sol, _ = backtrack_search(csp, use_fc=True, use_mrv=True)
    assert sol not in (None, "TIMEOUT")
    assert sol[s.SPORTS] <= s.LUNCH_AFTER, (
        f"sports scheduled in period {sol[s.SPORTS]} -- that is after lunch "
        f"(lunch is after period {s.LUNCH_AFTER}). Did you restrict its domain?"
    )
    print(f"  ok  sports lands in period {sol[s.SPORTS]} (<= {s.LUNCH_AFTER}, before lunch)")


# ---- Engine guarantees on the notebook's HARD Sudoku (no starter needed) -----

def test_ac3_prunes_hard_sudoku():
    csp = sudoku_csp(HARD)
    domains = {v: set(csp.domains[v]) for v in csp.variables}
    before = sum(len(x) for x in domains.values())
    ok = ac3(csp, domains)
    after = sum(len(x) for x in domains.values())
    assert ok, "AC-3 wrongly reported HARD as inconsistent"
    assert after < before, "AC-3 pruned nothing -- it must shrink domains before search"
    print(f"  ok  AC-3 shrinks HARD domains {before} -> {after} "
          f"({before - after} values eliminated before any guess)")


def test_plain_backtracking_blows_up():
    """'Complete' does not mean 'fast'. Plain backtracking exhausts a 300k-call
    budget on HARD; adding inference + ordering solves it in ~34k."""
    plain, cp = backtrack_search(sudoku_csp(HARD), limit=300_000)
    assert plain == "TIMEOUT", (
        f"expected plain backtracking to blow past 300k calls on HARD, "
        f"but it returned {type(plain).__name__} in {cp['calls']:,} calls"
    )
    smart, cs = backtrack_search(sudoku_csp(HARD), use_fc=True, use_mrv=True, use_ac3=True)
    assert valid_sudoku(smart, sudoku_csp(HARD)), "fc+mrv+ac3 did not solve HARD"
    assert cs["calls"] < cp["calls"], "inference should need far fewer calls"
    print(f"  ok  plain backtracking TIMES OUT on HARD; fc+mrv+ac3 solves in "
          f"{cs['calls']:,} calls (the guarantee fails on request)")


def test_lcv_can_hurt():
    """THE flagged result. LCV is 'least constraining value' -- it is supposed to
    help. On HARD it makes search strictly WORSE. Report what you measure."""
    _, no_lcv = backtrack_search(sudoku_csp(HARD), use_fc=True, use_mrv=True)
    _, with_lcv = backtrack_search(sudoku_csp(HARD), use_fc=True, use_mrv=True, use_lcv=True)
    assert with_lcv["calls"] > no_lcv["calls"], (
        f"expected LCV to HURT on HARD, but calls went {no_lcv['calls']:,} -> "
        f"{with_lcv['calls']:,}. The notebook measures 34,478 -> 56,813."
    )
    print(f"  ok  LCV HURTS on HARD: {no_lcv['calls']:,} -> {with_lcv['calls']:,} "
          f"backtrack calls (a heuristic gamble that did not pay back)")


TESTS = [
    test_scheduling_is_valid_timetable,
    test_scheduling_sports_before_lunch,
    test_ac3_prunes_hard_sudoku,
    test_plain_backtracking_blows_up,
    test_lcv_can_hurt,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: scheduling_csp not implemented yet")
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
