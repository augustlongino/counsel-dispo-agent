# Disposition eval

Model `claude-opus-5-5` · 20 cases · run `v3-ablation-new · ABLATION: no rules, no floor`

| | baseline | agent |
|---|---|---|
| **Urgent sensitivity** (ref EMERG or WITHIN_48H, pred either) | 100% | 100% |
| Emergency sensitivity | 100% | 100% |
| Critical misses (ref EMERG, pred ASYNC/SELF) | 0  | 0  |
| Under-triage | 2 | 2 |
| Over-triage | 0 | 1 |
| Harm score (lower is better) | 2 | 2.5 |
| Exact accuracy | 90% | 85% |
| Clarify recall (asked when reference asks) | 80% | 100% |
| Asked a question in an emergency | 0 | 0 |

Workflow labels have no WITHIN_48H tier; URGENT_ESCALATION is scored as EMERGENCY_NOW, the most generous reading.

## baseline

| reference \ predicted | EMERG | 48H | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 8 | · | · | · |
| 48H | · | · | · | · |
| ASYNC | · | · | 7 | 2 |
| SELF | · | · | · | 3 |

## agent

| reference \ predicted | EMERG | 48H | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 8 | · | · | · |
| 48H | · | · | · | · |
| ASYNC | · | · | 7 | 2 |
| SELF | · | · | 1 | 2 |

## Agent internals

- Rule floor raised the LLM's own answer on 0 case(s): none
- Cases routed to a human after an LLM failure: 0
- Grounding issues: 0

## Per case

| id | ref | workflow | baseline | agent | floor | rules |
|---|---|---|---|---|---|---|
| H01 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H02 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H03 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H04 | ASYNC_PHYSICIAN | — | **SELF_CARE** | **SELF_CARE** | SELF_CARE |  |
| H05 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H06 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H07 | ASYNC_PHYSICIAN | — | **SELF_CARE** | **SELF_CARE** | SELF_CARE |  |
| H08 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H09 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H10 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H11 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H12 | SELF_CARE | — | SELF_CARE | **ASYNC_PHYSICIAN** | SELF_CARE |  |
| H13 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H14 | SELF_CARE | — | SELF_CARE | SELF_CARE | SELF_CARE |  |
| H15 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H16 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H17 | SELF_CARE | — | SELF_CARE | SELF_CARE | SELF_CARE |  |
| H18 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H19 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H20 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
