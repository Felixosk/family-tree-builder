# Rules for AI agents in this project (Claude, Codex and others)

This project is a family archive. It should still be readable without software in 30 years and be
continued by an AI at any time. When convenience and traceability conflict, traceability wins.

The rules come from two real projects (2026) and were written after mistakes. The reasons are in the kit's
`LEARNINGS.md`. "The user" is the person who owns the project. The user decides, agents deliver.
These rules are a roadmap, not a cage: if you see a better, cheaper or faster way, propose it with a short reason.
Fixed are only the rules on evidence (2, 9, 11), privacy (5) and asking before expensive runs (10.1).

## 1. What lives where
| Path | Meaning | Rule |
|---|---|---|
| `family.ged` | the single source of truth for people, relations, events, sources | only through patch scripts (section 4) |
| `sources/base/family-base.ged` | base snapshot (first export), `scripts/rebuild.py` rebuilds from it | never edit |
| `scripts/patches/NNNN_topic.py` | every change to family.ged as a script, fixed ID range NNNN | section 4 |
| `sources/` | originals: `scans/`, `photos/`, `exports/`, `private/` (not in git) | never change or delete originals |
| `sources/evidence_links.tsv` | file -> link to its backup (e.g. a private cloud drive) | every piece of evidence gets a link |
| `sources/media.tsv` | file -> people/event | `scripts/add_media.py` |
| `sources/superseded-readings.tsv` | old and new reading of every correction | section 9.3 |
| `vault/` | notes: `People/`, `Places/`, `Documents/` (transcripts), `Research/` (reading rounds, reports) | every finding with source and date |
| `vault/Research/Watchlist.md` | all surnames of the direct line in every spelling | section 8.2 |
| `vault/Research/Coverage.md` | which books, years and images were read, with result | read before EVERY search (12.0) |
| `vault/Research/Proof_Plan.md` | weakest links of the direct line, next step per link | section 19 |
| `vault/Research/Proofs/` | proof arguments P01, P02 ... | section 11 |
| `PROCESS.md` | ONLY the current state (about 150 lines max) | section 17 |
| `journal/YYYY-MM.md` | diary, one entry per work session, newest on top | append only |
| `COSTS.md` | every payment and the Claude costs | section 10 |
| `SOURCES.md` | list of sources and archives with access route and pitfalls | add a new source right away |
| `letters/` | letters and emails (DRAFT_, SENT_), `SENT_LOG.md` | section 13 |
| `docs/error-log.md` | repeated mistakes become rules | section 18 |
| `reports/` | generated views (tree.html, tree_data.json) | never edit by hand |

## 2. Genealogical standard (not negotiable)
1. **Every statement has a status:** Proven, Probable, Possible, Unresolved, Disproven. Proven follows the
   Genealogical Proof Standard (GPS): reasonably exhaustive search, every fact cited, sources analysed,
   conflicts resolved. A separate proof file in `vault/Research/Proofs/` only for indirect evidence or a conflict;
   for a direct statement in an original, the citation with a quote is enough.
2. **Every new or changed fact gets a citation directly on the fact** (SOUR with PAGE and QUAY).
   PAGE holds where it was found, a verbatim excerpt and the link to the saved image.
   QUAY: 3 = original image read, 2 = transcript, index or secondary record, 1 = family story or someone else's tree, 0 = unreliable.
3. **Nothing is silently overwritten.** Conflicts stay as a NOTE, dates become ranges (`BET ... AND ...`).
4. **Other people's online trees are hints, not evidence.** They never support more than Possible. Mirror check:
   does that tree just reflect your own data back? The useful part of other trees is the attached images.
5. **"Not found" only counts with documented coverage** (collection, years, spellings, read completely yes/no).
6. **Relationship changes** (parents, merging, deleting) only with the user's approval, until then as a review document.
7. **Disproven only with strong counter-evidence** (an original or a hard impossibility). Age differences up to about 5 years are normal.
8. **Scope:** direct ancestors and their siblings with spouses. Side lines only if they answer a question of the main line.
9. **Online trees (Ancestry etc.) only get what can be proven.** Guesses stay in family.ged as a NOTE with status Possible.
   An entry "relationship unknown" still looks proven online and gets copied by others.

## 3. Git and several agents
1. Before any work: `git status` and `git log --oneline -10`. Commit other people's uncommitted changes first.
2. **Only one writer on `family.ged`.** Lock file `family.ged.lock` (agent, date, intent), delete after the commit.
3. Small, named commits after every unit. No `--force`.
4. Never stop with uncommitted changes.
5. No parallel versions (`family_new.ged`).
6. Whoever takes over another agent's work spot-checks its last claims first.

## 4. Required steps for changes to `family.ged`
1. Create the lock file.
2. New script `scripts/patches/NNNN_topic.py` from the template `0001_example_baptism.py`. **ID range = NNNN**
   (script 0012 only creates `@I0012001@`, `@S0012001@` ...). Never "find the next free ID": the result would depend
   on the order, and the rebuild would create duplicate IDs.
3. Test: `GED=/tmp/test.ged python3 scripts/patches/NNNN_topic.py` on a copy, then
   `python3 scripts/rebuild.py` (rebuilds everything from the base and compares). With 0 unexplained differences:
   `python3 scripts/rebuild.py --apply`.
4. `python3 scripts/build_all.py` (GEDCOM check 0 errors, readings, tree page, Obsidian).
5. An old patch was wrong: fix that script, `rebuild.py --apply`. Never patch family.ged directly.
6. PROCESS.md, journal, the affected vault note, commit, delete the lock file.
7. Technical: never renumber XREF IDs; `@` in text as `@@`; lines max 255 bytes (accented letters count double),
   `scripts/wrap_lines.py` does that.

## 5. Privacy
- Living people stay local. In shared views only the birth year. No uploads without consent to route and visibility.
- IDs, addresses of living people, filled-in forms only in `sources/private/` (not in git).
- **DNA raw data:** never open, copy or upload without an explicit yes. DNA match names only as pseudonyms (K01, K02).
- Online accounts: never send, buy, cancel or change settings without specific consent. After every change reload and read.
- Never bypass security checks (captcha, bot check). The user solves them.

## 6. Documents, photos, incoming material
1. Filing: portraits in `sources/photos/`, certificates and scans in `sources/scans/YYYY-MM-DD_topic/`, downloads in `sources/exports/`.
2. Back up every image right away (private cloud drive or similar) and put the link into `sources/evidence_links.tsv`.
   **Online finds** (index hits, gravestone photos, database pages) are saved as screenshot or PDF, with the original URL.
3. Every document gets a transcript in `vault/Documents/` (who, what, when, where, uncertain parts in [brackets?]).
4. **Inventory on arrival:** read every new file fully against the watchlist before the question of the day.
   Search PDFs with `pdftotext` first, extract images with `pdfimages`.
5. Family stories are sources with their own status (QUAY 1): record them word for word, check them sentence by sentence.
6. Transcribe voice messages locally; audio stays untracked, the transcript belongs in the project.

## 7. Working with the user
- Short, clear, honest. Name mistakes openly, your own too.
- **Every finding in an answer comes with its source and a clickable link** (evidence link plus archive reference), also in interim updates.
- The user makes the decisions; agents offer options with a clear recommendation.
- **No invented times.** Only the date or the real time (`date`). A letter only counts as sent when the user says so.
- **Before "new", "still open" or suggesting a search, search first:** `scripts/already_read.py`, `Coverage.md`, journal, family.ged.
  Overviews go stale, the journal does not.
- Do not suggest again what the user turned down (PROCESS.md, decisions).

## 8. Reading images and documents
1. **Inventory, not spot search:** screen every image against the watchlist once, then go to the place you are looking for.
   Full inventory (every line with neighbours) only on hit pages, not on hundreds of pages of a whole book.
2. **Extend the watchlist** in the same commit when an ancestor or spouse is added (all languages and spellings).
3. **FAN principle (friends, associates, neighbours):** for every hit note neighbours, godparents, witnesses and same surnames on the page in one line each.
4. **Coverage** per book in `vault/Research/Coverage.md`: image or entry range, read yes/no, searched for what, hits.
5. **Enlargement rule:** no name, date or place from handwriting goes into family.ged without a saved crop (at least 3x).
6. Compare disputed letters with a reference from the same hand on the same page.
7. **Blind second reading** only where it carries weight: readings that change a status of the direct line.
   The second reader gets the image, but not the expected names.
8. Small models do not read old handwriting reliably. Their "nothing found" never counts as "not there".
9. **Calibrate before large screenings:** run 20 pages with known hits through the same screening
   (`scripts/calibrate.py`). Below 90 % recall, a "nothing found" from that screening does not count.
10. Two readings by the same model family are an error check, not a second witness.

## 9. Securing readings
1. Whoever writes `[?]` saves the crop in the same pass.
2. **An index is not an image.** Facts taken from an index are QUAY 2 and Probable at most, until the image is read.
3. **Correction propagation:** put a changed reading into `sources/superseded-readings.tsv`, then run
   `python3 scripts/check_readings.py --only 1` and fix every place it reports.
4. Withdrawing a finding needs the image.
5. **Back-propagation at the end of every session:** which proof file, which line in SOURCES.md, which item in PROCESS.md
   is outdated by the finding? After a big finding many places go stale; search for them on purpose.

## 10. Costs and model choice
1. **Estimate and ask before big jobs:** more than 30 images, more than 3 helpers or a workflow only after an estimate and an OK.
2. **Index first, then records.** If a collection is searchable by name, use the index first; images only for the hits.
3. **Five questions before every book** (written into the research note): Can this record type answer the question at all?
   Is it the right parish or office for the place? Which years are we really missing? Is there a register or index?
   Is it already in `Coverage.md`? Then a sample of 20 images first; if the place or name never appears there, ask the user
   instead of reading on. Even if the task says "complete".
4. **Read in two stages, one image per call:** stage 1 with `scripts/read_images.py`: every image downsized (about 1200 px) in its own
   fresh call with a cheap model, result as one line in a file. No long helper chat with 50 images: there every image is billed
   again on every step (measured: 43 cents per image instead of a few cents). Stage 2 only for hit pages, full resolution, strongest model.
5. **Emergency brake:** at most 3-4 reading helpers at the same time, at most 25 images per helper, at most 2 retries.
   On "request limit" or "media removed" stop at once and report. Without this limit, helpers once retried
   thousands of times and burned 695 USD in a day. `scripts/read_images.py` has the brake built in.
6. **Always set the model explicitly** (helpers otherwise inherit the expensive main model).
7. Do not load images more than once, work from the transcript. Query big files only with grep.
8. **Track costs:** every payment right away in `COSTS.md`. Update Claude costs with `python3 scripts/claude_costs.py` at the end of
   every work round. Do not correct measured months downwards when old logs have been deleted.

## 11. Proof and status changes
1. Correlation table before every status change: statement x sources, weighted by record type, not by count.
2. **Independence:** two transcripts of the same original or two readings of the same original are one witness.
3. **No circular reasoning.**
4. **Second review with fresh context and the task "destroy this proof"**, not "check it".
5. The first place of residence is not the birthplace. Fathers and sons with the same name: check the birth year against the source.
6. **Back-calculate the age at death** (years, months, days) to the baptism day: an exact match is a strong identity argument.

## 12. Searching
0. **Before every search and every search suggestion:** `vault/Research/Coverage.md` and `python3 scripts/already_read.py "<name or book>"`.
   What has been read is not read again.
1. Index first, then images. "Nothing found" in an index is weak, hits are signposts.
2. **Rare associated names** (spouses, in-laws, godparents) as search keys, not the common main surname.
3. Search across all collections, also outside the place where you expect the event.
4. Web search in every language of the region is required. It is cheap, reading images is expensive.
5. Printed editions normalise place names: check the place of origin on the original before reading parish books there.
6. Clarify holdings before reading (which years the volume really has, chapels without their own books).
7. **Dead ends** in `vault/Research/Coverage.md` with question, source, spellings, coverage, result, date.
8. When nothing works anymore: the "around the corner" list in the kit's `LEARNINGS.md`.
9. **What only works on site** goes into `vault/Research/On_Site.md` (archive, what to order, opening hours). Travel only when
   online and post no longer help and several items add up.

## 13. Requests and letters
1. Before every draft read `letters/SENT_LOG.md` and the earlier exchange with that recipient.
2. Only what the recipient needs to act: thanks, the request, the necessary details, a cost limit. No report.
3. Messages in a foreign language always come with a translation underneath for the user.
4. Check the address on the official website. The user sends (or allows sending for exactly this letter).
5. After sending: SENT_LOG (date, time), PROCESS.md "Waiting for replies" with a follow-up date.
6. **Write first, then read:** every relevant archive and office gets a short email in the first week.
   All emails together cost 37 USD of compute in the reference project, and replies often named the right source.

## 14. DNA
1. Before recommending a test, check the line generation by generation for sex (Y-DNA only follows the pure paternal line).
2. Test older generations. Sort matches (Leeds method, shared matches).
3. No uploads (GEDmatch etc.) without explicit consent. Match names only in `sources/private/`.

## 15. Browser, archive portals, online trees
1. **curl/HTTP first, browser second.** Many image servers are open, only the search page is protected.
2. **Load slowly, one session per portal.** Loading too fast or two sessions at once trigger the bot block.
   Block = stop, the user solves the check, then restart more slowly.
3. Save the image paths of a book once (e.g. `sources/paths/<book>.json`), then never turn its pages again.
   Whoever loads a portal creates `sources/paths/<portal>.lock`; if it exists, no second session loads.
4. In the user's browser only work in the background, one tab per portal, close it at the end.
5. **Never redirect the download folder permanently.** A download setting via CDP applies to the whole browser.
   Set it right before, reset it to `default` right after (also on error).
6. Online forms (React, e.g. Ancestry): only real typing saves. After two failed attempts on a form:
   give the user click instructions instead of a third round.
7. **Update the online tree (Ancestry etc.) only in batches:** collect in PROCESS.md, enter at most once a month,
   only the direct line and only what can be proven. Every person created online produces new hints and click work.
8. Check helpers' success reports yourself (file, reload the page). A helper once passed off an old file as a new export.

## 16. Routine "sync"
When the user says "sync": check follow-ups, record what was done, `build_all.py` (0 errors), `rebuild.py` (0 differences),
look for conflicts between PROCESS.md, proof files and family.ged, update costs, commit, report briefly.

## 17. Handover between sessions
- **PROCESS.md stays short** (aim below 150 lines): proof status of the direct line, follow-ups, waiting for replies,
  open decisions, next 3 steps. Everything else goes to the journal. Every session reads PROCESS.md; a long file costs
  money at every start and hides the current state.
- At the start: PROCESS.md, `git log --oneline -20`, `build_all.py`.

## 18. Mistakes become rules
When the user corrects something that is not a rule yet: one line in `docs/error-log.md`. The second time, propose a fixed rule
(here or as a check in a script).

## 19. Way of working
1. **Weakest link first, with an eye on cost.** As long as a link of the direct line in `Proof_Plan.md` is below Probable, it comes first.
2. **A second record type** for every parent-child link: next to the parish register, land register, cadastre, tax list, civil registry, military.
3. Several helpers only on separate books or image ranges, each with its own result file.
4. Bring helpers' raw notes into the finding format on the same day and back them up.
