#!/usr/bin/env python3
"""Online-tree gap check: what is still missing in the online tree (Ancestry etc.)?

Last step of every research round ("count it, do not estimate it").
Reads family.ged only (no other helper files needed) plus two small optional files:
  sources/online_tree_ids.json   {"@I3@": "<online person id>", ...}   (local XREF -> online ID)
  output/online_people.json      list of online IDs (or list of objects with an "id" key),
                                 fetched fresh right before this run from the online tree's read interface.
                                 Stale list = false "missing" results, so fetch it first.

Status of a person = the LAST note that starts with "Status: <level>" (later notes overrule earlier ones).
Only Proven goes online. "Proven with proven parent link" = person is Proven AND (no parents recorded OR every
parent family is not challenged (FAMC ... STAT challenged) and every parent in it is Proven itself).
Stricter on purpose: the online tree only gets what can be proven.

Output: output/online_tree_gap.md and one console line. Exit code 1 while something is missing.
Usage: python3 scripts/online_tree_gap.py [--folder PATH]
"""
import os, re, sys, json

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if '--folder' in sys.argv:
    P = os.path.abspath(sys.argv[sys.argv.index('--folder') + 1])
LEVELS = 'Proven|Probable|Possible|Unresolved|Disproven'


def parse(path):
    people, fams, cur, kind, sub = {}, {}, None, None, None
    for line in open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n'):
        m = re.match(r'(\d+) (@[^@]+@) (INDI|FAM)\b', line)
        if m:
            kind, x = m[3], m[2]
            cur = {'name': '', 'notes': [], 'famc': [], 'unsure': set(), 'husb': None, 'wife': None}
            (people if kind == 'INDI' else fams)[x] = cur
            sub = None
            continue
        if line.startswith('0 '):
            cur = kind = None
            continue
        if cur is None:
            continue
        m = re.match(r'1 (\w+)\s*(.*)', line)
        if m:
            tag, val = m[1], m[2]
            sub = (tag, val)
            if kind == 'INDI' and tag == 'NAME' and not cur['name']:
                cur['name'] = val.replace('/', '').strip()
            elif kind == 'INDI' and tag == 'NOTE':
                cur['notes'].append(val)
            elif kind == 'INDI' and tag == 'FAMC':
                cur['famc'].append(val)
            elif kind == 'FAM' and tag in ('HUSB', 'WIFE'):
                cur[tag.lower()] = val
            continue
        m = re.match(r'2 STAT (\w+)', line)
        if m and sub and sub[0] == 'FAMC' and m[1].lower() in ('challenged', 'disproved'):
            cur['unsure'].add(sub[1])
    return people, fams


def status(p):
    s = [n for n in p['notes'] if n.startswith('Status:')]
    if not s:
        return ''
    m = re.match(r'Status:\s*(%s)' % LEVELS, s[-1])
    return m[1] if m else '?'


def load(*parts, default=None):
    f = os.path.join(P, *parts)
    if not os.path.exists(f):
        if default is None:
            sys.exit(f'Missing {os.path.join(*parts)}. See the docstring of this script.')
        return default
    return json.load(open(f, encoding='utf-8'))


people, fams = parse(os.path.join(P, 'family.ged'))
ids = load('sources', 'online_tree_ids.json', default={})
online = {str(o['id'] if isinstance(o, dict) else o) for o in load('output', 'online_people.json')}
ST = {x: status(p) for x, p in people.items()}


def parents_proven(x):
    p = people[x]
    if not p['famc']:
        return True, 'no parents recorded'
    for fx in p['famc']:
        if fx in p['unsure']:
            return False, f'parent link {fx} challenged'
        f = fams.get(fx, {})
        for e in (f.get('husb'), f.get('wife')):
            if e and ST.get(e) != 'Proven':
                return False, f"parent {people.get(e, {}).get('name', e)} is {ST.get(e) or 'without status'}"
    return True, ''


missing, held_back, unsure, no_status = [], [], [], []
for x, p in people.items():
    oid = ids.get(x)
    there = bool(oid and str(oid) in online)
    s = ST[x]
    label = f"- {p['name']} ({x})"
    if there:
        if s in ('Probable', 'Possible', 'Unresolved', 'Disproven', '?'):
            unsure.append(f'{label} = online {oid}: local **{s}** (list only, delete nothing)')
        elif not s:
            no_status.append(f'{label} = online {oid}')
    elif s == 'Proven':
        ok, why = parents_proven(x)
        (missing if ok else held_back).append(label + ('' if ok else f': {why}'))

out = ['# Online tree gap', '',
       f'Local {len(people)} people, online {len(online)} people. Status = last "Status:" note in family.ged.', '',
       f'## Missing online ({len(missing)}): Proven, parent link Proven, no online ID', ''] + (missing or ['- nothing']) + \
      ['', f'## Deliberately not entered ({len(held_back)}): Proven, but parent link not Proven', ''] + (held_back or ['- nothing']) + \
      ['', f'## Online but not Proven locally ({len(unsure)})', ''] + (unsure or ['- nothing']) + \
      ['', f'## Online, no status locally ({len(no_status)}): not counted', ''] + (no_status or ['- nothing'])
os.makedirs(os.path.join(P, 'output'), exist_ok=True)
open(os.path.join(P, 'output', 'online_tree_gap.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'Online tree gap: {len(missing)} missing, {len(held_back)} held back, {len(unsure)} not proven locally')
sys.exit(1 if missing else 0)
