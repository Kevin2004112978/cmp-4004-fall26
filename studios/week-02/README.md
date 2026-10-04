# Week 2 Studio — The Vacuum World: Completing the Taxonomy

**Companion to** [`../../weeks/week-02.md`](../../weeks/week-02.md) — Session B.
**Time budget:** Recap 5 · Breakouts 45 · Demos 20 · Debrief 10 (80 min total).
**Deliverables:** all provided tests pass, a tournament score table for the four
classical agents, an LLM-agent scorecard (all eight axes), and a Failure Atlas entry.

> **Recap (5 min).** *Name one thing the model-based agent can do that the reflex
> agent provably cannot.* (You will watch this exact guarantee fail in a test.)

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`vacuum.py`](vacuum.py) | Given: the world + `simple_reflex` + `model_based` + `run`, unchanged from the notebook | ❌ |
| [`configs.json`](configs.json) | Given: all 8 start configurations (2² dirt states × 2 locations) | ❌ |
| [`tournament.py`](tournament.py) | Given: the energy cost model + `net_utility` scorer + `tournament()` printer | ❌ (use it) |
| [`starter.py`](starter.py) | **Task 1** — implement `goal_based` and `utility_based` | ✅ |
| [`test_agents.py`](test_agents.py) | Provided tests, incl. `test_reflex_fails_under_partial_observability` | ❌ |
| [`_generate_configs.py`](_generate_configs.py) | Regenerates `configs.json` (it is a deterministic enumeration — no seed) | ❌ |

## Task 1 — Complete the taxonomy + provided tests (15 min)

You already have two of the four architectures (`simple_reflex`, `model_based`).
Open `starter.py` and add the other two:

- `goal_based` — plans toward an explicit goal (both rooms clean) and then
  **stops** (`NoOp`). The reflex agent oscillates forever; the goal-based agent
  knows when it is finished, the same way the model-based one does — but framed
  as *reaching a specified state* rather than reacting.
- `utility_based` — maximises **net utility** one step at a time under the cost
  model in `tournament.py`: a move costs 1, a `Suck` costs 2, and each clean
  room earns 3 per step. The agent function only sees the current percept — it
  has **no lookahead** — so it reasons greedily about the immediate net change.

Then:

```bash
python3 test_agents.py
```

All five tests must pass. Two of them assert a *surprising* property on purpose:

- `test_reflex_fails_under_partial_observability` — with the location sensor
  broken (`BrokenSensorWorld`), `simple_reflex` leaves a room dirty while
  `model_based` still cleans both. **This is the recap question, made into an
  assertion.** A test that expects the reflex agent to *fail* is not a mistake;
  watching a guarantee fail *once* is how you know internal state actually bought
  you something. (It uses only the given agents, so it passes before you write
  any code — a fixed point to check your setup against.)
- `test_utility_leaves_a_room_dirty` — your rational `utility_based` agent
  leaves at least one room dirty across the 8 configs. **This is not a bug.** It
  is rationality under a cost model: paying to travel to a room it cannot see the
  payoff of is not immediately worth it. Report it as a result.

Now run the tournament (all four agents, all 8 configs, net utility):

```python
from vacuum import simple_reflex, model_based
from tournament import tournament
from starter import goal_based, utility_based

tournament({
    "reflex":  lambda: simple_reflex,   # a bare function → wrap in a factory
    "model":   model_based,
    "goal":    goal_based,
    "utility": utility_based,
})
```

The **intended discovery**: the utility agent's total is not the highest, because
it leaves value on the table. Be able to say, in one sentence, *why the interface
(`percept → action`, no horizon) forces the greedy behaviour* — that is the honest
motivation for search and planning in weeks 3–9.

Fast-finishing pairs: **extend `VacuumWorld` to n rooms.** Which agents still
work unchanged, and which need rewriting? (This is the atomic → factored
representation question from the slides, arriving as a refactor.)

## Task 2 — LLM as agent function (20 min)

Drop a language model into the **same** `percept → action` socket. `starter.py`
has the sketch and the exact prompt from the plan. You supply the model call via
`aicourse.llm.LLM`; the abstraction from 1995 does the rest.

Requirements, each of which teaches something:

- `parse_action` must survive the model replying `"Suck."`, `"I would suck"`, or
  a paragraph of reasoning. **Log every parse failure** — malformed output is a
  failure mode with no classical counterpart, and it belongs on the scorecard
  (axis 8).
- Run the same **8 configurations**; compare to the four classical agents.
- Run **one** configuration **five times** and count distinct action sequences.
  Reproducibility (axis 5), made visceral. *Protect this run* — it matters more
  than breadth.
- **If Ollama is slow, cap Task 2 at 3 configurations** and note it. Keep the
  five-times reproducibility run regardless.

Do **not** let the model be its own oracle ("does your action look right?").
Judge every episode with the same `vacuum`/`tournament` code the classical
agents were judged with.

## Task 3 — Scorecard (10 min)

Fill in all **eight** axes for `utility_based` vs. `llm_agent`. This is your first
full scorecard; expect it to be weak — the demo slot is for strengthening it.
Count, specifically, *how many lines of defensive code the LLM agent needed that
the classical agents did not* (a parser, a retry, a fallback). That ratio is a
real engineering datum.

## Demos (20 min)

- One pair presents the **utility-leaves-dirt** result — solicit whether anyone
  first reported it as a bug, then reframe it as rationality under a cost model.
- One pair presents their **most interesting LLM parse failure**. Ask them: *how
  many lines of defensive code did the LLM agent need that the classical agents
  didn't?*
- Solicit the five-times reproducibility count. Different sequences from the same
  input is axis 5, live.

## Debrief (10 min)

1. The LLM agent is **not** a new architecture. It is a policy plugged into the
   same `percept → action` socket. The abstraction from 1995 still holds.
2. The LLM agent needed a parser, a retry, and a fallback. The classical agents
   needed none. **Reliability engineering is where the cost hides.**
3. On a 2-room world the LLM is expensive and worse. Ask: *when does that invert?*
   Answer: when the state space is huge, informal, and linguistic — when writing
   the rules down is the hard part. That honest case for LLM agents arrives in
   week 9.

**Failure Atlas entry due** — log your best parse failure (see the resources folder).

## Links

- Session A notebook — [`../../notebooks/week-02-vacuum-world.ipynb`](../../notebooks/week-02-vacuum-world.ipynb)
- Lesson plan — [`../../weeks/week-02.md`](../../weeks/week-02.md)
- Slides — [`../../slides/week-02/deck.md`](../../slides/week-02/deck.md)
- Paper: ReAct (Yao et al., 2022) — [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
