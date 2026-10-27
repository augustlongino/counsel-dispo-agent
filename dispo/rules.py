"""Step 2: deterministic red-flag rules set a disposition floor.

Each rule ID matches adjudication/rules.csv, where its source guideline and async adaptation
are recorded. Rules read extracted facts, never the patient's
framing, so "I figured it was nothing" cannot lower a floor. The LLM may escalate above the
floor in step 3 but never below it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .schema import RANK


class Facts:
    """Read-only view over verified extraction output."""

    def __init__(self, facts: dict):
        self.raw = facts
        self._f = {**(facts.get("context") or {}), **(facts.get("findings") or {})}

    def status(self, name: str) -> str:
        return (self._f.get(name) or {}).get("status", "not_mentioned")

    def p(self, *names: str) -> bool:
        """Any of the named items is present."""
        return any(self.status(n) == "present" for n in names)

    def unknown(self, name: str) -> bool:
        return self.status(name) == "not_mentioned"

    def num(self, key: str):
        v = self.raw.get(key)
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    @property
    def age(self):
        return self.num("age_years")

    def age_lt(self, years: float) -> bool:
        return self.age is not None and self.age < years

    def age_ge(self, years: float) -> bool:
        return self.age is not None and self.age >= years

    @property
    def pregnant_20wk_plus(self) -> bool:
        w = self.num("pregnancy_weeks")
        return self.p("pregnant") and w is not None and w >= 20

    @property
    def early_pregnancy(self) -> bool:
        w = self.num("pregnancy_weeks")
        return self.p("pregnant") and (w is None or w < 20)

    def postpartum_within(self, weeks: float) -> bool:
        w = self.num("postpartum_weeks")
        return self.p("postpartum") and (w is None or w <= weeks)


@dataclass(frozen=True)
class Rule:
    id: str
    floor: str
    when: Callable[[Facts], bool]
    summary: str
    lane: str = "none"


E, W, A = "EMERGENCY_NOW", "WITHIN_48H", "ASYNC_PHYSICIAN"

RULES: list[Rule] = [
    # ---- EMERGENCY_NOW ----
    Rule("R-ACS-01", E, lambda f: f.p("chest_pain_or_pressure") and f.p("pain_radiation_arm_jaw", "diaphoresis", "nausea_or_vomiting", "dyspnea_at_rest"),
         "Chest pressure with radiation, sweating, nausea or dyspnea"),
    Rule("R-SAH-01", E, lambda f: f.p("sudden_severe_headache"), "Thunderclap / worst-ever headache"),
    Rule("R-STROKE-01", E, lambda f: f.p("focal_deficit"), "New focal deficit, ongoing or resolved"),
    Rule("R-EYE-01", E, lambda f: f.p("monocular_vision_loss"), "Sudden monocular vision loss"),
    Rule("R-OB-01", E, lambda f: (f.pregnant_20wk_plus or f.postpartum_within(6)) and f.p("persistent_headache", "visual_disturbance", "dyspnea_at_rest"),
         "Pregnancy >= 20 wk or early postpartum with preeclampsia features"),
    Rule("R-OB-02", E, lambda f: f.early_pregnancy and f.p("vaginal_bleeding_more_than_spotting", "pelvic_or_lower_abdominal_pain"),
         "Early pregnancy with bleeding or pain (ectopic not excluded)"),
    Rule("R-CES-01", E, lambda f: f.p("back_pain") and f.p("bladder_or_bowel_dysfunction", "saddle_numbness"),
         "Back pain with bladder/bowel or saddle symptoms"),
    Rule("R-VTE-01", E, lambda f: f.p("unilateral_leg_swelling_pain") and f.p("vte_risk_factor"),
         "Unilateral leg swelling/pain with VTE risk factor"),
    Rule("R-VTE-02", E, lambda f: f.p("hemoptysis") or (f.p("unilateral_leg_swelling_pain") and f.p("dyspnea_at_rest", "pleuritic_chest_pain", "syncope_or_orthostatic")),
         "Possible PE"),
    Rule("R-GIB-01", E, lambda f: f.p("melena_or_hematemesis") and (f.p("syncope_or_orthostatic", "anticoagulant") or f.age_ge(60)),
         "GI bleed with orthostasis, anticoagulant or age >= 60"),
    Rule("R-ANAPH-01", E, lambda f: f.p("lip_tongue_throat_swelling") or (f.p("allergen_exposure") and f.p("hives") and f.p("dyspnea_at_rest", "nausea_or_vomiting", "syncope_or_orthostatic")),
         "Anaphylaxis criteria"),
    Rule("R-DKA-01", E, lambda f: f.p("diabetes") and f.p("hyperglycemia_over_300") and f.p("unable_to_keep_fluids", "nausea_or_vomiting", "altered_mental_status"),
         "Hyperglycemia with vomiting / cannot hydrate"),
    Rule("R-MEN-01", E, lambda f: f.p("fever") and f.p("neck_stiffness", "photophobia", "non_blanching_rash", "altered_mental_status"),
         "Fever with meningism, petechiae or altered mental status"),
    Rule("R-HEAD-01", E, lambda f: f.p("head_injury") and f.p("anticoagulant", "nausea_or_vomiting", "altered_mental_status", "persistent_headache"),
         "Head injury on anticoagulant or with symptoms"),
    Rule("R-SBO-01", E, lambda f: f.p("abdominal_distension") and f.p("nausea_or_vomiting") and f.p("obstipation"),
         "Bowel obstruction pattern"),
    Rule("R-TORS-01", E, lambda f: f.p("testicular_pain_sudden"), "Sudden testicular pain"),
    Rule("R-HIP-01", E, lambda f: f.p("fall") and f.p("unable_to_bear_weight") and (f.p("hip_or_groin_pain") or f.age_ge(65)),
         "Fall, cannot bear weight (possible hip fracture)"),
    Rule("R-VERT-02", E, lambda f: f.p("central_vertigo_features"), "Dizziness with central features"),
    Rule("R-SUI-02", E, lambda f: f.p("suicidal_ideation_active"), "Suicidal ideation with method, intent or plan", lane="crisis"),
    Rule("R-PPMH-02", E, lambda f: f.postpartum_within(52) and f.p("psychosis_features"), "Postpartum psychosis features", lane="crisis"),
    Rule("R-PPMH-01", E, lambda f: f.postpartum_within(52) and f.p("thoughts_harm_infant", "suicidal_ideation_passive"),
         "Postpartum thoughts of harming infant or self", lane="crisis"),
    Rule("R-PEDS-02", E, lambda f: f.age_lt(5) and f.p("fever") and (f.p("non_blanching_rash", "altered_mental_status") or f.age_lt(0.25)),
         "Child < 5 with fever and a NICE red feature"),
    Rule("R-PEDS-03", E, lambda f: f.age_lt(1) and f.p("fever") and f.p("reduced_urine_output") and f.p("poor_feeding"),
         "Infant with fever and >= 2 amber features (reduced urine, poor feeding)"),
    Rule("R-DFI-02", E, lambda f: f.p("diabetes") and f.p("foot_wound_infection_signs") and f.p("fever", "systemic_infection_signs"),
         "Diabetic foot infection with systemic signs"),
    Rule("R-COPD-02", E, lambda f: f.p("copd") and f.p("dyspnea_at_rest", "altered_mental_status"), "COPD with dyspnea at rest or confusion"),
    Rule("R-HF-01", E, lambda f: f.p("orthopnea_or_pnd") and not f.p("known_heart_failure"), "New-onset orthopnea/PND"),
    # ---- EMERGENCY_NOW: cannot safely wait 48 h ----
    Rule("R-SUI-01", E, lambda f: f.p("suicidal_ideation_passive"), "Passive suicidal ideation", lane="crisis"),
    Rule("R-PEDS-01", E, lambda f: f.age_lt(5) and f.p("fever") and (f.p("reduced_urine_output", "poor_feeding") or (f.num("fever_days") or 0) >= 5),
         "Child < 5 with fever and a NICE amber feature"),
    Rule("R-DFI-01", E, lambda f: f.p("diabetes") and f.p("foot_wound_infection_signs"), "Diabetic foot infection"),
    Rule("R-COPD-01", E, lambda f: f.p("copd") and f.p("dyspnea_minimal_exertion"), "COPD exacerbation limiting minimal activity"),
    # Async principle: a decision-rule item that can't be assessed remotely counts as positive.
    Rule("R-PLEUR-01", E, lambda f: f.p("pleuritic_chest_pain"), "Pleuritic chest pain; PERC vitals unavailable async"),
    # ---- WITHIN_48H ----
    Rule("R-PPMH-03", W, lambda f: f.postpartum_within(52) and f.p("depressive_symptoms"), "Postpartum depressive symptoms", lane="crisis"),
    Rule("R-HF-02", W, lambda f: f.p("known_heart_failure") and f.p("bilateral_leg_edema_progressive", "orthopnea_or_pnd"), "Known HF, worsening"),
    Rule("R-TB-01", W, lambda f: f.p("chronic_cough_3wk") and f.p("night_sweats", "weight_loss_unintentional", "hemoptysis", "tb_risk"),
         "Presumptive TB (in-person, masked)"),
    Rule("R-ANKLE-01", W, lambda f: f.p("ankle_injury") and (f.p("ottawa_unable_4_steps", "ottawa_bone_tenderness") or f.unknown("ottawa_bone_tenderness")),
         "Ankle injury; Ottawa item positive or not assessable"),
    # ---- ASYNC_PHYSICIAN (never self-care) ----
    Rule("R-RISK-01", A, lambda f: f.raw.get("request_type") == "symptom" and (f.p("immunocompromised", "active_cancer", "pregnant") or f.age_lt(0.25)),
         "Symptom in a high-risk population (immunocompromised, cancer, pregnancy, infant < 3 mo)"),
    Rule("R-VERT-01", A, lambda f: f.p("positional_vertigo_brief"), "Positional vertigo needs clinician diagnosis"),
]


def apply(facts: dict) -> dict:
    """Return the floor, the rules that fired, and the lane they imply."""
    f = Facts(facts)
    fired = [r for r in RULES if r.when(f)]
    floor = max((r.floor for r in fired), key=RANK.__getitem__, default="SELF_CARE")
    lane = "crisis" if any(r.lane == "crisis" for r in fired) else "none"
    return {"floor": floor, "lane": lane,
            "fired": [{"id": r.id, "floor": r.floor, "summary": r.summary} for r in fired]}
