#!/usr/bin/env bash
# Creates a new research folder from template/ and installs the skills.
# Usage: ./new_project.sh ~/FamilyHistory "Surname" [--extras]
# --extras also installs the two external tools (needs internet):
#   genealogy-research (skill, github.com/sliday/genealogy-research)
#   browser-harness   (Chrome control for Claude, github.com/browser-use/browser-harness)
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:?target folder missing, e.g. ~/FamilyHistory}"
NAME="${2:-Our}"
EXTRAS="${3:-}"
[ -e "$TARGET" ] && { echo "Already exists: $TARGET (nothing overwritten)"; exit 1; }
cp -R "$KIT/template" "$TARGET"
mkdir -p "$TARGET/sources/private"
rm -f "$TARGET/reports/tree.html" "$TARGET/reports/tree_data.json"
python3 - "$TARGET/project.json" "$NAME" <<'PY'
import json, sys
p, n = sys.argv[1], sys.argv[2]
c = json.load(open(p)); c['surname'] = n
json.dump(c, open(p, 'w'), ensure_ascii=False, indent=2)
PY
SK="$HOME/.claude/skills"
mkdir -p "$SK"
for s in "$KIT"/skills/*/; do
  n=$(basename "$s")
  if [ -e "$SK/$n" ]; then echo "Skill $n already exists, not overwritten"; else cp -R "$s" "$SK/$n"; echo "Skill $n installed"; fi
done
if [ "$EXTRAS" = "--extras" ]; then
  if [ -e "$SK/genealogy-research" ]; then echo "genealogy-research already exists"; else
    git clone -q https://github.com/sliday/genealogy-research "$SK/genealogy-research" && echo "Skill genealogy-research installed"; fi
  if [ -z "${NO_BROWSER:-}" ]; then
    if command -v browser-harness >/dev/null; then echo "browser-harness already installed"
    elif command -v uv >/dev/null; then uv tool install browser-harness && echo "browser-harness installed"
    else echo "browser-harness: install uv first (https://docs.astral.sh/uv/), then: uv tool install browser-harness"; fi
    if [ ! -e "$SK/browser-harness/SKILL.md" ] && command -v uv >/dev/null; then
      BH=$(find "$(uv tool dir)/browser-harness" -name SKILL.md -path '*browser_harness*' 2>/dev/null | head -1 || true)
      [ -n "$BH" ] && mkdir -p "$SK/browser-harness" && cp "$BH" "$SK/browser-harness/SKILL.md" && echo "Skill browser-harness installed"
    fi
  fi
fi
cd "$TARGET"
git init -q
git add -A
git -c user.name="Family history" -c user.email="family@example.invalid" commit -qm "Start from the kit (sample family)"
python3 scripts/build_all.py
echo
echo "Done: $TARGET"
echo "Next step: open the folder in Claude Code and send the first message from the README."
