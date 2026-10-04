"""Week 2 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_agents.py`` passes when this module is imported in place of
``starter``. Verify with ``studios/_verify_solutions.py`` (which aliases this file
to the name ``starter`` and runs the unmodified test).

DO NOT ship this to students — it is excluded via ``studios/.gitignore``. The
teaching walkthrough lives in ``solution.ipynb`` (which imports this file rather
than re-pasting it, so the two never drift).
"""
from vacuum import VacuumWorld, run, simple_reflex, model_based


# ---- Task 1: complete the taxonomy ------------------------------------------

def goal_based(goal=(False, False)):
    """Return an agent that PLANS toward an explicit goal, then STOPS.

    The goal is a target dirt-state; ``(False, False)`` means "both rooms
    clean". Unlike the reflex agent (which oscillates forever) the goal-based
    agent recognises the goal is reached and returns ``"NoOp"`` from then on.

    Reference design: keep a per-room record of what we have driven to clean.
    The percept exposes ``loc`` (the sensor WORKS in ``VacuumWorld``), so — unlike
    the given ``model_based``, which never reads ``loc`` and only survives a
    *broken* sensor because its hardcoded belief happens to be right — we read the
    true location and never need to guess where we are.
    """
    goal = tuple(goal)
    cleaned = [False, False]          # rooms we have observed/driven to clean

    def agent(percept):
        loc, dirty = percept
        if dirty:
            cleaned[loc] = True        # it will be clean right after this Suck
            return "Suck"
        cleaned[loc] = True            # current room is clean and we now know it
        # A room satisfies the goal when goal[i] is False (must be clean) and we
        # have cleaned it. Rooms still needing work:
        need = [i for i in range(2) if not goal[i] and not cleaned[i]]
        if not need:
            return "NoOp"              # goal reached — stop (reflex never does)
        target = need[0]
        return "Right" if target == 1 else "Left"   # move toward uncleaned room

    return agent


def utility_based(move_cost=1, suck_cost=2, clean_reward=3):
    """Return an agent that maximises NET utility one step at a time.

    Cost model (same numbers as ``tournament.py``): each move costs
    ``move_cost``, each Suck costs ``suck_cost``, and each clean room earns
    ``clean_reward`` per step. The agent function only sees ``percept`` — it has
    no lookahead — so it reasons *greedily* about the immediate net change.

    The intended discovery: this greedy agent SOMETIMES LEAVES A ROOM DIRTY. When
    the current room is clean, the only move it can make crosses to a room it
    cannot see. A crossing (Left/Right) does not clean anything on the step it
    happens, so the number of clean rooms is unchanged that step; the immediate
    net change of crossing is therefore ``-move_cost`` (a strict loss) versus
    ``0`` for ``NoOp``. A horizon-free agent will not pay to travel toward a
    payoff it cannot yet see — so it stops. Report it as a result, not a bug.
    """
    cleaned = [False, False]

    def agent(percept):
        loc, dirty = percept
        if dirty:
            # A dirty room repays its suck_cost fast (clean_reward accrues every
            # remaining step), so cleaning the room we are standing in is always
            # the rational immediate move.
            cleaned[loc] = True
            return "Suck"
        cleaned[loc] = True
        # Weigh the IMMEDIATE net change of crossing to the other (unseen) room.
        # Moving costs move_cost now and cleans nothing this step, so the clean-
        # room reward is unchanged: net(cross) = -move_cost. net(NoOp) = 0.
        net_of_crossing = -move_cost
        if net_of_crossing > 0:                     # never, under this cost model
            other = 1 - loc
            return "Right" if other == 1 else "Left"
        return "NoOp"                                # crossing does not pay off

    return agent


if __name__ == "__main__":
    from tournament import tournament, net_utility

    factories = {
        "reflex": lambda: simple_reflex,
        "model": model_based,
        "goal": goal_based,
        "utility": utility_based,
    }
    tournament(factories)
