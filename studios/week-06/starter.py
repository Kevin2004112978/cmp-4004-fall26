"""Week 6 studio — starter (model a CSP, then build the Logic-LM arm-B loop).

You fill in two things. Run ``python3 test_csp.py`` as you go.

  Task 1  scheduling_csp()               -- model the school-schedule CSP (graded).
  Task 2  solve_arm_b_with_refinement()  -- the LLM->CSP pipeline + refinement loop.

The provided tests include ``test_lcv_can_hurt`` and
``test_plain_backtracking_blows_up`` -- both assert that a technique which
"should" help does *not*, on the notebook's HARD Sudoku. That is not a broken
test. LCV is a heuristic gamble that sometimes costs more than it saves, and plain
backtracking is exponential; watching a guarantee (or a hoped-for speedup) fail
once is how you learn it was never unconditional. See README.
"""
from csp import CSP, backtrack_search


# ---- Task 1: model the school-schedule CSP ----------------------------------
# From the deck: assign each activity to a distinct period, and "sports cannot be
# scheduled after lunch." This is a CSP straight out of the notebook's own class:
# all activities take DISTINCT periods (an all-different over a complete neighbour
# graph), and the sports variable's domain is pre-restricted to morning periods.
#
# The instance below is fixed so the tests are deterministic. You supply the
# *modelling*: the domains (with the sports restriction) and the neighbour graph.

ACTIVITIES = ["Math", "English", "Science", "Sports", "Art", "Music"]
PERIODS = [1, 2, 3, 4, 5, 6]        # the school day, in order
LUNCH_AFTER = 3                     # periods strictly greater than 3 are afternoon
AFTERNOON = [p for p in PERIODS if p > LUNCH_AFTER]   # [4, 5, 6]
SPORTS = "Sports"                   # the one activity barred from the afternoon


def scheduling_csp():
    """Return a CSP over ACTIVITIES.

    Requirements:
      * every activity takes a DISTINCT period  (all-different)  -> encode by
        making every activity a neighbour of every other activity, so the
        engine's all-different ``consistent`` check does the work;
      * ``SPORTS`` may not be scheduled after lunch  -> its domain is the morning
        periods only (1..LUNCH_AFTER); every other activity may take any period.

    A solution is therefore a complete, consistent timetable with sports in the
    morning. Do NOT touch csp.py -- build the CSP object here and hand it to
    ``backtrack_search``.
    """
    # TODO: build `domains` -- {activity: set(periods)}. SPORTS gets morning only.
    # TODO: build `neighbors` -- {activity: set(every OTHER activity)} (complete graph).
    # TODO: return CSP(ACTIVITIES, domains, neighbors)
    raise NotImplementedError


def run_ablation(make_csp):
    """Convenience (provided): print the four-configuration ablation table for a
    factory that returns a fresh CSP each call. Use it to report Task 1's table."""
    import time
    configs = [
        ("plain backtracking",   dict()),
        ("+ forward checking",   dict(use_fc=True)),
        ("+ MRV",                dict(use_fc=True, use_mrv=True)),
        ("+ LCV",                dict(use_fc=True, use_mrv=True, use_lcv=True)),
        ("+ AC-3 preprocessing", dict(use_fc=True, use_mrv=True, use_ac3=True)),
    ]
    print(f"  {'configuration':<24}{'calls':>10}{'time':>10}{'solved':>9}")
    print("  " + "-" * 53)
    for label, kw in configs:
        csp = make_csp()
        t0 = time.perf_counter()
        result, counter = backtrack_search(csp, **kw)
        dt = time.perf_counter() - t0
        status = "TIMEOUT" if result == "TIMEOUT" else ("yes" if result else "no")
        print(f"  {label:<24}{counter['calls']:>10,}{dt:>9.4f}s{status:>9}")


# ---- Task 2: the Logic-LM arm-B pipeline + self-refinement loop -------------
# The plumbing is provided in logic_lm.py: MODEL_PROMPT, parse_json, build_csp,
# classify_arm_b, and the puzzle bank. YOU write the prompt wiring around your
# local model and the self-refinement loop the plan asks for.
#
# The full bank of 20 natural-language puzzles ships in puzzles.json; load it with
# logic_lm.load_puzzles(). Five are marked worked_example (logic_lm.worked_examples())
# -- fully-worked starters you can inspect and use as few-shot fuel. Run the three
# arms over all 20; report solve rate per arm and arm B's failure taxonomy.
#
# This function needs a live model, so the provided test suite does NOT run it.
# Validate it against the worked examples (each has a `gold` answer) before turning
# your LLM loose on the rest of the bank.

def solve_arm_b_with_refinement(model, puzzle, gold=None, max_retries=3):
    """Arm B: ask `model` to translate `puzzle` into a CSP spec, solve it with the
    course solver, and RETRY up to `max_retries` times when the reply fails to
    parse or the solver reports no solution -- feeding the error back into the
    prompt each round (this feedback loop is Logic-LM's actual contribution).

    Return (category, solution_or_None, n_attempts) where category is one of the
    logic_lm labels (MALFORMED / WRONG_MODEL / NO_SOLUTION / TIMEOUT / OK).

    `model` is any object with ``.complete(prompt) -> str`` (e.g. aicourse.llm.LLM
    or your own local client).
    """
    # TODO:
    #   1. Build the initial prompt from logic_lm.MODEL_PROMPT.format(puzzle=puzzle).
    #   2. Loop up to max_retries: call model.complete(prompt);
    #      classify with logic_lm.classify_arm_b(reply, gold=gold).
    #   3. On MALFORMED or NO_SOLUTION, append the error to the prompt and retry;
    #      on OK / WRONG_MODEL / TIMEOUT (or retries exhausted), return.
    raise NotImplementedError


if __name__ == "__main__":
    # Smoke test for Task 1: solve the schedule and show sports lands before lunch.
    try:
        csp = scheduling_csp()
    except NotImplementedError:
        print("  scheduling_csp not implemented yet")
    else:
        sol, counter = backtrack_search(csp, use_fc=True, use_mrv=True)
        print(f"  solved in {counter['calls']} calls:")
        for act in ACTIVITIES:
            print(f"    {act:<9} period {sol[act]}")
        print(f"  sports period = {sol[SPORTS]}  (lunch after {LUNCH_AFTER})")
        print("\n  ablation on this instance:")
        run_ablation(scheduling_csp)
