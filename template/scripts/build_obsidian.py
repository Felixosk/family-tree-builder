#!/usr/bin/env python3
"""Mirrors the family tree as person notes into an Obsidian folder (optional).

Input: reports/tree_data.json (written by scripts/build_tree_html.py on every run).
Target: project.json -> "obsidian_folder" (empty = step is skipped).
Generated notes carry `generated: family-tree` in their header and are rewritten on every run.
The note "Family Tree Inbox" is only created, never overwritten: write new things there from your phone
(stories, questions, photos), and Claude works them in next time.

Usage: python3 scripts/build_obsidian.py
"""
import os, re, json, datetime

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(P, 'project.json'), encoding='utf-8'))
TARGET = os.path.expanduser(CFG.get('obsidian_folder') or '')
if not TARGET:
    print('Obsidian: no obsidian_folder in project.json, skipped')
    raise SystemExit(0)

D = json.load(open(os.path.join(P, 'reports', 'tree_data.json'), encoding='utf-8'))
PE, FA = D['people'], D['fams']
SURNAME = CFG.get('surname', 'Family')
EV = {'BIRT': 'Birth', 'CHR': 'Baptism', 'BAPM': 'Baptism', 'MARR': 'Marriage', 'RESI': 'Residence', 'EMIG': 'Emigration',
      'IMMI': 'Immigration', 'EVEN': 'Event', 'DEAT': 'Death', 'BURI': 'Burial'}


def status(p):
    s = next((n.split(':', 1)[1].strip() for n in reversed(p['notes']) if n.startswith('Status:')), '')  # newest status note wins
    return (s.split(' ')[0].rstrip('.,') if s else 'not rated'), s


def note_name(pid):
    p = PE[pid]
    n = re.sub(r'[\\/:*?"<>|\[\]#^]', '', p['name']).strip() or 'Unknown'
    return f"{n} ({p['born'] or pid.strip('@')})"


def link(pid):
    return f"[[{note_name(pid)}|{PE[pid]['name']}]]" if pid in PE else ''


os.makedirs(os.path.join(TARGET, 'People'), exist_ok=True)
today = datetime.date.today().isoformat()
written = set()
for pid, p in PE.items():
    st, st_long = status(p)
    z = ['---', 'generated: family-tree', f'gedcom: "{pid}"', f'status: {st}', '---', '', f"# {p['name']}", '',
         f'Part of [[{SURNAME} Family Tree]]. Generated on {today}, do not edit by hand. Put new things in [[Family Tree Inbox]].', '',
         f"Life: {p['born'] or '?'} to {p['died'] or '?'}", f'Status: {st_long or st}', '', '## Family']
    parents = [x for f in p['famc'] if f in FA for x in (FA[f]['husb'], FA[f]['wife']) if x in PE]
    z.append('- Parents: ' + (' and '.join(link(x) for x in parents) if parents else 'not recorded'))
    for f in p['fams']:
        if f not in FA:
            continue
        partner = [x for x in (FA[f]['husb'], FA[f]['wife']) if x and x != pid and x in PE]
        kids = [link(c) for c in FA[f]['chil'] if c in PE]
        z.append(f"- Partner: {', '.join(link(x) for x in partner) or 'unknown'}; children: {', '.join(kids) or 'none recorded'}")
    z += ['', '## Events']
    for e in p['events']:
        z.append(f"- {EV.get(e['tag'], e['tag'])}: {e['date'] or '?'} {e['place']}".rstrip())
        for q in e['sources']:
            z.append(f"  - Evidence: {q['title']}: {q['page']}" + (f" (QUAY {q['quay']})" if q['quay'] else ''))
    if p['notes']:
        z += ['', '## Notes'] + [f'- {n}' for n in p['notes']]
    fn = os.path.join(TARGET, 'People', note_name(pid) + '.md')
    open(fn, 'w', encoding='utf-8').write('\n'.join(z) + '\n')
    written.add(os.path.basename(fn))

# remove outdated generated notes (only those marked "generated: family-tree")
for fn in os.listdir(os.path.join(TARGET, 'People')):
    pf = os.path.join(TARGET, 'People', fn)
    if fn.endswith('.md') and fn not in written and 'generated: family-tree' in open(pf, encoding='utf-8').read(400):
        os.remove(pf)

inbox = os.path.join(TARGET, 'Family Tree Inbox.md')
if not os.path.exists(inbox):
    open(inbox, 'w', encoding='utf-8').write('# Family Tree Inbox\n\nWrite new things here. Claude works them in and moves them to "Done".\n\n## Open\n\n## Done\n')
open(os.path.join(TARGET, f'{SURNAME} Family Tree.md'), 'w', encoding='utf-8').write(
    f'# {SURNAME} Family Tree\n\nGenerated on {today}. {len(PE)} people.\n\n' + '\n'.join(f'- {link(x)}' for x in sorted(PE, key=note_name)) + '\n')
print(f'Obsidian: {len(written)} person notes in {TARGET}')
