# Recorded runs

Each folder holds `raw.jsonl` (recorded LLM outputs), `per_case.csv` and `results.md`.
v3 and v3.1 runs re-score from `raw.jsonl` with the current code (`--replay`); v2 results were scored with
the v2 code and reference standard.

| Folder | Set | Arm | Reference |
|---|---|---|---|
| `v2-development`, `v2-new`, `v2-downplayed` | 50 / 20 / 26 | agent and Claude alone | v2 |
| `v3-development`, `v3-new`, `v3-downplayed` | 50 / 20 / 26 | agent and Claude alone | v3 |
| `v3-ablation-*` | 50 / 20 / 26 | agent without rules | v3 |
| `v3.1-development`, `v3.1-new`, `v3.1-downplayed` | 50 / 20 / 26 | agent and Claude alone (current) | v3 |
