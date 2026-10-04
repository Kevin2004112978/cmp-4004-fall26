"""Generator for the week-2 studio's start-configuration bank. Run once at
build time; commits ``configs.json`` alongside.

Unlike the week-4 grid bank, this bank is *not* random — the 2-room vacuum
world has exactly 8 non-trivial start configurations (2^2 dirt states x 2
agent locations), so we enumerate all of them deterministically. There is no
seed to rotate; regenerating always yields the same 8 rows in the same order.
"""
import itertools
import json
from pathlib import Path


def main():
    configs = [
        {"dirt": list(dirt), "loc": loc}
        for dirt, loc in itertools.product(
            itertools.product([True, False], repeat=2),   # (room0, room1) dirty?
            [0, 1],                                        # agent location
        )
    ]
    out = {"note": "all 8 start configurations of the 2-room world (enumerated)",
           "n": len(configs), "configs": configs}
    dest = Path(__file__).with_name("configs.json")
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest} — {len(configs)} configurations")


if __name__ == "__main__":
    main()
