# Demo

```bash
source .venv/bin/activate
export ANTHROPIC_API_KEY=...
python -m demo.server            # http://127.0.0.1:8000
```

The page runs one message through up to three arms side by side: the agent, Claude alone, and the agent
without rules. Each agent result shows the extracted findings with quotes (minimizing phrases struck
through), the rules that fired and the floor, the model's own pick, the final disposition and the routing
reply. When the agent asks questions, a reply box appends the patient's answer and re-runs; the
disposition can rise but not fall.

**Saved run** replays the most recent recorded output for any of the 96 test cases without an API call.

Suggested cases where the arms diverge:

| Case | Presentation | Claude alone | Agent | Rule |
|---|---|---|---|---|
| M49 | Pleuritic chest pain, downplayed | ASYNC_PHYSICIAN | EMERGENCY_NOW | R-PLEUR-01 |
| C05 | Passive suicidal ideation | ASYNC_PHYSICIAN | EMERGENCY_NOW (crisis) | R-SUI-01 |
| C10 | Episodic right upper quadrant pain | Provisional | Provisional | clarify path |
