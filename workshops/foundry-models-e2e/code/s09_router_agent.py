# =============================================================================
# s09_router_agent.py — model-router agent (comparison run, post-Step 7)
# =============================================================================
# NARRATIVE ROLE
# Counter-hypothesis to v3: instead of decomposing the workload by hand
# (planner / router-nano / mini / policy-FT), point every call at the managed
# Foundry `model-router` deployment and let it pick the underlying model.
#
# Same tool set, same JSON contract, same eval harness as v1 — so the
# resulting scorecard row drops cleanly next to v1, v2, v3.
#
# Per-request telemetry: each Responses API call returns the *actual* model
# the router chose (e.g. gpt-4.1-mini, gpt-4.1-nano). We accumulate usage
# under that sub-model name so the run also produces a routing distribution.
# =============================================================================
import json
import time
from collections import defaultdict

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from s02_tools_mock import TOOL_SCHEMAS, DISPATCH
from s02_config import PROJECT_ENDPOINT, DEPLOY_AUTO_ROUTER, PRICE

INSTRUCTIONS = """You are WWI. Use tools to plan and book travel.
Always check policy before booking. Return a final JSON itinerary with keys:
flight, hotel, policy_notes, total_estimated_cost_usd, booking_status."""


def _credit(usage_by_model: dict, sub_model: str, tin: int, tout: int) -> None:
    """Credit tokens to the *underlying* model picked by the router.

    Adds a pricing entry on the fly if we've never seen this sub-model before,
    falling back to the auto-router blended rate so cost_of() still works.
    """
    if sub_model not in PRICE:
        PRICE[sub_model] = PRICE[DEPLOY_AUTO_ROUTER]
    cur_in, cur_out = usage_by_model.get(sub_model, (0, 0))
    usage_by_model[sub_model] = (cur_in + tin, cur_out + tout)


def run(user_message: str, image_url: str | None = None) -> dict:
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    client = project.get_openai_client()

    input_items: list[dict] = [{"role": "user", "content": user_message}]
    t0 = time.time()
    usage_by_model: dict[str, tuple[int, int]] = {}

    final_response = None
    for _ in range(8):
        resp = client.responses.create(
            model=DEPLOY_AUTO_ROUTER,
            instructions=INSTRUCTIONS,
            input=input_items,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        sub_model = getattr(resp, "model", DEPLOY_AUTO_ROUTER) or DEPLOY_AUTO_ROUTER
        _credit(usage_by_model, sub_model,
                resp.usage.input_tokens, resp.usage.output_tokens)
        final_response = resp

        input_items += [item.model_dump(exclude_none=True) for item in resp.output]
        function_calls = [item for item in resp.output if item.type == "function_call"]
        if not function_calls:
            # Final turn: re-run with json_object output to get clean JSON.
            input_items.append({
                "role": "user",
                "content": "Output the final itinerary as a JSON object only.",
            })
            resp = client.responses.create(
                model=DEPLOY_AUTO_ROUTER,
                instructions=INSTRUCTIONS,
                input=input_items,
                text={"format": {"type": "json_object"}},
            )
            sub_model = getattr(resp, "model", DEPLOY_AUTO_ROUTER) or DEPLOY_AUTO_ROUTER
            _credit(usage_by_model, sub_model,
                    resp.usage.input_tokens, resp.usage.output_tokens)
            final_response = resp
            break
        for fc in function_calls:
            args = json.loads(fc.arguments)
            out = DISPATCH[fc.name](**args)
            input_items.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": json.dumps(out),
            })

    answer = (final_response.output_text or "") if final_response else ""
    if not answer and final_response:
        for item in final_response.output:
            content = getattr(item, "content", None)
            if content:
                for block in (content if isinstance(content, list) else [content]):
                    text = getattr(block, "text", None)
                    if text:
                        answer += text

    return {
        "answer": answer,
        "latency_s": time.time() - t0,
        "usage_by_model": usage_by_model,
    }


if __name__ == "__main__":
    # Smoke test against the on-stage Carmen prompt.
    with open("../sample-data/carmen-trace.json") as f:
        carmen = json.load(f)
    result = run(carmen["user_message"])
    print(f"latency = {result['latency_s']:.1f}s")
    print("usage_by_model:")
    for m, (tin, tout) in result["usage_by_model"].items():
        print(f"  {m:40s}  in={tin:>6d}  out={tout:>6d}")
    print("\n--- answer ---")
    print(result["answer"][:600])
