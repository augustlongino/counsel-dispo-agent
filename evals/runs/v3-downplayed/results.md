# Disposition eval

Model `claude-opus-5-5` · 26 cases · run `v3-downplayed`

| | workflow | baseline | agent |
|---|---|---|---|
| **Urgent sensitivity** (ref EMERG or WITHIN_48H, pred either) | 54% | 92% | 100% |
| Emergency sensitivity | 58% | 88% | 100% |
| Critical misses (ref EMERG, pred ASYNC/SELF) | 10 M04 M08 M12 M16 M17 M23 M25 M35 M44 M49 | 1 M49 | 0  |
| Under-triage | 12 | 4 | 0 |
| Over-triage | 0 | 0 | 0 |
| Harm score (lower is better) | 106 | 21 | 0 |
| Exact accuracy | 54% | 85% | 100% |
| Clarify recall (asked when reference asks) | — | 100% | 100% |
| Asked a question in an emergency | — | 3 | 0 |

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
| EMERG | 24 | · | · | · |
| 48H | · | 2 | · | · |
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
| M04 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **WITHIN_48H** | EMERGENCY_NOW | EMERGENCY_NOW | R-DFI-01 |
| M05 | EMERGENCY_NOW | EMERGENCY_NOW | **WITHIN_48H** | EMERGENCY_NOW | EMERGENCY_NOW | R-SUI-01 |
| M08 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-SAH-01 |
| M09 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-OB-01 |
| M12 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-COPD-01 |
| M14 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-ANAPH-01 |
| M16 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-PEDS-03,R-PEDS-01 |
| M17 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-CES-01 |
| M20 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-HEAD-01 |
| M21 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-STROKE-01,R-EYE-01 |
| M22 | WITHIN_48H | **ASYNC_PHYSICIAN** | **SELF_CARE** | WITHIN_48H | WITHIN_48H | R-ANKLE-01 |
| M23 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-STROKE-01 |
| M25 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-VTE-01 |
| M27 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-SBO-01 |
| M28 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-OB-02,R-RISK-01 |
| M31 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-MEN-01 |
| M33 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-DKA-01 |
| M35 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-GIB-01 |
| M37 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-TORS-01 |
| M39 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-PPMH-01,R-PPMH-03 |
| M41 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-MEN-01 |
| M43 | WITHIN_48H | **ASYNC_PHYSICIAN** | WITHIN_48H | WITHIN_48H | WITHIN_48H | R-TB-01 |
| M44 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-HF-01 |
| M48 | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | EMERGENCY_NOW | R-HIP-01 |
| M49 | EMERGENCY_NOW | **ASYNC_PHYSICIAN** | **ASYNC_PHYSICIAN** | EMERGENCY_NOW | EMERGENCY_NOW | R-PLEUR-01 |
