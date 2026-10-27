"""The hybrid agent: extract (LLM) -> ground (code) -> red-flag floor (code) -> judgment (LLM, floor-bounded).

    python -m dispo.agent "My 6-month-old has a fever..."
"""

from __future__ import annotations

import argparse
import json

from . import extract, llm, prompts, rules, verify
from .schema import RANK, max_disposition

RISK_MODIFIERS = {"immunocompromised": "a weakened immune system (transplant, chemotherapy, steroids, biologics)",
                  "active_cancer": "cancer or cancer treatment",
                  "anticoagulant": "blood thinners"}


def _facts_summary(facts: dict) -> str:
    lines = []
    for group in ("context", "findings"):
        for name, f in (facts.get(group) or {}).items():
            if f["status"] != "not_mentioned":
                ev = "; ".join(f.get("evidence") or [])
                lines.append(f"- {name}: {f['status']}" + (f' ("{ev}")' if ev else ""))
    head = {k: facts.get(k) for k in ("chief_complaint", "request_type", "age_years", "sex",
                                      "pregnancy_weeks", "postpartum_weeks", "fever_days")}
    return json.dumps(head) + "\n" + "\n".join(lines)


def judge(message: str, facts: dict, ruling: dict | None, *, cli=None, model=llm.DEFAULT_MODEL) -> dict:
    """ruling=None is the ablation arm: the judge sees the facts but no rules and no floor."""
    user = f"<message>\n{message}\n</message>\n\n<extracted_facts>\n{_facts_summary(facts)}\n</extracted_facts>"
    if ruling is not None:
        fired = "\n".join(f"- {r['id']} ({r['floor']}): {r['summary']}" for r in ruling["fired"]) or "- none"
        user += f"\n\n<rules_fired>\n{fired}\n</rules_fired>\nFloor: {ruling['floor']}"
    system = prompts.JUDGE_SYSTEM if ruling is not None else prompts.JUDGE_NO_RULES_SYSTEM
    return llm.structured_call(system=system, user=user, schema=prompts.OUTPUT_SCHEMA,
                               effort="high", model=model, cli=cli)


def finalize(facts: dict | None, ruling: dict, judgment: dict | None) -> dict:
    """Combine the code floor and the LLM judgment. Pure function: replayable and unit-tested."""
    needs_human = facts is None or judgment is None
    j = judgment or {}
    floor = ruling["floor"]
    # A failed LLM step never silently lands in self-care: route to a physician at least.
    proposed = j.get("disposition") or "ASYNC_PHYSICIAN"
    final = max_disposition(floor, proposed, "ASYNC_PHYSICIAN" if needs_human else "SELF_CARE")
    lane = "crisis" if "crisis" in (ruling["lane"], j.get("lane")) else (j.get("lane") or "none")
    questions = list(j.get("clarifying_questions") or [])
    trigger = j.get("escalation_trigger") or ""
    if final == "EMERGENCY_NOW":
        questions, trigger = [], ""          # policy: no questions in emergencies
    risk_q = None
    if facts and final != "EMERGENCY_NOW" and facts.get("request_type") == "symptom":
        f = rules.Facts(facts)
        unknown = [txt for k, txt in RISK_MODIFIERS.items() if f.unknown(k)]
        if unknown:
            risk_q = "Do you have " + ", ".join(unknown[:-1]) + (" or " if len(unknown) > 1 else "") + unknown[-1] + "?"
    return {
        "disposition": final,
        "status": "Provisional" if questions else "Final",
        "lane": lane,
        "floor": floor,
        "llm_disposition": j.get("disposition"),
        "floor_overrode_llm": bool(j.get("disposition")) and RANK[floor] > RANK[j["disposition"]],
        "rules_fired": [r["id"] for r in ruling["fired"]],
        "clarifying_questions": questions,
        "risk_modifier_question": risk_q,
        "escalation_trigger": trigger,
        "patient_reply": j.get("patient_reply", ""),
        "rationale": j.get("rationale", ""),
        "needs_human": needs_human,
    }


NO_RULES = {"floor": "SELF_CARE", "lane": "none", "fired": []}


def triage(message: str, *, cli=None, model=llm.DEFAULT_MODEL, raw_facts=None, raw_judgment=None,
           use_rules: bool = True) -> dict:
    """Run one message. Pass raw_facts/raw_judgment to replay recorded LLM output without the API.
    use_rules=False is the ablation: rules are neither shown to the judge nor applied as a floor
    (the rules that would have fired are still reported, as shadow_rules)."""
    errors = []
    facts = raw_facts
    if facts is None:
        try:
            facts = extract.extract_facts(message, cli=cli, model=model)
        except Exception as e:  # noqa: BLE001 - any failure fails safe
            errors.append(f"extract: {e}")
    verified, issues = verify.ground(facts, message) if facts else (None, [])
    shadow = rules.apply(verified) if verified else NO_RULES
    ruling = shadow if use_rules else NO_RULES
    judgment = raw_judgment
    if judgment is None and verified is not None:
        try:
            judgment = judge(message, verified, ruling if use_rules else None, cli=cli, model=model)
        except Exception as e:  # noqa: BLE001
            errors.append(f"judge: {e}")
    out = finalize(verified, ruling, judgment)
    out.update(grounding_issues=issues, errors=errors, shadow_rules=[r["id"] for r in shadow["fired"]],
               shadow_floor=shadow["floor"],
               minimizing_quotes=(verified or {}).get("minimizing_quotes", []),
               raw_facts=facts, raw_judgment=judgment)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("message")
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    ap.add_argument("--json", action="store_true", help="print the full record")
    a = ap.parse_args()
    out = triage(a.message, model=a.model)
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"{out['disposition']} ({out['status']}, lane={out['lane']}); floor {out['floor']} from {out['rules_fired'] or 'no rules'}")
    for q in out["clarifying_questions"]:
        print(f"  ? {q}")
    if out["risk_modifier_question"]:
        print(f"  ? {out['risk_modifier_question']}")
    print(f"\n{out['patient_reply']}")


if __name__ == "__main__":
    main()
