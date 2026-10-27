# Disposition eval

Model `claude-opus-5-5` · 26 cases · run `v3-ablation-downplayed · ABLATION: no rules, no floor`

| | workflow | baseline | agent |
|---|---|---|---|
| **Urgent sensitivity** (ref EMERG or WITHIN_48H, pred either) | 54% | 92% | 92% |
| Emergency sensitivity | 58% | 88% | 88% |
| Critical misses (ref EMERG, pred ASYNC/SELF) | 10 M04 M08 M12 M16 M17 M23 M25 M35 M44 M49 | 1 M49 | 1 M49 |
| Under-triage | 12 | 4 | 4 |
| Over-triage | 0 | 0 | 0 |
| Harm score (lower is better) | 106 | 21 | 21 |
| Exact accuracy | 54% | 85% | 85% |
| Clarify recall (asked when reference asks) | — | 100% | 100% |
| Asked a question in an emergency | — | 3 | 3 |

Workflow labels have no WITHIN_48H tier; URGENT_ESCALATION is scored as EMERGENCY_NOW, the most generous reading.

## workflow

| reference \ predicted | EMERG | 48H | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 14 | · | 10 | · |
| 48H | · | · | 2 | · |
| ASYNC | · | · | · | · |
| SELF | · | · | · | · |

## baseline

| reference \ predicted | EMERG | 48H | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 21 | 2 | 1 | · |
| 48H | · | 1 | · | 1 |
| ASYNC | · | · | · | · |
| SELF | · | · | · | · |

## agent

| reference \ predicted | EMERG | 48H | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 21 | 2 | 1 | · |
| 48H | · | 1 | · | 1 |
| ASYNC | · | · | · | · |
| SELF | · | · | · | · |

## Agent internals

- Rule floor raised the LLM's own answer on 0 case(s): none
- Cases routed to a human after an LLM failure: 0
- Grounding issues: 0

## Per case

| id | ref | workflow | baseline | agent | floor | rules |
|---|---|---|---|---|---|---|
| M02 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M04 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **WITHIN_48H** | **WITHIN_48H** | SELF_CARE |  |
| M05 | EMERGENCY_NOW | EMERGENCY_NOW | **WITHIN_48H** | **WITHIN_48H** | SELF_CARE |  |
| M08 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M09 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M12 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M14 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M16 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M17 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M20 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M21 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M22 | WITHIN_48H | **ASYNC_PHYSICIAN** | **SELF_CARE** | **SELF_CARE** | SELF_CARE |  |
| M23 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M25 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M27 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M28 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M31 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M33 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M35 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M37 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M39 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M41 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M43 | WITHIN_48H | **ASYNC_PHYSICIAN** | WITHIN_48H | WITHIN_48H | SELF_CARE |  |
| M44 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M48 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| M49 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **ASYNC_PHYSICIAN** | **ASYNC_PHYSICIAN** | SELF_CARE |  |
