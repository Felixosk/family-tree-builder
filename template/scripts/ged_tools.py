"""Small helpers for patch scripts. A patch never edits family.ged by hand. It is always a script
that can be tested on a copy and replayed later.

Ground rules (see template/AGENTS.md section 4):
- Every script has its OWN, FIXED ID range (e.g. 0012 -> @I0012001@, @F0012001@, @S0012001@).
  Never "find the next free ID": then the result depends on the order, and the rebuild creates
  duplicate IDs as soon as a script runs earlier or later.
- Every script is idempotent: run it twice and the second run does nothing.
- The path comes from the GED environment variable, so you can test on a copy.
"""
import os, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GED = os.environ.get('GED') or os.path.join(P, 'family.ged')


class Ged:
    def __init__(self, path=GED):
        self.path = path
        raw = open(path, encoding='utf-8').read()
        self.nl = '\r\n' if '\r\n' in raw else '\n'
        self.L = raw.replace('\r\n', '\n').split('\n')
        while self.L and self.L[-1] == '':
            self.L.pop()
        assert self.L[-1] == '0 TRLR', 'family.ged does not end with 0 TRLR'

    def has(self, xref):
        return any(l.startswith(f'0 {xref} ') for l in self.L)

    def already_done(self, xref):
        """Idempotency check at the top of a script."""
        if self.has(xref):
            print(f'{os.path.basename(sys.argv[0])}: already applied ({xref}), nothing to do')
            sys.exit(0)

    def _end(self, xref):
        i = next(k for k, l in enumerate(self.L) if l.startswith(f'0 {xref} '))
        return next(k for k in range(i + 1, len(self.L)) if self.L[k].startswith('0 '))

    def add(self, lines):
        """Append new records before 0 TRLR. IDs must be free."""
        for l in lines:
            if l.startswith('0 @'):
                x = l.split()[1]
                if self.has(x):
                    sys.exit(f'ABORT: {x} already exists. Check this script\'s ID range.')
        self.L[-1:-1] = lines

    def append_to(self, xref, lines):
        """Append lines to the end of an existing record (e.g. NOTE, SOUR, FAMS, CHIL, an event)."""
        k = self._end(xref)
        self.L[k:k] = lines

    def save(self, dry=False):
        if dry or '--dry' in sys.argv:
            print('dry run, nothing written')
            return
        open(self.path, 'w', encoding='utf-8').write(self.nl.join(self.L) + self.nl)
        print(f'{os.path.basename(sys.argv[0])}: applied')


def cite(sid, page, quay):
    """SOUR citation under a fact (level 2). page = where found + verbatim excerpt + link to the saved image.
    QUAY: 3 original image read, 2 transcript/index/secondary, 1 family story or someone else's tree, 0 unreliable."""
    assert str(quay) in '0123', 'QUAY is 0, 1, 2 or 3'
    return [f'2 SOUR {sid}', f'3 PAGE {page.replace("@", "@@")}', f'3 QUAY {quay}']


def status(level, text):
    """Status note on a person or family. level: Proven, Probable, Possible, Unresolved, Disproven."""
    assert level in ('Proven', 'Probable', 'Possible', 'Unresolved', 'Disproven')
    return [f'1 NOTE Status: {level}. {text}'.replace('@', '@@')]
