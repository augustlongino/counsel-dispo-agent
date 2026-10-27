# dispo-agent

This is a disposition agent for asynchronous patient messages. It reads a message and decides where it
should go: emergency care now, an in-person visit within 48 hours, the physician's async queue, or self-care.
I built it for the Counsel Health Physician AI Engineer take-home. All of the messages are synthetic.

The short version of the design: Claude pulls the clinical facts out of the message, a set of rules taken
from published guidelines sets the lowest disposition the case can get, and Claude makes the final call
from there. It can escalate past the rules but it can't go below them.

## Why I built it this way

I'm an internist, and the failure I worry about most in triage is the patient who tells you it's probably
nothing. Models are trained to be agreeable, and their sense of when chest pain can wait comes from training
data nobody vetted. I didn't want the decision to depend on the model getting both of those right every
time.

So I split the work the way it's split on a teaching service. Someone takes the history and presents the
pertinent positives and negatives without deciding anything. Then someone with the thresholds in their head
makes the call. Here, Claude takes the history, and the guideline rules are the thresholds.

## Results

Claude Opus 5.5, one live run per case, current version (v3.1). Each cell is critical misses · harm score ·
exact accuracy.

| Test set | Workflow labels | Claude alone | Agent |
|---|---|---|---|
| Development (n = 50) | 10 · 109 · 66% | 2 · 30 · 86% | **0 · 3 · 92%** |
| New, written blind to the rules (n = 20) | — | 0 · 1.5 · 90% | **0 · 1.5 · 90%** |
| Downplayed rewrites of the urgent cases (n = 26) | 10 · 106 · 54% | 1 · 21 · 85% | **0 · 0 · 100%** |

A critical miss is an emergency that got routed to the async queue or to self-care. The agent didn't have
any, on any set, in any version.

Claude alone missed passive suicidal ideation ("everyone would be better off without me") and pleuritic
chest pain in a young man whose vitals we couldn't check, and it missed the chest pain again when the patient
downplayed it. The agent caught all three because a rule fired: C-SSRS for the first, PERC for the others.

The ablation was the most useful thing I ran. I gave Claude the same extracted facts but took away the rules
and the floor, and it scored exactly like Claude alone (harm 23 vs 23, against 3.5 for the full agent). So the
extraction structure isn't what helps. The guideline thresholds are. That also explains the tie on the 20 new
cases: 17 of them didn't match any of my rules, and without a rule the agent is just Claude.

Results for every version are in [VERSIONS.md](VERSIONS.md), and the raw outputs are in
[`evals/runs/`](evals/runs).

## Dispositions

| Disposition | What it means |
|---|---|
| `EMERGENCY_NOW` | Needs in-person care today: 911, the ED or urgent care. No questions asked. |
| `WITHIN_48H` | Needs an exam, imaging or labs within 48 hours. |
| `ASYNC_PHYSICIAN` | A physician can handle it in the async queue, within about a day. |
| `SELF_CARE` | No clinician action needed. |

The task came with three buckets. I split `URGENT_ESCALATION` in two because it lumped "call 911" together with
"get seen soon," and those are very different instructions to give a patient. I drew the line at 48 hours
because that's what an async service can actually schedule. If it can't wait 48 hours, it's an emergency.

There's also a crisis lane (988 and immediate human outreach) and an admin lane for refills and paperwork. If
the agent asks a clarifying question, the case is Provisional, and the patient's answer can move it up but
never down. The agent only triages. It doesn't diagnose, suggest home treatment or give doses.

## How it works

```
message ─▶ extract (LLM) ─▶ ground (code) ─▶ rule floor (code) ─▶ judge (LLM) ─▶ combine (code)
```

1. **Extract** ([`dispo/extract.py`](dispo/extract.py)). Claude marks each of 65 findings as present, denied
   or not mentioned, with a verbatim quote, and doesn't make a disposition. Phrases like "probably nothing"
   are saved separately, and the rules never read them.
2. **Ground** ([`dispo/verify.py`](dispo/verify.py)). Code checks every quote against the message. If a
   denial has no quote, it becomes "not mentioned," because a made-up negative could turn off a rule. If a
   red flag has no quote, it's kept and flagged, because dropping it could hide an emergency.
3. **Rule floor** ([`dispo/rules.py`](dispo/rules.py)). There are 37 rules, each tied to a guideline in
   [`adjudication/rules.csv`](adjudication/rules.csv). Several of those guidelines assume an exam or vitals
   (Ottawa ankle, PERC). We can't check those remotely, so I count anything that can't be assessed as
   positive.
4. **Judge** ([`dispo/agent.py`](dispo/agent.py)). Claude sees the message, the checked facts and the rules
   that fired, then picks a disposition, writes any clarifying questions and drafts a short routing reply.
5. **Combine.** The final disposition is the higher of the rule floor and Claude's pick. Emergencies never
   get questions. If Claude errors out or refuses, the case goes to a physician, never to self-care.

"Claude alone" ([`dispo/baseline.py`](dispo/baseline.py)) gets the same bucket definitions, the same
question policy and the same scope in a single prompt, so the only thing that differs is the architecture.

## How I evaluated it

I didn't use the provided workflow labels as the answer key. When I went through them, 10 of the 24
emergencies had been routed to async or self-care, including a resolved TIA, a thunderclap headache, a DVT
after a long flight and a febrile infant. So I adjudicated all 50 messages myself against published
guidelines ([`adjudication/sources.csv`](adjudication/sources.csv), with every PMID checked in PubMed). I froze
those labels before finishing the rules
([`data/reference_standard_v3.csv`](data/reference_standard_v3.csv)).

Because I wrote the rules with those 50 cases in front of me, their scores are a ceiling, not an estimate.
So I froze the rules and built two more test sets:

| Set | n | How it was made |
|---|---|---|
| Development | 50 | The provided messages. |
| New | 20 | Written after the rules were frozen, by a separate agent with no access to the code. I labeled them before looking at what the writer intended, and we agreed on 16 of 20 (κ = 0.72). |
| Downplayed | 26 | Every urgent development case rewritten so the patient minimizes it. I checked that every fact survived, so each one keeps its original label. |

Accuracy treats a missed stroke the same as an extra visit, so I report critical misses first, then a harm
score, then exact accuracy. The harm score sums the errors using these weights:

| Error (correct → predicted) | Weight |
|---|---|
| Emergency → async or self-care | 10 |
| Within 48 h → self-care | 5 |
| Emergency → within 48 h, or within 48 h → async | 3 |
| Async → self-care | 1 |
| Any over-triage | 0.5 |

When scoring the workflow labels I counted `URGENT_ESCALATION` as `EMERGENCY_NOW`, which is the most
generous reading I could give them.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                                   # offline tests

# Re-score the recorded runs (no API key needed)
python -m evals.run_eval --replay evals/runs/v3.1-development/raw.jsonl
python -m evals.run_eval --cases data/heldout/heldout_cases.csv \
    --reference data/heldout/reference_heldout_v3.csv --replay evals/runs/v3.1-new/raw.jsonl
python -m evals.run_eval --cases data/minimized/minimized_cases.csv --replay evals/runs/v3.1-downplayed/raw.jsonl

# Live runs (need ANTHROPIC_API_KEY)
python -m evals.run_eval                              # development set
python -m evals.run_eval --no-rules --facts-from evals/runs/v3.1-development/raw.jsonl   # ablation
python -m dispo.agent "My 6-month-old has had a fever since yesterday and isn't feeding."
python -m demo.server                                 # local demo page, see DEMO.md
```

The default model is `claude-opus-5-5`; set `DISPO_MODEL` to change it.

## What's in here

| Path | Contents |
|---|---|
| `dispo/` | The agent: schema, extraction, grounding, rules, judge, and the single-prompt comparison |
| `evals/` | Metrics, the eval harness and the recorded runs |
| `data/` | The messages, the reference standards, and the new and downplayed test sets |
| `adjudication/` | The rule table with sources and async adaptations, and the source list |
| `demo/` | A local web page that runs the agent, Claude alone and the no-rules version side by side |
| `tests/` | Offline unit tests |

## Limitations

The biggest one is rule coverage. 17 of the 20 new cases didn't match any rule, and on those the agent is just
Claude. My 37 rules were enough to make the point, but they won't cover what real patients send.

The extraction checklist is fixed, so it misses anything that isn't on it. One of the new cases was giant cell
arteritis, and there's no item for jaw claudication.

The evidence is thin. I'm the only rater, the messages were written by an LLM, the test sets are small and
every case was run once.

The floor never actually had to override Claude in these runs, so I can say it's there, but I haven't seen it
tested under pressure.

An async message is a bad way to tell someone they're having a stroke. In production, `EMERGENCY_NOW` needs a
person or a phone call, not just a reply.

## What I'd do next

The next version would look up the relevant guideline instead of relying on my hand-written rules. That would
mean a curated, versioned library of guideline excerpts keyed by chief complaint, not the open web, which would
bring the unvetted-source problem right back. Claude would have to quote the passage it relied on, code would
check the quote, and the rules would stay as the floor. Long term, that library should be built from licensed
telephone-triage protocols.

After that: extraction driven by the complaint with a free-text field for anything off the list, chart context
(age, problem list, medications), a second physician rater, real de-identified messages, and repeated runs to
measure variance.
