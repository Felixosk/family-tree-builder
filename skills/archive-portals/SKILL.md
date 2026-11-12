---
name: archive-portals
description: "Rules for archive websites and online family trees in the browser (FamilySearch, Matricula, Ancestry, national digital archives with bot protection): curl first, browser second, load slowly, one session per portal, save image paths, reset the download folder, React forms on Ancestry. Triggers: open an archive portal, browse a parish register online, save whole books, 'blocked', 'captcha', 'Radware', enter people on Ancestry."
---

# Archive portals: archive websites and online trees

Fixed rules here: never bypass a bot check, never send or buy anything without a yes. Portal tips for Poland and Czechia: `regions/poland-czechia.md` in the kit.

Works together with a browser control tool, ideally [browser-harness](https://github.com/browser-use/browser-harness)
(controls the user's own Chrome over CDP, so logged-in sites like Ancestry work). Every rule here comes from a mistake
in the reference project.

## 1. Without a browser first
- Many portals only protect the search page. The images often sit on a separate, open server (tiles, IIIF,
  direct download links). Look up the image URL of one page in the browser once, then load with `curl` and a `Referer`.
- Read public pages and APIs with `curl`. Use the browser only for login, clicks or bot protection.

## 2. Avoiding blocks
- **One session per portal.** Two sessions at once triggered the block on the very first request in the reference project.
  Lock file `sources/paths/<portal>.lock`, delete it at the end.
- **Slowly:** pauses between pages (several seconds), no parallel `fetch()` on protected paths.
- On a block, captcha or "Server Exception": stop at once. The user solves the check, never bypass it.
  Then continue more slowly, jump by image number instead of turning pages.
- **Save the image paths of a book once** (`sources/paths/<book>.json`). Then the book can be loaded again any time
  without a browser, and nobody turns its pages twice.

## 3. In the user's browser
- Work only in the background, never bring the tab to the front, never take over the screen. One tab per portal,
  close it at the end and check that no empty tabs are left.
- With browser-harness: every parallel session gets its own `BU_NAME`; first navigation with `new_tab(url)`, then reuse that tab.
- **Download folder:** a setting like `Browser.setDownloadBehavior` applies to the WHOLE browser while the connection lives.
  Set it right before the download and reset it to `default` right after (in `finally`). Otherwise the user's own downloads
  land in a strange folder.
- Login, two-factor, consent: stop and ask the user.

## 4. Online trees (Ancestry and similar)
- Navigate only by direct URL to the person page (ID from the GEDCOM export), not through the search.
- React forms: `element.value = ...` does not save. Only real typing (click, triple-click the field to select, type, Tab).
  Check the field value afterwards. `cmd+a` often does not select the field content there ("Max" became "MaxMax Peter").
- After two failed attempts on a form, no third round: give the user click instructions with all values and direct links.
- Read APIs are faster and cheaper than screenshots: read pages as text, check everything once at the end.
- The export often comes as a ZIP. Check it is fresh by the date in the GEDCOM header; `cmp old.ged new.ged` exposes an old file.
- Only enter what can be proven, delete nothing, do not accept hints, do not change settings.

### Ancestry in detail (as of November 2026)
- Read the person list: `/api/treesui-list/trees/<TREE-ID>/persons?limit=100&page=N` in the logged-in tab (pages 1, 2, ...
  until empty; bigger limits gave server errors). Compare with that instead of looking at pages.
- Person page: `https://www.ancestry.com/family-tree/person/tree/<TREE-ID>/person/<PERSON-ID>/facts` (or your country domain).
- **Citations can be attached to an event** (birth, death, marriage). The details field takes at most 256 characters.
  Media (images) only attach to the person, not to an event.
- Date field on the German site: "Juli" was not recognised, "Jul" was. Use short month names.
- Places in the format "town, district, region, country" with the country in English ("..., Poland"). A region name in another
  language was once matched to a completely different place.
- Upload an image: click the upload button first, wait about 10 s, then set the file on the file input (`DOM.setFileInputFiles`).
- Web link as a source: the save button only becomes active after Tab and about 2.5 s.
- Many people: several parallel sessions with a cheap model, each with its own group of people and its own
  browser connection. Long runs as a background script that skips what is already entered.
- About 1-2 minutes per person. Read everything back once at the end.

## 5. Check success reports
Helpers sometimes report success that is not (an old file as a new export, a name typed twice). Always check yourself:
the file, reload the page, name AND dates.
