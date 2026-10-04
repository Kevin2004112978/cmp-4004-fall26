"""ckgen-style soundness check for the week-6 puzzle bank (puzzles.json).

For EVERY puzzle this script:

  1. builds the CSP from the recorded spec via the GIVEN ``logic_lm.build_csp``
     (the same machinery arm B uses, so a puzzle that passes here is a puzzle the
     studio's plumbing can actually solve);
  2. enumerates ALL complete, consistent assignments by brute force -- independent
     of ``backtrack_search`` -- and asserts there is EXACTLY ONE (no ambiguous key);
  3. asserts that single solution equals the recorded ``gold``;
  4. re-solves with the course solver ``csp.backtrack_search`` (fc + MRV, the same
     call ``classify_arm_b`` makes) and asserts it returns the same answer.

Also checks the worked-example contract: exactly 5 puzzles marked
``worked_example`` and that the first three match ``logic_lm.EXAMPLE_PUZZLES``.

Run: ``python3 _verify_puzzles.py``. Prints ``ALL 20 PUZZLES SOUND`` on success;
exits non-zero (naming the offending puzzle) otherwise.
"""
import itertools
import sys

from csp import backtrack_search
from logic_lm import build_csp, EXAMPLE_PUZZLES, load_puzzles


def all_solutions(csp):
    """Every complete assignment that satisfies the spec, by exhaustive product.

    ``build_csp`` has already folded the unary constraints (eq pins, X!=value
    exclusions) into ``csp.domains``; the only remaining structure is the list of
    binary ``neq`` pairs in ``csp._binary`` (alldiff expands to these too). So a
    full solution is any tuple over the domains that violates no binary neq. This
    is a second, independent solver -- if it and backtrack_search ever disagreed,
    one of them would be wrong; we assert they agree."""
    variables = csp.variables
    domains = [sorted(csp.domains[v], key=repr) for v in variables]
    sols = []
    for combo in itertools.product(*domains):
        assignment = dict(zip(variables, combo))
        if all(assignment[a] != assignment[b]
               for (a, b, kind) in csp._binary if kind == "neq"):
            sols.append(assignment)
    return sols


def verify_one(p):
    pid = p.get("id", "<?>")
    csp = build_csp(p["spec"])

    sols = all_solutions(csp)
    assert len(sols) >= 1, f"{pid}: NO solution -- puzzle is over-constrained"
    assert len(sols) == 1, (
        f"{pid}: AMBIGUOUS -- {len(sols)} solutions, e.g. {sols[0]} and {sols[1]}"
    )
    only = sols[0]
    assert only == p["gold"], (
        f"{pid}: unique solution {only} does NOT match recorded gold {p['gold']}"
    )

    # The course solver (same switches classify_arm_b uses) must agree.
    sol, _ = backtrack_search(csp, use_fc=True, use_mrv=True)
    assert sol not in (None, "TIMEOUT"), f"{pid}: backtrack_search failed to solve"
    assert sol == p["gold"], (
        f"{pid}: backtrack_search returned {sol}, not gold {p['gold']}"
    )
    return only


def main():
    puzzles = load_puzzles()
    n = len(puzzles)
    if n != 20:
        print(f"FAIL expected 20 puzzles, found {n}")
        sys.exit(1)

    ids = [p.get("id") for p in puzzles]
    if len(set(ids)) != n:
        print(f"FAIL duplicate puzzle ids: {ids}")
        sys.exit(1)

    worked = [p for p in puzzles if p.get("worked_example")]
    if len(worked) != 5:
        print(f"FAIL expected 5 worked examples, found {len(worked)}: "
              f"{[p['id'] for p in worked]}")
        sys.exit(1)

    # The three shipped EXAMPLE_PUZZLES must still be represented verbatim.
    for i, ex in enumerate(EXAMPLE_PUZZLES):
        p = puzzles[i]
        if p["puzzle"] != ex["puzzle"] or p["spec"] != ex["spec"] or p["gold"] != ex["gold"]:
            print(f"FAIL puzzle {p['id']} drifted from logic_lm.EXAMPLE_PUZZLES[{i}]")
            sys.exit(1)
        if not p.get("worked_example"):
            print(f"FAIL {p['id']} mirrors an EXAMPLE_PUZZLE but is not worked_example")
            sys.exit(1)

    failed = 0
    for p in puzzles:
        try:
            sol = verify_one(p)
        except AssertionError as e:
            print(f"  FAIL {e}")
            failed += 1
        else:
            tag = " [worked]" if p.get("worked_example") else ""
            print(f"  ok  {p['id']}  unique + matches gold{tag}")

    if failed:
        print(f"\n{failed}/{n} puzzles UNSOUND")
        sys.exit(1)

    print(f"\nworked examples ({len(worked)}): {', '.join(p['id'] for p in worked)}")
    print(f"\nALL {n} PUZZLES SOUND")


if __name__ == "__main__":
    main()
