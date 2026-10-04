"""Provided tests for the week-2 studio.

Run: ``python3 test_agents.py``. Prints one line per test.

Two of these tests assert a *surprising* property, and that is the point:

  - ``test_reflex_fails_under_partial_observability`` — the simple reflex agent
    PROVABLY leaves a room dirty on a world (broken location sensor) that the
    model-based agent cleans completely. Watch a guarantee fail. (This one uses
    only the given agents, so it passes even before you fill in ``starter.py``.)

  - ``test_utility_leaves_a_room_dirty`` — your rational utility agent leaves a
    room dirty on at least one config. Not a bug: rationality under a cost model.
"""
import sys

from vacuum import (VacuumWorld, BrokenSensorWorld, run, run_in,
                    simple_reflex, model_based)
from tournament import load_configs, net_utility
import starter as s

CONFIGS = load_configs()


def _final(agent_or_factory, dirt, loc, steps=20, broken=False):
    """Run an agent to completion; return the resulting world.

    Accepts a bare agent function (reflex) or a factory (model/goal/utility).
    """
    world = BrokenSensorWorld(dirt, loc) if broken else VacuumWorld(dirt, loc)
    agent = agent_or_factory() if callable_is_factory(agent_or_factory) else agent_or_factory
    return run_in(world, agent, steps)


def callable_is_factory(fn):
    """model_based/goal_based/utility_based are zero-arg factories; simple_reflex
    is the agent itself. Distinguish by trying a no-arg call is unsafe, so we tag
    the bare reflex explicitly."""
    return fn is not simple_reflex


# ---- given-agent guarantee (passes even with unfilled starter) --------------

def test_reflex_fails_under_partial_observability():
    """simple_reflex breaks on >=1 config when the location sensor dies; the
    model-based agent still cleans BOTH rooms. Watch a guarantee fail.

    Scope: configs where the world starts at room 0 — i.e. where model_based's
    hardcoded *initial belief* (loc=0) is correct. That the model-based agent's
    memory is only ever as reliable as its initial belief is itself worth a
    sentence in the debrief; here we hold that belief correct and isolate the
    variable that matters: memory vs. no memory."""
    loc0 = [(dirt, loc) for dirt, loc in CONFIGS if loc == 0]
    reflex_failures = 0
    for dirt, loc in loc0:
        # model-based must clean both rooms even with a broken sensor:
        wm = _final(model_based, dirt, loc, broken=True)
        assert wm.dirt == [False, False], (
            f"model_based left a room dirty on broken-sensor dirt={dirt} loc={loc}: {wm}"
        )
        # reflex may fail — count it:
        wr = _final(simple_reflex, dirt, loc, broken=True)
        if wr.dirt != [False, False]:
            reflex_failures += 1
    assert reflex_failures > 0, (
        "simple_reflex cleaned every broken-sensor world — the partial-"
        "observability failure did not reproduce (check BrokenSensorWorld)."
    )
    print(f"  ok  reflex failed on {reflex_failures}/{len(loc0)} broken-sensor "
          f"configs; model_based cleaned all (and that is the lesson)")


# ---- goal-based agent (needs starter) ---------------------------------------

def test_goal_based_reaches_goal_on_every_config():
    for dirt, loc in CONFIGS:
        w = _final(s.goal_based, dirt, loc)
        assert w.dirt == [False, False], (
            f"goal_based did not reach the goal on dirt={dirt} loc={loc}: {w}"
        )
    print("  ok  goal_based reaches (both rooms clean) on all 8 configs")


def test_goal_based_stops_when_done():
    # Once the world is clean, a goal-based agent must NoOp — not oscillate.
    agent = s.goal_based()
    w = VacuumWorld((True, True), 0)
    run_in(w, agent, steps=20)                 # drive it to the clean goal state
    assert w.dirt == [False, False]
    # From a settled clean world, further actions must be NoOp (no cost, no move).
    loc_before = w.loc
    for _ in range(5):
        a = agent(w.percept())
        assert a == "NoOp", f"goal_based kept acting after the goal was reached: {a!r}"
        w.step(a)
    assert w.loc == loc_before
    print("  ok  goal_based returns NoOp once the goal is reached (does not oscillate)")


# ---- utility-based agent (needs starter) ------------------------------------

def test_utility_cleans_the_room_it_starts_in():
    # A dirty starting room repays its suck cost quickly, so a rational agent
    # cleans it. (dirt[loc] is True in these configs.)
    for dirt, loc in CONFIGS:
        if not dirt[loc]:
            continue
        w = _final(s.utility_based, dirt, loc)
        assert w.dirt[loc] is False, (
            f"utility_based never cleaned its own starting room dirt={dirt} loc={loc}: {w}"
        )
    print("  ok  utility_based always cleans the (dirty) room it starts in")


def test_utility_leaves_a_room_dirty():
    """The discovery. A greedy utility agent leaves >=1 room dirty on >=1 config,
    because travelling to an unseen room is not immediately worth it."""
    left_dirty = 0
    for dirt, loc in CONFIGS:
        w = _final(s.utility_based, dirt, loc)
        if w.dirt != [False, False]:
            left_dirty += 1
    assert left_dirty > 0, (
        "utility_based cleaned every world — with this cost model a purely "
        "greedy agent should leave at least one room dirty. Make it weigh the "
        "IMMEDIATE net change of crossing, not the whole horizon."
    )
    print(f"  ok  utility_based rationally left a room dirty on {left_dirty}/{len(CONFIGS)} "
          f"configs (and that is the lesson)")


TESTS = [
    test_reflex_fails_under_partial_observability,
    test_goal_based_reaches_goal_on_every_config,
    test_goal_based_stops_when_done,
    test_utility_cleans_the_room_it_starts_in,
    test_utility_leaves_a_room_dirty,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: agent not implemented yet")
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
