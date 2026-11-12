# Guide: from zero to a family tree with evidence

The order that worked in the reference project. Each step says what you do and what Claude does.
It is a roadmap, not a rulebook: if Claude sees a better way, it should say so.

## Week 1: lay the groundwork

### 1. Create an Ancestry account and start the tree
- Sign up at ancestry.com (or your country's site). The tree itself is free. You only need a subscription for the
  databases (records, passenger lists, other people's trees). In the reference project: a 6-month plan for 39 EUR.
  Use the trial period and put the cancellation date into your calendar right away.
- Start the tree with yourself: you, parents, grandparents, everything you know. Living people are private there automatically.
- Why Ancestry: the largest DNA database, many hints and other people's trees as leads. The truth lives in your
  folder (`family.ged`) though; Ancestry is a tool and a shop window.

### 2. Create your research folder
```bash
~/family-tree-builder/new_project.sh ~/FamilyHistory "Yoursurname" --extras
```
Then export the Ancestry tree (tree settings, "Export tree"; it comes as a ZIP with a .ged file)
and load it as the base as described in README step 5.

### 3. Collect everything the family has
You ask, Claude does the work. Ask parents, grandparents, aunts, uncles and cousins for:
- Certificates: birth, marriage, death, baptism, family register book, ancestry passports, IDs (IDs stay private)
- Photos including the back (names, places and years are often written there), albums, memorial cards, letters, field post
- Stories: who came from where, when and why? Voice messages are best. Claude transcribes them and checks them sentence by sentence.
- Family trees or family folders someone already made

Put photos and scans into one folder, Claude turns them into:
1. Files in `sources/scans/<date>_<topic>/` and a backup (e.g. a private Google Drive), link in `sources/evidence_links.tsv`
2. A transcript of every document in `vault/Documents/`
3. Entries in `family.ged` through a patch script, every fact with its source
4. A fresh tree page `reports/tree.html`

With many images (e.g. 200 photos from a family folder) Claude reads in blocks with a cheap model and checks only the
important places itself. It tells you the rough cost first.

Claude gives you questions for relatives as a ready message you can forward, simple and numbered.

### 4. Order DNA tests
The older the generation, the more the test shows. Order:
1. **Grandparents or even great-grandparents**, while you can. A grandparent shows twice as much of the old lines as a grandchild.
2. **Father and mother.** Then your matches can be sorted to the father's or the mother's side.
3. **Yourself.**

Which test: **AncestryDNA** (autosomal, largest database, matches right next to the tree). In the reference project
49 EUR per test plus about 10 EUR shipping. Y-DNA or mtDNA only for one specific question, and check first that the line
is really purely male or purely female (the surname may have come through a woman).

When the results are in, download the raw data from Ancestry and upload it for free to other sites to get more matches.
What happened in the reference project (November 2026):

| Site | Upload of Ancestry raw data | Note |
|---|---|---|
| GEDmatch | worked | free, matches after 1-2 days. Choose "opt out" for law-enforcement matching. Upload a GEDCOM extract with direct ancestors only, living people as "Private" |
| MyHeritage | no longer worked | the site only offered to sell its own test |
| FamilyTreeDNA | rejected | "unsupported version", probably because of the newer Ancestry chip |

Better if the budget allows: also test one person with a second large company (e.g. MyHeritage DNA) instead
of only uploading raw data. Claude sorts matches with the Leeds method (shared matches, parent sides).
Important: raw data and match names never go into git, only into `sources/private/`. Uploads only after your yes.

### 5. Write to archives and offices
The cheapest thing there is: in the reference project all emails together cost 37 USD of compute, and replies often named
exactly the source that helped. Claude finds the responsible registry office, parish office, diocesan archive, city archive
and state archive for every place, checks the address on the official website and writes short drafts (foreign languages
with a translation underneath). You send them. Fees are usually small (5 to 45 EUR). Then wait patiently; replies take
days to weeks.

## From week 2: research

### 6. Search online, cheapest first
1. Web search and name indexes (FamilySearch, Geneteka, Ancestry search, Matricula index volumes)
2. Check hits on the image ("an index is not an image")
3. Whole books only after the five questions and a sample of 20 images
4. Reading with `scripts/read_images.py` (one image per call, emergency brake)

Poland and Czechia have their own guide: [regions/poland-czechia.md](regions/poland-czechia.md).

### 7. Prove
Every person has a status (Proven, Probable, Possible). Claude works on the weakest link of the direct line first
(`vault/Research/Proof_Plan.md`) and looks for a second record type for every parent-child link
(land register, cadastre, civil registry, military next to the parish register).

### 8. Update Ancestry (once a month)
What is proven in `family.ged` goes to Ancestry in one batch. Only what can be proven, only the direct line with siblings.
How it ran in the reference project:
1. Claude reads the person list through Ancestry's read interface and compares it with `family.ged`.
   Result: a list "what is missing or different".
2. Claude enters it in your Chrome, in the background, with
   [browser-harness](https://github.com/browser-use/browser-harness) (you need to be logged in).
   With many people: several Claude sessions in parallel with a cheap model, each with its own group of people
   and its own browser tab.
3. Attach the source as a citation to every event, the image as media to the person, a link to the saved evidence.
4. Check everything once at the end, not after every person.
The click tricks (React fields, date format, place names) are in the skill `archive-portals`.

### 9. When you are stuck
The "around the corner" list in [LEARNINGS.md](LEARNINGS.md) section 6. And: what only works on site, Claude collects in
`vault/Research/On_Site.md`. An archive trip is only worth it when several items add up there and emails no longer help.
Ask first whether the archive sends scans for a fee; that is usually cheaper.

## Every week
- Say "sync": Claude checks everything, measures costs, keeps `PROCESS.md` short, commits.
- Look at `COSTS.md`. If a run was unusually expensive: why? That becomes a rule.
