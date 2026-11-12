#!/usr/bin/env python3
"""EXAMPLE patch (sample family, fictional). Template for your own patches: copy this file,
give it the next number, adapt the text, then delete the example.

Finding: baptism of John Sample in the Sampletown baptism register 1910-1930, image 112, no. 14/1925.
Usage: GED=/tmp/test.ged python3 scripts/patches/0001_example_baptism.py [--dry]

ID range of this script: 0001 (so @S0001001@, @I0001001@ and so on). Never "the next free ID".
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ged_tools import Ged, cite, status

g = Ged()
g.already_done('@S0001001@')

# 1. The source as its own record: archive, collection, call number, image, path or link to the saved image
g.add([
    '0 @S0001001@ SOUR',
    '1 TITL Catholic parish of Sampletown, baptism register 1910-1930 (Sample Archive, call no. PR 3)',
    '1 TEXT Image 112, no. 14/1925. Saved: sources/scans/2026-01-05_baptisms-sampletown/image112.jpg',
])

# 2. The fact on the person, with the citation directly on the fact (the person record alone is not enough)
g.append_to('@I3@', [
    '1 CHR',
    '2 DATE 4 MAR 1925',
    '2 PLAC Sampletown',
    *cite('@S0001001@', 'Image 112, no. 14: "John, legitimate son of the farmer Joseph Sample and Anna nee Example" '
          '(read on a 3x enlarged crop, blind second reading)', 3),
    *status('Probable', 'Baptism read on the original. Parents match the 1924 marriage; a second record type (land register) is still missing.'),
])

g.save()
