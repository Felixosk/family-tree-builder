#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wraps overlong GEDCOM lines with CONC (GEDCOM 5.5.1 allows at most 255 bytes per line).

Run it once after every fresh Ancestry export. After that, scripts/check_readings.py reports
every new overlong line as an ERROR; this script is the fix.

Content stays the same: before writing, the logical values (CONC appended, CONT as a line break)
are compared before and after. If they differ, nothing is written. Cuts are made by byte, but never
inside a UTF-8 character.

    python3 scripts/wrap_lines.py [--check]

--check only reports what would be done and writes nothing.
"""
import os
import re
import sys

LIMIT = 254
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GED = os.environ.get("GED") or os.path.join(P, "family.ged")


def unfold(lines):
    """Logical values: CONC appends directly, CONT starts a new line."""
    out = []
    for l in lines:
        m = re.match(r"^(\d+) (CONC|CONT)(?: (.*))?$", l)
        if m and out:
            out[-1] += ("" if m.group(2) == "CONC" else "\n") + (m.group(3) or "")
        else:
            out.append(l)
    return out


def wrap(lines):
    new = []
    for l in lines:
        if len(l.encode("utf-8")) <= LIMIT:
            new.append(l)
            continue
        m = re.match(r"^(\d+) (\S+)(?: (.*))?$", l)
        if not m:
            new.append(l)
            continue
        lvl, tag, val = int(m.group(1)), m.group(2), (m.group(3) or "")
        # A CONC continuation stays on its level, everything else goes one level deeper.
        head_first = ("%d %s " % (lvl, tag)).encode("utf-8")
        head_next = ("%d CONC " % (lvl if tag == "CONC" else lvl + 1)).encode("utf-8")
        rest, first = val.encode("utf-8"), True
        while rest:
            head = head_first if first else head_next
            piece = rest[:LIMIT - len(head)]
            while piece and len(piece) < len(rest) and (rest[len(piece)] & 0xC0) == 0x80:
                piece = piece[:-1]
            new.append((head + piece).decode("utf-8"))
            rest, first = rest[len(piece):], False
    return new


def main():
    check_only = "--check" in sys.argv
    with open(GED, encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    long_ = [i + 1 for i, l in enumerate(lines) if len(l.encode("utf-8")) > LIMIT]
    if not long_:
        print("No line over %d bytes." % LIMIT)
        return 0
    print("%d lines over %d bytes, first at line %d." % (len(long_), LIMIT, long_[0]))
    if check_only:
        return 1
    new = wrap(lines)
    if unfold(lines) != unfold(new):
        print("ABORT: content would have changed. Nothing written.")
        return 2
    left = [l for l in new if len(l.encode("utf-8")) > LIMIT]
    if left:
        print("ABORT: %d lines stayed too long. Nothing written." % len(left))
        return 2
    with open(GED, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(new))
    print("Wrapped. Lines: %d -> %d, content unchanged." % (len(lines), len(new)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
