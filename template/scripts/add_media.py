#!/usr/bin/env python3
"""Attaches media from sources/media.tsv to family.ged as OBJE records.
Idempotent: files that are already linked (same FILE path) are skipped.
Columns (tab separated): file, title, date, place, description, persons (xref|xref), event (optional), source (optional)
Usage: python3 scripts/add_media.py [--dry]"""
import csv, os, re, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ged = os.environ.get("GED") or f"{P}/family.ged"; dry = '--dry' in sys.argv
raw = open(ged, encoding='utf-8').read(); L = raw.split('\n')
if L and L[-1] == '': L = L[:-1]
existing = set(re.findall(r'^\d+ FILE (.+)$', raw, re.M))
nums = [int(m) for m in re.findall(r'^0 @O(\d+)@ OBJE', raw, re.M)]; nxt = max(nums + [0]) + 1
def esc(t): return t.replace('@', '@@')
def _chunks(text, budget):
    """Splits by BYTES, not characters. GEDCOM 5.5.1 limits a line to 255 bytes;
    with accented or Cyrillic text, 200 characters can be up to 400 bytes."""
    out = []; rest = text
    while rest:
        n = 0; used = 0
        while n < len(rest):
            w = len(rest[n].encode('utf-8'))
            if used + w > budget: break
            used += w; n += 1
        if n == 0: n = 1
        out.append(rest[:n]); rest = rest[n:]
    return out or ['']

def wrap(level, tag, text, limit=240):
    out = []; first = True
    for para in text.split('\n'):
        pre_first = f"{level} {tag} "; pre_cont = f"{level+1} CONT "; pre_conc = f"{level+1} CONC "
        budget = limit - max(len(pre_first.encode('utf-8')), len(pre_cont.encode('utf-8')), len(pre_conc.encode('utf-8')))
        for j, c in enumerate(_chunks(para, budget)):
            if first: out.append(f"{level} {tag} {c}".rstrip()); first = False
            elif j == 0: out.append(f"{level+1} CONT {c}".rstrip())
            else: out.append(f"{level+1} CONC {c}")
    return out
new_recs = []; links = {}; added = 0; skipped = 0
with open(f"{P}/sources/media.tsv", encoding='utf-8') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        file = row['file'].strip()
        if not file or file in existing: skipped += 1; continue
        if not os.path.exists(os.path.join(P, file)): print("MISSING:", file); continue
        ext = file.rsplit('.', 1)[-1].lower(); form = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'pdf': 'pdf', 'tif': 'tiff', 'tiff': 'tiff'}.get(ext, ext)
        x = f"@O{nxt}@"; nxt += 1
        rec = [f"0 {x} OBJE", "1 FILE " + file, f"2 FORM {form}", f"3 TYPE {'document' if form == 'pdf' else 'photo'}"] + wrap(2, 'TITL', esc(row['title'].strip()))
        if row.get('date', '').strip(): rec.append("1 DATE " + row['date'].strip())
        if row.get('place', '').strip(): rec.append("1 PLAC " + row['place'].strip())
        if row.get('description', '').strip(): rec += wrap(1, 'NOTE', esc(row['description'].strip()))
        if row.get('source', '').strip(): rec.append("1 SOUR " + row['source'].strip())
        new_recs += rec; added += 1
        for pid in [p.strip() for p in row['persons'].split('|') if p.strip()]:
            links.setdefault(pid, []).append((x, row.get('event', '').strip()))
# Insert links: under the matching event (level 2), otherwise at the end of the record (level 1)
out = []; i = 0; linked = 0
while i < len(L):
    l = L[i]; m = re.match(r'^0 (@I\w+@) INDI', l)
    if m and m.group(1) in links:
        pid = m.group(1); j = i + 1
        while j < len(L) and not L[j].startswith('0 '): j += 1
        rec = L[i:j]; pending = links[pid]
        for x, ev in pending:
            placed = False
            if ev:
                for k in range(1, len(rec)):
                    if rec[k] == f"1 {ev}":
                        e = k + 1
                        while e < len(rec) and not rec[e].startswith('1 '): e += 1
                        rec[e:e] = [f"2 OBJE {x}"]; placed = True; break
            if not placed: rec.append(f"1 OBJE {x}")
            linked += 1
        out += rec; i = j; continue
    out.append(l); i += 1
if new_recs:
    t = out.index('0 TRLR'); out[t:t] = new_recs
print(f"new media: {added}, skipped: {skipped}, links: {linked}")
if dry: print("(dry run, nothing written)")
else:
    open(ged, 'w', encoding='utf-8', newline='').write('\n'.join(out) + '\n'); print("family.ged updated")
