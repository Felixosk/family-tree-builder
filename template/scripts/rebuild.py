#!/usr/bin/env python3
"""Rebuilds family.ged from the base snapshot plus all patches and compares with the current file.

Why: if an old patch was wrong, you fix that script and replay everything. Every change stays
traceable, and nobody edits family.ged by hand.

  Base:     sources/base/family-base.ged      (e.g. your first Ancestry export, never edit)
  Patches:  scripts/patches/NNNN_topic.py     (run in number order)

Usage:
  python3 scripts/rebuild.py                 dry run on a copy, compare with family.ged
  python3 scripts/rebuild.py --apply         write the result to family.ged (backup first)
  python3 scripts/rebuild.py --apply --force also when family.ged has lines no patch creates
                                             (first import), or when the check reports errors
  python3 scripts/rebuild.py --new-base      freeze: today's checked state becomes the new base,
                                             old patches move to scripts/patches/archive/

A new patch gets the next number and exactly that number as its ID range (script 0012 only
creates @I0012xxx@, @F0012xxx@, @S0012xxx@, @O0012xxx@). Then the order does not matter for IDs
and there are no duplicate IDs. This script refuses patches that leave their range.
"""
import glob, os, re, shutil, subprocess, sys, tempfile, datetime

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(P, 'sources', 'base', 'family-base.ged')
TARGET = os.path.join(P, 'family.ged')
PATCHES = os.path.join(P, 'scripts', 'patches')


def logical(path):
    """Content without CONC line breaks, so wrap positions do not count as differences."""
    out = []
    for l in open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n'):
        m = re.match(r'^\d+ CONC (.*)$', l)
        if m and out:
            out[-1] += m.group(1)
        elif l:
            out.append(l)
    i = next((k for k, l in enumerate(out) if l.startswith('0 ') and not l.startswith('0 HEAD')), 0)
    return out[i:]  # HEAD changes (export date) and does not count


def main():
    if not os.path.exists(BASE):
        sys.exit(f'Base snapshot missing: {BASE}')
    scripts = sorted(glob.glob(os.path.join(PATCHES, '[0-9][0-9][0-9][0-9]_*.py')))
    numbers = [os.path.basename(s)[:4] for s in scripts]
    if len(numbers) != len(set(numbers)):
        sys.exit('ABORT: two patches with the same number')
    tmp = os.path.join(tempfile.mkdtemp(prefix='rebuild_'), 'family.ged')
    shutil.copy(BASE, tmp)
    env = dict(os.environ, GED=tmp)

    def ids():
        return set(re.findall(r'^0 (@[^@]+@)', open(tmp, encoding='utf-8').read(), re.M))

    for s in scripts:
        before = ids()
        r = subprocess.run([sys.executable, s], env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout + r.stderr)
            sys.exit(f'ABORT in {os.path.basename(s)}')
        nr = os.path.basename(s)[:4]
        foreign = [x for x in ids() - before if not re.match(r'^@[A-Z]+%s\d+@$' % nr, x)]
        if foreign:
            sys.exit(f'ABORT: {os.path.basename(s)} creates IDs outside its range {nr}: {foreign[:5]}')
    r = subprocess.run([sys.executable, os.path.join(P, 'scripts', 'wrap_lines.py')], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('ABORT while wrapping lines')
    r = subprocess.run([sys.executable, os.path.join(P, 'scripts', 'check_gedcom.py'), tmp], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        if '--force' not in sys.argv:
            sys.exit('ABORT: the rebuilt file has errors (first import of a foreign export: --apply --force, then fix them with a patch)')
        print('WARNING: check reported errors, continuing because of --force')
    print(f'Rebuild: {len(scripts)} patches applied -> {tmp}')

    new = logical(tmp)
    differences = 0
    if os.path.exists(TARGET):
        old = logical(TARGET)
        a, b = set(old), set(new)
        only_old, only_new = [l for l in old if l not in b], [l for l in new if l not in a]
        differences = len(only_old) + len(only_new)
        print(f'Compared with family.ged: {len(only_old)} lines only in the current file, {len(only_new)} only in the rebuild')
        for l in only_old[:10]:
            print('  - ', l[:120])
        for l in only_new[:10]:
            print('  + ', l[:120])
        if only_old and '--apply' in sys.argv and '--force' not in sys.argv:
            sys.exit('Not applied: the current file has lines that no patch creates. '
                     'Find out first (hand edit? missing patch?), then use --apply --force.')
    if '--apply' in sys.argv:
        if os.path.exists(TARGET):
            stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
            os.makedirs(os.path.join(P, 'sources', 'base', 'backups'), exist_ok=True)
            shutil.copy(TARGET, os.path.join(P, 'sources', 'base', 'backups', f'family-before-rebuild-{stamp}.ged'))
        shutil.copy(tmp, TARGET)
        print('family.ged replaced (backup in sources/base/backups/)')
        differences = 0
    return differences


def new_base():
    """Freeze the chain when it gets long (e.g. over 30 patches)."""
    if main() != 0:
        sys.exit('No new base: rebuild and family.ged differ. Sort that out first.')
    stamp = datetime.date.today().isoformat()
    old = os.path.join(P, 'sources', 'base', f'family-base-until-{stamp}.ged')
    shutil.move(BASE, old)
    shutil.copy(TARGET, BASE)
    arch = os.path.join(PATCHES, 'archive')
    os.makedirs(arch, exist_ok=True)
    for s in glob.glob(os.path.join(PATCHES, '[0-9][0-9][0-9][0-9]_*.py')):
        shutil.move(s, arch)
    print(f'New base set ({stamp}). Old base: {os.path.relpath(old, P)}. Keep counting patch numbers, do not restart at 0001.')


if __name__ == '__main__':
    if '--new-base' in sys.argv:
        new_base()
    else:
        main()
