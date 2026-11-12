---
name: family-tree-builder
description: "Workflow for a family history project built from this kit (family.ged + patch scripts + vault): work in new findings, certificates, photos or family stories, read parish registers and records cheaply, build the tree page and Obsidian notes, track costs, keep the Ancestry tree in sync. Triggers: 'genealogy', 'family tree', 'family history', 'ancestors', 'new certificate', 'read this parish register', 'DNA match', 'sync'. For archive knowledge and old scripts also use genealogy-research, for archive websites in the browser archive-portals and browser-harness."
---

# Family tree builder: family history research with Claude

**This is a roadmap, not a cage.** The steps here worked in a real project. If you (Claude) see a better, cheaper
or faster way, propose it with a short reason. Fixed are only the rules on evidence, privacy and asking before
expensive runs in AGENTS.md.

**New project or beginner?** Start with `GUIDE.md` in the kit: Ancestry account, collect family papers,
DNA tests (oldest generation first), write to archives, then research. Propose the next step from there.
For Poland and Czechia: `regions/poland-czechia.md` in the kit.

Works in a project folder created from the kit's `template/`. The rules are in the project's `AGENTS.md`,
this skill is the workflow. If they disagree, AGENTS.md wins.

## At the start of every session
1. Read `PROCESS.md` (current state only), `git status`, `git log --oneline -20`.
2. `python3 scripts/build_all.py`: GEDCOM 0 errors? Otherwise fix that first.
3. Does the user have an inbox note (e.g. Obsidian "Family Tree Inbox", section "Open")? Work it in too.

## Before searching or reading
1. `python3 scripts/already_read.py "<name>"` and `"<book/call no.>"`. Read the hits first.
2. Answer the five questions from `vault/Research/Coverage.md` and write them into the research note.
3. Cheapest step first: web search and indexes (FamilySearch, Geneteka, Matricula index volumes, Ancestry search),
   then an email to the responsible archive, only then reading images.
4. Estimate the cost and ask if more than 30 images or more than 3 helpers.

## Reading images (the expensive part)
In the reference project more than 70 % of the cost went into reading old handwriting. So:
1. **Sample:** 20 images. If the place or name never appears: stop and ask.
2. **Screen with `scripts/read_images.py`** (one image per fresh call, 1200 px, sonnet or haiku, emergency brake built in).
   Result TSV into `vault/Research/`. No long helper chats with 50 images.
3. If you do use helpers (sub-agents): set `model` explicitly, at most 3-4 at a time, at most 25 images each,
   each on its own book with its own result file. Write into the task: "On 'request limit' or 'media removed'
   stop at once and report, at most 2 retries."
4. Read **hits** on the full image with the strongest model and save a crop enlarged at least 3x
   (`sources/scans/<date>_<topic>/crops/`).
5. **Blind second reading** only when the reading carries a status of the direct line: the second helper gets only the image.
6. Before a big "nothing found" counts: calibration (`scripts/calibrate.py`), recall at least 90 %.
7. Update `vault/Research/Coverage.md`: book, years, images, read yes/no, result. Also when nothing was found.

## New documents, photos, voice messages from the user
1. Everything into `sources/scans/<date>_<topic>/` (photos of people into `sources/photos/`), back it up, link in `evidence_links.tsv`.
2. Many images: contact sheets or `scripts/read_images.py`, transcription by a cheap model in blocks, check the important places
   (names and dates of the direct line, conflicts) yourself on the enlarged image.
3. Read backs, stamps and margin notes too. Transcribe voice messages, record statements as family knowledge (QUAY 1).
4. Give open questions for relatives as a ready, simple message the user can forward.
5. Then continue with "Working in a finding" below.

## DNA
Raw data and match names only in `sources/private/`. Sort matches by parent side and shared matches (Leeds method).
Upload to GEDmatch and others only after the user says yes; for GEDmatch use a GEDCOM extract with direct ancestors only,
living people as "Private", without notes and images.

## Working in a finding
1. Back up the image (e.g. a private cloud drive), link in `sources/evidence_links.tsv`. Save online finds as screenshot or PDF.
2. Transcript into `vault/Documents/`.
3. Patch script: copy `scripts/patches/0001_example_baptism.py`, next number NNNN, ID range NNNN.
   Every fact with `cite(...)` (where found, verbatim excerpt, link, QUAY) and `status(...)`.
4. Test on a copy: `GED=/tmp/t.ged python3 scripts/patches/NNNN_x.py`, then `python3 scripts/rebuild.py`,
   with 0 unexplained differences `python3 scripts/rebuild.py --apply`.
5. `python3 scripts/build_all.py`, look at `reports/tree.html`.
6. Status per AGENTS.md 2 and 11. A proof file only for indirect evidence or a conflict.
7. New names into the watchlist. A changed reading into `sources/superseded-readings.tsv` and
   `python3 scripts/check_readings.py --only 1`.
8. Journal entry (`journal/YYYY-MM.md`), PROCESS.md only if the state changes. Commit.
9. Tell the user what was entered, with source and link.

## Online tree (Ancestry, MyHeritage ...)
Only in batches, at most once a month, only the direct line and only what can be proven (batch list in PROCESS.md).
Before entering: does every new person and link have a source? Guesses stay local.
Afterwards read everything back once (reload the page), not after every person.
How to click through Ancestry with browser-harness: skill `archive-portals`.

## Costs
- Every payment right away into `COSTS.md`, postage too.
- At the end of every work round `python3 scripts/claude_costs.py`, update the monthly values in COSTS.md.
- A run was unusually expensive: a line under "Most expensive runs" with the lesson, a rule in the error log if it repeats.

## "sync" (end of a work round)
Check follow-ups, `build_all.py` 0 errors, `rebuild.py` 0 differences, measure costs, keep PROCESS.md short
(done items out, into the journal), commit, tell the user in a few lines: found, open, next step.

## Sharing the tree page
`reports/tree.html` is a single file. Before sharing: living people only with the birth year, no documents of living people.
If you use Claude artifacts, you can publish the file as a private artifact; check it locally in a browser for errors first.
