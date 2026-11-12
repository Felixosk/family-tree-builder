#!/usr/bin/env python3
"""Before every search: has this been read or searched already?
Searches a name, place, book or call number in Coverage.md, vault/Research, journal/, letters/ and PROCESS.md.

Usage: python3 scripts/already_read.py "<term>" ["<another term>" ...]   (all terms on the same line)
Exit code 0 = hits found (read them first!), 1 = nothing found.
"""
import os, re, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) < 2:
    sys.exit(__doc__)
patterns = [re.compile(re.escape(w), re.I) for w in sys.argv[1:]]
places = [os.path.join(P, 'vault', 'Research'), os.path.join(P, 'journal'), os.path.join(P, 'letters'), os.path.join(P, 'PROCESS.md')]
hits = 0
for place in places:
    files = [place] if os.path.isfile(place) else [os.path.join(w, f) for w, _, fs in os.walk(place) for f in fs if f.endswith(('.md', '.tsv', '.txt'))]
    for d in sorted(files):
        try:
            lines = open(d, encoding='utf-8').read().split('\n')
        except Exception:
            continue
        for i, z in enumerate(lines, 1):
            if all(m.search(z) for m in patterns):
                print(f'{os.path.relpath(d, P)}:{i}: {z.strip()[:160]}')
                hits += 1
print(f'\n{hits} hits.' + (' Read these first, then decide whether a new search makes sense.' if hits else ' Nothing about this in the project yet.'))
sys.exit(0 if hits else 1)
