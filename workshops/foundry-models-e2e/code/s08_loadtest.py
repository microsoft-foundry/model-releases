#!/usr/bin/env python3
# =============================================================================
# s08_loadtest.py — Long-running adversarial load generator (Step 8 / Operate)
# =============================================================================
# NARRATIVE ROLE
# Step 8 is the Operate phase. To make the portal monitoring dashboards
# *interesting* (not flat), we need traffic with realistic shape — a base
# rate that rises and falls, occasional spikes, occasional silent windows,
# and a mix of normal / edge-case / adversarial prompts.
#
# This script drives the v3 multi-model agent over many hours with that
# shape. Every request lands as a real trace in the Foundry portal,
# powering the dashboards the instructor walks through in Step 8 — and
# motivating the closing narrative beat: "we noticed X in production →
# built custom evaluator Y → fed it into a managed adaptive Eval Rubric."
#
# TRAFFIC SHAPE
#   - Base rate: configurable, default 6 req/min (~0.1 req/s)
#   - Sinusoidal envelope over duration: peaks ≈ 2× base, troughs ≈ 0.25×
#   - Spike events: 3-5 random bursts, 2-4 min each at 5× base rate
#   - Lull windows: 2-3 random silent windows, 3-8 min each (no traffic)
#   - Prompt mix per request: 60% normal · 25% edge · 15% adversarial
#     (during a spike, adversarial weight bumps to 35% to simulate attack)
#
# OUTPUT
#   - Real Foundry traces (portal → Monitoring → Traces)
#   - Local CSV: generated/loadtest_<label>.csv  (append-as-you-go)
#     columns: ts_iso, elapsed_s, class, kind, intent, latency_s, ok,
#              ans_chars, err
#   - Periodic summary line every 60s to stdout
#
# USAGE
#   python -u s08_loadtest.py --duration 2h --label monitor-demo
#   python -u s08_loadtest.py --duration 30m --base-rpm 15 --label burst-demo
#
# SAFE TO RUN: bounded concurrency (default 6 workers) and respects the
# configured TPM caps on the underlying deployments. Ctrl-C stops cleanly.
# =============================================================================
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

# Import the v3 agent's run() entrypoint. We import lazily so --help works
# even when env vars aren't set.

ROOT = Path(__file__).parent
GENERATED = ROOT / "generated"
GENERATED.mkdir(exist_ok=True)
PROMPT_FILE = ROOT.parent / "sample-data" / "loadtest-prompts.jsonl"


# ─── prompt corpus ──────────────────────────────────────────────────────
def load_prompts() -> list[dict]:
    prompts: list[dict] = []
    with open(PROMPT_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(json.loads(line))
    return prompts


def pick_prompt(corpus: list[dict], in_spike: bool) -> dict:
    """Class-weighted random pick. Spikes lean adversarial."""
    weights = {"normal": 0.35, "edge": 0.30, "adversarial": 0.35} if in_spike \
        else {"normal": 0.60, "edge": 0.25, "adversarial": 0.15}
    cls = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    pool = [p for p in corpus if p["class"] == cls]
    return random.choice(pool) if pool else random.choice(corpus)


# ─── traffic scheduler ──────────────────────────────────────────────────
def plan_events(duration_s: float, n_spikes: int, n_lulls: int) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Pre-plan spike + lull windows over the full duration. Avoid the first
    minute (warm-up) and last minute (clean teardown)."""
    rng = random.Random()
    spikes: list[tuple[float, float]] = []
    lulls: list[tuple[float, float]] = []
    margin = 60.0
    usable = max(0.0, duration_s - 2 * margin)
    if usable <= 0:
        return spikes, lulls
    for _ in range(n_spikes):
        start = margin + rng.uniform(0, usable * 0.9)
        dur = rng.uniform(120, 240)  # 2-4 min
        spikes.append((start, start + dur))
    for _ in range(n_lulls):
        start = margin + rng.uniform(0, usable * 0.9)
        dur = rng.uniform(180, 480)  # 3-8 min
        lulls.append((start, start + dur))
    spikes.sort()
    lulls.sort()
    return spikes, lulls


def current_rate(elapsed: float, duration_s: float, base_rps: float,
                 spikes: list, lulls: list) -> float:
    """Instantaneous target req/s at this time-in-run."""
    # in a lull → silent
    for s, e in lulls:
        if s <= elapsed < e:
            return 0.0
    # sinusoidal envelope, one full cycle over duration
    phase = 2 * math.pi * elapsed / max(duration_s, 1.0)
    envelope = 1.0 + 0.5 * math.sin(phase)  # range 0.5 .. 1.5; clamp below
    envelope = max(0.25, envelope)
    rate = base_rps * envelope
    # spike?
    for s, e in spikes:
        if s <= elapsed < e:
            rate *= 5.0
            break
    return rate


def in_spike(elapsed: float, spikes: list) -> bool:
    return any(s <= elapsed < e for s, e in spikes)


# ─── worker ─────────────────────────────────────────────────────────────
class Stats:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.total = 0
        self.ok = 0
        self.err = 0
        self.by_class: dict[str, int] = {}
        self.last_window_total = 0

    def record(self, cls: str, ok: bool) -> None:
        with self.lock:
            self.total += 1
            if ok:
                self.ok += 1
            else:
                self.err += 1
            self.by_class[cls] = self.by_class.get(cls, 0) + 1

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "total": self.total,
                "ok": self.ok,
                "err": self.err,
                "by_class": dict(self.by_class),
            }


def make_worker(agent_mod, csv_writer, csv_lock, stats: Stats, start_t: float):
    def work(prompt: dict) -> None:
        t0 = time.time()
        ts_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
        elapsed = t0 - start_t
        ok = True
        err = ""
        intent = ""
        ans_chars = 0
        latency = 0.0
        try:
            result = agent_mod.run(prompt["input"])
            latency = float(result.get("latency_s", time.time() - t0))
            intent_val = result.get("intent", "")
            if isinstance(intent_val, dict):
                intent = str(intent_val.get("intent", ""))
            else:
                intent = str(intent_val)
            ans_chars = len(result.get("answer", "") or "")
        except Exception as exc:
            ok = False
            latency = time.time() - t0
            err = f"{type(exc).__name__}: {exc}"[:200]
        finally:
            with csv_lock:
                csv_writer.writerow([
                    ts_iso, f"{elapsed:.1f}", prompt["class"], prompt["kind"],
                    intent, f"{latency:.2f}", int(ok), ans_chars, err,
                ])
            stats.record(prompt["class"], ok)
    return work


# ─── main loop ──────────────────────────────────────────────────────────
def parse_duration(s: str) -> float:
    s = s.strip().lower()
    if s.endswith("h"):
        return float(s[:-1]) * 3600
    if s.endswith("m"):
        return float(s[:-1]) * 60
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


_STOP = threading.Event()


def _handle_sigint(signum, frame):  # noqa: ARG001
    print("\n⏹  shutdown requested — finishing in-flight requests...")
    _STOP.set()


def run_loadtest(args) -> None:
    signal.signal(signal.SIGINT, _handle_sigint)

    corpus = load_prompts()
    print(f"loaded {len(corpus)} prompts from {PROMPT_FILE.name}")
    print(f"  classes: {sorted({p['class'] for p in corpus})}")

    # late import so --help works without env
    import importlib
    agent_mod = importlib.import_module(args.agent)

    duration_s = parse_duration(args.duration)
    base_rps = args.base_rpm / 60.0
    spikes, lulls = plan_events(duration_s, args.spikes, args.lulls)

    print(f"\nLOAD PLAN")
    print(f"  agent      : {args.agent}")
    print(f"  duration   : {duration_s:.0f}s  (≈ {duration_s/3600:.2f}h)")
    print(f"  base rate  : {args.base_rpm} req/min  (envelope 0.25× .. 1.5×)")
    print(f"  spikes     : {len(spikes)}  (5× rate, 2-4 min each)")
    for s, e in spikes:
        print(f"     {s/60:6.1f}–{e/60:6.1f} min")
    print(f"  lulls      : {len(lulls)}  (silent, 3-8 min each)")
    for s, e in lulls:
        print(f"     {s/60:6.1f}–{e/60:6.1f} min")
    print(f"  workers    : {args.workers}")
    print(f"  output csv : generated/loadtest_{args.label}.csv")
    print()

    csv_path = GENERATED / f"loadtest_{args.label}.csv"
    new_file = not csv_path.exists()
    csv_f = open(csv_path, "a", newline="", buffering=1)  # line-buffered
    csv_writer = csv.writer(csv_f)
    if new_file:
        csv_writer.writerow([
            "ts_iso", "elapsed_s", "class", "kind", "intent",
            "latency_s", "ok", "ans_chars", "err",
        ])
    csv_lock = threading.Lock()
    stats = Stats()

    start_t = time.time()
    pool = ThreadPoolExecutor(max_workers=args.workers)
    work_fn = make_worker(agent_mod, csv_writer, csv_lock, stats, start_t)

    last_print = start_t
    last_total = 0
    next_event_t = start_t  # first request immediately
    try:
        while not _STOP.is_set():
            now = time.time()
            elapsed = now - start_t
            if elapsed >= duration_s:
                break

            # dispatch any scheduled events that are due
            if now >= next_event_t:
                rate = current_rate(elapsed, duration_s, base_rps, spikes, lulls)
                if rate > 0:
                    prompt = pick_prompt(corpus, in_spike(elapsed, spikes))
                    pool.submit(work_fn, prompt)
                    # next event ~ exponential(1/rate)
                    delta = random.expovariate(rate)
                else:
                    delta = 5.0  # poll again in 5s during a lull
                next_event_t = now + delta

            # periodic summary every 60s
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


# ─── CLI ────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Long-running adversarial load tester for the v3 multi-model agent.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--duration", default="2h",
                   help="total run time, e.g. 30m, 2h, 90s")
    p.add_argument("--base-rpm", type=float, default=6.0,
                   help="base request rate in requests/minute")
    p.add_argument("--spikes", type=int, default=4,
                   help="number of random spike windows (5× rate, 2-4 min)")
    p.add_argument("--lulls", type=int, default=2,
                   help="number of random silent windows (3-8 min)")
    p.add_argument("--workers", type=int, default=6,
                   help="max concurrent in-flight requests")
    p.add_argument("--agent", default="s05_multi_model_agent",
                   help="agent module to load-test (must expose run(text))")
    p.add_argument("--label", default="monitor-demo",
                   help="output csv suffix: generated/loadtest_<label>.csv")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_loadtest(args)
