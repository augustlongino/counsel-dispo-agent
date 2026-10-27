"""Local demo UI: run one message through the agent, Claude alone and the no-rules ablation, side by side.

    python -m demo.server                 # http://127.0.0.1:8000, live API calls
    python -m demo.server --port 8080

Live calls need ANTHROPIC_API_KEY. If the API is slow or down, tick "Saved run" in the page:
any of the 96 eval cases is replayed from the newest run in evals/runs/ with no API call.
Binds to 127.0.0.1 only.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dispo import agent, baseline, llm, rules, verify
from dispo.schema import max_disposition

ROOT = Path(__file__).resolve().parents[1]
PAGE = Path(__file__).with_name("index.html")
CASE_FILES = ["data/messages.csv", "data/heldout/heldout_cases.csv", "data/minimized/minimized_cases.csv"]
# The scripted demo, in order. Everything else is in the case picker.
SCRIPT = [("M49", "Pleuritic pain, downplayed"), ("C05", "Passive suicidal ideation"),
          ("C10", "Upper right belly pain (clarify)"), ("C49", "Pleuritic pain"), ("M23", "TIA, downplayed")]


def load_cases() -> dict:
    cases = {}
    for rel in CASE_FILES:
        for r in csv.DictReader(open(ROOT / rel, encoding="utf-8-sig")):
            cases[r["id"]] = r["message"]
    return cases


def load_saved(use_rules: bool) -> dict:
    """Newest clean record per case id across every run in evals/runs/, for one arm."""
    saved = {}
    for path in sorted((ROOT / "evals/runs").glob("*/raw.jsonl")):
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            if r.get("use_rules", True) == use_rules and r.get("agent_facts") and not r.get("agent_errors"):
                saved[r["id"]] = {**r, "run": path.parent.name}
    return saved


CASES = load_cases()
SAVED, SAVED_NO_RULES = load_saved(True), load_saved(False)
BY_TEXT = {v.strip(): k for k, v in CASES.items()}


def rule_detail(message: str, raw_facts: dict | None) -> list[dict]:
    if not raw_facts:
        return []
    verified, _ = verify.ground(raw_facts, message)
    return rules.apply(verified)["fired"]


def run(mode: str, message: str, saved: bool) -> dict:
    t0 = time.time()
    rec = (SAVED_NO_RULES if mode == "no_rules" else SAVED).get(BY_TEXT.get(message.strip(), "")) if saved else None
    if saved and rec is None:
        return {"error": "No saved output for this message. Untick 'Saved run' to call the API."}
    if mode == "baseline":
        out = dict(rec["baseline"]) if rec else baseline.triage(message)
        out.setdefault("status", "Provisional" if out.get("clarifying_questions") else "Final")
    elif mode in ("agent", "no_rules"):
        kw = dict(raw_facts=rec["agent_facts"], raw_judgment=rec["agent_judgment"]) if rec else {}
        out = agent.triage(message, use_rules=(mode == "agent"), **kw)
        out["rule_detail"] = rule_detail(message, out.get("raw_facts"))
    else:
        return {"error": f"unknown mode {mode}"}
    out["seconds"] = round(time.time() - t0, 1)
    out["source"] = f"saved run {rec['run']}" if rec else f"live, {llm.DEFAULT_MODEL}"
    return out


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode(), "application/json")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/cases":
            self._json({"script": [{"id": i, "label": l, "message": CASES[i]} for i, l in SCRIPT if i in CASES],
                        "all": [{"id": i, "message": m, "saved": i in SAVED} for i, m in CASES.items()]})
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/run":
            return self._send(404, b"not found", "text/plain")
        req = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        message = (req.get("message") or "").strip()
        if req.get("answer"):  # clarify round: the answer is appended, and can only raise the bucket
            message = f"{message}\n\nPatient's reply to our questions: {req['answer'].strip()}"
        try:
            out = run(req.get("mode", "agent"), message, bool(req.get("saved")) and not req.get("answer"))
        except Exception as e:  # noqa: BLE001 - show the failure on the page, keep the server up
            return self._json({"error": f"{type(e).__name__}: {e}"})
        prior = req.get("prior_disposition")
        if prior and out.get("disposition"):
            out["answer_disposition"] = out["disposition"]
            out["disposition"] = max_disposition(prior, out["disposition"])
            out["prior_disposition"] = prior
        self._json(out)

    def log_message(self, fmt, *args):  # one short line per request
        print(time.strftime("%H:%M:%S"), fmt % args)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    print(f"{len(CASES)} cases, {len(SAVED)} saved agent runs, {len(SAVED_NO_RULES)} saved no-rules runs. Open http://127.0.0.1:{a.port}")
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
