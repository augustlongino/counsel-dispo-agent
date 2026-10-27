# Versions

I froze the development labels before finishing the rules, and froze the rules before the new and
downplayed cases were written. Every change after that is listed here. You can compare harm within a
version but not across versions, because v3 changed the answer key itself.

| Version | Date | Change |
|---|---|---|
| v2 | 2026-10-24 | Reference standard and 37 rules frozen. Buckets: `EMERGENCY_NOW`, `SAME_DAY`, `ASYNC_PHYSICIAN`, `SELF_CARE`. New and downplayed sets written and labeled blind. |
| v3 | 2026-10-25 | `SAME_DAY` replaced by `WITHIN_48H`; `EMERGENCY_NOW` extended to urgent care today. Nine rule floors re-assigned (R-SUI-01, R-PEDS-01, R-DFI-01, R-COPD-01, R-PLEUR-01 to `EMERGENCY_NOW`; R-PPMH-03, R-HF-02, R-TB-01, R-ANKLE-01 to `WITHIN_48H`). Seven reference labels raised (C04, C05, C12, C49, H13 to `EMERGENCY_NOW`; C22, C43 to `WITHIN_48H`). Rule conditions unchanged. |
| v3 ablation | 2026-10-25 | Comparison arm: same extracted facts, no rules shown to the judge, no floor. Default agent unchanged. |
| v3.1 | 2026-10-26 | Triage-only output: advice and safety-net text removed from all arms; replies route only. Rules unchanged. |

Because the new cases had been seen before v3, the v2 result on that set is the fully blind one.

## Harm by version

| Version | Development (Workflow · Claude alone · Agent) | New (Claude alone · Agent) | Downplayed (Claude alone · Agent) |
|---|---|---|---|
| v2 | 88.5 · 28 · 3.5 | 7.5 · 5 | 23 · 0 |
| v3 | 109 · 23 · 3.5 | 2 · 2 | 21 · 0 |
| v3 ablation (agent without rules) | — · 23 · 23 | 2 · 2.5 | 21 · 21 |
| v3.1 | 109 · 30 · 3 | 1.5 · 1.5 | 21 · 0 |

The agent had zero critical misses on every set in every version. Removing advice (v3.1) changed no agent
disposition; Claude alone moved from 23 to 30 between runs, which reflects run-to-run variance.

## Current file hashes (sha256)

```
491491d64d129b2552852285eb7ff8fe83172a3e3aa7c00732292f788f6d70fa  dispo/__init__.py
7ec8fad166dcca397c362558784595bee39b7f24c18ad30f21059611426aac83  dispo/agent.py
e748ed4569d96afea18303d13e567a7f9380e762bea510f448ebd2031371f929  dispo/baseline.py
d793a9f45c6623b2b502bd4335e818338b3325b0b9daa68f8e12c430b627c74a  dispo/extract.py
f32d676409250ab4f7719b3f2d7b5bf089066f9748a381fcb2406fcd68c2abf0  dispo/llm.py
6ceeeee1d96167fff9f76f79dcfd763c82ce9e16293e0445a133564c5743b9cf  dispo/prompts.py
56af9d8bdeeb220e034a36ea294407c5439d3f5363c4e573362e14f09269bcce  dispo/rules.py
622391ad77fbd5e4e786d5a2b78cdee76dacd806520b0b815866397e10bfb6b3  dispo/schema.py
9106d62be6a5f3003ff379bb614f9649bc46e47379e05609661a27d42a15b94d  dispo/verify.py
```

Rule logic is unchanged since v3. The extraction wire format was changed once before any agent run
(sparse list in place of one object per item, after the API rejected the original schema as too large); item
names, definitions and the dense form the rules read are unchanged.
