"""Dispositions and the fact schema the extractor fills in.

Every clinical finding is tri-state. "not_mentioned" is a first-class answer, not a default:
it is what drives the clarify path, and for decision rules that need an exam (Ottawa, PERC)
an item that cannot be assessed remotely counts as positive.
"""

from __future__ import annotations

DISPOSITIONS = ["SELF_CARE", "ASYNC_PHYSICIAN", "WITHIN_48H", "EMERGENCY_NOW"]
RANK = {d: i for i, d in enumerate(DISPOSITIONS)}
LANES = ["none", "crisis", "admin/refill"]
STATUSES = ["present", "denied", "not_mentioned"]
REQUEST_TYPES = ["symptom", "refill", "results", "screening", "referral", "medication_question", "other"]


def max_disposition(*ds: str) -> str:
    return max((d for d in ds if d), key=RANK.__getitem__)


# name -> question the extractor answers. Grouped for readability only.
CONTEXT = {
    "immunocompromised": "Is the patient immunocompromised (transplant, chemotherapy, high-dose steroids, HIV with low CD4, biologics)?",
    "active_cancer": "Does the patient have active cancer or current cancer treatment?",
    "anticoagulant": "Does the patient take an anticoagulant or antiplatelet (warfarin, DOAC, clopidogrel)?",
    "diabetes": "Does the patient have diabetes?",
    "copd": "Does the patient have COPD?",
    "known_heart_failure": "Does the patient have a previously diagnosed heart failure?",
    "pregnant": "Is the patient currently pregnant?",
    "postpartum": "Is the patient within 12 months after giving birth?",
}

FINDINGS = {
    # cardiopulmonary
    "chest_pain_or_pressure": "Chest pain, pressure, tightness or squeezing (not pleuritic-only)",
    "pain_radiation_arm_jaw": "Chest pain radiating to arm, jaw, neck or back",
    "diaphoresis": "Sweating / diaphoresis with the symptoms",
    "nausea_or_vomiting": "Nausea or vomiting",
    "dyspnea_at_rest": "Short of breath at rest or while talking",
    "dyspnea_minimal_exertion": "Short of breath with minimal activity (walking in the home, to the bathroom) or worse than usual",
    "pleuritic_chest_pain": "Chest pain that is worse with breathing in",
    "orthopnea_or_pnd": "Must sit up to breathe, or wakes at night short of breath",
    "bilateral_leg_edema_progressive": "Swelling of both legs/ankles that is new or getting worse",
    "unilateral_leg_swelling_pain": "One calf/leg swollen, painful or warm compared with the other",
    "vte_risk_factor": "VTE risk factor: travel > 4 h, recent surgery, immobility, estrogen, cancer, prior clot",
    "hemoptysis": "Coughing up blood",
    "purulent_sputum": "Green/yellow/discolored phlegm",
    "chronic_cough_3wk": "Cough lasting about 3 weeks or longer",
    # neuro
    "sudden_severe_headache": "Sudden, severe, 'worst ever' or thunderclap headache",
    "persistent_headache": "Headache that is severe, persistent or worsening",
    "neck_stiffness": "Stiff neck",
    "photophobia": "Light hurts / sensitivity to light",
    "focal_deficit": "New face droop, arm/leg weakness, slurred or abnormal speech, or vision loss - ongoing OR already resolved",
    "monocular_vision_loss": "Sudden loss of vision in one eye",
    "visual_disturbance": "Blurry vision, spots or other visual change",
    "altered_mental_status": "Confusion, unusually sleepy, hard to wake, floppy",
    "head_injury": "Hit head / head injury",
    "positional_vertigo_brief": "Brief spinning triggered by head position that settles",
    "central_vertigo_features": "Dizziness with double vision, trouble walking, numbness, new severe headache, or constant vertigo",
    "numbness_tingling_hand": "Numbness or tingling in a hand",
    # infection / systemic
    "fever": "Fever (subjective or measured)",
    "non_blanching_rash": "Purple/red spots or rash that does not fade when pressed",
    "systemic_infection_signs": "Chills/rigors, spreading redness with fever, or feeling very unwell with infection",
    "foot_wound_infection_signs": "Foot wound/cut with redness, swelling, warmth, tenderness or pus",
    "night_sweats": "Night sweats",
    "weight_loss_unintentional": "Unintentional weight loss",
    "tb_risk": "TB exposure or origin from a high-TB country",
    "reduced_urine_output": "Fewer wet diapers or passing urine less than usual",
    "poor_feeding": "Not feeding/eating or drinking normally",
    "dysuria_or_frequency": "Burning with urination or urinary frequency",
    "flank_pain": "Flank or back pain with urinary symptoms",
    # GI / GU / OB
    "abdominal_pain_severe": "Severe abdominal pain",
    "abdominal_distension": "Bloated/distended abdomen",
    "obstipation": "No bowel movement or gas for days",
    "melena_or_hematemesis": "Black/tarry stools or vomiting blood",
    "syncope_or_orthostatic": "Fainting, or lightheaded when standing",
    "vaginal_bleeding_more_than_spotting": "Vaginal bleeding more than spotting",
    "pelvic_or_lower_abdominal_pain": "Pelvic or lower abdominal pain/cramping",
    "testicular_pain_sudden": "Sudden severe testicular pain",
    "facial_or_hand_edema": "Swelling of face or hands",
    # MSK / back
    "back_pain": "Back pain",
    "bladder_or_bowel_dysfunction": "New trouble controlling or emptying bladder or bowels",
    "saddle_numbness": "Numbness in the groin/genital/buttock area",
    "fall": "A fall",
    "unable_to_bear_weight": "Cannot put weight on the injured leg",
    "hip_or_groin_pain": "Hip or groin pain",
    "ankle_injury": "Ankle injury (sprain/roll)",
    "ottawa_unable_4_steps": "Unable to take 4 steps on the injured ankle",
    "ottawa_bone_tenderness": "Pain when pressing on the ankle bones or base of 5th metatarsal",
    # allergy / metabolic
    "allergen_exposure": "Recent exposure to a food, sting, drug or other allergen",
    "lip_tongue_throat_swelling": "Swelling of lips, tongue or throat, or throat tightness",
    "hives": "Hives / widespread itchy welts",
    "hyperglycemia_over_300": "Blood sugar over 300 or meter reads HI",
    "unable_to_keep_fluids": "Cannot keep fluids down",
    # mental health
    "suicidal_ideation_passive": "Wishes to be dead or thinks others would be better off without them, without plan/intent",
    "suicidal_ideation_active": "Thoughts of killing self with method, intent, plan or preparation",
    "thoughts_harm_infant": "Thoughts of harming the baby",
    "depressive_symptoms": "Low mood, hopelessness, crying, detachment",
    "psychosis_features": "Hallucinations, delusional beliefs, or not sleeping for days",
}
