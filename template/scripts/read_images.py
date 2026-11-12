#!/usr/bin/env python3
"""Screening (stage 1): reads images ONE BY ONE, each in a fresh Claude call without history,
and writes one line per image to a TSV file. With an emergency brake.

Why: in a long helper chat, every image already read is billed again on every later step.
One image per call costs only that one image.

Usage:
  python3 scripts/read_images.py <image_folder> <result.tsv> [--model sonnet] [--max 25] [--px 1200]
                                 [--question "Find baptisms with the watchlist names"] [--dry]

- Names come from vault/Research/Watchlist.md (table columns 1 and 2).
- Resumable: images already in result.tsv are skipped.
- Emergency brake: stops after --max images per run (default 25), after 2 errors in a row,
  and at once on "request limit", "rate limit", "media removed", "usage limit" or "not logged in".
- Downsizes with `sips` (Mac) or Pillow to --px on the long edge, copy in /tmp, original untouched.
- Needs Claude Code in the terminal (`claude`, logged in). --dry only shows what would happen.

Afterwards: read the hits (column hit=yes) with the strongest model on the full image and save a crop.
"""
import argparse, csv, glob, os, re, shutil, subprocess, tempfile

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAKE = re.compile(r'request limit|rate.?limit|media removed|usage limit|overloaded|not logged in', re.I)

a = argparse.ArgumentParser()
a.add_argument('folder'); a.add_argument('result')
a.add_argument('--model', default='sonnet'); a.add_argument('--max', type=int, default=25)
a.add_argument('--px', type=int, default=1200)
a.add_argument('--question', default='Which entries contain one of the names searched for?')
a.add_argument('--dry', action='store_true')
x = a.parse_args()


def names():
    f = os.path.join(P, 'vault', 'Research', 'Watchlist.md')
    out = []
    if os.path.exists(f):
        for l in open(f, encoding='utf-8'):
            z = [c.strip(' *') for c in l.strip().strip('|').split('|')]
            if len(z) >= 2 and z[0] and not z[0].startswith(('Name', '---', '-')):
                out.append(z[0] + (' (' + z[1] + ')' if z[1] else ''))
    return out


def shrink(src, dst):
    if shutil.which('sips'):
        subprocess.run(['sips', '-Z', str(x.px), src, '--out', dst], capture_output=True)
        if os.path.exists(dst):
            return dst
    try:
        from PIL import Image
        im = Image.open(src); im.thumbnail((x.px, x.px)); im.convert('RGB').save(dst, 'JPEG', quality=85)
        return dst
    except Exception:
        return src


images = sorted(f for f in glob.glob(os.path.join(x.folder, '*')) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')))
done = set()
if os.path.exists(x.result):
    done = {r['image'] for r in csv.DictReader(open(x.result, encoding='utf-8'), delimiter='\t')}
todo = [b for b in images if os.path.basename(b) not in done]
watch = names()
print(f'{len(images)} images, {len(done)} already read, {len(todo)} open, this run max {x.max}. Names: {len(watch)}')
if not watch:
    print('Note: watchlist empty, searching only by the question.')

new_file = not os.path.exists(x.result)
out = open(x.result, 'a', encoding='utf-8', newline='')
w = csv.writer(out, delimiter='\t')
if new_file:
    w.writerow(['image', 'hit', 'year', 'kind', 'summary'])
tmp = tempfile.mkdtemp(prefix='read_')
errors_in_row = 0
for n, b in enumerate(todo[:x.max], 1):
    k = shrink(b, os.path.join(tmp, os.path.splitext(os.path.basename(b))[0] + '.jpg'))
    prompt = (f'Read the image {k} (old handwriting, parish register or record). Names searched for, in all spellings: '
              f'{"; ".join(watch) or "no list"}. Question: {x.question} '
              'Answer in EXACTLY ONE line, fields separated by " | ": hit (yes/no/unsure) | year(s) on the page | '
              'kind (baptisms/marriages/burials/land register/other) | if hit: entry number, name as written, parents or spouse; '
              'otherwise "no hit". Invent nothing. Mark illegible parts as [?].')
    cmd = ['claude', '-p', prompt, '--model', x.model, '--allowedTools', 'Read', '--output-format', 'text']
    if x.dry:
        print('DRY', os.path.basename(b), '->', ' '.join(cmd[:2]), '...')
        continue
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        text = (r.stdout or '') + (r.stderr or '')
    except Exception as e:
        r, text = None, str(e)
    if BRAKE.search(text):
        print(f'EMERGENCY BRAKE at {os.path.basename(b)}: {text.strip()[:200]}')
        break
    line = next((l for l in (r.stdout if r else '').splitlines() if '|' in l), '')
    if not line:
        errors_in_row += 1
        print(f'Error at {os.path.basename(b)} ({errors_in_row}/2): {text.strip()[:150]}')
        if errors_in_row >= 2:
            print('EMERGENCY BRAKE: 2 errors in a row'); break
        continue
    errors_in_row = 0
    f = [s.strip() for s in line.split('|')] + ['', '', '', '']
    w.writerow([os.path.basename(b), f[0].lower(), f[1], f[2], ' | '.join(f[3:]).strip(' |')]); out.flush()
    print(f'{n:3d} {os.path.basename(b)}: {f[0]}')
out.close()
print(f'Result: {x.result}. Add the coverage to vault/Research/Coverage.md.')
