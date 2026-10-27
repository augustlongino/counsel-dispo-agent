"""Offline tests: rules, floor enforcement, the emergency no-question policy, fail-safe routing,
grounding asymmetry, and eval scoring. No API key needed."""

from dispo import agent, extract, rules, verify
from dispo.extract import fact_schema
from dispo.schema import CONTEXT, DISPOSITIONS, FINDINGS
from evals import metrics, run_eval


def facts(present=(), denied=(), request_type="symptom", **fields):
    def item(n):
        s = "present" if n in present else "denied" if n in denied else "not_mentioned"
        return {"status": s, "evidence": [] if s == "not_mentioned" else [n]}
    out = {"chief_complaint": "", "request_type": request_type, "age_years": None, "sex": "unknown",
           "pregnancy_weeks": None, "postpartum_weeks": None, "fever_days": None, "minimizing_quotes": [],
           "context": {k: item(k) for k in CONTEXT}, "findings": {k: item(k) for k in FINDINGS}}
    out.update(fields)
    return out


def sparse(present=None, denied=None, request_type="symptom", **fields):
    """What the extraction call returns on the wire: only the items the message addresses."""
    items = [{"name": k, "status": "present", "evidence": [q]} for k, q in (present or {}).items()]
    items += [{"name": k, "status": "denied", "evidence": [q]} for k, q in (denied or {}).items()]
    out = {"chief_complaint": "", "request_type": request_type, "age_years": None, "sex": "unknown",
           "pregnancy_weeks": None, "postpartum_weeks": None, "fever_days": None, "minimizing_quotes": [],
           "context": [i for i in items if i["name"] in CONTEXT],
           "findings": [i for i in items if i["name"] in FINDINGS]}
    out.update(fields)
    return out


def floor(**kw):
    return rules.apply(facts(**kw))


def judgment(disp, questions=(), lane="none"):
    return {"disposition": disp, "lane": lane, "rationale": "", "clarifying_questions": list(questions),
            "escalation_trigger": "if worse", "patient_reply": ""}


# ---- rules ----

def test_resolved_tia_is_emergency_despite_minimizing():
    r = floor(present=["focal_deficit"], minimizing_quotes=["I figured it was nothing"])
    assert r["floor"] == "EMERGENCY_NOW" and "R-STROKE-01" in [x["id"] for x in r["fired"]]


def test_infant_fever_with_amber_features_is_emergency():
    assert floor(present=["fever", "reduced_urine_output", "poor_feeding"], age_years=0.5)["floor"] == "EMERGENCY_NOW"
    assert floor(present=["fever", "poor_feeding"], age_years=0.5)["floor"] == "EMERGENCY_NOW"
    assert floor(present=["fever"], age_years=3)["floor"] == "SELF_CARE"


def test_ankle_unknown_tenderness_counts_as_positive():
    assert floor(present=["ankle_injury"])["floor"] == "WITHIN_48H"
    assert floor(present=["ankle_injury"], denied=["ottawa_bone_tenderness", "ottawa_unable_4_steps"])["floor"] == "SELF_CARE"


def test_pleuritic_pain_is_emergency_because_perc_needs_vitals():
    assert floor(present=["pleuritic_chest_pain"], age_years=28)["floor"] == "EMERGENCY_NOW"


def test_dvt_with_risk_factor_is_emergency():
    assert floor(present=["unilateral_leg_swelling_pain", "vte_risk_factor"])["floor"] == "EMERGENCY_NOW"
    assert floor(present=["unilateral_leg_swelling_pain"])["floor"] == "SELF_CARE"


def test_new_vs_known_heart_failure():
    assert floor(present=["orthopnea_or_pnd"])["floor"] == "EMERGENCY_NOW"
    assert floor(present=["orthopnea_or_pnd", "known_heart_failure"])["floor"] == "WITHIN_48H"


def test_postpartum_thoughts_of_harm_are_crisis_emergency():
    r = floor(present=["postpartum", "thoughts_harm_infant"], postpartum_weeks=2)
    assert r["floor"] == "EMERGENCY_NOW" and r["lane"] == "crisis"


def test_passive_and_active_si_are_crisis_emergencies():
    assert floor(present=["suicidal_ideation_passive"])["floor"] == "EMERGENCY_NOW"
    assert floor(present=["suicidal_ideation_passive"])["lane"] == "crisis"
    assert floor(present=["suicidal_ideation_active"])["floor"] == "EMERGENCY_NOW"


def test_high_risk_population_never_self_care():
    assert floor(present=["immunocompromised", "dysuria_or_frequency"])["floor"] == "ASYNC_PHYSICIAN"
    assert floor(present=["immunocompromised"], request_type="refill")["floor"] == "SELF_CARE"


def test_same_day_is_retired():
    assert "SAME_DAY" not in DISPOSITIONS and all(r.floor in DISPOSITIONS for r in rules.RULES)


def test_rule_ids_are_unique():
    ids = [r.id for r in rules.RULES]
    assert len(ids) == len(set(ids))


# ---- finalize: floor, emergency policy, fail-safe ----

def test_floor_overrides_lower_llm_answer():
    f = facts(present=["sudden_severe_headache"])
    out = agent.finalize(f, rules.apply(f), judgment("ASYNC_PHYSICIAN", ["How bad is it?"]))
    assert out["disposition"] == "EMERGENCY_NOW" and out["floor_overrode_llm"]
    assert out["clarifying_questions"] == [] and out["status"] == "Final"


def test_llm_may_escalate_above_floor():
    f = facts(present=["dysuria_or_frequency"])
    out = agent.finalize(f, rules.apply(f), judgment("WITHIN_48H"))
    assert out["disposition"] == "WITHIN_48H" and not out["floor_overrode_llm"]


def test_questions_make_case_provisional():
    f = facts(present=["fever"], age_years=3)
    out = agent.finalize(f, rules.apply(f), judgment("ASYNC_PHYSICIAN", ["How many wet diapers?"]))
    assert out["status"] == "Provisional" and out["risk_modifier_question"]


def test_llm_failure_routes_to_physician():
    out = agent.finalize(None, {"floor": "SELF_CARE", "lane": "none", "fired": []}, None)
    assert out["disposition"] == "ASYNC_PHYSICIAN" and out["needs_human"]


def test_judge_failure_keeps_rule_floor():
    f = facts(present=["testicular_pain_sudden"])
    out = agent.finalize(f, rules.apply(f), None)
    assert out["disposition"] == "EMERGENCY_NOW" and out["needs_human"]


# ---- grounding ----

def test_grounding_keeps_ungrounded_red_flag_but_drops_ungrounded_denial():
    msg = "My neck is stiff. No vomiting."
    f = facts(present=["neck_stiffness"], denied=["nausea_or_vomiting"])
    f["findings"]["neck_stiffness"]["evidence"] = ["neck feels stiff"]          # paraphrase, not in message
    f["findings"]["nausea_or_vomiting"]["evidence"] = ["never threw up"]       # not in message
    out, issues = verify.ground(f, msg)
    assert out["findings"]["neck_stiffness"]["status"] == "present"
    assert out["findings"]["neck_stiffness"]["ungrounded"]
    assert out["findings"]["nausea_or_vomiting"]["status"] == "not_mentioned"
    assert len(issues) == 2


def test_grounded_quotes_pass():
    msg = "I have a fever of 101.5 and my neck is stiff."
    f = facts(present=["fever"])
    f["findings"]["fever"]["evidence"] = ["a fever of 101.5"]
    _, issues = verify.ground(f, msg)
    assert issues == []


# ---- schema and eval ----

def test_fact_schema_is_strict():
    def walk(s):
        if s.get("type") == "object":
            assert s.get("additionalProperties") is False
            assert set(s["required"]) == set(s["properties"])
            for v in s["properties"].values():
                walk(v)
    walk(fact_schema())


def test_expand_fills_unlisted_items_and_present_wins():
    raw = sparse(present={"fever": "temp 101"}, denied={"neck_stiffness": "neck is fine"})
    raw["findings"].append({"name": "fever", "status": "denied", "evidence": ["no fever now"]})
    out = extract.expand(raw)
    assert set(out["findings"]) == set(FINDINGS) and set(out["context"]) == set(CONTEXT)
    assert out["findings"]["fever"]["status"] == "present"
    assert out["findings"]["neck_stiffness"]["status"] == "denied"
    assert out["findings"]["focal_deficit"] == {"status": "not_mentioned", "evidence": []}


def test_harm_weights_favor_under_triage():
    assert metrics.harm("EMERGENCY_NOW", "ASYNC_PHYSICIAN") > metrics.harm("SELF_CARE", "EMERGENCY_NOW")
    assert metrics.harm("WITHIN_48H", "WITHIN_48H") == 0


def test_replay_scoring_end_to_end():
    cases = run_eval.load_cases(run_eval.ROOT / "data/messages.csv", only=["C08", "C01"])
    raw = {
        "C08": {"agent_facts": facts(present=["sudden_severe_headache", "neck_stiffness"]),
                "agent_judgment": judgment("WITHIN_48H"), "baseline": judgment("ASYNC_PHYSICIAN")},
        "C01": {"agent_facts": facts(present=["chest_pain_or_pressure"]),      # no radiation etc. -> no floor
                "agent_judgment": judgment("SELF_CARE"), "baseline": judgment("SELF_CARE")},
    }
    summ, detail = run_eval.score(cases, raw)
    assert summ["agent"]["emergency_sensitivity"] == 1.0
    assert summ["baseline"]["critical_misses"] == ["C08"]
    assert summ["workflow"]["critical_misses"] == ["C08"]


# ---- full pipeline with a fake client (no network) ----

class _Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Resp:
    def __init__(self, payload, stop="end_turn"):
        import json
        self.content, self.stop_reason, self.stop_details = [_Block(json.dumps(payload))], stop, None


class _FakeClient:
    """Returns canned extraction then judgment, in call order."""

    def __init__(self, *payloads):
        self.payloads, self.calls = list(payloads), []
        outer = self

        class _M:
            def create(self, **kw):
                outer.calls.append(kw)
                return _Resp(outer.payloads.pop(0))
        self.messages = _M()
        self.beta = type("B", (), {"messages": _M()})()


def test_triage_with_fake_client_enforces_floor_and_grounds():
    msg = "60M. My speech got slurred for 10 minutes. It's back to normal now so I figured it was nothing."
    f = sparse(present={"focal_deficit": "My speech got slurred for 10 minutes"},
               minimizing_quotes=["I figured it was nothing"])
    cli = _FakeClient(f, judgment("ASYNC_PHYSICIAN", ["Any weakness?"]))
    out = agent.triage(msg, cli=cli)
    assert out["disposition"] == "EMERGENCY_NOW" and out["floor_overrode_llm"]
    assert out["clarifying_questions"] == [] and out["grounding_issues"] == []
    assert out["minimizing_quotes"] == ["I figured it was nothing"]
    assert all(c["output_config"]["format"]["type"] == "json_schema" for c in cli.calls)


def test_refusal_fails_safe():
    cli = _FakeClient()
    cli.beta.messages.create = lambda **kw: _Resp({}, stop="refusal")
    cli.messages.create = cli.beta.messages.create
    out = agent.triage("I have a cough.", cli=cli)
    assert out["disposition"] == "ASYNC_PHYSICIAN" and out["needs_human"] and out["errors"]


def test_ablation_hides_rules_and_drops_floor():
    msg = "60M. My speech got slurred for 10 minutes. It's back to normal now so I figured it was nothing."
    f = sparse(present={"focal_deficit": "My speech got slurred for 10 minutes"})
    cli = _FakeClient(judgment("ASYNC_PHYSICIAN"))
    out = agent.triage(msg, cli=cli, raw_facts=extract.expand(f), use_rules=False)
    assert out["disposition"] == "ASYNC_PHYSICIAN" and out["rules_fired"] == []
    assert out["shadow_rules"] == ["R-STROKE-01"] and out["shadow_floor"] == "EMERGENCY_NOW"
    sent = cli.calls[0]
    assert "rules_fired" not in sent["messages"][0]["content"] and "rules engine" not in sent["system"]


def test_replay_scoring_respects_ablation_flag():
    cases = run_eval.load_cases(run_eval.ROOT / "data/messages.csv", only=["C08"])
    raw = {"C08": {"use_rules": False, "agent_facts": facts(present=["sudden_severe_headache"]),
                   "agent_judgment": judgment("WITHIN_48H"), "baseline": judgment("WITHIN_48H")}}
    summ, _ = run_eval.score(cases, raw)
    assert summ["agent"]["emergency_sensitivity"] == 0.0


def test_output_is_triage_only():
    from dispo import prompts
    assert "safety_net" not in prompts.OUTPUT_SCHEMA["properties"]
    assert "Never give medical advice" in prompts.BASELINE_SYSTEM and "Never give medical advice" in prompts.JUDGE_SYSTEM
