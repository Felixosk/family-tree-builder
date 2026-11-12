#!/usr/bin/env python3
"""One command after every change to family.ged: check, build the tree page, mirror to Obsidian.
Afterwards (Claude does this, not the script): share the page if wanted, update PROCESS.md, git commit.
Usage: python3 scripts/build_all.py
Exit code 1 if the GEDCOM check has errors (then nothing is built).
"""
import os, subprocess, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(*cmd):
    r = subprocess.run([sys.executable, *cmd], cwd=P, capture_output=True, text=True)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, lines


rc, z = run('scripts/check_gedcom.py')
print('\n'.join(z[:2]))
if rc != 0:
    print('\n'.join(z[2:]))
    sys.exit('Stopped: fix the GEDCOM errors first.')
rc, z = run('scripts/check_readings.py')
print('Readings:', 'ok' if rc == 0 else 'open findings, list: python3 scripts/check_readings.py')
rc, z = run('scripts/build_tree_html.py')
print(z[-1] if z else f'Tree page: exit code {rc}')
if rc != 0:
    sys.exit('Stopped: tree page not built.')
rc, z = run('scripts/build_obsidian.py')
print(z[-1] if z else f'Obsidian: exit code {rc}')
print('Next: look at reports/tree.html, update PROCESS.md, git commit.')
