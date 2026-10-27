"""The single-prompt baseline: same bucket definitions and clarify policy, no extraction or rules."""

from __future__ import annotations

from . import llm, prompts


def triage(message: str, *, cli=None, model: str = llm.DEFAULT_MODEL) -> dict:
    out = llm.structured_call(system=prompts.BASELINE_SYSTEM, user=f"<message>\n{message}\n</message>",
                              schema=prompts.OUTPUT_SCHEMA, effort="high", model=model, cli=cli)
    out["status"] = "Provisional" if out.get("clarifying_questions") else "Final"
    return out
