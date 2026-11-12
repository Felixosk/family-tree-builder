#!/usr/bin/env python3
"""What did the research cost in Claude compute? Reads the local Claude Code logs
(~/.claude/projects/*/*.jsonl, sub-agents included) and prices them at API list price in USD.
On a subscription you do not pay this amount, but the number shows which work is expensive.

A session counts as research if its tool calls touch this project folder
(or contain a keyword from project.json -> "cost_keywords").

Usage: python3 scripts/claude_costs.py [--since 2026-01-01] [--top 10]
Note: Claude Code deletes old logs after a while. Keep months you already measured in COSTS.md
and do not correct them downwards.

Adjust PRICES below to the current price list if needed (USD per million tokens:
input, output, cache read). Cache write = 1.25x (5 min) or 2x (1 h) input.
"""
import collections, datetime, glob, json, os, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(P, 'project.json'), encoding='utf-8'))
KEYWORDS = [os.path.basename(P), 'family.ged'] + CFG.get('cost_keywords', [])
PRICES = {'opus': (5, 25, 0.50), 'sonnet': (3, 15, 0.30), 'haiku': (1, 5, 0.10), 'fable': (10, 50, 1.00)}


def price(model):
    for k, v in PRICES.items():
        if k in (model or ''):
            return v
    return PRICES['opus']


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


since = datetime.datetime.fromisoformat(arg('--since', '2000-01-01')).timestamp()


def hits(path):
    return sum(1 for line in open(path, errors='ignore') if '"tool_use"' in line and any(k in line for k in KEYWORDS))


def cost(path, seen):
    usd, per_model, first = 0.0, collections.Counter(), None
    for line in open(path, errors='ignore'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        first = first or d.get('timestamp')
        if d.get('type') != 'assistant':
            continue
        m = d.get('message') or {}
        u, mid = m.get('usage'), m.get('id') or d.get('requestId')
        if not u or mid in seen:
            continue
        seen.add(mid)
        i, o, r = price(m.get('model'))
        cc = u.get('cache_creation') or {}
        c5, c1 = cc.get('ephemeral_5m_input_tokens'), cc.get('ephemeral_1h_input_tokens')
        if c5 is None and c1 is None:
            c5, c1 = u.get('cache_creation_input_tokens', 0) or 0, 0
        x = (u.get('input_tokens', 0) * i + u.get('output_tokens', 0) * o + (u.get('cache_read_input_tokens', 0) or 0) * r
             + (c5 or 0) * i * 1.25 + (c1 or 0) * i * 2) / 1e6
        usd += x
        model = m.get('model') or '?'
        per_model[model.split('-')[1] if '-' in model else '?'] += x
    return usd, per_model, first


rows, months, models = [], collections.Counter(), collections.Counter()
for f in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl')):
    if os.path.getmtime(f) < since:
        continue
    sid = os.path.basename(f)[:-6]
    helpers = glob.glob(os.path.join(os.path.dirname(f), sid, 'subagents', '*.jsonl'))
    if hits(f) + sum(hits(h) for h in helpers) < 3:
        continue
    seen, usd, pm, first = set(), 0.0, collections.Counter(), None
    for g in [f] + helpers:
        a, b, e = cost(g, seen)
        usd += a; pm += b; first = first or e
    rows.append((usd, (first or '')[:10], sid, len(helpers)))
    months[(first or '????-??')[:7]] += usd
    models += pm

print(f'Sessions: {len(rows)} | total: {sum(r[0] for r in rows):.2f} USD (API list price)')
for k, v in sorted(months.items()):
    print(f'  {k}: {v:.2f} USD')
print('By model: ' + ' | '.join(f'{k} {v:.2f}' for k, v in models.most_common()))
print('Most expensive sessions:')
for usd, day, sid, nh in sorted(rows, reverse=True)[:int(arg('--top', '5'))]:
    print(f'  {usd:8.2f} USD  {day}  {sid[:8]}  ({nh} helpers)')
