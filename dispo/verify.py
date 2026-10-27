"""Evidence grounding, with an asymmetry that favors safety.

A finding marked present or denied must quote the message. When the quote isn't there:
- a hallucinated *denial* could suppress a red-flag rule, so it is downgraded to not_mentioned;
- a hallucinated *presence* can only raise urgency, so it is kept but flagged for review.
Downgrading an ungrounded red flag would turn a paraphrased quote into a missed emergency.
"""

from __future__ import annotations

import copy
import re

_PUNCT = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


def normalize(text: str) -> str:
    text = (text or "").translate(_PUNCT).lower()
    return re.sub(r"\s+", " ", text).strip(" .;:,")


def ground(facts: dict, message: str) -> tuple[dict, list[dict]]:
    src = normalize(message)
    out = copy.deepcopy(facts)
    issues = []
    for group in ("context", "findings"):
        for name, f in (out.get(group) or {}).items():
            if f.get("status") not in ("present", "denied"):
                continue
            quotes = [q for q in f.get("evidence") or [] if q and q.strip()]
            missing = [q for q in quotes if normalize(q) not in src]
            if quotes and not missing:
                continue
            problem = "no evidence quote" if not quotes else f"quote not in message: {missing[0]!r}"
            if f["status"] == "denied":
                f["status"] = "not_mentioned"
                action = "denial downgraded to not_mentioned"
            else:
                f["ungrounded"] = True
                action = "kept as present, flagged"
            issues.append({"fact": name, "problem": problem, "action": action})
    out["minimizing_quotes"] = [q for q in out.get("minimizing_quotes") or [] if normalize(q) in src]
    return out, issues
