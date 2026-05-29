# =============================================================================
# render_scorecards.py — Wrap-up scorecard renderer
# =============================================================================
# Reads previously-saved eval result JSONs (written by s05_run_eval.py into
# generated/eval_results_<label>.json) and renders them as a stack of
# scorecards.  The first label is treated as the baseline; every subsequent
# scorecard shows a colored Δ column (green = trending the desired
# direction, red = regression).
#
# Usage:
#   python render_scorecards.py v1-demo v2-demo
#   python render_scorecards.py v1-demo v2-demo v3-demo
# =============================================================================
from __future__ import annotations

import argparse
import sys

from s02_scorecard import load_baseline, print_scorecard


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels", nargs="+", help="eval labels in order; first = baseline")
    args = ap.parse_args()

    runs = []
    for lbl in args.labels:
        m = load_baseline(lbl)
        if m is None:
            sys.exit(f"missing generated/eval_results_{lbl}.json")
        runs.append((lbl, m))

    base_lbl, base = runs[0]
    print_scorecard(base_lbl, base["quality"], base["cost"], base["latency"])
    for lbl, m in runs[1:]:
        print_scorecard(lbl, m["quality"], m["cost"], m["latency"], baseline=base)


if __name__ == "__main__":
    main()
