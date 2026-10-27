"""Step 1: the LLM extracts facts into a fixed schema. It does not triage."""

from __future__ import annotations

from . import llm
from .schema import CONTEXT, FINDINGS, REQUEST_TYPES

EXTRACT_SYSTEM = """You extract facts from an asynchronous patient message for a triage system. You do not decide urgency.

List under `context` and `findings` only the checklist items the message addresses (names from the checklist below):
- status: "present" if the message states it, "denied" if the patient explicitly says it is absent.
- evidence: quotes copied EXACTLY, character for character, from the message.
Items you leave out are recorded as not mentioned.

Rules:
- Record what happened, not the patient's interpretation. "It went away so I figured it was nothing" still means the symptom was present.
- A symptom that resolved is still present (e.g. a 10-minute episode of slurred speech).
- Findings in other people do not count for the patient (except: when a parent writes about a child, the child is the patient).
- Only mark "denied" when the patient says it is absent ("no fever", "breathing fine" = dyspnea denied).
- Do not infer diagnoses or add facts. When unsure, leave the item out.
- minimizing_quotes: exact phrases where the patient downplays or dismisses their symptoms.

""" + "\n".join(
    [f"{title} checklist:\n" + "\n".join(f"- {k}: {q}" for k, q in items.items())
     for title, items in (("Context", CONTEXT), ("Findings", FINDINGS))])


def _items(names) -> dict:
    # Sparse list instead of one property per item: a fully enumerated strict object
    # (~80 nested objects) compiles to a grammar the API rejects as too large.
    return {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["name", "status", "evidence"],
        "properties": {"name": {"type": "string", "enum": list(names)},
                       "status": {"type": "string", "enum": ["present", "denied"]},
                       "evidence": {"type": "array", "items": {"type": "string"}}}}}


def fact_schema() -> dict:
    """Wire schema for the extraction call. `expand` turns its output into the dense form the rules read."""
    num = {"type": ["number", "null"]}
    props = {
        "chief_complaint": {"type": "string", "description": "Main reason for the message in a few words"},
        "request_type": {"type": "string", "enum": REQUEST_TYPES},
        "age_years": {**num, "description": "Patient age in years (fractions for infants), null if not stated"},
        "sex": {"type": "string", "enum": ["female", "male", "unknown"]},
        "pregnancy_weeks": {**num, "description": "Weeks pregnant if stated"},
        "postpartum_weeks": {**num, "description": "Weeks since delivery if stated"},
        "fever_days": {**num, "description": "Days of fever if stated"},
        "minimizing_quotes": {"type": "array", "items": {"type": "string"}},
        "context": _items(CONTEXT),
        "findings": _items(FINDINGS),
    }
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


def expand(raw: dict) -> dict:
    """Sparse extraction -> one entry per checklist item (status present / denied / not_mentioned).
    If an item is listed twice with conflicting status, present wins (the cautious reading)."""
    out = {k: v for k, v in raw.items() if k not in ("context", "findings")}
    for group, names in (("context", CONTEXT), ("findings", FINDINGS)):
        dense = {k: {"status": "not_mentioned", "evidence": []} for k in names}
        for it in raw.get(group) or []:
            cur = dense[it["name"]]
            if cur["status"] != "present":
                cur["status"] = it["status"]
            cur["evidence"] += list(it.get("evidence") or [])
        out[group] = dense
    return out


def extract_facts(message: str, *, cli=None, model: str = llm.DEFAULT_MODEL) -> dict:
    raw = llm.structured_call(system=EXTRACT_SYSTEM, user=f"<message>\n{message}\n</message>",
                              schema=fact_schema(), effort="medium", model=model, cli=cli)
    return expand(raw)
