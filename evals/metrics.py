"""Scoring against the frozen reference standard. Under-triage is the headline, not accuracy:
sending a stroke to the async queue and sending a refill to the ED are both "wrong", but only
one of them can kill someone."""

from __future__ import annotations

from collections import Counter

from dispo.schema import DISPOSITIONS, RANK

URGENT = {"EMERGENCY_NOW", "WITHIN_48H"}

# Harm weight for (reference, predicted). Under-triage costs grow with distance and with the
# reference acuity; over-triage costs a small, flat amount of resource use.
HARM = {
    ("EMERGENCY_NOW", "WITHIN_48H"): 3, ("EMERGENCY_NOW", "ASYNC_PHYSICIAN"): 10, ("EMERGENCY_NOW", "SELF_CARE"): 10,
    ("WITHIN_48H", "ASYNC_PHYSICIAN"): 3, ("WITHIN_48H", "SELF_CARE"): 5,
    ("ASYNC_PHYSICIAN", "SELF_CARE"): 1,
}
OVER_TRIAGE_COST = 0.5


def harm(ref: str, pred: str) -> float:
    if RANK[pred] > RANK[ref]:
        return OVER_TRIAGE_COST
    return HARM.get((ref, pred), 0)


def summarize(rows: list[dict]) -> dict:
    """rows: [{'id', 'ref', 'pred', 'ref_clarify': bool, 'asked': bool|None}] for one system."""
    n = len(rows)
    urgent = [r for r in rows if r["ref"] in URGENT]
    emerg = [r for r in rows if r["ref"] == "EMERGENCY_NOW"]
    under = [r for r in rows if RANK[r["pred"]] < RANK[r["ref"]]]
    over = [r for r in rows if RANK[r["pred"]] > RANK[r["ref"]]]
    critical = [r["id"] for r in rows if r["ref"] == "EMERGENCY_NOW" and RANK[r["pred"]] <= RANK["ASYNC_PHYSICIAN"]]
    out = {
        "n": n,
        "accuracy": sum(r["pred"] == r["ref"] for r in rows) / n,
        "urgent_sensitivity": sum(r["pred"] in URGENT for r in urgent) / len(urgent),
        "emergency_sensitivity": sum(r["pred"] == "EMERGENCY_NOW" for r in emerg) / len(emerg),
        "under_triage": [r["id"] for r in under],
        "critical_misses": critical,
        "over_triage": [r["id"] for r in over],
        "harm_score": sum(harm(r["ref"], r["pred"]) for r in rows),
        "confusion": Counter((r["ref"], r["pred"]) for r in rows),
    }
    clar = [r for r in rows if r.get("asked") is not None]
    if clar:
        need = [r for r in clar if r["ref_clarify"]]
        out["clarify_recall"] = sum(r["asked"] for r in need) / len(need) if need else None
        out["asked_in_emergency"] = [r["id"] for r in clar if r["asked"] and r["ref"] == "EMERGENCY_NOW"]
        out["asked_total"] = sum(r["asked"] for r in clar)
    return out


def confusion_table(conf: Counter) -> str:
    short = {"EMERGENCY_NOW": "EMERG", "WITHIN_48H": "48H", "ASYNC_PHYSICIAN": "ASYNC", "SELF_CARE": "SELF"}
    order = DISPOSITIONS[::-1]
    lines = ["| reference \\ predicted | " + " | ".join(short[d] for d in order) + " |",
             "|---|" + "---|" * len(order)]
    for ref in order:
        lines.append(f"| {short[ref]} | " + " | ".join(str(conf.get((ref, p), 0) or "·") for p in order) + " |")
    return "\n".join(lines)
