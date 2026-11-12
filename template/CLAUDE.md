# Family history project

The binding rules are in AGENTS.md and apply to Claude too:

@AGENTS.md

Also for Claude:
- At the start: read `PROCESS.md` (current state only), `git log --oneline -20`, `python3 scripts/build_all.py`.
- Before every search: `python3 scripts/already_read.py "<name or book>"`.
- Load the skill `family-tree-builder` for the workflow, plus `genealogy-research` for archive knowledge and old scripts,
  plus `archive-portals` and `browser-harness` for work in the browser.
- Always start helpers (sub-agents) with an explicit `model`: `sonnet` or `haiku` for screening, search, click work;
  `opus` only for handwriting on hits and for judging proofs.
- More than 30 images, more than 3 helpers or a workflow: estimate the cost first and ask.
