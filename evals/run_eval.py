"""Score three systems against the frozen reference standard.

Systems
  workflow   Counsel's existing labels (URGENT_ESCALATION scored as EMERGENCY_NOW, the most generous reading)
  baseline   one prompt: bucket definitions + message -> disposition
  agent      extract facts -> ground -> red-flag floor -> floor-bounded LLM judgment

Usage
  python -m evals.run_eval                                   # live (needs ANTHROPIC_API_KEY); saves raw outputs
  python -m evals.run_eval --replay evals/runs/<run>/raw.jsonl  # re-score saved LLM outputs, no API calls
  python -m evals.run_eval --only C08 C23                    # subset
  python -m evals.run_eval --cases data/minimized/minimized_cases.csv      # rows carry source_id -> development labels
  python -m evals.run_eval --cases data/heldout/heldout_cases.csv --reference data/heldout/reference_heldout.csv
  python -m evals.run_eval --no-rules --facts-from evals/runs/<run>/raw.jsonl   # ablation: same facts, no rules
Ablation (--no-rules): the judge sees the extracted facts but no rules and no floor. With --facts-from, the
recorded extraction and single-prompt answers of an earlier run are reused, so only the judgment is new.
Replay re-runs grounding, rules and finalize on the recorded LLM output, so a rule change can be
re-scored for free.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path

from dispo import agent, baseline, llm
from evals import metrics

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_MAP = {"URGENT_ESCALATION": "EMERGENCY_NOW", "ASYNC_PHYSICIAN": "ASYNC_PHYSICIAN", "SELF_CARE": "SELF_CARE"}


def load_cases(path: Path, only=None, reference: Path | None = None) -> list[dict]:
    msgs = {r["id"]: r for r in csv.DictReader(open(path, encoding="utf-8-sig"))}
    ref = {r["id"]: r for r in csv.DictReader(open(reference or ROOT / "data/reference_standard_v3.csv", encoding="utf-8-sig"))}
    cases = []
    for cid, m in msgs.items():
        src = m.get("source_id") or cid          # minimized variants point back to their source case
        if only and cid not in only:
            continue
        r = ref[src]
        cases.append({"id": cid, "source_id": src, "message": m["message"],
                      "workflow": m.get("disposition") or r.get("original_label") or None,
                      "ref": r["reference_label"], "ref_clarify": r["clarify"] == "Y"})
    return cases


def run_live(cases, model, out_path: Path, use_rules: bool = True, prior: dict | None = None):
    cli = llm.client()
    with open(out_path, "w") as fh:
        for c in cases:
            t0 = time.time()
            rec = {"id": c["id"], "model": model, "use_rules": use_rules}
            p = (prior or {}).get(c["id"])
            if p:
                rec["facts_from"] = True
            a = agent.triage(c["message"], cli=cli, model=model, use_rules=use_rules,
                             raw_facts=p["agent_facts"] if p else None)
            rec["agent_facts"], rec["agent_judgment"], rec["agent_errors"] = a["raw_facts"], a["raw_judgment"], a["errors"]
            if p:
                rec["baseline"] = p.get("baseline")
            else:
                try:
                    rec["baseline"] = baseline.triage(c["message"], cli=cli, model=model)
                except Exception as e:  # noqa: BLE001
                    rec["baseline"], rec["baseline_error"] = None, str(e)
            rec["seconds"] = round(time.time() - t0, 1)
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"  {c['id']}: ref={c['ref']:<15} agent={a['disposition']:<15} "
                  f"baseline={(rec['baseline'] or {}).get('disposition', 'ERROR')}")


def score(cases, raw: dict, use_rules: bool = True):
    rows = {"workflow": [], "baseline": [], "agent": []}
    detail = []
    for c in cases:
        r = raw[c["id"]]
        a = agent.triage(c["message"], raw_facts=r["agent_facts"] or {}, raw_judgment=r["agent_judgment"],
                         use_rules=r.get("use_rules", use_rules)) \
            if r.get("agent_facts") else agent.finalize(None, {"floor": "SELF_CARE", "lane": "none", "fired": []}, None)
        b = r.get("baseline") or {"disposition": "ASYNC_PHYSICIAN", "clarifying_questions": [], "error": True}
        base = dict(id=c["id"], ref=c["ref"], ref_clarify=c["ref_clarify"])
        if c["workflow"]:                         # held-out cases have no workflow label
            rows["workflow"].append({**base, "pred": WORKFLOW_MAP[c["workflow"]], "asked": None})
        rows["baseline"].append({**base, "pred": b["disposition"], "asked": bool(b.get("clarifying_questions"))})
        rows["agent"].append({**base, "pred": a["disposition"], "asked": bool(a["clarifying_questions"])})
        detail.append({"id": c["id"], "ref": c["ref"], "workflow": c["workflow"], "baseline": b["disposition"],
                       "agent": a["disposition"], "floor": a["floor"], "llm": a.get("llm_disposition"),
                       "rules": ",".join(a["rules_fired"]), "shadow_rules": ",".join(a.get("shadow_rules", [])), "floor_overrode_llm": a["floor_overrode_llm"],
                       "agent_status": a["status"], "minimizing": " | ".join(a.get("minimizing_quotes", [])),
                       "grounding_issues": len(a.get("grounding_issues", [])), "needs_human": a["needs_human"]})
    return {k: metrics.summarize(v) for k, v in rows.items() if v}, detail


def report(summ: dict, detail: list[dict], model: str, run_name: str) -> str:
    pct = lambda x: "—" if x is None else f"{100 * x:.0f}%"
    systems = [s for s in ("workflow", "baseline", "agent") if s in summ]
    out = [f"# Disposition eval", "", f"Model `{model}` · {summ['agent']['n']} cases · run `{run_name}`", "",
           "| | " + " | ".join(systems) + " |", "|---|" + "---|" * len(systems)]
    def row(label, fn):
        out.append(f"| {label} | " + " | ".join(fn(summ[s]) for s in systems) + " |")
    row("**Urgent sensitivity** (ref EMERG or WITHIN_48H, pred either)", lambda s: pct(s["urgent_sensitivity"]))
    row("Emergency sensitivity", lambda s: pct(s["emergency_sensitivity"]))
    row("Critical misses (ref EMERG, pred ASYNC/SELF)", lambda s: f"{len(s['critical_misses'])} {' '.join(s['critical_misses'])}")
    row("Under-triage", lambda s: str(len(s["under_triage"])))
    row("Over-triage", lambda s: str(len(s["over_triage"])))
    row("Harm score (lower is better)", lambda s: f"{s['harm_score']:g}")
    row("Exact accuracy", lambda s: pct(s["accuracy"]))
    row("Clarify recall (asked when reference asks)", lambda s: pct(s.get("clarify_recall")))
    row("Asked a question in an emergency", lambda s: "—" if "asked_in_emergency" not in s else str(len(s["asked_in_emergency"])))
    out += ["", "Workflow labels have no WITHIN_48H tier; URGENT_ESCALATION is scored as EMERGENCY_NOW, the most generous reading.", ""]
    for s in systems:
        out += [f"## {s}", "", metrics.confusion_table(summ[s]["confusion"]), ""]
    overrides = [d["id"] for d in detail if d["floor_overrode_llm"]]
    out += ["## Agent internals", "",
            f"- Rule floor raised the LLM's own answer on {len(overrides)} case(s): {' '.join(overrides) or 'none'}",
            f"- Cases routed to a human after an LLM failure: {sum(d['needs_human'] for d in detail)}",
            f"- Grounding issues: {sum(d['grounding_issues'] for d in detail)}", ""]
    out += ["## Per case", "", "| id | ref | workflow | baseline | agent | floor | rules |", "|---|---|---|---|---|---|---|"]
    for d in detail:
        flag = lambda p: f"**{p}**" if p != d["ref"] else p
        wf = flag(WORKFLOW_MAP[d["workflow"]]) if d["workflow"] else "—"
        out.append(f"| {d['id']} | {d['ref']} | {wf} | {flag(d['baseline'])} | "
                   f"{flag(d['agent'])} | {d['floor']} | {d['rules']} |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", type=Path, default=ROOT / "data/messages.csv")
    ap.add_argument("--reference", type=Path, help="reference labels (default: data/reference_standard_v3.csv)")
    ap.add_argument("--replay", type=Path)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    ap.add_argument("--no-rules", action="store_true", help="ablation: no rules shown to the judge, no floor")
    ap.add_argument("--facts-from", type=Path, help="reuse extraction and single-prompt answers from this raw.jsonl")
    a = ap.parse_args()
    cases = load_cases(a.cases, a.only, a.reference)
    if a.replay:
        run_dir, raw_path = a.replay.parent, a.replay
    else:
        run_dir = ROOT / "evals/runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir.mkdir(parents=True)
        raw_path = run_dir / "raw.jsonl"
        prior = {r["id"]: r for r in map(json.loads, a.facts_from.read_text().splitlines()) if r} if a.facts_from else None
        run_live(cases, a.model, raw_path, use_rules=not a.no_rules, prior=prior)
    raw = {r["id"]: r for r in map(json.loads, raw_path.read_text().splitlines()) if r}
    model = next(iter(raw.values()))["model"]
    summ, detail = score([c for c in cases if c["id"] in raw], raw, use_rules=not a.no_rules)
    (run_dir / "results.md").write_text(report(summ, detail, model, run_dir.name + (" · ABLATION: no rules, no floor" if a.no_rules else "")))
    with open(run_dir / "per_case.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(detail[0]))
        w.writeheader()
        w.writerows(detail)
    print((run_dir / "results.md").read_text().split("## workflow")[0])


if __name__ == "__main__":
    main()
