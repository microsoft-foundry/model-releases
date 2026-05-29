# =============================================================================
# s05_multi_model_agent.py — v2/v3 multi-model agent (Steps 5 & 6)
# =============================================================================
# NARRATIVE ROLE
# This is the payoff of Step 3's task decomposition.  Instead of one model
# doing everything, each task is routed to the cheapest model capable of it:
#
#   router-nano      → intent classification      (~50ms, fractions of a cent)
#   mini-vision      → receipt OCR (if needed)    (mini pricing)
#   policy-mini-*    → policy QA                  (mini or fine-tuned)
#   planner-gpt41    → orchestration + booking    (frontier, but fewer turns)
#
# v2  (USE_FT_POLICY=False): uses the base mini model for policy
# v3  (USE_FT_POLICY=True):  uses the Step-6 fine-tuned model for policy
#
# The only code difference between v2 and v3 is the boolean below.
# This illustrates the key architectural benefit: because deployments are
# named by job, swapping the underlying model requires zero agent code changes.
# =============================================================================
import json
import re
import time
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI

from s02_tools_mock import TOOL_SCHEMAS, DISPATCH
from s03_router import route
from s02_config import (
    PROJECT_ENDPOINT, DEPLOY_PLANNER, DEPLOY_ROUTER,
    DEPLOY_MINI_VISION, DEPLOY_POLICY_BASE, DEPLOY_POLICY_FT,
)

# DeveloperTier fine-tuned deployments are not routable via the project endpoint.
# Use the Azure OpenAI resource endpoint directly for FT policy calls.
_aoai_match = re.match(r"https://([^.]+)\.services\.ai\.azure\.com", PROJECT_ENDPOINT)
_AOAI_ENDPOINT = f"https://{_aoai_match.group(1)}.openai.azure.com/"

USE_FT_POLICY = True  # v3: route policy QA through the Step-6 fine-tune (policy-mini-ft).

_project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
_client = _project.get_openai_client()  # standard OpenAI client, Responses API

# Separate client for FT model — DeveloperTier SKU requires direct AOAI endpoint
_ft_client = AzureOpenAI(
    azure_endpoint=_AOAI_ENDPOINT,
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
    api_version="2025-01-01-preview",
)


def _bump(usage: dict, model: str, resp) -> None:
    """Accumulate token counts per model for cost calculation."""
    cur = usage.get(model, (0, 0))
    # Responses API uses input_tokens/output_tokens; Chat API uses prompt_tokens/completion_tokens
    u = resp.usage
    tin  = getattr(u, "input_tokens",       None) or getattr(u, "prompt_tokens",     0)
    tout = getattr(u, "output_tokens",      None) or getattr(u, "completion_tokens",  0)
    usage[model] = (cur[0] + tin, cur[1] + tout)


def run(user_message: str, image_url: str | None = None) -> dict:
    t0 = time.time()
    usage: dict[str, tuple[int, int]] = {}  # model -> (input_tokens, output_tokens)

    # 1. Route — cheap nano model classifies intent in ~50ms
    intent = route(user_message, has_image=bool(image_url))
    # router usage isn't returned from route(); bill it conservatively
    usage[DEPLOY_ROUTER] = (250, 35)

    # 2. Optional vision pre-step — extract receipt fields before planning
    vision_facts = None
    if image_url:
        r = _client.responses.create(
            model=DEPLOY_MINI_VISION,
            temperature=0,
            instructions=("Extract receipt fields as JSON: "
                          "merchant, amount, date, category."),
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text",  "text": "Extract. Return JSON only."},
                    {"type": "input_image", "image_url": image_url},
                ],
            }],
            text={"format": {"type": "json_object"}},
        )
        _bump(usage, DEPLOY_MINI_VISION, r)
        try:
            vision_facts = json.loads(r.output_text)
        except Exception:
            vision_facts = {"_raw": r.output_text}  # keep raw if JSON parse fails

    # 3. Pre-resolve policy with the cheap (optionally fine-tuned) model.
    #    The answer is injected into the planner's instructions, so the
    #    frontier model never has to reason about policy from scratch.
    policy_model = DEPLOY_POLICY_FT if USE_FT_POLICY else DEPLOY_POLICY_BASE
    if USE_FT_POLICY:
        # FT model is on DeveloperTier — must call via direct AOAI endpoint
        pol_resp = _ft_client.chat.completions.create(
            model=policy_model,
            temperature=0,
            messages=[
                {"role": "system", "content": "You answer WWI policy questions. Concise."},
                {"role": "user",   "content": user_message},
            ],
        )
        _bump(usage, policy_model, pol_resp)
        policy_note = pol_resp.choices[0].message.content
    else:
        pol = _client.responses.create(
            model=policy_model,
            temperature=0,
            instructions="You answer WWI policy questions. Concise.",
            input=user_message,
        )
        _bump(usage, policy_model, pol)
        policy_note = pol.output_text

    # 4. Planner with tools — frontier model orchestrates the booking turn(s)
    planner_instructions = (
        "You are WWI planner. Use tools. Respect policy. "
        f"Pre-resolved policy: {policy_note}. "
        f"Receipt facts: {vision_facts}. "
        "Return final JSON with keys: flight, hotel, policy_notes, "
        "total_estimated_cost_usd, booking_status."
    )
    input_items: list[dict] = [{"role": "user", "content": user_message}]

    final_response = None
    for _ in range(6):  # max 6 turns to prevent runaway loops
        r = _client.responses.create(
            model=DEPLOY_PLANNER,
            instructions=planner_instructions,
            input=input_items,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        _bump(usage, DEPLOY_PLANNER, r)
        final_response = r
        input_items += [item.model_dump(exclude_none=True) for item in r.output]

        function_calls = [item for item in r.output if item.type == "function_call"]
        if not function_calls:
            break
        for fc in function_calls:
            args = json.loads(fc.arguments)
            out = DISPATCH[fc.name](**args)
            input_items.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": json.dumps(out),
            })

    return {
        "answer": final_response.output_text if final_response else "",
        "latency_s": time.time() - t0,
        "usage_by_model": usage,
        "intent": intent,
        "vision": vision_facts,
        "policy_model_used": policy_model,
    }


if __name__ == "__main__":
    with open("../sample-data/carmen-trace.json") as f:
        carmen = json.load(f)
    out = run(carmen["user_message"], image_url=carmen.get("image_url"))
    print(json.dumps(out, indent=2, default=str))
