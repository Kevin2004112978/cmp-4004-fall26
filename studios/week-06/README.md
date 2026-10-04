# Week 6 Studio — Inference Beats Search, and the Solver Owns the Guarantee

**Companion to** [`../../weeks/week-06.md`](../../weeks/week-06.md) — Session 6B.
**Time budget:** Recap 5 · Breakouts 45 · Demos 20 · Debrief 10 (80 min total).
**Deliverables:** all provided tests pass, a Task-1 ablation table for your own
schedule, and the three-arm scorecard (A / B / C) with arm B's failure taxonomy.

> **Recap (5 min).** *Which gave the bigger win — forward checking or MRV? Why?*
> Cold-call. If nobody has it: on the notebook's HARD Sudoku, forward checking
> **times out** and MRV is the difference between *solved* and *never finishes*.
> Variable ordering wants to **fail fast**; value ordering wants to **succeed first**.

> **Duel 1 (Search) was collected at Session 6A.** If your pair has not handed it
> in, do that first — spec at [`../../projects/duel-1-search.md`](../../projects/duel-1-search.md).

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`csp.py`](csp.py) | Given: the `CSP`, `backtrack_search` (fc / mrv / lcv / ac3 switches), `ac3`, and the Sudoku (`EASY`/`MED`/`HARD`) + Australia map fixtures — unchanged from the notebook | ❌ |
| [`logic_lm.py`](logic_lm.py) | Given: the arm-B plumbing — `MODEL_PROMPT`, `parse_json`, `build_csp` (alldiff / neq / eq), `classify_arm_b`, worked-example puzzles, and `load_puzzles()` | ❌ (use it) |
| [`puzzles.json`](puzzles.json) | Given: the bank of **20** verified NL logic puzzles (NL statement + CSP spec + unique gold). 5 marked `worked_example` | ❌ (use it) |
| [`_verify_puzzles.py`](_verify_puzzles.py) | Given: the soundness check — every puzzle builds via `build_csp`, has a **unique** solution matching its gold, and re-solves under `backtrack_search` | ❌ (run it) |
| [`starter.py`](starter.py) | **Tasks 1–2** — model the schedule CSP, write the arm-B refinement loop | ✅ |
| [`test_csp.py`](test_csp.py) | Provided tests, incl. `test_lcv_can_hurt` and `test_plain_backtracking_blows_up` | ❌ |

The CSP engine has no `instances.json`: the notebook's search instances are fixed
strings (`HARD`/`EASY`/`MED`) and the Australia map, so they live inline in `csp.py`
exactly as the notebook defines them — nothing is randomly generated. The Logic-LM
puzzle bank, by contrast, ships as [`puzzles.json`](puzzles.json): 20 hand-written
puzzles, each with a solver-verified unique answer (run `python3 _verify_puzzles.py`
— it prints `ALL 20 PUZZLES SOUND`). Because `build_csp` supports only `alldiff`,
`neq`, and `eq`, every puzzle is a small (3–5 entity) assignment problem in exactly
that vocabulary.

## Task 1 — Solve a scheduling CSP (15 min)

Open `starter.py` and fill in `scheduling_csp()`. Model the school-schedule problem
from the deck: assign each activity a **distinct period**, and honour the one hard
rule — **sports cannot be scheduled after lunch**.

Both parts map straight onto the notebook's `CSP` class:

- *All-different* → make every activity a **neighbour** of every other activity
  (a complete graph). The engine's `consistent` check is already all-different, so
  the complete graph is the whole encoding.
- *No sports after lunch* → pre-restrict `Sports`'s **domain** to the morning
  periods (`1..LUNCH_AFTER`). Every other activity may take any period.

Then run:

```bash
python3 test_csp.py
```

`test_scheduling_is_valid_timetable` and `test_scheduling_sports_before_lunch`
check that your model produces a complete, all-different timetable with sports in
the morning. Report the ablation for **your** instance with `run_ablation` — same
four configurations as the notebook, on your schedule.

The other three tests need no code from you — they are the point of the week, run
against the notebook's HARD Sudoku:

- `test_ac3_prunes_hard_sudoku` — AC-3 shrinks the domains *before any guess*.
- `test_plain_backtracking_blows_up` — plain backtracking is **complete**, so it
  "should" solve any solvable puzzle. On HARD it exhausts a 300 000-call budget
  and never finishes, while fc + MRV + AC-3 solves in ~34 000. "Complete" says
  nothing about *when*.
- `test_lcv_can_hurt` — LCV is *least constraining value*; it is supposed to help.
  On HARD it makes search **strictly worse** (34,478 → 56,813 backtrack calls).
  A test that asserts a heuristic *fails* is not a bug — value ordering is a gamble
  you pay for on every branch, and you report what you measure, not what the
  textbook implies.

## Task 2 — The three-arm experiment (25 min)

This is the course's central experiment; it recurs in weeks 8, 9 and the capstone.
Same puzzles, three pipelines:

| Arm | Pipeline |
|---|---|
| **A — Hand-modeled** | you write the CSP by hand → your solver |
| **B — Hybrid (Logic-LM)** | the LLM writes the CSP → your solver |
| **C — End-to-end LLM** | the LLM reads the puzzle and answers directly |

Arm B is the engineering. The plumbing is provided in `logic_lm.py` — the exact
`MODEL_PROMPT` from the plan, a forgiving `parse_json`, `build_csp` (which turns the
JSON spec into a CSP your *same* `backtrack_search` solves), and `classify_arm_b`,
which labels every reply into the plan's four buckets:

1. **`malformed_json`** — the reply did not parse (or the spec is structurally broken)
2. **`valid_json_wrong_model`** — the solver returns a solution, but the wrong one
3. **`valid_no_solution`** — over-constrained: a translation error the solver rejects
4. **`timeout`** — the solver hit its call limit

What **you** write in `starter.py`: `solve_arm_b_with_refinement()` — the prompt
wiring around your local model **and the self-refinement loop**. When the solver
reports no solution or the JSON fails to parse, feed the error back and retry (max
3). Report solve rate **with and without** refinement — that delta is Logic-LM's
actual contribution and it is usually large.

```python
from aicourse.llm import LLM        # or your own local client
from logic_lm import load_puzzles, worked_examples
from starter import solve_arm_b_with_refinement

model = LLM()
for ex in worked_examples():        # the 5 fully-worked starters, each with a `gold`
    cat, sol, tries = solve_arm_b_with_refinement(model, ex["puzzle"], gold=ex["gold"])
    print(ex["id"], ex["puzzle"][:40], "->", cat, f"({tries} attempts)")

# then the full run over all 20:
for p in load_puzzles():
    cat, sol, tries = solve_arm_b_with_refinement(model, p["puzzle"], gold=p["gold"])
```

The full run uses the **20** natural-language logic puzzles in
[`puzzles.json`](puzzles.json), loaded with `load_puzzles()`. **Five are marked
`worked_example`** (`worked_examples()`) — the three that were always inline in
`logic_lm.py` (`p01`–`p03`) plus two more (`p04`–`p05`) — fully-worked so you can
inspect the NL → spec → gold mapping and use them as few-shot fuel; run the arms
over the other 15 and report how many you solved on the scorecard. Every puzzle's
gold is solver-verified unique (`_verify_puzzles.py`), so arm A / arm C answers can
be graded against it unambiguously. Small local models struggle to emit valid JSON;
that is realistic — tighten the prompt or use constrained decoding rather than
reaching for a bigger model.

**Task 3 — Scorecard (5 min).** Three columns this time: A, B, C. Solve rate per
arm, plus arm B's failure taxonomy.

## Demos (20 min)

Ask for arm B failure taxonomies specifically. The most valuable class discovery:
**arm B's failures are visible and arm C's are not.** When the LLM writes a bad
CSP, the solver frequently *tells you* (no solution, or a parse error). When the
LLM answers directly and is wrong, nothing signals it. Get a student to say it out
loud; if nobody does, ask: *"which arm would you rather deploy, and how would you
know it broke?"*

## Debrief (10 min)

- Arm A is best on correctness, worst on human effort per puzzle.
- Arm C is easiest and least reliable — with **silent** failures.
- Arm B is usually close to A on correctness while handling messy natural language,
  and its errors are **loud**. That combination is why the pattern matters.
- **The guarantee lives in the solver.** Once the model is faithful, correctness is
  *provable* (recall the map-colouring proof of non-existence in `csp.py` — a
  categorical capability with no LLM analogue). The remaining risk concentrates in
  translation, which is where you aim your verification effort.
- Preview: weeks 7–9 apply this pattern to logic and planning, with progressively
  more powerful solvers.

## Links

- Session 6A notebook — [`../../notebooks/week-06-csp.ipynb`](../../notebooks/week-06-csp.ipynb)
- Duel 1 spec (collected this week) — [`../../projects/duel-1-search.md`](../../projects/duel-1-search.md)
- Duel scorecard — [`../../resources/duel-scorecard.md`](../../resources/duel-scorecard.md)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
