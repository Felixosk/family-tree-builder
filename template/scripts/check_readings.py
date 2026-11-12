#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks family.ged and the project files for the kinds of mistakes that caused corrections
in a real project. See AGENTS.md section 9.

  1 Superseded readings that are still standing somewhere (correction propagation).
  2 Uncertain readings without a saved enlarged crop.
  3 Media links pointing to missing files.
  4 Single documents under sources/scans/ that are not in the media index.
  5 GEDCOM lines over 254 bytes.
  6 Back-propagation: journal entries about a proof (P01, P02 ...) newer than the proof file.
  7 PROCESS.md "Updated:" date older than the newest journal entry.

Usage: python3 scripts/check_readings.py [--only 1,2,3]
Exit code 1 if an ERROR is open, so the script can gate the workflow.
"""
import csv, glob, io, os, re, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GED = os.environ.get("GED") or os.path.join(P, "family.ged")
SUPERSEDED = os.path.join(P, "sources", "superseded-readings.tsv")
MEDIA = os.path.join(P, "sources", "media.tsv")

# Folders with bulk material (whole film reels) that are deliberately not indexed image by image.
# Example: BULK = ("sources/scans/parish-sampletown-1780/",)
BULK = ()
IMAGE = (".jpg", ".jpeg", ".png", ".pdf", ".tif", ".tiff")

only = None
for a in sys.argv[1:]:
    if a.startswith("--only"):
        only = set(int(x) for x in (a.split("=", 1)[1] if "=" in a else sys.argv[sys.argv.index(a) + 1]).split(","))

findings = []


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


ged = read(GED)
gedlines = ged.split("\n")


def record_of(idx):
    """XREF of the record that line idx belongs to."""
    for i in range(idx, -1, -1):
        m = re.match(r"^0 (@\w+@)", gedlines[i])
        if m:
            return m.group(1)
    return "?"


def fulltext(xref):
    """Record as one string, CONC/CONT joined."""
    try:
        s = next(i for i, l in enumerate(gedlines) if l.startswith("0 " + xref + " "))
    except StopIteration:
        return ""
    e = s + 1
    while e < len(gedlines) and not gedlines[e].startswith("0 "):
        e += 1
    out = []
    for l in gedlines[s:e]:
        m = re.match(r"^\d+ (CONC|CONT) (.*)$", l)
        out.append(m.group(2) if m else re.sub(r"^\d+ \w+ ?", "", l))
    return " ".join(out)


# ---------------------------------------------------------------- 1 Superseded readings
def check_1():
    if not os.path.exists(SUPERSEDED):
        findings.append(("NOTE", SUPERSEDED, "File missing: superseded readings cannot be checked."))
        return
    with io.open(SUPERSEDED, encoding="utf-8") as f:
        entries = [r for r in csv.DictReader(f, delimiter="\t") if r.get("old", "").strip()]
    # sources/base/ holds dated snapshots that are meant to show the old state.
    skip = (os.path.join(P, "sources", "base"), os.path.join(P, ".git"), os.path.join(P, "tmp"), os.path.join(P, "archive"))
    files = []
    for root, dirs, fs in os.walk(P):
        if any(root.startswith(a) for a in skip):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in (".git", "tmp", "archive")]
        for fn in fs:
            if "Audit " in fn:
                continue
            if fn.endswith((".md", ".ged", ".tsv")):
                files.append(os.path.join(root, fn))
    for e in entries:
        old, new, date = e["old"].strip(), e.get("new", "").strip(), e.get("date", "").strip()
        for d in files:
            if os.path.abspath(d) == os.path.abspath(SUPERSEDED):
                continue
            try:
                t = read(d)
            except Exception:
                continue
            if old not in t:
                continue
            # Allowed if the new reading or a dated correction note stands nearby.
            new_core = re.sub(r"\s*\([^)]*\)\s*$", "", new).strip()
            for hit in re.finditer(re.escape(old), t):
                around = t[max(0, hit.start() - 700):hit.end() + 700]
                ok = (new_core and new_core in around) or re.search(
                    r"[Cc]orrect|[Ss]uperseded|[Aa]ddendum|[Mm]isread|wrong reading|[Rr]evised|no longer|removed", around)
                if not ok:
                    line = t[:hit.start()].count("\n") + 1
                    findings.append(("ERROR", "%s:%d" % (os.path.relpath(d, P), line),
                                     "Superseded reading '%s' stands without a correction note (correct since %s: '%s')." % (old, date, new)))
                    break


# ---------------------------------------------------------------- 2 Uncertain readings
UNCERTAIN = re.compile(r"\[[^\]\n]{1,40}\?\]|\?\]|reading uncertain|uncertain reading|spelling uncertain")

def check_2():
    """Only INDI and FAM: there an uncertain reading stands for an adopted value.
    In OBJE and SOUR, bracket marks are honest transcription marks, not a defect."""
    seen = set()
    for i, l in enumerate(gedlines):
        if not UNCERTAIN.search(l):
            continue
        x = record_of(i)
        if not re.match(r"@[IF]\w", x) or x in seen:
            continue
        seen.add(x)
        t = fulltext(x)
        if re.search(r"crops/|enlarg|image not available|no image|transcript only|original not seen", t, re.I):
            continue
        findings.append(("CHECK", x, "Uncertain reading without a note about an enlarged crop."))


# ---------------------------------------------------------------- 3 Missing media files
def check_3():
    for m in re.finditer(r"^\d+ FILE (.+)$", ged, re.M):
        rel = m.group(1).strip()
        if not os.path.exists(os.path.join(P, rel)):
            findings.append(("ERROR", rel, "FILE link points to a file that does not exist."))


# ---------------------------------------------------------------- 4 Scans without media index
def check_4():
    indexed = set()
    if os.path.exists(MEDIA):
        with io.open(MEDIA, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                indexed.add(r["file"].strip())
    for root, dirs, fs in os.walk(os.path.join(P, "sources", "scans")):
        for fn in fs:
            rel = os.path.relpath(os.path.join(root, fn), P)
            if not fn.lower().endswith(IMAGE) or rel in indexed or rel.startswith(BULK):
                continue
            findings.append(("CHECK", rel, "Single document without a line in sources/media.tsv."))


# ---------------------------------------------------------------- 5 Line length
def check_5():
    long_ = [(i + 1, len(l.encode("utf-8"))) for i, l in enumerate(gedlines) if len(l.encode("utf-8")) > 254]
    if long_:
        findings.append(("ERROR", "family.ged",
                         "%d lines over 254 bytes (GEDCOM 5.5.1). First: line %d with %d bytes. Fix with scripts/wrap_lines.py."
                         % (len(long_), long_[0][0], long_[0][1])))


def _dates(text):
    for m in re.finditer(r"(\d{4})-(\d{2})-(\d{2})", text):
        yield (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _journal_sections():
    out = []
    for f in glob.glob(os.path.join(P, "journal", "*.md")):
        for part in re.split(r"\n#{2,3} (?=\d{4}-\d{2}-\d{2})", read(f)):
            d = re.match(r"(\d{4})-(\d{2})-(\d{2})", part)
            if d:
                out.append((tuple(int(x) for x in d.groups()), part))
    return out


def check_6():
    """Back-propagation: journal mentions a proof after the proof file's newest date."""
    pdir = os.path.join(P, "vault", "Research", "Proofs")
    if not os.path.isdir(pdir):
        return
    sections = _journal_sections()
    for fn in sorted(os.listdir(pdir)):
        m = re.match(r"(P\d{2})[ _-]", fn)
        if not m or m.group(1) == "P00":
            continue
        code = m.group(1)
        latest = max((d for d, part in sections if re.search(r"\b%s\b" % code, part)), default=None)
        if not latest:
            continue
        pmax = max(_dates(read(os.path.join(pdir, fn))), default=None)
        if pmax is None or pmax < latest:
            findings.append(("CHECK", "Proofs/" + fn[:28],
                             "Journal mentions %s on %04d-%02d-%02d, the file has no date from that day on. Update it (AGENTS.md 9.5)." % (code, *latest)))


def check_7():
    """PROCESS.md: the 'Updated:' date must not lag behind the newest journal entry."""
    proc = os.path.join(P, "PROCESS.md")
    if not os.path.exists(proc):
        return
    m = re.search(r"^Updated: (\d{4})-(\d{2})-(\d{2})", read(proc), re.M)
    heads = [d for d, _ in _journal_sections()]
    if m and heads:
        upd = tuple(int(x) for x in m.groups())
        if max(heads) > upd:
            findings.append(("NOTE", "PROCESS.md", "Updated %04d-%02d-%02d, newest journal entry %04d-%02d-%02d. Refresh PROCESS.md." % (*upd, *max(heads))))


CHECKS = {1: check_1, 2: check_2, 3: check_3, 4: check_4, 5: check_5, 6: check_6, 7: check_7}
for n, fn in sorted(CHECKS.items()):
    if only is None or n in only:
        fn()

if not findings:
    print("No findings.")
    sys.exit(0)

rank = {"ERROR": 0, "CHECK": 1, "NOTE": 2}
for kind, where, text in sorted(findings, key=lambda b: rank[b[0]]):
    print("%-6s %-46s %s" % (kind, where, text))
print("\n%d findings (%d errors)." % (len(findings), sum(1 for b in findings if b[0] == "ERROR")))
sys.exit(1 if any(b[0] == "ERROR" for b in findings) else 0)
