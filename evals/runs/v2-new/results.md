# Disposition eval

Model `claude-opus-5-5` · 20 cases · run `20261024-152641`

| | baseline | agent |
|---|---|---|
| **Urgent sensitivity** (ref EMERG or SAME_DAY, pred either) | 100% | 100% |
| Emergency sensitivity | 71% | 86% |
| Critical misses (ref EMERG, pred ASYNC/SELF) | 0  | 0  |
| Under-triage | 3 | 3 |
| Over-triage | 1 | 0 |
| Harm score (lower is better) | 7.5 | 5 |
| Exact accuracy | 80% | 85% |
| Clarify recall (asked when reference asks) | 83% | 83% |
| Asked a question in an emergency | 2 | 1 |

Workflow labels have no SAME_DAY tier; URGENT_ESCALATION is scored as EMERGENCY_NOW, the most generous reading.

## baseline

| reference \ predicted | EMERG | SAME_DAY | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 5 | 2 | · | · |
| SAME_DAY | · | 1 | · | · |
| ASYNC | · | · | 8 | 1 |
| SELF | · | · | 1 | 2 |

## agent

| reference \ predicted | EMERG | SAME_DAY | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 6 | 1 | · | · |
| SAME_DAY | · | 1 | · | · |
| ASYNC | · | · | 7 | 2 |
| SELF | · | · | · | 3 |

## Agent internals

- Rule floor raised the LLM's own answer on 0 case(s): none
- Cases routed to a human after an LLM failure: 0
- Grounding issues: 0

## Per case

| id | ref | workflow | baseline | agent | floor | rules |
|---|---|---|---|---|---|---|
| H01 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H02 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H03 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-PEDS-02,R-RISK-01 |
| H04 | ASYNC_PHYSICIAN | — | **SELF_CARE** | **SELF_CARE** | SELF_CARE |  |
| H05 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H06 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | ASYNC_PHYSICIAN | R-RISK-01 |
| H07 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | **SELF_CARE** | SELF_CARE |  |
| H08 | EMERGENCY_NOW | — | **SAME_DAY** | **SAME_DAY** | SELF_CARE |  |
| H09 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H10 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H11 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H12 | SELF_CARE | — | **ASYNC_PHYSICIAN** | SELF_CARE | SELF_CARE |  |
| H13 | SAME_DAY | — | SAME_DAY | SAME_DAY | ASYNC_PHYSICIAN | R-RISK-01 |
| H14 | SELF_CARE | — | SELF_CARE | SELF_CARE | SELF_CARE |  |
| H15 | EMERGENCY_NOW | — | EMERGENCY_NOW | EMERGENCY_NOW | SELF_CARE |  |
| H16 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H17 | SELF_CARE | — | SELF_CARE | SELF_CARE | SELF_CARE |  |
| H18 | EMERGENCY_NOW | — | **SAME_DAY** | EMERGENCY_NOW | SELF_CARE |  |
| H19 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
| H20 | ASYNC_PHYSICIAN | — | ASYNC_PHYSICIAN | ASYNC_PHYSICIAN | SELF_CARE |  |
