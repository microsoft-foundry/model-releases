#!/usr/bin/env python3
# =============================================================================
# s08_loadtest_agent.py — Loadtest a Foundry Prompt Agent with OTel traces
# =============================================================================
# NARRATIVE ROLE (Step 8 / Operate)
# Variant of s08_loadtest.py that targets the *hosted* Foundry Prompt Agent
# created by s08_agent_setup.py instead of the in-process multi-model code.
# Each request goes through the OpenAI Responses API with an
# `agent_reference={name, version}` extra-body — which lands the call as a
# real run on the agent visible in the portal Agents tab and emits an
# OpenTelemetry span (auto-instrumented by AIProjectInstrumentor) into
# Application Insights / portal Tracing tab.
#
# WHY THIS MATTERS FOR STEP 8
#   - The new Foundry portal surfaces traces under Agents/Tracing. Raw
#     chat-completion SDK calls land in App Insights but NOT in the
#     friendly per-agent dashboards.
#   - Each invocation here is annotated with custom OTel attributes that
#     let you pivot dashboards (and a future custom evaluator!) on signal
#     that matters for policy adherence — class, kind, expected intent,
#     adversarial flag, workload label.
#
# CUSTOM OTEL ATTRIBUTES (per request span "wwi.concierge.invoke")
#   wwi.prompt.id              corpus id (e.g. "pol-008")
#   wwi.prompt.class           normal | edge | adversarial
#   wwi.prompt.kind            policy_question | jailbreak | pii_fishing | ...
#   wwi.expected.is_policy     bool — answer should cite policy
#   wwi.expected.is_adversarial bool — agent should refuse
#   wwi.workload               label of this load-test run
#   wwi.run.status             completed | failed | incomplete | ...
#   wwi.run.latency_s          end-to-end seconds
#   wwi.run.answer_chars       length of final assistant message
#   wwi.run.ok                 bool — terminal success
#   wwi.agent.name             the Foundry agent name being driven
#
# OUTPUT
#   - Real Foundry traces + agent runs (portal)
#   - Local CSV: generated/loadtest_agent_<label>.csv
#
# USAGE
#   python s08_agent_setup.py                                # one-time bootstrap
#   python -u s08_loadtest_agent.py --duration 2h --label monitor-demo
# =============================================================================
from __future__ import annotations

import argparse
import csv
import os
import random
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Reuse scheduler primitives from the SDK-flavored loadtester so traffic
# shape (sin envelope + spikes + lulls + class mix) is identical.
from s08_loadtest import (
    GENERATED,
    PROMPT_FILE,
    Stats,
    current_rate,
    in_spike,
    load_prompts,
    parse_duration,
    pick_prompt,
    plan_events,
)

ROOT = Path(__file__).parent
AGENT_NAME_FILE = GENERATED / "agent_concierge_loadtest.name"

# Categorize kinds so the policy-eval signal travels on every span.
POLICY_KINDS = {"policy_question", "policy_question_long", "policy_violation_request"}
ADVERSARIAL_KINDS = {"prompt_injection", "jailbreak", "pii_fishing",
                     "off_topic", "policy_violation_request"}


# ─── OTel setup ─────────────────────────────────────────────────────────
def configure_telemetry(project, workload_label: str):
    """Wire OTel SDK + Azure Monitor exporter + AI Project auto-instrumentation.

    The AIProjectInstrumentor adds spans around `responses.create` and
    `agents.*` calls; we add a *parent* span per request with WWI custom
    attributes so dashboards can pivot on policy-eval signal.
    """
    from azure.monitor.opentelemetry import configure_azure_monitor
    from azure.ai.projects.telemetry import AIProjectInstrumentor
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource

    # Required feature gate for genai instrumentation (this SDK is preview).
    os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"
    # Capture user/assistant message content on spans for the portal Tracing tab.
    os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")
    os.environ.setdefault("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")

    # Try to fetch the project's App Insights connection. If the project
    # has no AI Foundry → App Insights link yet, fall back to local-only
    # spans: server-side agent run traces still flow to the portal Tracing
    # tab via the hosted agent runtime, but our client-side custom spans
    # become local-only (CSV is the durable record either way).
    conn_str = None
    try:
        conn_str = project.telemetry.get_application_insights_connection_string()
        print(f"app insights connection: {conn_str.split(';')[0]}…")
    except Exception as e:
        print(f"⚠ no App Insights linked to this Foundry project ({type(e).__name__}).")
        print("  client-side custom spans will NOT be exported. Server-side")
        print("  agent run traces will still appear in the portal Agents/Tracing tab.")
        print("  To enable App Insights export, attach an Application Insights")
        print("  resource to the Foundry account and re-run.")

    if conn_str:
        configure_azure_monitor(
            connection_string=conn_str,
            resource=Resource.create({
                "service.name": "wwi-concierge-loadtest",
                "service.namespace": "wwi.travel",
                "wwi.workload": workload_label,
            }),
        )
    AIProjectInstrumentor().instrument(enable_content_recording=True)

    # Patch a NonRecordingSpan bug in azure-ai-projects 2.1.0 responses
    # instrumentor: `_append_to_message_attribute` calls
    # `span.span_instance.attributes` without a hasattr guard, which raises
    # AttributeError when the active span is non-recording (intermittent
    # under concurrent load). Wrap it to noop when the span lacks
    # `attributes`.
    from azure.ai.projects.telemetry import _responses_instrumentor as _ri
    _orig_append = _ri._ResponsesInstrumentorPreview._append_to_message_attribute

    def _safe_append(self, span, attribute_name, new_messages):
        try:
            if not hasattr(getattr(span, "span_instance", None), "attributes"):
                return  # NonRecordingSpan — nothing to attach to
            return _orig_append(self, span, attribute_name, new_messages)
        except AttributeError:
            return

    _ri._ResponsesInstrumentorPreview._append_to_message_attribute = _safe_append

    print("AIProjectInstrumentor wired up"
          + (" + Azure Monitor exporter" if conn_str else " (exporter: none)")
          + " (NonRecordingSpan patch applied)")
    return trace.get_tracer("wwi.concierge.loadtest")


# ─── worker ─────────────────────────────────────────────────────────────
def _response_text(resp) -> str:
    """Extract concatenated assistant text from a Responses API result."""
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text
    parts: list[str] = []
    for item in getattr(resp, "output", []) or []:
        for c in getattr(item, "content", []) or []:
            txt = getattr(c, "text", None)
            if isinstance(txt, str):
                parts.append(txt)
            elif txt is not None and hasattr(txt, "value"):
                parts.append(txt.value)
    return "".join(parts)


def make_agent_worker(openai_client, agent_name: str, agent_version: str,
                      tracer, csv_writer, csv_lock, stats: Stats,
                      start_t: float, workload_label: str):
    """Return a callable that invokes the hosted Prompt Agent for one prompt
    and emits a manual span with WWI-flavored custom attributes."""

    def work(prompt: dict) -> None:
        t0 = time.time()
        ts_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
        elapsed = t0 - start_t
        ok = True
        err = ""
        ans_chars = 0
        run_status = ""
        latency = 0.0

        kind = prompt.get("kind", "")
        cls = prompt.get("class", "")
        is_policy = kind in POLICY_KINDS
        is_adversarial = (cls == "adversarial") or (kind in ADVERSARIAL_KINDS)

        with tracer.start_as_current_span("wwi.concierge.invoke") as span:
            # Stamp the span up front so failures still carry the signal.
            span.set_attribute("wwi.prompt.id", prompt.get("id", ""))
            span.set_attribute("wwi.prompt.class", cls)
            span.set_attribute("wwi.prompt.kind", kind)
            span.set_attribute("wwi.expected.is_policy", is_policy)
            span.set_attribute("wwi.expected.is_adversarial", is_adversarial)
            span.set_attribute("wwi.workload", workload_label)
            span.set_attribute("wwi.agent.name", agent_name)
            try:
                resp = openai_client.responses.create(
                    input=prompt["input"],
                    extra_body={
                        "agent_reference": {
                            "type": "agent_reference",
                            "name": agent_name,
                            "version": agent_version,
                        },
                    },
                )
                latency = time.time() - t0
                run_status = str(getattr(resp, "status", "") or "completed")
                answer = _response_text(resp)
                ans_chars = len(answer or "")
                ok = run_status in ("completed", "succeeded", "")
                if not ok and not err:
                    err = f"run_status={run_status}"
            except Exception as exc:
                latency = time.time() - t0
                err = f"{type(exc).__name__}: {exc}"[:200]
                # Content-filter rejection on an adversarial prompt is the
                # expected/positive signal — record as ok with a distinct
                # run_status so the dashboard pivots cleanly.
                exc_name = type(exc).__name__
                if exc_name == "BadRequestError" and "content" in str(exc).lower() and "filter" in str(exc).lower():
                    run_status = "content_filtered"
                    ok = True
                    span.set_attribute("wwi.run.content_filtered", True)
                else:
                    ok = False
                    span.record_exception(exc)
            finally:
                span.set_attribute("wwi.run.status",
                                   run_status or ("error" if not ok else ""))
                span.set_attribute("wwi.run.latency_s", round(latency, 3))
                span.set_attribute("wwi.run.answer_chars", ans_chars)
                span.set_attribute("wwi.run.ok", ok)

        with csv_lock:
            csv_writer.writerow([
                ts_iso, f"{elapsed:.1f}", cls, kind, run_status,
                f"{latency:.2f}", int(ok), ans_chars, err,
            ])
        stats.record(cls, ok)

    return work


# ─── main loop ──────────────────────────────────────────────────────────
_STOP = threading.Event()


def _handle_sigint(signum, frame):  # noqa: ARG001
    print("\n⏹  shutdown requested — finishing in-flight requests...")
    _STOP.set()


def resolve_agent_name(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    if "FOUNDRY_LOADTEST_AGENT_NAME" in os.environ:
        return os.environ["FOUNDRY_LOADTEST_AGENT_NAME"]
    if AGENT_NAME_FILE.exists():
        return AGENT_NAME_FILE.read_text().strip()
    raise SystemExit(
        "no agent name — run `python s08_agent_setup.py` first, pass "
        "--agent-name, or set FOUNDRY_LOADTEST_AGENT_NAME")


def run_loadtest(args) -> None:
    signal.signal(signal.SIGINT, _handle_sigint)

    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    load_dotenv(ROOT.parent / ".env")
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = resolve_agent_name(args.agent_name)

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    tracer = configure_telemetry(project, args.label)
    # NOTE: get the OpenAI client AFTER instrument() so trace-context
    # propagation hooks are registered on the underlying http client.
    openai_client = project.get_openai_client()

    # Warm up: prime the OTel + instrumentor pipeline with a single
    # serialized call. Without this, the first ~5 concurrent worker
    # requests race against TracerProvider setup and hit
    # `'NonRecordingSpan' object has no attribute 'attributes'`.
    print("warming up instrumentation pipeline (1 priming call)...")
    try:
        with tracer.start_as_current_span("wwi.concierge.warmup") as span:
            span.set_attribute("wwi.workload", args.label)
            openai_client.responses.create(
                input="ping",
                extra_body={"agent_reference": {
                    "type": "agent_reference",
                    "name": agent_name,
                    "version": args.agent_version,
                }},
            )
        print("warmup ok")
    except Exception as exc:
        print(f"warmup failed (continuing anyway): {type(exc).__name__}: {exc}")

    corpus = load_prompts()
    print(f"\nloaded {len(corpus)} prompts from {PROMPT_FILE.name}")
    print(f"  classes: {sorted({p['class'] for p in corpus})}")

    duration_s = parse_duration(args.duration)
    base_rps = args.base_rpm / 60.0
    spikes, lulls = plan_events(duration_s, args.spikes, args.lulls)

    print(f"\nLOAD PLAN")
    print(f"  agent      : {agent_name}  (version={args.agent_version})")
    print(f"  endpoint   : {endpoint}")
    print(f"  duration   : {duration_s:.0f}s  (≈ {duration_s/3600:.2f}h)")
    print(f"  base rate  : {args.base_rpm} req/min  (envelope 0.25× .. 1.5×)")
    print(f"  spikes     : {len(spikes)}  (5× rate, 2-4 min each)")
    for s, e in spikes:
        print(f"     {s/60:6.1f}–{e/60:6.1f} min")
    print(f"  lulls      : {len(lulls)}  (silent, 3-8 min each)")
    for s, e in lulls:
        print(f"     {s/60:6.1f}–{e/60:6.1f} min")
    print(f"  workers    : {args.workers}")
    print(f"  output csv : generated/loadtest_agent_{args.label}.csv")
    print()

    csv_path = GENERATED / f"loadtest_agent_{args.label}.csv"
    new_file = not csv_path.exists()
    csv_f = open(csv_path, "a", newline="", buffering=1)
    csv_writer = csv.writer(csv_f)
    if new_file:
        csv_writer.writerow([
            "ts_iso", "elapsed_s", "class", "kind", "run_status",
            "latency_s", "ok", "ans_chars", "err",
        ])
    csv_lock = threading.Lock()
    stats = Stats()

    start_t = time.time()
    pool = ThreadPoolExecutor(max_workers=args.workers)
    work_fn = make_agent_worker(openai_client, agent_name, args.agent_version,
                                tracer, csv_writer, csv_lock, stats,
                                start_t, args.label)

    last_print = start_t
    last_total = 0
    next_event_t = start_t
    try:
        while not _STOP.is_set():
            now = time.time()
            elapsed = now - start_t
            if elapsed >= duration_s:
                break
            if now >= next_event_t:
                rate = current_rate(elapsed, duration_s, base_rps, spikes, lulls)
                if rate > 0:
                    prompt = pick_prompt(corpus, in_spike(elapsed, spikes))
                    pool.submit(work_fn, prompt)
                    delta = random.expovariate(rate)
                else:
                    delta = 5.0
                next_event_t = now + delta

            if now - last_print >= 60:
                snap = stats.snapshot()
                window = snap["total"] - last_total
                last_total = snap["total"]
                rate_now = current_rate(elapsed, duration_s, base_rps, spikes, lulls)
                spike_tag = " 🔥SPIKE" if in_spike(elapsed, spikes) else ""
                lull_tag = " 🌙LULL" if rate_now == 0 else ""
                cls_str = " ".join(f"{k}={v}" for k, v in sorted(snap["by_class"].items()))
                print(f"[t+{elapsed/60:6.1f}m]  total={snap['total']:5d}  "
                      f"+{window:3d}/min  ok={snap['ok']}  err={snap['err']}  "
                      f"rate={rate_now*60:5.1f}/min{spike_tag}{lull_tag}  "
                      f"({cls_str})")
                last_print = now

            time.sleep(min(0.5, max(0.0, next_event_t - time.time())))
    finally:
        print("\nshutting down worker pool (waiting up to 60s for in-flight)...")
        pool.shutdown(wait=True, cancel_futures=False)
        csv_f.close()
        snap = stats.snapshot()
        print(f"\nFINAL  total={snap['total']}  ok={snap['ok']}  err={snap['err']}")
        print(f"       by class: {snap['by_class']}")
        print(f"       csv: {csv_path}")
        print(f"       portal: Agents → {agent_name} → Threads/Tracing tab")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Loadtest a hosted Foundry Prompt Agent with OTel-traced custom attributes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--duration", default="2h")
    p.add_argument("--base-rpm", type=float, default=6.0)
    p.add_argument("--spikes", type=int, default=4)
    p.add_argument("--lulls", type=int, default=2)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--agent-name", default=None,
                   help="defaults to generated/agent_concierge_loadtest.name "
                        "or FOUNDRY_LOADTEST_AGENT_NAME env")
    p.add_argument("--agent-version", default="1",
                   help="agent version selector (explicit integer, e.g. '1')")
    p.add_argument("--label", default="monitor-demo")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_loadtest(args)
