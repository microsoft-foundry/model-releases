# =============================================================================
# s05_policy_adherence_evaluator.py — Custom prompt-based evaluator (Step 5+)
# =============================================================================
# NARRATIVE ROLE
# Schema and a generic LLM judge can both rate "did this answer look right?"
# but neither can answer the only question that matters for policy Q&A:
# **does the answer stay inside the four corners of travel-policy.md?**
#
# That gap is what this evaluator fills. It implements the 5-axis Policy
# Adherence rubric defined in sample-data/README.md (#evaluating-policy-
# adherence), exactly as documented there:
#   A. Grounding (0.30)              D. Approval-path correctness (0.15)
#   B. Citation correctness (0.20)   E. Scope discipline (0.15)
#   C. Value & threshold accuracy (0.20)
#
# This is the workshop's first **custom prompt-based evaluator** — a story
# beat we revisit in Step 8 (Operate) when we discuss promoting it to a
# managed Foundry Eval Rubric that auto-updates from production traces.
# =============================================================================
from __future__ import annotations

import json
from pathlib import Path

from s02_config import DEPLOY_PLANNER

_POLICY_PATH = (Path(__file__).parent.parent / "sample-data" / "travel-policy.md")
_POLICY_DOC  = _POLICY_PATH.read_text(encoding="utf-8")

_RUBRIC_INSTRUCTIONS = """You are a strict, evidence-bound evaluator for the
World Wide Importers (WWI) Travel & Expense Policy assistant. Score one model
answer at a time against the policy document, on a single metric: POLICY
ADHERENCE. POLICY ADHERENCE is the degree to which the answer stays inside the
four corners of the policy — no invented rules, no misquoted thresholds, no
wrong approval paths, no confident hallucinations.

Score five sub-axes from 0 to 2 (integers only). Cite the policy section
number when you award full marks or deduct points.

A. Grounding (weight 0.30):           every factual claim supported by policy
B. Citation correctness (weight 0.20): cited sections actually contain claim
C. Value & threshold accuracy (0.20): dollar amounts, hours, days exact
D. Approval-path correctness (0.15):  correct approver + correct trigger
                                       (use "n/a" if question has no approval)
E. Scope discipline (weight 0.15):    refuses to invent rules; out-of-scope OK

FINAL = (0.30*A + 0.20*B + 0.20*C + 0.15*D + 0.15*E) / 2,
        rounded to 2 decimal places, in [0.00, 1.00].
        For D=n/a, treat D as 2 in the formula.

VERDICT:  >= 0.85 -> "pass"   0.70-0.8499 -> "ship-with-caveats"   < 0.70 -> "fail"

If the answer is empty / refuses / non-English, all sub-scores 0,
final_score 0.00, verdict "fail", violations ["non_answer"].

Return JSON ONLY (no prose, no code fences) with this shape:
{"A":0|1|2,"B":0|1|2,"C":0|1|2,"D":0|1|2,"E":0|1|2,
 "final_score":0.00,"verdict":"pass|ship-with-caveats|fail",
 "violations":["short_tag",...],"rationale":"<= 40 words"}"""


class PolicyAdherenceEvaluator:
    """LLM-as-judge implementation of the 5-axis Policy Adherence rubric.

    Only scores rows where `intent == "policy_question"`; for every other
    intent it returns score=None / applicable=False so the metric stays
    interpretable (we want the policy-adherence aggregate to reflect ONLY
    policy answers — the slice the fine-tune is supposed to fix).
    """

    def __init__(self, client):
        self._client = client

    def __call__(self, *, answer=None, input=None, intent=None, **kwargs):
        if (intent or "").strip() != "policy_question":
            return {"policy_adherence_score": None,
                    "applicable": False,
                    "verdict": "n/a",
                    "violations": "",
                    "rationale": ""}

        msg = (f"POLICY DOCUMENT (authoritative):\n---\n{_POLICY_DOC}\n---\n\n"
               f"QUESTION:\n{input or ''}\n\n"
               f"MODEL ANSWER:\n{answer or ''}\n\n"
               "Score now. Return only the JSON object.")
        try:
            r = self._client.responses.create(
                model=DEPLOY_PLANNER, temperature=0,
                instructions=_RUBRIC_INSTRUCTIONS,
                input=msg,
                text={"format": {"type": "json_object"}},
            )
            raw = json.loads(r.output_text)
            score = float(raw.get("final_score", 0.0))
            return {
                "policy_adherence_score": max(0.0, min(1.0, score)),
                "applicable": True,
                "verdict": str(raw.get("verdict", "fail")),
                "violations": ",".join(raw.get("violations", []) or []),
                "rationale": str(raw.get("rationale", ""))[:240],
            }
        except Exception as e:
            return {"policy_adherence_score": 0.0,
                    "applicable": True,
                    "verdict": "fail",
                    "violations": "evaluator_error",
                    "rationale": f"evaluator error: {e}"[:240]}
