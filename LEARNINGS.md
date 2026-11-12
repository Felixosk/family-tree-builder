# Learnings: what was expensive, what was fast, how to save

The basis is a real project: eight weeks of family history research with Claude Code (September to November 2026),
380 people in the tree, 93 of them proven on the original, main line back to the 17th century. On top of that come the
lessons from an earlier project the rules were first built on. At the end a second model (Claude Fable) reviewed the
whole project. Family names and places are removed.

## The numbers

| Item | Amount |
|---|---|
| Claude, measured from the logs, at API list price | about 2,800 USD (paid through a subscription; the number shows where the work went) |
| Fees, postage, copies, DNA tests, subscription, one archive trip | about 800 EUR (about 430 EUR of it the trip) |

Where the Claude money went:

| Area | Share |
|---|---|
| Reading old handwriting (parish registers, land registers, civil records) | over 70 % |
| Maintaining the online tree (entering people, sources, images) | 14 % |
| Transcribing family papers (photos, family folder) | 7 % |
| Tree page, Obsidian, GEDCOM file, check scripts | 7 % |
| Emails and requests to offices | 2 % |

By model: Sonnet 65 %, Opus 18 %. So the expensive model was not the problem.

## 1. What was expensive (and avoidable)

**A helper loop for 695 USD.** Several reading helpers got many images at the same time. The service answered
"request limit", and the helpers retried thousands of times. A quarter of all costs on one day.
Fix: an emergency brake (at most 25 images per helper, at most 2 retries, stop at once on "request limit").
`scripts/read_images.py` has it built in. A rule written only into the task text was not enough.

**43 cents per image instead of a few cents.** A land register with 748 pages cost 319 USD. The reason was not the model
but the method: one helper read 50 images in one chat, and every image already read was billed again on every later step.
Two helpers got stuck completely.
Fix: one image per fresh call, downsized to 1200 px, result as one line in a file (`scripts/read_images.py`).
Only the hits are read by the strong model on the full image. Estimated saving: 60 to 80 % of the reading cost.

**Reading books that could never answer the question.** 270 images of marriages from a town parish where the village
never appears in 60 years, and from a certain year on the right books had already been read. A nobility register that
only holds nobility business. Both times it only stopped when the user asked.
Fix: five questions before every book (in `template/vault/Research/Coverage.md`) and a sample of 20 images.

**Duplicate searches.** Several times a search was suggested or done that was already finished. The status file
`PROCESS.md` had grown to 215 KB, the "current state" at the top alone to 70 KB. Every session had to read it (which costs
money at every start) and still did not find the state in it.
Fix: `PROCESS.md` below about 150 lines, the diary in `journal/`, everything read in `Coverage.md`,
`scripts/already_read.py` before every search.

**Maintaining the online tree: 14 %.** Click work in a tree that is really only a source of hints, and redone after every
small change.
Fix: once a month in one batch, only the direct line, only what can be proven, read pages as text instead of screenshots.

**Server blocks.** A digital archive with bot protection blocked six times: from loading too fast and once from two sessions
at the same time. Each time the user had to unlock by hand, 30 to 60 minutes of standstill.
Fix: one session per portal (lock file), pauses, save image paths once and load without a browser afterwards.

**The patch chain.** Every change to the tree was a script, 82 in the end, which had to run in a fixed order.
Two scripts looked for "the next free ID" themselves; when the order was different once, IDs were duplicated.
The order was written as one long line in a set of instructions.
Fix in the kit: patches are called `NNNN_topic.py` and only create IDs from their own range NNNN.
`scripts/rebuild.py` checks that, replays everything and compares. When the chain gets long: `rebuild.py --new-base`.

**A triple blind reading of a passage** whose reading was never in doubt. The open question was which of several people
with the same name was meant, and no further reading answers that.
Fix: blind readings only where a reading carries a status. Full inventory with neighbours only on hit pages.

## 2. What was fast and cheap (should be the default)

1. **Emails to archives and offices.** All requests together cost 37 USD of compute. One archive reply named the digitised
   land register that proved two generations. Another saved a day of travel.
   Rule: in the first week every responsible archive gets a short email.
2. **Index first.** The line with good index volumes cost 236 USD, the line without an index 2,143 USD.
3. **A second record type.** Land register and farm handovers next to the parish register brought two links to Proven.
4. **Back-calculating the age at death.** "72 years, 3 months, 11 days" gives the exact baptism day. Costs nothing, carries a proof.
5. **curl instead of a browser** where the image server is open. No captcha, no block, no tab.
6. **Measuring costs instead of guessing** (`scripts/claude_costs.py`). Only the measurement revealed the 695 USD loop.
7. **A DNA test** (autosomal) of an older generation confirmed a line that was only probable on paper.
8. **One folder with git as the truth**, the online tree only a tool. Nothing got lost.

## 3. Method: what was right, what was missing

Right and kept: status levels (Proven, Probable, Possible, Unresolved, Disproven), a citation with a verbatim excerpt on every
fact, "an index is not an image", "not found" only with coverage, a second review with the task "destroy this proof"
(it found real mistakes several times).

What was missing:
- **Calibration.** A "nothing found" over 270 images rested on a screening whose recall had never been measured.
  Now: `scripts/calibrate.py` with 20 known pages; below 90 % the "nothing found" does not count.
- **Two readings by the same model family are not a second witness.** They share the same reading mistakes.
- **A proof file for every proven person** was required but could not be kept up (93 Proven, 2 files).
  Now: a proof file only for indirect evidence or a conflict.
- **DNA match names** ended up in the status file and so in git. Now: pseudonyms, real names only in `sources/private/`.
- **"Unlimited time" and "costs matter"** were both in the rules. They contradict each other. Now: thorough, but with a cost
  estimate before every big run.

## 4. Rough calculation

With the reading script, the emergency brake and the five questions, the same work would have cost 1,200 to 1,500 USD
instead of 2,800 USD by the review's estimate. The research itself (status, citations, coverage) was clean.

## 5. Older lessons that still apply

1. **The imported online tree is a starting point.** 85 % of an imported tree rested only on other people's trees; one line was
   impossible from generation 5 on (father aged 5 at his son's birth) and had been copied by others.
2. **Regional specialist sources beat the big portals:** village books, local historians, regional forums, authors of transcriptions.
3. **Only the line searched for was read.** On images already loaded there were overlooked entries two numbers further on.
4. **Handwriting read without enlargement is often wrong.** A groom stood in the tree under a wrong name for three days.
5. **Corrections have to go everywhere** (person, media, notes, letters): `sources/superseded-readings.tsv` plus the check script.
6. **Two transcripts of the same record are one witness.** Ages carried forward do not count twice.
7. **Do not set a status too early.** Disproven only with an original or a hard impossibility.
8. **The rare associated name finds everything:** the marriage being searched for was only found by searching for the bride's name.
9. **Printed editions normalise place names.** Check the place of origin on the original before reading books there.
10. **The answer was already in your own folder:** source notes, stamps, margin notes on certificates you already have.
11. **Short letters work better:** thanks, the request, the necessary details. No report on your own findings.
12. **Check helpers' success reports:** a helper passed off an old file as a new export.
13. **DNA: check the line for sex first.** Y-DNA only tests the pure paternal line.
14. **Invented times are invented facts.** Only the date or the real time.
15. **Overviews go stale, the journal does not.** Before "this is still open", look at the newest entry.

## 6. When nothing works: "around the corner"

Through other people:
1. Siblings and their descendants (estates, letters, search requests).
2. In-laws, godparents, witnesses: they often lead to the place of origin.
3. The second marriage: whoever remarried had to state what happened to the first spouse.
4. Living relatives in side lines as DNA testers and witnesses (never without consent).

Through records that are not called "genealogy" (Germany):
5. German Red Cross tracing service, church tracing service and home-town card indexes (today the Federal Archives), Arolsen Archives.
6. Equalisation of burdens files (Federal Archives, Bayreuth): expellees described farm and family in detail.
7. Wehrmacht and prisoner-of-war records (former WASt, today the Federal Archives), WWI casualty lists (CompGen).
8. Admission and naturalisation files (late repatriates: Federal Office of Administration, access request under GDPR art. 15).
9. Residents' registers, address books, land registers, cadastre, tax lists.
10. Margin notes on certificates (name changes, corrections, allowances).

Through places:
11. Village chronicle, local family book (Ortsfamilienbuch), home-town association.
12. The mother parish: chapel villages often have no books of their own.
13. Marriage place on the way: emigrants, soldiers and refugees married where they happened to be.
14. Check place names on the original: duplicate names, renamings, translations.

Through people who searched before:
15. Regional forums, old threads about the place.
16. Write to authors of books and transcriptions.
17. Search other people's trees for attached images, not for personal data. Ask the owner for the source.

Through technology:
18. Name index across all collections with rare associated names (FamilySearch, Geneteka).
19. Web archive (web.archive.org) for pages that have disappeared.
20. Read your own folder again with what you know today.

And then wait. Many routes take weeks. Put follow-ups with a date into PROCESS.md.
