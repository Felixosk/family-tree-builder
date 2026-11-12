#!/usr/bin/env bash
# Fresh install test: uses the kit the way a fresh machine would. No network, no own skills, its own HOME.
# Usage: tests/fresh_install_test.sh   (exit 0 = all good)
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"
export HOME="$T/home"; mkdir -p "$HOME"
fail(){ echo "!! FAILED: $*"; exit 1; }

"$KIT/new_project.sh" "$T/research" "Testfamily" > "$T/log.txt" 2>&1 || { cat "$T/log.txt"; fail "new_project.sh"; }
cd "$T/research"
[ -f "$HOME/.claude/skills/family-tree-builder/SKILL.md" ] || fail "skill family-tree-builder not installed"
[ -f "$HOME/.claude/skills/archive-portals/SKILL.md" ] || fail "skill archive-portals not installed"
[ -d sources/private ] || fail "sources/private missing"
python3 scripts/check_gedcom.py >/dev/null || fail "GEDCOM check"
python3 scripts/check_readings.py >/dev/null || fail "check_readings"
python3 scripts/rebuild.py | grep -q "0 lines only in the current file, 0 only in the rebuild" || fail "rebuild differs"
grep -q "Testfamily" reports/tree.html || fail "tree page without surname"

# New patch from the template, ID range 0002
sed -e 's/@S0001001@/@S0002001@/g' -e "s/g.append_to('@I3@'/g.append_to('@I4@'/" -e 's/4 MAR 1925/1 JUN 1928/' \
  scripts/patches/0001_example_baptism.py > scripts/patches/0002_test.py
python3 scripts/rebuild.py --apply >/dev/null || fail "rebuild --apply"
grep -q "@S0002001@" family.ged || fail "patch 0002 missing"
python3 scripts/rebuild.py --apply >/dev/null || fail "second run not idempotent"
[ "$(grep -c '^0 @S0002001@' family.ged)" = "1" ] || fail "duplicate ID"

# Wrong ID range must stop the rebuild
sed -e 's/@S0001001@/@S0099001@/g' scripts/patches/0001_example_baptism.py > scripts/patches/0003_wrong.py
if python3 scripts/rebuild.py >/dev/null 2>&1; then fail "wrong ID range not detected"; fi
rm scripts/patches/0003_wrong.py

# A broken file must be noticed
cp family.ged "$T/ok.ged"; echo "1 FAMC @F999@" >> family.ged
if python3 scripts/check_gedcom.py >/dev/null 2>&1; then fail "dangling reference not detected"; fi
cp "$T/ok.ged" family.ged

python3 scripts/build_all.py >/dev/null || fail "build_all"
python3 scripts/already_read.py "Sampletown" >/dev/null || fail "already_read does not find the example"
mkdir -p "$T/images"; python3 -c "open('$T/images/b1.jpg','wb').write(b'x')"
python3 scripts/read_images.py "$T/images" "$T/result.tsv" --dry | grep -q "DRY b1.jpg" || fail "read_images --dry"
printf 'image\thit\nb1.jpg\tyes\nb2.jpg\tno\n' > "$T/expected.tsv"; printf 'image\thit\tyear\tkind\tsummary\nb1.jpg\tyes\t\t\t\nb2.jpg\tno\t\t\t\n' > "$T/actual.tsv"
python3 scripts/calibrate.py "$T/expected.tsv" "$T/actual.tsv" >/dev/null || fail "calibrate"
python3 -m py_compile scripts/portals/digi_archives_cz.py || fail "portal script"
python3 scripts/rebuild.py --new-base >/dev/null || fail "new base"
ls scripts/patches/archive/0002_test.py >/dev/null || fail "archive after new base"
python3 scripts/rebuild.py | grep -q "Rebuild: 0 patches" || fail "rebuild after new base"
echo "FRESH INSTALL OK ($T)"
