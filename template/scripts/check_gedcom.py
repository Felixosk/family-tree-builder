#!/usr/bin/env python3
"""Checks family.ged without external tools: structure, dangling references, duplicate IDs,
line length, hard impossibilities (parent younger than child, death before birth).

Usage: python3 scripts/check_gedcom.py [file.ged]
Exit code 1 on errors, 0 when clean. Notes (e.g. people without any source) do not fail the check.
"""
import os, re, sys
from collections import Counter

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GED = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('GED') or os.path.join(P, 'family.ged')
raw = open(GED, encoding='utf-8-sig').read().replace('\r\n', '\n')
L = raw.split('\n')
while L and L[-1] == '':
    L.pop()

errors, notes = [], []
LINE = re.compile(r'^(\d+) (@[^@]+@ )?(\w+)( (.*))?$')

# 1 Structure
if not L or not L[0].startswith('0 HEAD'):
    errors.append('file does not start with 0 HEAD')
if not L or L[-1].strip() != '0 TRLR':
    errors.append('file does not end with 0 TRLR')
prev = 0
for i, l in enumerate(L, 1):
    m = LINE.match(l)
    if not m:
        errors.append(f'line {i}: unreadable: {l[:60]!r}')
        continue
    lvl = int(m.group(1))
    if lvl > prev + 1:
        errors.append(f'line {i}: level jumps from {prev} to {lvl}')
    prev = lvl
    if len(l.encode('utf-8')) > 255:
        errors.append(f'line {i}: {len(l.encode("utf-8"))} bytes (max 255, use scripts/wrap_lines.py)')

# 2 Records and references
recs = {}
for l in L:
    m = re.match(r'^0 (@[^@]+@) (\w+)', l)
    if m:
        recs.setdefault(m.group(1), []).append(m.group(2))
for x, t in recs.items():
    if len(t) > 1:
        errors.append(f'ID {x} is used {len(t)} times (check patch order or ID range)')
for i, l in enumerate(L, 1):
    m = re.match(r'^\d+ (\w+) (@[^@]+@)\s*$', l)
    if m and m.group(2) not in recs:
        errors.append(f'line {i}: reference {m.group(2)} ({m.group(1)}) points nowhere')

# 3 People, families, years
def record(x):
    s = next(i for i, l in enumerate(L) if l.startswith(f'0 {x} '))
    e = s + 1
    while e < len(L) and not L[e].startswith('0 '):
        e += 1
    return L[s:e]

def year(lines, tag):
    for k, l in enumerate(lines):
        if l == f'1 {tag}' or l.startswith(f'1 {tag} '):
            for l2 in lines[k + 1:]:
                if l2.startswith('1 '):
                    break
                m = re.match(r'^2 DATE .*?(\d{4})', l2)
                if m and not re.match(r'^2 DATE (BEF|AFT|BET|FROM)', l2):
                    return int(m.group(1))
    return None

indi = {x: record(x) for x, t in recs.items() if t[0] == 'INDI'}
born = {x: year(z, 'BIRT') or year(z, 'CHR') or year(z, 'BAPM') for x, z in indi.items()}
died = {x: year(z, 'DEAT') or year(z, 'BURI') for x, z in indi.items()}
for x in indi:
    if born[x] and died[x] and died[x] < born[x]:
        errors.append(f'{x}: death {died[x]} before birth {born[x]}')
    if not any(re.match(r'^\d+ SOUR @', l) for l in indi[x]):
        notes.append(f'{x}: no source at all')
for x, t in recs.items():
    if t[0] != 'FAM':
        continue
    z = record(x)
    parents = [l.split()[2] for l in z if re.match(r'^1 (HUSB|WIFE) @', l)]
    children = [l.split()[2] for l in z if l.startswith('1 CHIL @')]
    for p in parents:
        for c in children:
            if born.get(p) and born.get(c):
                d = born[c] - born[p]
                if d < 12:
                    errors.append(f'{x}: parent {p} (*{born[p]}) would be {d} at the birth of {c} (*{born[c]})')
                elif d > 65:
                    notes.append(f'{x}: parent {p} would be {d} at the birth of {c}, check')

types = Counter(t[0] for t in recs.values())
print(f'GEDCOM: {os.path.basename(GED)} | people {types["INDI"]}, families {types["FAM"]}, sources {types["SOUR"]}, media {types["OBJE"]}')
print(f'Errors: {len(errors)} | Notes: {len(notes)}')
for f in errors[:40]:
    print('  ERROR ', f)
for h in notes[:15]:
    print('  NOTE  ', h)
if len(notes) > 15:
    print(f'  ... and {len(notes) - 15} more notes')
sys.exit(1 if errors else 0)
