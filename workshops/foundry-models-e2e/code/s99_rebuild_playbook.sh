#!/usr/bin/env bash
# s99_rebuild_playbook.sh — regenerate the numeric bits of PLAYBOOK.md from
# whatever .github/agents/brk230-demo/generated/narrative.json currently says.
#
# The companion Python helper does the actual work; this wrapper just gives
# you a friendly entry point and prints clear next-steps.
#
# USAGE
#     # from workshops/foundry-models-e2e/code/
#     ./s99_rebuild_playbook.sh
#
#     # or write the suggested edits to a file you can diff
#     ./s99_rebuild_playbook.sh > /tmp/playbook-update.md
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
NARRATIVE="$REPO_ROOT/.github/agents/brk230-demo/generated/narrative.json"
ANALYZER="$REPO_ROOT/.github/agents/brk230-demo/tools/analyze_eval_run.py"
GENERATED_DIR="$REPO_ROOT/.github/agents/brk230-demo/generated"

if [[ ! -f "$NARRATIVE" ]]; then
  echo "❌ No narrative.json yet at $NARRATIVE" >&2
  echo "   Run the analyzer against your latest workshop run first:" >&2
  echo "     python3 $ANALYZER $GENERATED_DIR" >&2
  exit 1
fi

# Detect a stale narrative.json (any eval JSON newer than the manifest)
if find "$GENERATED_DIR" -name 'eval_results_*.json' -newer "$NARRATIVE" \
     -print -quit | grep -q .; then
  echo "ℹ️  narrative.json looks stale — re-running the analyzer first..." >&2
  python3 "$ANALYZER" "$GENERATED_DIR" >&2
  echo >&2
fi

python3 "$HERE/s99_rebuild_playbook.py" --narrative "$NARRATIVE" "$@"

cat >&2 <<'EOF'

────────────────────────────────────────────────────────────────────
Next steps:
  1. Open workshops/foundry-models-e2e/PLAYBOOK.md side-by-side with
     the output above.
  2. Replace the v1-demo / v2-demo / v3-demo rows in the Meta Moment
     table with the regenerated rows.
  3. Replace the Hills-Are-Alive code block with the regenerated one.
  4. Re-read the "Lesson cashed in" column on each updated row and
     rewrite it to match what your numbers actually teach.

The BRK230 demo agent (live mode) will pick up your fresh
generated/narrative.json automatically the next time it loads —
no agent-prompt edits needed.
────────────────────────────────────────────────────────────────────
EOF
