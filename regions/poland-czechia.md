# Guide for Poland and Czechia (Silesia, Moravia)

Experience from the reference project, as of November 2026. Portals change; if something no longer works,
correct it here. General rules (load slowly, one session per portal) are in the skill `archive-portals`.

## Where is what?

**Closure periods in Poland:** birth registers stay with the registry office (Urząd Stanu Cywilnego, USC) for 100 years,
marriage and death registers for 80 years, counted from the end of the year. Then they go to the state archive within two years.
Rule of thumb for 2026: births up to about 1925, marriages and deaths up to about 1945 are in the state archive
(Archiwum Państwowe, AP), everything younger is at the USC. So "nothing found" in an online database for younger years
means nothing. Source: Prawo o aktach stanu cywilnego, art. 28.

**Prussian civil registration from 1874:** in Upper Silesia there are civil registers from 1874 next to the parish registers.
Death records usually name the parents of the deceased, marriage records the parents of both sides. That is often the fastest
way one generation back.

**Border regions:** some areas of Silesia belonged to other administrations in the past than today. Older books may then be
in the Czech provincial archive (Zemský archiv v Opavě), younger ones in Poland. Before searching, find out which state
and which diocese were responsible at that time.

## Portals

| Portal | What | Access | Experience |
|---|---|---|---|
| Geneteka (geneteka.genealodzy.pl) | name index from more than 4,500 parishes and registry offices | free, web form | use the web form. The programming interface returned data in a test that ignored the filters |
| Skanoteka (metryki.genealodzy.pl) | scans for many Geneteka hits, civil and parish records | free, no login | **no browser needed:** pages `https://metryki.genealodzy.pl/id<ID>-sy<unit>-kt<N>`, the image URL is in the HTML of the image page (`metryka_get.php?op=download&dir=...`), loadable with `curl` and a Referer |
| szukajwarchiwach.gov.pl | central scan portal of all Polish state archives, more than 55 million scans | free | bot protection (Imperva) blocks curl and often automated Chrome too. Worked with a separate browser profile the user opens; control only through the address bar and "save page". Full size: image hash ending `_max` instead of `_mid` |
| Silius Radicum (siliusradicum.pl) | Upper Silesian society: indexes (skorowidze) for about 126 registry offices, images from AP Katowice | free, forum with account | no name search, folders of images instead; loadable with curl, the cloud storage slows down after about 100 files |
| Geneszukacz | meta search across Geneteka, casualty lists, military, Metryki | free | good first sweep |
| Matricula (matricula-online.eu) | Catholic parish registers, including Silesia and Bavaria | free | images by direct URL; index volumes are often at the end of a collection |
| FamilySearch | index worldwide, many films | free account | person search in the logged-in tab via `fetch('/service/search/hr/v2/personas?q.surname=...&q.anyPlace=...')`. Images of Silesian parish registers were often "Image Restricted" |
| digi.archives.cz (Zemský archiv v Opavě) | parish registers, land registers, land table from Moravia and Silesia | free | bot protection (Radware). The site only reveals image paths slowly, but the images are open tiles on `images.archives.cz`. Tool: `template/scripts/portals/digi_archives_cz.py` |
| PRADZIAD (inside szukajwarchiwach) | directory: which books for which place are where | free | before every request to an archive |
| WWI casualty lists (des.genealogy.net) | wounded, killed, missing | free | try spelling variants |

## digi.archives.cz: saving whole books
1. You open the book in Chrome, solve the bot check, set the viewer to "single image", page 1.
2. Claude turns the pages in a background tab and saves the image path per page (`sources/paths/<book>.json`), about 10 s per page.
3. In parallel the script stitches the pages together from the tiles in full resolution.
4. With the path file the book can be loaded again later without a browser.
Rules: only one tab, never two sessions at once (that triggered the block immediately), no `fetch()` on the viewer pages.
One session lasted about 35 to 70 minutes. On a block: you solve the check again, then continue.

## Letters to Poland and Czechia
- Write in Polish or Czech with a translation underneath for you. Short: request, details, cost limit.
- State archives (AP) usually answer emails within 1-3 weeks and state fees with a reference number.
  Examples from the project: copy of a record 10 PLN, digital copy 2 PLN, search fee 60 PLN per hour.
- Registry offices (USC) often want a formal application, sometimes by registered mail with return receipt, and fees by
  bank transfer (e.g. 10 PLN per record). Someone local who calls or pays saves weeks.
- Parish offices: friendly, in Polish, one specific question, offer a donation.
- Czech provincial archives help by email with the question which collection is digitised. That is how the reference
  project found a digitised land register that proved two generations.

## Names and places
- Every name in German, Polish, Czech and Latin into the watchlist (e.g. -ski, -sky, -ek, -ik).
- Place names in every language of the period: German name, Polish or Czech name, old spelling.
- On Ancestry enter places as "town, district, voivodeship, Poland". A region name in Polish was once matched to Pilsen.
