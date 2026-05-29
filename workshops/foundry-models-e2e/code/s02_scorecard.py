# =============================================================================
# s02_scorecard.py — Scorecard renderer (Steps 2, 5, 6, 7)
# =============================================================================
# NARRATIVE ROLE
# Every step of this workshop measures the same three dimensions: quality,
# cost, and latency.  This module renders those numbers as a visual bar chart
# (via Rich) so learners can see exactly which needle moved — and which
# didn't — after each architectural change.
#
# The three target thresholds (QUALITY_TARGET, COST_TARGET, LATENCY_TARGET)
# define "good enough for production".  A green ✅ only lights up when that
# bar is met.  The goal of Steps 3-7 is to turn all three green.
# =============================================================================
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box as rich_box

from s02_config import PRICE

QUALITY_TARGET = 0.92
COST_TARGET    = 0.03
LATENCY_TARGET = 8.0

_console = Console()


def _bar(value: float, max_value: float, width: int = 10) -> str:
    frac = max(0.0, min(1.0, value / max_value))
    filled = int(round(frac * width))
    return "█" * filled + "░" * (width - filled)


def cost_of(usage_by_model: dict[str, tuple[int, int]]) -> float:
    total = 0.0
    for model, (tin, tout) in usage_by_model.items():
        p = PRICE.get(model)
        if p is None:
            continue
        total += tin / 1000 * p["in"] + tout / 1000 * p["out"]
    return total


GENERATED_DIR = Path(__file__).parent / "generated"


def load_baseline(label: str) -> dict | None:
    """Re-derive {quality, cost, latency} from a saved eval JSON so a later
    run can render its Δ column against an earlier label. Returns None if
    the file isn't present (e.g. first-ever run).
    """
    path = GENERATED_DIR / f"eval_results_{label}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    rows = data.get("rows", [])
    if not rows:
        return None
    schema = [r.get("outputs.schema.schema_score", 0.0) for r in rows]
    judge  = [r.get("outputs.judge.judge_score",  0.0) for r in rows]
    quality = 0.5 * mean(schema) + 0.5 * mean(judge)

    acc: dict[str, tuple[int, int]] = {m: (0, 0) for m in PRICE}
    for r in rows:
        usage = r.get("outputs.usage_json") or {}
        if isinstance(usage, str):
            try:
                usage = json.loads(usage)
            except Exception:
                usage = {}
        for model, pair in usage.items():
            if model not in acc:
                continue
            tin_add, tout_add = pair if isinstance(pair, (list, tuple)) else (0, 0)
            tin, tout = acc[model]
            acc[model] = (tin + tin_add, tout + tout_add)
    cost = cost_of(acc) / len(rows)

    lats = sorted(r.get("outputs.latency_s", 0.0) for r in rows)
    latency = lats[len(lats) // 2]
    return {"quality": quality, "cost": cost, "latency": latency}


def _delta_cell(curr: float, base: float | None, *,
                lower_is_better: bool, kind: str) -> str:
    """Colored delta vs baseline. Green = trending the desired direction.
    `kind` is one of: "quality" (raw +0.01), "cost" (-$0.005), "latency" (-2.3s).
    """
    if base is None or base == 0:
        return "[dim]      [/dim]"
    diff = curr - base
    if abs(diff) < 1e-9:
        return "[dim]  ─   [/dim]"
    good = (diff < 0) if lower_is_better else (diff > 0)
    color = "green" if good else "red"
    arrow = "▼" if diff < 0 else "▲"
    sign  = "-" if diff < 0 else "+"
    mag   = abs(diff)
    if kind == "cost":
        body = f"{sign}${mag:.3f}"
    elif kind == "latency":
        body = f"{sign}{mag:.1f}s"
    else:  # quality
        body = f"{sign}{mag:.2f}"
    pct = "" if kind == "quality" else f" ({sign}{mag / base * 100:.0f}%)"
    return f"[{color}]{arrow} {body}{pct}[/{color}]"


def print_scorecard(version: str, quality: float, cost: float, latency: float,
                    baseline: dict | None = None):
    """Render one scorecard.

    Bars always use the same fixed scales (relative to the goal/ceiling) so
    visual reading is consistent across runs:
      - Quality fills toward 1.0  (more filled = better)
      - Cost fills toward $0.15   (less filled = better)
      - Latency fills toward 15s  (less filled = better)

    If `baseline` is provided (a dict with quality/cost/latency from an
    earlier run, typically v1), a colored Δ column is added that shows the
    signed delta + percentage, green when trending the desired direction
    (cost/latency down, quality up) and red on regression.
    """
    q_ok = quality >= QUALITY_TARGET
    c_ok = cost    <= COST_TARGET
    l_ok = latency <= LATENCY_TARGET

    tbl = Table(box=rich_box.SIMPLE, show_header=False, padding=(0, 1))
    tbl.add_column("Metric",  style="bold")
    tbl.add_column("Bar",     no_wrap=True)
    tbl.add_column("Value",   justify="right")
    if baseline:
        tbl.add_column("Δ vs v1", justify="left")
    tbl.add_column("Status")

    def _row(label, bar_val, bar_max, value_str, ok, delta):
        cells = [label, _bar(bar_val, bar_max), value_str]
        if baseline:
            cells.append(delta)
        cells.append("[green]✅[/green]" if ok else "[dim]  [/dim]")
        tbl.add_row(*cells)

    _row("Quality", quality, 1.0,  f"{quality:.2f}", q_ok,
         _delta_cell(quality, baseline["quality"] if baseline else None,
                     lower_is_better=False, kind="quality"))
    _row("Cost",    cost,    0.15, f"${cost:.3f}", c_ok,
         _delta_cell(cost, baseline["cost"] if baseline else None,
                     lower_is_better=True, kind="cost"))
    _row("Latency", latency, 15.0, f"{latency:.1f}s", l_ok,
         _delta_cell(latency, baseline["latency"] if baseline else None,
                     lower_is_better=True, kind="latency"))

    title = f"[bold cyan]{version}[/bold cyan]"
    if baseline is None:
        title += "  [dim](baseline)[/dim]"
    _console.print(Panel(tbl, title=title, border_style="cyan", expand=False))
