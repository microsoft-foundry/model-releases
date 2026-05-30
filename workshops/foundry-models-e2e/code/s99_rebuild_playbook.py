#!/usr/bin/env python3
"""
s99_rebuild_playbook.py — regenerate the numeric bits of PLAYBOOK.md from
the BRK230 agent's narrative.json so the playbook always reflects YOUR
last workshop run.

This script is intentionally **non-destructive**: it prints the freshly
computed Markdown to stdout (or to --out). You then splice the three
meta-table rows and the Hills-Are-Alive block into
workshops/foundry-models-e2e/PLAYBOOK.md by hand. Two reasons:

  1. PLAYBOOK.md is mostly hand-authored narrative — the lessons are
     yours to write, only the numbers are mechanical.
  2. A copy-paste step keeps you in the loop on what changed: you see
     the throttle clear (or not), the policy regression flip (or not),
     and you write the lesson it teaches.

USAGE
    # default: read .github/agents/brk230-demo/generated/narrative.json
    python3 s99_rebuild_playbook.py

    # or point at any narrative.json
    python3 s99_rebuild_playbook.py \\
        --narrative .github/agents/brk230-demo/generated/narrative.json

The shell wrapper s99_rebuild_playbook.sh is the friendlier entry point.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[3]
DEFAULT_NARRATIVE = (
    REPO_ROOT_DEFAULT
    / ".github" / "agents" / "brk230-demo" / "generated" / "narrative.json"
)


def _flag(status: str) -> str:
    return {"green": "✅", "amber": "⚠️", "red": "🚨", "na": "  "}.get(status, "  ")


def _fmt_q(v: float | None) -> str:
    return f"{v:.2f}" if v is not None else "  na"


def _fmt_cost(v: float | None) -> str:
    return f"${v:.3f}" if v is not None else "    na"


def _fmt_lat(v: float | None) -> str:
    return f"{v:.1f}s" if v is not None else "  na"


def _fmt_pol(v: float | None) -> str:
    return f"{v:.2f}" if v is not None else "  na"


def render_meta_rows(runs: dict) -> str:
    """Three meta-table rows: v1-demo, v2-demo, v3-demo, all numbers from narrative.json."""
    out = []

    v1 = runs["v1-demo"]
    v1_lat_flag = _flag(v1["target_status"]["latency"])
    out.append(
        f"| **✅ v1-demo**       | (your run)      | 50-row baseline run | "
        f"Q **{v1['quality']:.3f}** · {_fmt_cost(v1['cost_usd'])} {_flag(v1['target_status']['cost'])} · "
        f"**{v1['latency_s']:.1f}s** {v1_lat_flag} · 📜 {_fmt_pol(v1['policy_score'])} "
        f"{_flag(v1['target_status']['policy'])} | A clean signal unlocks the next move — even if one dial is still red. |"
    )

    v2 = runs["v2-demo"]
    out.append(
        f"| **🪶 v2-demo**       | (your run)      | Multi-model split, FT off | "
        f"Q **{v2['quality']:.3f}** · {_fmt_cost(v2['cost_usd'])} {_flag(v2['target_status']['cost'])} · "
        f"**{v2['latency_s']:.1f}s** {_flag(v2['target_status']['latency'])} · 📜 {_fmt_pol(v2['policy_score'])} "
        f"{_flag(v2['target_status']['policy'])} | "
        + (
            "Cost & quality moved; the custom evaluator says policy *regressed*. "
            if v2["delta_vs_v1"] and v2["delta_vs_v1"]["policy"] and v2["delta_vs_v1"]["policy"]["abs"] < 0
            else "Cost & quality moved; check the custom-evaluator row before you celebrate. "
        )
        + "|"
    )

    v3 = runs["v3-demo"]
    # Use the v2 → v3 delta (the boolean-flip delta) — that's the punchline
    # of Pattern 8 ("one boolean is the punchline"). The delta_vs_v1 fields
    # in the manifest are computed against v1-demo, so derive v2→v3 here.
    v2_pol = v2.get("policy_score")
    v3_pol = v3.get("policy_score")
    if v2_pol and v3_pol:
        pol_delta_pct = (v3_pol - v2_pol) / v2_pol * 100.0
    else:
        pol_delta_pct = None
    pol_blurb = (
        f"📜 Policy {v2_pol:.2f} → {v3_pol:.2f} "
        f"({'+' if pol_delta_pct >= 0 else ''}{pol_delta_pct:.0f}% on the boolean flip)"
        if pol_delta_pct is not None
        else f"📜 {_fmt_pol(v3_pol)}"
    )
    out.append(
        f"| **🎯 v3-demo**       | (your run)      | `USE_FT_POLICY=True` (one boolean) | "
        f"**{pol_blurb}** · Q {v3['quality']:.2f} · {_fmt_cost(v3['cost_usd'])} "
        f"{_flag(v3['target_status']['cost'])} · **{v3['latency_s']:.1f}s** "
        f"{_flag(v3['target_status']['latency'])} | "
        + (
            "One flag flip lands policy + cost; "
            + (
                "latency is the next hill."
                if v3["target_status"]["latency"] != "green"
                else "everything you measured is in target."
            )
        )
        + " |"
    )

    return "\n".join(out)


def render_hills(runs: dict, targets: dict) -> str:
    """Hills-Are-Alive ASCII block, numbers pulled from narrative.json."""
    v1, v2, v3 = runs["v1-demo"], runs["v2-demo"], runs["v3-demo"]

    def lat_glyph(r):
        return _flag(r["target_status"]["latency"])

    def pol_glyph(r):
        return _flag(r["target_status"]["policy"])

    def cost_glyph(r):
        return _flag(r["target_status"]["cost"])

    next_hill = (
        "(summit)" if v3["target_status"]["latency"] == "green"
        else "(next hill)"
    )

    block = f"""```
                        🏔️  v3-demo
                      ╱  ┃  🎯 Q {v3['quality']:.2f}
                    ╱    ┃  📜 {v3['policy_score']:.2f}  {pol_glyph(v3)}
                  ╱      ┃  💸 ${v3['cost_usd']:.3f} {cost_glyph(v3)}
            🏔️ v2-demo   ┃  ⚡ {v3['latency_s']:.1f}s  {lat_glyph(v3)} {next_hill}
         ╱  ┃  🎯 Q {v2['quality']:.2f}   ┃
       ╱    ┃  📜 {v2['policy_score']:.2f} {pol_glyph(v2)} ┃   ← one boolean flip
   🏔️ v1   ┃  💸 ${v2['cost_usd']:.3f} {cost_glyph(v2)}┃     fixed policy + held cost,
   ┃ Q {v1['quality']:.2f}  ┃  ⚡ {v2['latency_s']:.1f}s {lat_glyph(v2)} ┃     and TPM-warming cleared
   ┃ 📜 {v1['policy_score']:.2f}  ┃            ┃     part of the latency hill.
   ┃ ${v1['cost_usd']:.3f}  ┃            ┃
   ┃ {v1['latency_s']:.1f}s {lat_glyph(v1)}┃            ┃
```

Targets: 🎯 Quality ≥ {targets['quality']:.2f} · 💸 Cost ≤ ${targets['cost']:.3f} · ⚡ Latency ≤ {targets['latency']:.1f}s · 📜 Policy ≥ {targets['policy']:.2f}"""
    return block


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--narrative",
        type=Path,
        default=DEFAULT_NARRATIVE,
        help=f"Path to narrative.json (default: {DEFAULT_NARRATIVE})",
    )
    p.add_argument("--out", type=Path, default=None, help="Write to file instead of stdout.")
    args = p.parse_args()

    if not args.narrative.exists():
        print(f"ERROR: narrative.json not found at {args.narrative}")
        print("Run `python3 .github/agents/brk230-demo/tools/analyze_eval_run.py "
              ".github/agents/brk230-demo/generated` first to build it.")
        return 1

    manifest = json.loads(args.narrative.read_text())
    runs = manifest["runs"]
    targets = manifest["targets"]

    if any(runs[k].get("missing") for k in ("v1-demo", "v2-demo", "v3-demo")):
        print("ERROR: one or more required runs missing from narrative.json")
        return 1

    parts = [
        "<!-- ───────────────────────────────────────────────────────────── -->",
        "<!--   Regenerated from " + str(args.narrative.relative_to(REPO_ROOT_DEFAULT)) + "  -->",
        "<!--   content_hash: " + manifest.get("content_hash", "?")[:16] + "…             -->",
        "<!-- ───────────────────────────────────────────────────────────── -->",
        "",
        "## ✏️ Splice these three rows into PLAYBOOK.md's Meta Moment table",
        "",
        "(Replace the existing **v1-demo**, **v2-demo**, **v3-demo** rows.)",
        "",
        render_meta_rows(runs),
        "",
        "---",
        "",
        "## ✏️ Replace the Hills Are Alive code block with this",
        "",
        render_hills(runs, targets),
        "",
        "---",
        "",
        "When you're done, also re-read the lesson cells in those three rows —",
        "what shifted? Did the throttle clear? Did policy still regress on v2?",
        "Did v3 land latency this time, or is it still the next hill?",
        "Write the lesson the new numbers actually teach. That's the playbook.",
        "",
    ]
    rendered = "\n".join(parts)

    if args.out:
        args.out.write_text(rendered)
        print(f"Wrote {args.out}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
