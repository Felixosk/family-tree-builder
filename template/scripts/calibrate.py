#!/usr/bin/env python3
"""Calibration: how reliably does the screening (scripts/read_images.py) find known hits?

1. Pick 20 images where you know for sure whether a searched name appears.
2. File expected.tsv with columns: image, hit (yes/no)
3. Screen the same images with read_images.py -> actual.tsv
4. python3 scripts/calibrate.py expected.tsv actual.tsv

Below 90 % recall, a "nothing found" from this screening does not count as "not there"
(then use a bigger model, higher resolution or a narrower question).
"""
import csv, sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
exp = {r['image']: r['hit'].strip().lower() for r in csv.DictReader(open(sys.argv[1], encoding='utf-8'), delimiter='\t')}
act = {r['image']: r['hit'].strip().lower() for r in csv.DictReader(open(sys.argv[2], encoding='utf-8'), delimiter='\t')}
common = [b for b in exp if b in act]
real = [b for b in common if exp[b] == 'yes']
found = [b for b in real if act[b] in ('yes', 'unsure')]
false_alarms = [b for b in common if exp[b] == 'no' and act[b] == 'yes']
recall = len(found) / len(real) if real else 0
print(f'Images compared: {len(common)} | real hits: {len(real)} | found: {len(found)} | recall: {recall:.0%}')
print(f'False alarms: {len(false_alarms)}')
for b in real:
    if b not in found:
        print('  missed:', b)
print('OK, "nothing found" from this screening is usable.' if recall >= 0.9 else 'TOO UNRELIABLE: "nothing found" from this screening does not count.')
sys.exit(0 if recall >= 0.9 else 1)
