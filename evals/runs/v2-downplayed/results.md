# Disposition eval

Model `claude-opus-5-5` · 26 cases · run `20261024-160206`

| | workflow | baseline | agent |
|---|---|---|---|
| **Urgent sensitivity** (ref EMERG or SAME_DAY, pred either) | 54% | 92% | 100% |
| Emergency sensitivity | 65% | 75% | 100% |
| Critical misses (ref EMERG, pred ASYNC/SELF) | 7 M08 M16 M17 M23 M25 M35 M44 | 0  | 0  |
| Under-triage | 12 | 7 | 0 |
| Over-triage | 1 | 0 | 0 |
| Harm score (lower is better) | 85.5 | 23 | 0 |
| Exact accuracy | 50% | 73% | 100% |
| Clarify recall (asked when reference asks) | — | 100% | 100% |
| Asked a question in an emergency | — | 5 | 0 |

Workflow labels have no SAME_DAY tier; URGENT_ESCALATION is scored as EMERGENCY_NOW, the most generous reading.

## workflow

| reference \ predicted | EMERG | SAME_DAY | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 13 | · | 7 | · |
| SAME_DAY | 1 | · | 5 | · |
| ASYNC | · | · | · | · |
| SELF | · | · | · | · |

## baseline

| reference \ predicted | EMERG | SAME_DAY | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 15 | 5 | · | · |
| SAME_DAY | · | 4 | 1 | 1 |
| ASYNC | · | · | · | · |
| SELF | · | · | · | · |

## agent

| reference \ predicted | EMERG | SAME_DAY | ASYNC | SELF |
|---|---|---|---|---|
| EMERG | 20 | · | · | · |
| SAME_DAY | · | 6 | · | · |
| ASYNC | · | · | · | · |
| SELF | · | · | · | · |

## Agent internals

- Rule floor raised the LLM's own answer on 0 case(s): none
- Cases routed to a human after an LLM failure: 0
- Grounding issues: 0

## Per case

| id | ref | workflow | baseline | agent | floor | rules |
|---|---|---|---|---|---|---|
| M02 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-ACS-01 |
| M04 | SAME_DAY | **ASYNC_PHYSICIAN** | SAME_DAY | SAME_DAY | SAME_DAY | R-DFI-01 |
| M05 | SAME_DAY | **EMERGENCY_NOW** | SAME_DAY | SAME_DAY | SAME_DAY | R-SUI-01 |
| M08 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-SAH-01 |
| M09 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-OB-01 |
| M12 | SAME_DAY | **ASYNC_PHYSICIAN** | SAME_DAY | SAME_DAY | SAME_DAY | R-COPD-01 |
| M14 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-ANAPH-01 |
| M16 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **SAME_DAY** | EMERGENCY_NOW | EMERGENCY_NOW | R-PEDS-03,R-PEDS-01 |
| M17 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-CES-01 |
| M20 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-HEAD-01 |
| M21 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-STROKE-01,R-EYE-01 |
| M22 | SAME_DAY | **ASYNC_PHYSICIAN** | **SELF_CARE** | SAME_DAY | SAME_DAY | R-ANKLE-01 |
| M23 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-STROKE-01 |
| M25 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **SAME_DAY** | EMERGENCY_NOW | EMERGENCY_NOW | R-VTE-01 |
| M27 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-SBO-01 |
| M28 | EMERGENCY_NOW | EMERGENCY_NOW | **SAME_DAY** | EMERGENCY_NOW | EMERGENCY_NOW | R-OB-02,R-RISK-01 |
| M31 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-MEN-01 |
| M33 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-DKA-01 |
| M35 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-GIB-01 |
| M37 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-TORS-01 |
| M39 | EMERGENCY_NOW | EMERGENCY_NOW | **SAME_DAY** | EMERGENCY_NOW | EMERGENCY_NOW | R-PPMH-01,R-PPMH-03 |
| M41 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-MEN-01 |
| M43 | SAME_DAY | **ASYNC_PHYSICIAN** | SAME_DAY | SAME_DAY | SAME_DAY | R-TB-01 |
| M44 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **SAME_DAY** | EMERGENCY_NOW | EMERGENCY_NOW | R-HF-01 |
| M48 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-HIP-01 |
| M49 | SAME_DAY | **ASYNC_PHYSICIAN** | **ASYNC_PHYSICIAN** | SAME_DAY | SAME_DAY | R-PLEUR-01 |
