# =============================================================================
# s02_baseline_agent.py — v1 agent: single-model baseline (Step 2)
# =============================================================================
# NARRATIVE ROLE
# This is the simplest possible agent: one frontier model (gpt-4.1) handles
# every task — routing, vision, policy lookup, planning, and booking — in a
# single tool-calling loop.  It sets the quality/cost/latency baseline that
# all later steps measure themselves against.
#
# WHAT TO OBSERVE
# • High latency: every turn calls the expensive frontier model.
# • High cost: frontier pricing applies to all tokens, including cheap tasks.
# • Decent quality: gpt-4.1 is capable, but the single-model approach gives
#   no room to specialise or fine-tune individual tasks.
#
# Step 3 will decompose these tasks; Step 5 will show the v2 improvement.
# =============================================================================
import json
import re
import time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from s02_tools_mock import TOOL_SCHEMAS, DISPATCH
from s02_config import PROJECT_ENDPOINT, DEPLOY_PLANNER

INSTRUCTIONS = """You are WWI. Use tools to plan and book travel.
Always check policy before booking. Return a final JSON itinerary with keys:
flight, hotel, policy_notes, total_estimated_cost_usd, booking_status."""


def run(user_message: str, image_url: str | None = None) -> dict:
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    client = project.get_openai_client()

    input_items: list[dict] = [{"role": "user", "content": user_message}]
    t0 = time.time()
    total_in = total_out = 0  # track tokens for cost calculation

    final_response = None
    for _ in range(8):  # max 8 turns; typical task resolves in 3-4
        resp = client.responses.create(
            model=DEPLOY_PLANNER,
            instructions=INSTRUCTIONS,
            input=input_items,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        total_in  += resp.usage.input_tokens
        total_out += resp.usage.output_tokens
        final_response = resp

        # Carry every output item back into the next turn.
        input_items += [item.model_dump(exclude_none=True) for item in resp.output]

        function_calls = [item for item in resp.output if item.type == "function_call"]
        if not function_calls:
            # No more tool calls — re-run once with json_object mode to get
            # a clean structured JSON final answer.  The extra user message
            # containing "json" satisfies the Responses API requirement that
            # the word "json" appear in the input when using json_object format.
            input_items.append({
                "role": "user",
                "content": "Output the final itinerary as a JSON object only.",
            })
            resp = client.responses.create(
                model=DEPLOY_PLANNER,
                instructions=INSTRUCTIONS,
                input=input_items,
                text={"format": {"type": "json_object"}},
            )
            total_in  += resp.usage.input_tokens
            total_out += resp.usage.output_tokens
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

    # output_text is empty when the last response had no text item (e.g.
    # the model only emitted function_call items on the final turn).
    # Fall back to scanning output items for text content.
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
        "usage_by_model": {DEPLOY_PLANNER: (total_in, total_out)},
    }


if __name__ == "__main__":
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    from s02_scorecard import cost_of

    console = Console()

    with open("../sample-data/carmen-trace.json") as f:
        carmen = json.load(f)

    with console.status("[bold cyan]Running v1 agent (planner-gpt41)…[/]"):
        result = run(carmen["user_message"])

    # Strip markdown code fences if the model wrapped its JSON.
    answer_raw = result["answer"].strip()
    if answer_raw.startswith("```"):
        answer_raw = "\n".join(
            line for line in answer_raw.splitlines()
            if not line.strip().startswith("```")
        ).strip()
    # If prose was returned, extract the first {...} JSON block.
    if answer_raw and not answer_raw.lstrip().startswith("{"):
        m = re.search(r"\{.*\}", answer_raw, re.DOTALL)
        answer_raw = m.group() if m else ""
    if not answer_raw:
        console.print("[bold red]Agent returned no parseable JSON.[/] Raw answer:", repr(result["answer"]))
        raise SystemExit(1)
    itinerary = json.loads(answer_raw)
    tin, tout = result["usage_by_model"][DEPLOY_PLANNER]
    cost = cost_of(result["usage_by_model"])

    # ── Itinerary panel ──────────────────────────────────────────────────
    # Handle both nested {"selected": {...}} and flat {"carrier": ...} structures
    raw_flight = itinerary.get("flight", {})
    raw_hotel  = itinerary.get("hotel",  {})
    flight  = raw_flight.get("selected", raw_flight) if isinstance(raw_flight, dict) else {}
    hotel   = raw_hotel.get("selected",  raw_hotel)  if isinstance(raw_hotel,  dict) else {}
    booking_raw = itinerary.get("booking_status", {})
    # booking_status may be a dict {"booking_id":..., "status":...} or a plain string
    if isinstance(booking_raw, dict):
        booking_id  = booking_raw.get("booking_id", "?")
        booking_status = booking_raw.get("status", "?")
    else:
        booking_id  = "—"
        booking_status = str(booking_raw)

    itinerary_lines = (
        f"[bold]Flight[/]   {flight.get('carrier','')} {flight.get('number','')}  "
        f"{flight.get('depart','')} → {flight.get('arrive_local','')}  "
        f"${flight.get('price_usd','?')}\n"
        f"[bold]Hotel[/]    {hotel.get('name','')}  "
        f"${hotel.get('nightly_usd','?')}/night × {hotel.get('checkout','?')} → {hotel.get('checkin','?')}  "
        f"(${hotel.get('total_usd','?')})\n"
        f"[bold]Total[/]    ${itinerary.get('total_estimated_cost_usd', '?')} USD\n"
        f"[bold]Booking[/]  {booking_id}  [{booking_status}]"
    )
    console.print(Panel(itinerary_lines, title="[bold green]Carmen's Itinerary — v1[/]", expand=False))

    # ── Policy notes ─────────────────────────────────────────────────────
    policy_notes = itinerary.get("policy_notes", [])
    if isinstance(policy_notes, str):
        policy_notes = [policy_notes] if policy_notes else []
    for note in policy_notes:
        console.print(f"  [dim]·[/] {note}")

    # ── Scorecard table ───────────────────────────────────────────────────
    table = Table(title="\nv1 Scorecard", show_header=True, header_style="bold magenta")
    table.add_column("Metric",  style="bold")
    table.add_column("Value",   justify="right")
    table.add_column("Target",  justify="right", style="dim")
    table.add_column("Pass?",   justify="center")

    table.add_row("Latency",    f"{result['latency_s']:.1f}s",  "≤ 8.0s",  "❌")
    table.add_row("Tokens in",  f"{tin:,}",                     "—",       "")
    table.add_row("Tokens out", f"{tout:,}",                    "—",       "")
    table.add_row("Cost/task",  f"${cost:.4f}",                 "≤ $0.030","❌")
    table.add_row("Quality",    "? (no eval yet)",              "≥ 0.92",  "❓")

    console.print(table)
