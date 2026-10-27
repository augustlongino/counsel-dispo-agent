"""Thin wrapper around the Messages API: one structured-output call, refusal-aware."""

from __future__ import annotations

import json
import os

DEFAULT_MODEL = os.environ.get("DISPO_MODEL", "claude-opus-5-5")
# Server-side refusal fallback (Claude API only). Set DISPO_FALLBACKS=0 to turn it off.
USE_FALLBACKS = os.environ.get("DISPO_FALLBACKS", "1") != "0"


class LLMRefusal(RuntimeError):
    pass


def client():
    import anthropic  # lazy, so tests and replay mode don't need the SDK or a key
    return anthropic.Anthropic()


def structured_call(*, system: str, user: str, schema: dict, effort: str = "medium",
                    model: str = DEFAULT_MODEL, cli=None, max_tokens: int = 16000) -> dict:
    """Return the JSON object the model produced under `schema`."""
    cli = cli or client()
    kwargs = dict(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
    )
    if USE_FALLBACKS:
        resp = cli.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
    else:
        resp = cli.messages.create(**kwargs)
    if resp.stop_reason == "refusal":
        cat = getattr(getattr(resp, "stop_details", None), "category", None)
        raise LLMRefusal(f"model declined (category={cat})")
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("output truncated at max_tokens")
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return json.loads(text)
