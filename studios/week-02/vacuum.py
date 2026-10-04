"""Week 2 studio — the shared vacuum world (GIVEN to you; do not modify).

This is the environment and the three agents from the Session-A notebook,
unchanged. Week 2 is about *agent architectures*, not about re-implementing the
world — so the world and the two agents you already saw built live are provided.
You write the missing agents (goal-based, utility-based) in ``starter.py``.

The world is two rooms. A percept is ``(location, is_dirty_here)`` — note what
the agent *cannot* see: whether the *other* room is dirty.

Interface (one socket, four policies plug into it):
    world.percept()      -> (location, is_dirty_here)
    world.step(action)   -> apply 'Suck' | 'Left' | 'Right' | 'NoOp'
    agent(percept)        -> one action word
    run(agent, steps, dirt, loc) -> the world after `steps` actions
"""


class VacuumWorld:
    """Two rooms. Percept = (location, status_here)."""

    def __init__(self, dirt=(True, True), loc=0):
        self.dirt, self.loc, self.score, self.t = list(dirt), loc, 0, 0

    def percept(self):
        return (self.loc, self.dirt[self.loc])

    def step(self, action):
        if action == "Suck":
            self.dirt[self.loc] = False
        elif action == "Left":
            self.loc = 0
        elif action == "Right":
            self.loc = 1
        # performance measure: clean rooms, summed over time
        self.score += sum(not d for d in self.dirt)
        self.t += 1

    def __repr__(self):
        rooms = "".join("D" if d else "." for d in self.dirt)
        return f"[{rooms}] agent@{self.loc} t={self.t} score={self.score}"


class BrokenSensorWorld(VacuumWorld):
    """The location sensor has died and reports None. Everything else is
    identical. This is *partial observability*, live, in four lines of change."""

    def percept(self):
        return (None, self.dirt[self.loc])   # location unknown


# ---- given agents (built live in Session A) ---------------------------------

def simple_reflex(percept):
    """Maps the current percept straight to an action. No memory of any kind."""
    loc, dirty = percept
    if dirty:
        return "Suck"
    return "Right" if loc == 0 else "Left"


def model_based():
    """Adds internal state: track what has been cleaned and where we are. This
    is what buys the agent the ability to *know it is finished* (NoOp), and it is
    what lets it survive the broken location sensor — it never reads `loc`."""
    state = {"loc": 0, "clean": [False, False]}

    def agent(percept):
        _, dirty = percept
        if dirty:
            state["clean"][state["loc"]] = True
            return "Suck"
        state["clean"][state["loc"]] = True
        if all(state["clean"]):
            return "NoOp"                  # knows it is done — reflex never does
        state["loc"] = 1 - state["loc"]
        return "Right" if state["loc"] == 1 else "Left"

    return agent


def utility_agent(move_cost=1.0):
    """The simplified utility agent from the notebook. With ``move_cost=1.0`` it
    RATIONALLY leaves the other room dirty — a specification-gaming agent you
    built in week 2, before you knew the term. Kept here for reference; the
    studio asks you to build a properly parameterised ``utility_based``."""
    state = {"loc": 0, "clean": [False, False]}

    def agent(percept):
        _, dirty = percept
        if dirty:
            state["clean"][state["loc"]] = True
            return "Suck"
        state["clean"][state["loc"]] = True
        other = 1 - state["loc"]
        if not state["clean"][other] and move_cost < 1.0:
            state["loc"] = other
            return "Right" if other == 1 else "Left"
        return "NoOp"          # crossing is not worth it

    return agent


# ---- evaluation harness (verbatim from the notebook) ------------------------

def run(agent, steps=20, dirt=(True, True), loc=0, trace=0):
    """Run `agent` against a fresh world for `steps` actions; return the world."""
    world = VacuumWorld(dirt, loc)
    for i in range(steps):
        action = agent(world.percept())
        if trace and i < trace:
            print(f"  {world}  ->  {action}")
        world.step(action)
    return world


def run_in(world, agent, steps=20, trace=0):
    """Like `run`, but against a world you supply (e.g. a BrokenSensorWorld)."""
    for i in range(steps):
        action = agent(world.percept())
        if trace and i < trace:
            print(f"  {world}  ->  {action}")
        world.step(action)
    return world
