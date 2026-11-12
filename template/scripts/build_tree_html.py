#!/usr/bin/env python3
"""Builds a self-contained HTML family tree page from family.ged (with an evidence colour per person).
Also writes reports/tree_data.json (used by scripts/build_obsidian.py).
Usage: python3 scripts/build_tree_html.py [family.ged] [reports/tree.html]"""
import re, sys, json, os, html
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else f"{P}/family.ged"
dst = sys.argv[2] if len(sys.argv) > 2 else f"{P}/reports/tree.html"
lines = open(src, encoding='utf-8-sig').read().split('\n')
recs = {}; order = []; stack = []
for ln in lines:
    m = re.match(r'^(\d+) (@[^@]+@ )?(\S+)( (.*))?$', ln.rstrip('\r'))
    if not m: continue
    lvl = int(m.group(1)); xref = (m.group(2) or '').strip(); tag = m.group(3); val = m.group(5) or ''
    node = {'tag': tag, 'val': val, 'sub': []}
    if lvl == 0:
        node['xref'] = xref; recs[xref or tag] = node; order.append(xref or tag); stack = [node]
    else:
        stack = stack[:lvl]; stack[-1]['sub'].append(node); stack.append(node)
def get(n, t): return [s for s in n['sub'] if s['tag'] == t]
def first(n, t):
    g = get(n, t); return g[0] if g else None
def text(n):
    out = n['val']
    for s in n['sub']:
        if s['tag'] == 'CONT': out += '\n' + s['val']
        elif s['tag'] == 'CONC': out += s['val']
    return out.replace('@@', '@')
SO = {k: text(first(v, 'TITL')) if first(v, 'TITL') else k for k, v in recs.items() if v['tag'] == 'SOUR'}
# Settings from project.json (see README, section "Settings in project.json"). Other people's trees are also recognised by the source title.
CFG = {}
try: CFG = json.load(open(os.path.join(P, 'project.json'), encoding='utf-8'))
except Exception: pass
TREE = set(CFG.get('user_tree_sources', [])) | {k for k, t in SO.items() if re.search(r'Family Trees|Stammb(ä|ae)ume|user tree|Geneanet|MyHeritage|FamilySearch Family Tree|WikiTree|GEDBAS', t, re.I)}
FAMILY = set(CFG.get('family_knowledge_sources', []))
def classify(ids):
    if not ids: return 'none'
    if ids - TREE - FAMILY: return 'record'
    if ids & FAMILY: return 'family'
    return 'usertree'
def collect_sources(n, acc):
    for s in n['sub']:
        if s['tag'] == 'SOUR' and s['val'] in SO:
            pg = first(s, 'PAGE'); q = first(s, 'QUAY')
            acc.append({'id': s['val'], 'title': SO[s['val']], 'page': text(pg) if pg else '', 'quay': q['val'] if q else ''})
        collect_sources(s, acc)
media = {}
def media_refs(n):
    return [s['val'] for s in n['sub'] if s['tag'] == 'OBJE' and s['val'] in media]
def ev(n, t):
    out = []
    for e in get(n, t):
        d = first(e, 'DATE'); p = first(e, 'PLAC'); notes = [text(x) for x in get(e, 'NOTE')]; ss = []; collect_sources(e, ss)
        typ = first(e, 'TYPE')
        out.append({'tag': t, 'type': typ['val'] if typ else '', 'date': d['val'] if d else '', 'place': p['val'] if p else '', 'notes': notes, 'sources': ss, 'media': media_refs(e)})
    return out
for k, v in recs.items():
    if v['tag'] != 'OBJE': continue
    f = first(v, 'FILE'); path = f['val'].strip() if f else ''
    titl = first(f, 'TITL') if f else None
    d = first(v, 'DATE'); pl = first(v, 'PLAC'); dscr = first(v, '_DSCR')
    ext = path.rsplit('.', 1)[-1].lower() if '.' in path else ''
    media[k] = {'id': k, 'file': path, 'isImage': ext in ('jpg', 'jpeg', 'png', 'gif', 'webp'), 'pdf': ext == 'pdf',
                'title': text(titl) if titl else (text(first(v, 'TITL')) if first(v, 'TITL') else ''),
                'date': d['val'] if d else '', 'place': pl['val'] if pl else '',
                'description': '\n'.join([text(x) for x in get(v, 'NOTE')] + ([dscr['val']] if dscr else [])),
                'external': not path}
people = {}; fams = {}
for k, v in recs.items():
    if v['tag'] == 'FAM':
        h = first(v, 'HUSB'); w = first(v, 'WIFE')
        fams[k] = {'husb': h['val'] if h else None, 'wife': w['val'] if w else None, 'chil': [c['val'] for c in get(v, 'CHIL')], 'marr': ev(v, 'MARR')}
for k, v in recs.items():
    if v['tag'] != 'INDI': continue
    names = []
    for n in get(v, 'NAME'):
        typ = first(n, 'TYPE'); ss = []; collect_sources(n, ss)
        names.append({'name': n['val'].replace('/', ' ').replace('  ', ' ').strip(), 'type': typ['val'] if typ else '', 'sources': ss})
    sex = first(v, 'SEX'); ss = []; collect_sources(v, ss)
    events = []
    for t in ('BIRT', 'CHR', 'BAPM', 'MARR', 'RESI', 'EMIG', 'IMMI', 'EVEN', 'DEAT', 'BURI'): events += ev(v, t)
    people[k] = {'id': k, 'name': names[0]['name'] if names else '?', 'names': names, 'sex': sex['val'] if sex else '',
                 'famc': [f['val'] for f in get(v, 'FAMC')], 'fams': [f['val'] for f in get(v, 'FAMS')],
                 'events': events, 'notes': [text(x) for x in get(v, 'NOTE')], 'sources': ss, 'cls': classify({s['id'] for s in ss}), 'media': media_refs(v)}
def yr(s):
    """Year for the card; qualifiers like AFT/BEF/ABT/BET stay visible."""
    s = (s or '').strip(); u = s.upper(); ys = re.findall(r'\d{4}', s)
    if not ys: return ''
    if u.startswith('BET') and len(ys) > 1: return ys[0] + '/' + (ys[1][2:] if ys[0][:2] == ys[1][:2] else ys[1])
    if u.startswith('AFT'): return 'after ' + ys[0]
    if u.startswith('BEF'): return 'before ' + ys[0]
    if u.startswith(('ABT', 'EST', 'CAL')): return '~' + ys[0]
    return ys[0]
for p in people.values():
    b = next((e for e in p['events'] if e['tag'] in ('BIRT', 'CHR', 'BAPM')), None); d = next((e for e in p['events'] if e['tag'] == 'DEAT'), None)
    p['born'] = yr(b['date']) if b else ''; p['died'] = yr(d['date']) if d else ''
    allm = list(dict.fromkeys(p['media'] + [m for e in p['events'] for m in e['media']]))
    p['media'] = allm
    p['photo'] = next((m for m in allm if media[m]['isImage'] and media[m]['file'].startswith('sources/photos/')), None)  # portraits only from sources/photos
data = {'people': people, 'fams': fams, 'media': media, 'root': CFG.get('root_person') or next((k for k in order if k.startswith('@I')), ''), 'base': '../'}
stats = {c: sum(1 for p in people.values() if p['cls'] == c) for c in ('record', 'family', 'usertree', 'none')}
tpl = open(os.path.join(P, 'scripts', 'templates', 'tree.html'), encoding='utf-8').read()
out = tpl.replace('__SURNAME__', html.escape(CFG.get('surname', 'Our'))).replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
os.makedirs(os.path.dirname(dst), exist_ok=True); open(dst, 'w', encoding='utf-8').write(out)
json.dump(data, open(os.path.join(os.path.dirname(dst), 'tree_data.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(f"written: {dst} | people: {len(people)} | {stats}")
