# Family tree builder: genealogy research with Claude Code

A starter kit for researching your family history with [Claude Code](https://claude.com/claude-code): a ready project folder,
rules and skills that let Claude read parish registers and records, enter every finding with a citation into a GEDCOM file,
write to archives, keep your Ancestry tree in sync and build a family tree page. It comes with the lessons from a real project
(8 weeks, 380 people, main line back to the 17th century): what was expensive, what was fast and how to save money.

Beginners start with [GUIDE.md](GUIDE.md) (the path step by step, from Ancestry account and DNA test to a tree with evidence),
then read [LEARNINGS.md](LEARNINGS.md) (that saves money).

The rules are a roadmap, not a cage: Claude may and should propose better ways. Fixed are only the evidence rules, privacy
and asking before expensive runs.

## What's inside

| Folder / file | What for |
|---|---|
| `template/` | your future research folder, with a fictional sample family to try things out |
| `template/AGENTS.md`, `template/CLAUDE.md` | rules for Claude (read automatically) |
| `template/PROCESS.md`, `journal/`, `COSTS.md` | current state, diary, costs |
| `template/vault/Research/` | watchlist, coverage (what has been read), proof plan, proof template |
| `template/scripts/` | check, patches, rebuild, tree page, Obsidian, reading with an emergency brake, costs, archive portal tool |
| `skills/` | two Claude skills: `family-tree-builder` (workflow), `archive-portals` (archive websites and Ancestry in the browser) |
| `GUIDE.md` | step by step: Ancestry account, family papers, DNA tests, writing to archives, research, updating Ancestry |
| `regions/poland-czechia.md` | portals, closure periods, letters and tricks for Poland and Czechia |
| `LEARNINGS.md` | what was expensive, what was fast, how to save, and "around the corner" for when you are stuck |
| `new_project.sh` | creates your folder and installs the skills |
| `tests/fresh_install_test.sh` | checks that everything runs on a fresh machine |

## Quick start (about 15 minutes)

You need: macOS or Linux, Python 3, git, [Claude Code](https://claude.com/claude-code).

1. Get the kit:
   ```bash
   git clone https://github.com/Felixosk/family-tree-builder ~/family-tree-builder
   ```
2. Create your research folder. With `--extras` you also get the two tools this kit builds on (see "Built on"):
   the skill [genealogy-research](https://github.com/sliday/genealogy-research) and
   [browser-harness](https://github.com/browser-use/browser-harness), with which Claude drives your Chrome in the background
   (entering people on Ancestry, browsing archive portals). browser-harness needs [uv](https://docs.astral.sh/uv/).
   ```bash
   ~/family-tree-builder/new_project.sh ~/FamilyHistory "Yoursurname" --extras
   ```
3. Connect browser-harness to Chrome once: keep Chrome open, run `browser-harness --doctor` in the terminal and follow the hints
   (Chrome asks once to allow remote debugging). The author's instructions:
   [install.md](https://github.com/browser-use/browser-harness/blob/main/install.md). Claude works in your logged-in Chrome,
   only in a background tab, and resets the download folder afterwards (rules in the skill `archive-portals`).
4. Get your tree: on Ancestry "Export tree" (comes as a ZIP with a .ged file), or a GEDCOM from any other program.
   If you have none yet, keep the sample family and start with yourself.
5. Replace the sample family (in the research folder, one after another):
   ```bash
   cd ~/FamilyHistory
   ```
   ```bash
   cp ~/Downloads/mytree.ged sources/base/family-base.ged
   ```
   ```bash
   rm scripts/patches/0001_example_baptism.py
   ```
   ```bash
   GED=sources/base/family-base.ged python3 scripts/wrap_lines.py
   ```
   ```bash
   python3 scripts/rebuild.py --apply --force
   ```
   If the check reports errors in the foreign export (e.g. impossible dates), that is normal: Claude fixes them afterwards
   with your first own patch. Then edit `project.json` (Claude can do it for you, see the table below): put your own ID from
   the file into `root_person` and empty the sample values in `user_tree_sources`.
6. Open the folder in Claude Code and send as the first message:
   > Read CLAUDE.md, AGENTS.md, and GUIDE.md and LEARNINGS.md from the kit (~/family-tree-builder). Take stock of family.ged:
   > how many people, which direct ancestors, which facts rest only on other people's trees, which hard errors exist.
   > Create the watchlist, enter the proof status in PROCESS.md and suggest which archives I should write to this week.
   > Do not change family.ged yet.

## Settings in project.json

| Key | Meaning |
|---|---|
| `surname` | family name shown on the tree page |
| `root_person` | your own ID in family.ged (e.g. `@I123456@`), the tree page starts there |
| `user_tree_sources` | source IDs that are only other people's online trees (coloured as hints, not evidence). Titles like "Ancestry Family Trees" are recognised automatically |
| `family_knowledge_sources` | source IDs that are family stories or papers without an official record |
| `obsidian_folder` | folder in your Obsidian vault for person notes; empty = no Obsidian |
| `cost_keywords` | extra words that mark a Claude session as part of this research for `claude_costs.py` |

## How to work with it

- **One question at a time,** direct line first, weakest link first.
- **Write first, then read:** in the first week every responsible archive gets a short email. That is the cheapest thing there is
  and often brings the right source. Claude writes the draft, you send it.
- **Index first, then images.** Reading images is expensive, searching is cheap. Claude asks before more than 30 images.
- **"sync"** at the end of every round: Claude checks everything, measures costs, keeps `PROCESS.md` short, commits.
- **"Around the corner?"** when you are stuck: Claude goes through the list in LEARNINGS.md.
- **Online tree** (Ancestry and co.) only once a month in one batch, and only what can be proven.

## The main commands

| Command | What it does |
|---|---|
| `python3 scripts/build_all.py` | checks family.ged, builds `reports/tree.html`, mirrors to Obsidian (if set up) |
| `python3 scripts/rebuild.py` | rebuilds family.ged from the base plus all patches and compares |
| `python3 scripts/rebuild.py --apply` | takes over the rebuild (with a backup) |
| `python3 scripts/already_read.py "name"` | has this been searched or read before? |
| `python3 scripts/read_images.py <folder> <result.tsv>` | screens images one by one and cheaply, with an emergency brake |
| `python3 scripts/calibrate.py expected.tsv actual.tsv` | how reliable is the screening? |
| `python3 scripts/claude_costs.py` | what did the research cost in Claude compute? |

Every change to the tree is a small script in `scripts/patches/` (template: `0001_example_baptism.py`).
That keeps track of where every fact comes from, and a mistake can be fixed cleanly later.

## What it costs

In the reference project about 2,800 USD of Claude compute at API price (paid through a subscription) and about 800 EUR in fees,
copies, DNA tests and one archive trip. Over 70 % of the compute went into reading old handwriting. With the rules in this kit
(one image per call, emergency brake, five questions before every book) it would have been about half, by estimate.
Details in [LEARNINGS.md](LEARNINGS.md).

## Privacy

- Data of living people stays local. IDs, addresses and DNA match names belong in `sources/private/` (in `.gitignore`).
- DNA raw data never in the folder, no uploads without your consent.
- If you back up your research folder on GitHub: only as a **private** repository.

## Built on (thank you)

| Project | What for in this kit | License |
|---|---|---|
| [sliday/genealogy-research](https://github.com/sliday/genealogy-research) | source knowledge for many countries, old scripts, GEDCOM method following the Genealogical Proof Standard | MIT |
| [browser-use/browser-harness](https://github.com/browser-use/browser-harness) | Claude drives Chrome over CDP: Ancestry, FamilySearch, archive portals | MIT |
| [Claude Code](https://claude.com/claude-code) | the agent that does the work | |

Neither tool is included in this repository; `new_project.sh --extras` installs them from their original repositories.

## License

[PolyForm Noncommercial 1.0.0](LICENSE). In short: free for personal use (your own family research, hobby, study, private
projects) and for charitable, educational, public research and government organisations. Not allowed: commercial use, for example selling it, offering it as an app or a paid service,
or using it in client work. For commercial use, open an issue on GitHub and ask.
