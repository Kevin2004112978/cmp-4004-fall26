"""Week 2 studio — Task 1 starter (complete the agent taxonomy).

Fill in the two agents below, then run ``python3 test_agents.py``. All required
tests must pass, INCLUDING the ones that assert a *surprising* property:

  - the simple reflex agent PROVABLY fails on a world the model-based agent
    handles (partial observability) — watch a guarantee fail;
  - the utility agent RATIONALLY leaves a room dirty on at least one config —
    not a bug, but specification-following under a cost model.

You are given the world and two agents in ``vacuum.py`` (simple_reflex,
model_based). You write ``goal_based`` and ``utility_based`` here.
"""
from vacuum import VacuumWorld, run, simple_reflex, model_based


# ---- Task 1: complete the taxonomy ------------------------------------------

def goal_based(goal=(False, False)):
    """Return an agent that PLANS toward an explicit goal, then STOPS.

    The goal is a target dirt-state; ``(False, False)`` means "both rooms
    clean". Unlike the reflex agent (which oscillates forever) the goal-based
    agent must recognise the goal is reached and return ``"NoOp"`` from then on.

    Suggested internal state (like model_based): remember which rooms you have
    cleaned and where you are, since the percept only shows the current room.

    Returns: a function ``agent(percept) -> action``.
    """
    # TODO: build an agent with internal state that:
    #   - reads `loc` from the percept (the sensor WORKS here — unlike the given
    #     model_based, which assumes loc=0 and so only survives a broken sensor
    #     when that belief happens to be right),
    #   - Sucks when the current room is dirty (and records it clean),
    #   - moves toward an as-yet-uncleaned room otherwise,
    #   - returns "NoOp" once its record matches `goal` (all rooms clean).
    raise NotImplementedError


def utility_based(move_cost=1, suck_cost=2, clean_reward=3):
    """Return an agent that maximises NET utility one step at a time.

    Cost model (same numbers as ``tournament.py``): each move costs
    ``move_cost``, each Suck costs ``suck_cost``, and each clean room earns
    ``clean_reward`` per step. The agent function only sees ``percept`` — it has
    no lookahead — so it must reason *greedily* about the immediate net change.

    The intended discovery: a greedy utility agent SOMETIMES LEAVES A ROOM
    DIRTY, because paying to travel to a room it cannot see the payoff of is not
    immediately worth it. Report it as a result, not a bug — this is the first
    time an agent makes a decision you did not intend but cannot argue with.

    Returns: a function ``agent(percept) -> action``.
    """
    # TODO: build an agent with internal state that:
    #   - reads `loc` from the percept (the sensor works here),
    #   - Sucks the current room when dirty (a clean room repays suck_cost fast),
    #   - otherwise weighs the immediate cost of crossing against the immediate
    #     reward of doing so, and returns "NoOp" when crossing does not pay off.
    raise NotImplementedError


# ---- Task 2 sketch (the LLM as agent function) ------------------------------
# See README.md §"Task 2". Drop a language model into the SAME percept->action
# socket. You supply the model call; you must handle malformed output and LOG
# every parse failure (it belongs on the scorecard — axis 8).
#
#   from aicourse.llm import LLM
#   model = LLM()  # your configured local backend
#
#   PROMPT = """You control a vacuum robot in a 2-room world.
#   Rooms 0 and 1. Each is Clean or Dirty.
#   Actions: Left, Right, Suck, NoOp.
#   History of (percept, action) so far:
#   {history}
#   Current percept: location={loc}, status={status}
#   Reply with exactly one action word and nothing else."""
#
#   def parse_action(raw):
#       # must survive "Suck.", "I would suck", or a paragraph of reasoning.
#       ...  # return one of Left/Right/Suck/NoOp, or None on failure (log it!)
#
#   def llm_agent(history):
#       def agent(percept):
#           loc, dirty = percept
#           resp = model.complete(PROMPT.format(history=fmt(history),
#                                               loc=loc,
#                                               status="Dirty" if dirty else "Clean"))
#           return parse_action(resp.text)
#       return agent
#
# Run the same 8 configs; run ONE config 5x and count distinct action sequences
# (reproducibility — axis 5, made visceral). Compare to the four classical agents.


if __name__ == "__main__":
    # Quick smoke test: run each agent you've filled in on one config.
    from tournament import tournament, net_utility

    factories = {
        "reflex": lambda: simple_reflex,
        "model": model_based,
    }
    for name, make in [("goal", goal_based), ("utility", utility_based)]:
        try:
            make()  # will raise NotImplementedError until you fill it in
            factories[name] = make
        except NotImplementedError:
            print(f"  {name:<10} not implemented yet")

    if len(factories) > 2:
        print()
        tournament(factories)
