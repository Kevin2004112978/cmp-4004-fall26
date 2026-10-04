# Week 5 Studio — The Connect-4 Tournament

**Companion to** [`../../weeks/week-05.md`](../../weeks/week-05.md) — Session 5B.
**Time budget:** Setup 10 · Rounds + commentary 35 · LLM challenger 20 · Debrief 15 (80 min total).
**Deliverable:** a working `choose_move` agent, **submitted 24 h before class** so it can be smoke-tested.

> **This studio is different.** Session 5B *is the tournament* — the 80 minutes
> are spent running the round-robin, narrating it, and entering the LLM
> challenger. The agent you play is built **before** class using this kit. Read
> "Build your agent" first; do it at home. Bring a passing `test_alphabeta.py`.

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`connect4.py`](connect4.py) | Given: the board, `minimax`, `alphabeta`, the static orderings, and the `play` self-play harness — verbatim from the notebook | ❌ |
| [`starter.py`](starter.py) | **Your agent** — `order_moves` + iterative-deepening `choose_move(board, time_budget_ms)` | ✅ |
| [`test_alphabeta.py`](test_alphabeta.py) | Provided tests, incl. the two *guarantee* tests | ❌ |

## Build your agent (at home, before Session 5B)

The tournament enforces one interface and one hard constraint:

```python
def choose_move(board, time_budget_ms) -> int: ...
```

**Hard rules (from the plan):** 500 ms per move · no external processes · no
network calls · no opening book larger than 20 positions. A move over budget
forfeits.

Open `starter.py` and fill in two functions:

- **`order_moves(board)`** — the legal columns, best-first. α-β's O(b^(m/2)) best
  case (double the reachable depth) only happens if you examine strong moves
  first. A center-first static order (`CENTER_FIRST` = `[3, 2, 4, 1, 5, 0, 6]`,
  provided) is a fine start.
- **`choose_move(board, time_budget_ms)`** — **iterative deepening** over the
  given `alphabeta`: search depth 1, then 2, then 3, …, keep the best move from
  the last *completed* depth, and stop when the clock runs out. This is what the
  plan calls a *time-bounded anytime* agent, and it is the single thing that
  most often decides the bracket — a fixed-depth agent either wastes budget or
  forfeits.

Then run:

```bash
python3 test_alphabeta.py
```

All seven tests must pass. Five exercise *your* `choose_move` /`order_moves`
(legality, taking an immediate win, blocking an immediate threat, respecting the
budget). The other two use the given engine and are the point of the week — see
below. With the starter unfilled they print `not implemented yet`; that is
expected until you write the code.

**Fast-finishing pairs:** the biggest cheap win is a *dynamic* order — put the
previous iteration's best move first. Add a transposition table only after that.
Do not over-engineer the evaluation before you have depth: *depth beats
knowledge at this scale* is a result you will watch happen in the bracket.

## The two guarantee tests (why they matter)

1. **`test_alphabeta_matches_minimax_value_with_fewer_nodes`** — α-β returns the
   **identical** value minimax returns while expanding **strictly fewer** nodes.
   From the notebook, at the two-center-discs position:

   | depth | minimax nodes | α-β nodes | speed-up |
   |---|---|---|---|
   | 2 | 57 | 45 | 1.3× |
   | 4 | 2,801 | 1,002 | 2.8× |
   | 5 | 19,607 | 4,103 | 4.8× |
   | 6 | 132,179 | 17,030 | 7.8× |

   Pruning is **not** approximation — it discards only provably irrelevant
   branches. Same answer, a fraction of the cost.

2. **`test_horizon_effect_shallow_agent_loses`** — a guarantee *failing* on
   purpose. `play(2, 5)` → the depth-5 side wins; `play(6, 4)` → the depth-6 side
   wins. The shallow agent is not blundering — **every move it plays is optimal
   with respect to its horizon.** It simply cannot see the threat that resolves
   one ply past where it stopped looking. No evaluation function fixes this; only
   depth does. (The notebook's `play(5, 5)` → second player wins is an *artifact*
   of `evaluate()` at equal depth, not the horizon effect, so the test does not
   assert on it — ask yourself why before class.)

## Session 5B — in class (80 min)

**Setup (10 min).** The round-robin driver runs live with the bracket on screen;
every pair plays every other pair, both colors. While it runs, each pair gives a
30-second description of its evaluation function.

**Rounds + commentary (35 min).** Predict winners before each match; when an
agent loses, its authors explain what happened. Watch for the three recurring
results: a *simpler* agent that searched two plies deeper beats a sophisticated
one; a fixed-depth agent times out and **forfeits** (iterative deepening is what
prevents this); an agent that is stronger as MAX than MIN has an asymmetry bug.

**The LLM challenger (20 min).** An LLM agent enters the bracket with the plan's
prompt (`{board}` rendered by `Connect4.__str__`, `{legal}` from `legal_moves()`):

```python
from aicourse.llm import LLM
model = LLM()
PROMPT = """Connect-4. You are 'X'. Columns numbered 0-6, left to right.
Board (bottom row last):
{board}
Legal columns: {legal}
Reply with one column number and nothing else."""
reply = model.complete(PROMPT.format(board=str(board), legal=board.legal_moves()))
```

Expect it to: play legal moves *most* of the time (validate + retry the rest);
**miss immediate wins** (col 3 wins now and it plays elsewhere — it is not
searching); fail to block immediate threats; and run ~100× slower than the α-β
agent. Every missed-immediate-win board is a Failure Atlas entry — record the
**exact** board state so it reproduces.

**Debrief (15 min).** α-β returns *exactly* minimax's answer while exploring far
less — pruning is free, not an approximation. Move ordering is a heuristic about
search *order* and it doubles reachable depth. The LLM lost to a 40-line agent at
a game it has seen thousands of times: **pattern-matching a game's description is
not computing in it.** Reconcile that with Ruoss et al. (2024) — grandmaster
chess with no search at inference — and land the answer: *the search did not
disappear; it moved to training time.*

## Links

- Session A notebook — [`../../notebooks/week-05-minimax-alphabeta.ipynb`](../../notebooks/week-05-minimax-alphabeta.ipynb)
- Slides — [`../../slides/week-05/deck.md`](../../slides/week-05/deck.md)
- Lesson plan (tournament rules, Session 5A "Assignment") — [`../../weeks/week-05.md`](../../weeks/week-05.md)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
