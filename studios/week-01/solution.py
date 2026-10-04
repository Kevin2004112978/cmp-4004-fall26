"""Week 1 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_eliza.py`` passes when this module is imported in place of
``starter``. Verify with ``studios/_verify_solutions.py`` (which aliases this file
to the name ``starter`` and runs the unmodified test).

DO NOT ship this to students — it is excluded via ``studios/.gitignore``. The
teaching walkthrough lives in ``solution.ipynb`` (which imports this file rather
than re-pasting it, so the two never drift).
"""
import re

from eliza import RULES, FALLBACK, REFLECT, reflect, respond
import eliza
import random


# ---- Task 1a — add THREE new rules ------------------------------------------
def new_rules():
    """Three novel rules. Each has a real trigger (none matches the empty
    string) and none duplicates a base pattern in ``eliza.RULES``."""
    return [
        (r"\bI want (.*)", ["What would it mean to you to get {0}?",
                            "Why do you want {0}?"]),
        (r"\bI can't (.*)", ["What makes you feel you can't {0}?",
                             "Have you ever been able to {0}?"]),
        (r"\bI think (.*)", ["Do you really think {0}?",
                             "What led you to think {0}?"]),
    ]


# ---- Task 1b — the extended responder ---------------------------------------
def extended_respond(text):
    """Base rules FIRST (so the demo never regresses), then ``new_rules()``,
    then the fallback. Same loop as ``eliza.respond``, over the joined table."""
    for pattern, templates in RULES + new_rules():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            groups = [reflect(g) for g in m.groups()]
            return random.choice(templates).format(*groups)
    return random.choice(FALLBACK)


# ---- Task 1c — declare your deliberate failure ------------------------------
def failure_case():
    """A compound sentence whose SECOND clause ELIZA drops entirely: it matches
    ``my mother`` in clause A and never looks at ``my father is a lawyer``."""
    return (
        "My mother is a doctor and my father is a lawyer",
        "First-match-wins: the 'my (mother|father|family)' rule fires on clause "
        "A, so clause B ('my father is a lawyer') is never inspected — fluent, "
        "on-topic, and half-blind.",
    )


if __name__ == "__main__":
    probe = "I am not feeling great about the exam"
    print("base    >", respond(probe))
    print("extended>", extended_respond(probe))
    text, why = failure_case()
    print(f"failure > {text!r}\n          -> {extended_respond(text)}\n          ({why})")
