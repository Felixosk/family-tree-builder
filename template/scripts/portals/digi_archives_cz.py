#!/usr/bin/env python3
"""Tool for the digital archive of the Zemský archiv v Opavě (digi.archives.cz): save whole books.
Built in 2026 in a real project (land registers, parish registers, the provincial land table).

How it works:
- digi.archives.cz has bot protection (Radware). Which image belongs to page N is only revealed by the
  web page itself, and slowly (server about 2-3 s per page). Direct fetch() calls trigger the block.
- So `browse` turns the pages in the user's Chrome tab (in the background, via browser-harness) by clicking
  the next button of the single-image viewer, and writes the image paths to a JSON file (about 10 s per page).
- The images themselves are Zoomify tiles on images.archives.cz. That server is open, without a block.
  `download` stitches the pages together in full resolution. With a saved path file this works again
  any time later, without Chrome.

Steps:
1. The user opens the book in Chrome and solves the check (viewer "single image", page 1 visible).
2. python3 scripts/portals/digi_archives_cz.py browse <TAB_ID> <paths.json> [until_page]
   (TAB_ID from browser-harness list_tabs(); resumable, stops on a block)
3. python3 scripts/portals/digi_archives_cz.py download <paths.json> <target_folder> [prefix]
   (runs in parallel, waits for new paths while browse is running)
Path files stay in sources/paths/ (in git), so nobody has to turn the pages of the same book twice.

Rules: only ONE tab, never fetch() on /da/..., never activate_tab(). On a block: the user solves the check, then restart.
"""
import io, json, math, os, re, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

# ---------- Tiles (images.archives.cz, open) ----------
def _get(u):
    # Server "inventare" (land table) needs the session cookie from Chrome (file in DIGI_COOKIE_FILE) and blocks on speed (429): load slowly
    ck = open(os.environ['DIGI_COOKIE_FILE']).read().strip() if os.environ.get('DIGI_COOKIE_FILE') else ''
    time.sleep(float(os.environ.get('DIGI_TILE_PAUSE', '0')))
    for i in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers={'Cookie': ck, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'Referer': 'https://digi.archives.cz/'}), timeout=60).read()
        except Exception:
            time.sleep(2)
    raise RuntimeError('Download failed: ' + u)


def _try(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'Referer': 'https://digi.archives.cz/'}), timeout=60).read()
    except Exception:
        return None

def _tile(base, L, x, y, groups=range(0, 8)):
    for g in groups:
        d = _try(f'{base}/TileGroup{g}/{L}-{x}-{y}.jpg')
        if d: return d
    return None

def _dims_probe(base):
    """Read image size from the Zoomify tiles (when ImageProperties.xml is missing)."""
    from PIL import Image
    L = 0
    while _tile(base, L + 1, 0, 0): L += 1
    tx = 1
    while _tile(base, L, tx, 0): tx += 1
    ty = 1
    while _tile(base, L, 0, ty): ty += 1
    lw = Image.open(io.BytesIO(_tile(base, L, tx - 1, 0))).size[0]
    lh = Image.open(io.BytesIO(_tile(base, L, 0, ty - 1))).size[1]
    return (tx - 1) * 256 + lw, (ty - 1) * 256 + lh

def zoomify(base, out, dims=None):
    """Stitches a Zoomify image together in full resolution."""
    from PIL import Image
    try:
        p = _get(base + '/ImageProperties.xml').decode()
        W = int(re.search(r'WIDTH="(\d+)"', p).group(1)); H = int(re.search(r'HEIGHT="(\d+)"', p).group(1))
        T = int(re.search(r'TILESIZE="(\d+)"', p).group(1))
    except Exception:
        W, H = dims if dims else _dims_probe(base); T = 256   # server "inventare" (land table): no ImageProperties.xml, size from the tiles
    sizes = [(W, H)]
    while sizes[-1][0] > T or sizes[-1][1] > T:
        w, h = sizes[-1]; sizes.append((math.ceil(w / 2), math.ceil(h / 2)))
    sizes.reverse()
    L = len(sizes) - 1
    tiles = [(math.ceil(w / T), math.ceil(h / T)) for w, h in sizes]
    before = sum(tx * ty for tx, ty in tiles[:L])
    tx, ty = tiles[L]
    img = Image.new('RGB', sizes[L])
    for y in range(ty):
        for x in range(tx):
            g = (before + y * tx + x) // 256
            img.paste(Image.open(io.BytesIO(_get(f'{base}/TileGroup{g}/{L}-{x}-{y}.jpg'))), (x * T, y * T))
    img.save(out, quality=90)

def download(paths, target, prefix='b'):
    os.makedirs(target, exist_ok=True)
    def one(k, u):
        f = os.path.join(target, f'{prefix}_{int(k):03d}.jpg')
        try:
            zoomify(u, f + '.tmp.jpg', (json.load(open(paths+'.dims')) if os.path.exists(paths+'.dims') else {}).get(str(k))); os.rename(f + '.tmp.jpg', f); print('ok', k, flush=True)
        except Exception as e:
            print('error', k, e, flush=True)
    idle = 0
    while idle < 90:
        m = json.load(open(paths))
        todo = [k for k in sorted(m, key=int) if not os.path.exists(os.path.join(target, f'{prefix}_{int(k):03d}.jpg'))]
        if not todo:
            idle += 1; time.sleep(10); continue
        idle = 0
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(lambda k: one(k, m[k]), todo))

# ---------- Page turning (in the user's Chrome, via browser-harness) ----------
BROWSE = r'''
import json,time,os
P=%(paths)r; TAB=%(tab)r; UNTIL=%(until)d
m=json.load(open(P)) if os.path.exists(P) else {}
def cur():
    # read the image path from the HTML, not from drawn tiles: with a locked screen Chrome draws nothing
    return json.loads(js("""(()=>{const B='https://images.archives.cz/ximage/';const s=[...new Set(document.documentElement.outerHTML.split(B).slice(1).map(x=>B+x.split('.jpg')[0]+'.jpg'))];
const b=document.querySelector('#nextSingleImage');const r=b?b.getBoundingClientRect():null;
const mm=document.documentElement.outerHTML.match(/IMAGE_PROPERTIES WIDTH='(\\d+)' HEIGHT='(\\d+)'/);
return JSON.stringify({s,r:r?[r.x+r.width/2,r.y+r.height/2]:null,d:mm?[+mm[1],+mm[2]]:null})})()"""))
switch_tab(TAB)
n=max([int(k) for k in m] or [0])
s0=cur()['s']
if s0 and s0[0] not in m.values():
    n+=1; m[str(n)]=s0[0]; json.dump(m,open(P,'w'),indent=0); print(n,flush=True)
while n<UNTIL:
    if 'perfdrive' in page_info()['url']:
        print('BLOCKED at',n,flush=True); break
    # session 40 min: 2 min before it ends the page shows "extend session", click the button normally
    ka=json.loads(js("""(()=>{const b=document.getElementById('sessionKeepAliveButton');if(!b||!b.offsetParent)return 'null';const q=b.getBoundingClientRect();return JSON.stringify([q.x+q.width/2,q.y+q.height/2])})()"""))
    if ka: click_at_xy(*ka); print('session extended at',n,flush=True); time.sleep(4)
    st=cur(); before=st['s']
    if not st['r']: print('no next button at',n,flush=True); break
    click_at_xy(*st['r'])
    fresh=None
    for k in range(20):
        time.sleep(1.5)
        fresh=[x for x in cur()['s'] if x not in before]
        if fresh: break
    if not fresh: print('no new page after',n,flush=True); break
    # after a session restart the viewer may stand before the last page: skip known pages
    if fresh[0] in m.values(): print('known, next',flush=True); time.sleep(1.5); continue
    n+=1; m[str(n)]=fresh[0]; json.dump(m,open(P,'w'),indent=0); print(n,flush=True)
    dd=json.load(open(P+'.dims')) if os.path.exists(P+'.dims') else {}
    dd[str(n)]=cur()['d']; json.dump(dd,open(P+'.dims','w'))
    time.sleep(1.5)
print('END',n,flush=True)
'''

def browse(tab, paths, until=9999):
    """Restarts browser-harness when the connection drops (e.g. a clean-up job)."""
    code = BROWSE % {'paths': os.path.abspath(paths), 'tab': tab, 'until': until}
    for attempt in range(6):
        out = subprocess.run(['browser-harness'], input=code, capture_output=True, text=True).stdout
        print(out, end='', flush=True)
        # block, end of book (no next button) or target reached: done; otherwise (timeout, crash) restart
        if 'BLOCKED' in out or 'no next button' in out or f'END {until}' in out:
            return
        time.sleep(20)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['browse']:
        browse(a[1], a[2], int(a[3]) if len(a) > 3 else 9999)
    elif a[:1] == ['download']:
        download(a[1], a[2], a[3] if len(a) > 3 else 'b')
    else:
        print(__doc__)
