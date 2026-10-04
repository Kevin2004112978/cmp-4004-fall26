"""Week 2 studio — tournament + net-utility scoring (GIVEN; use it, don't edit).

The vacuum world's built-in ``score`` counts clean-room-steps. Task 1 asks a
different question: with an *energy cost model*, what is the agent's **net**
utility? So everyone uses the same numbers, the cost model lives here:

    move (Left/Right) ....... costs MOVE_COST   = 1
    Suck .................... costs SUCK_COST   = 2
    each clean room, per step earns CLEAN_REWARD = 3
    NoOp .................... costs 0

``net_utility`` recomputes the reward/cost ledger itself — it does NOT trust
the agent to report anything. Pass a *factory* (a zero-arg callable returning a
fresh agent) so each run starts with clean internal state.
"""
import json
from pathlib import Path

from vacuum import VacuumWorld

MOVE_COST = 1
SUCK_COST = 2
CLEAN_REWARD = 3


def load_configs(path=None):
    """Return the 8 start configs as a list of ``(dirt_tuple, loc)`` pairs."""
    path = Path(path or Path(__file__).with_name("configs.json"))
    data = json.loads(path.read_text())
    return [(tuple(c["dirt"]), c["loc"]) for c in data["configs"]]


def net_utility(make_agent, dirt, loc, steps=20):
    """Run a fresh agent for `steps` and return net utility under the cost model.

    `make_agent` is a zero-arg callable returning an ``agent(percept)`` function
    (e.g. ``model_based`` or ``lambda: simple_reflex``).
    """
    agent = make_agent()
    world = VacuumWorld(dirt, loc)
    net = 0
    for _ in range(steps):
        action = agent(world.percept())
        if action == "Suck":
            net -= SUCK_COST
        elif action in ("Left", "Right"):
            net -= MOVE_COST
        world.step(action)
        net += CLEAN_REWARD * sum(not d for d in world.dirt)
    return net


def tournament(factories, steps=20, configs=None):
    """Score every factory on every config; print a table and return the totals.

    `factories` is a dict ``{name: make_agent}``. Returns ``{name: total_net}``.
    """
    configs = configs or load_configs()
    names = list(factories)
    header = f"{'start':<22}" + "".join(f"{n:>14}" for n in names)
    print(header)
    print("-" * len(header))
    totals = {n: 0 for n in names}
    for dirt, loc in configs:
        row = f"dirt={dirt} loc={loc}"
        line = f"{row:<22}"
        for n in names:
            u = net_utility(factories[n], dirt, loc, steps)
            totals[n] += u
            line += f"{u:>14}"
        print(line)
    print("-" * len(header))
    print(f"{'TOTAL':<22}" + "".join(f"{totals[n]:>14}" for n in names))
    return totals
