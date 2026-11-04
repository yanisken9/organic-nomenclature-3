# Workshop welcome and first set card — 2026-11-04

Approved request `b08e3395296b4ddf89d19d98dd901c72`: turn the existing workshop
entrance into a general welcome with first Alkanes card; remove the rehearsal and
start directly in four missions; return/reset confirmation for in-progress work.
This consolidates the previously requested, unimplemented rehearsal removal.
User then requested the visible header say «ΜΙΚΡΕΣ ΑΠΟΣΤΟΛΕΣ ΟΝΟΜΑΤΟΛΟΓΙΑΣ»
instead of «ΧΗΜΕΙΑΣ»; that exact in-scope text edit is included before review.
A targeted4-assertion Firefox check verifies the text and overlap-free header
at1500/1000/920px. No broad functional rerun after this text-only steering.

The same `games/name-repair.html` route now displays the accepted 3D workshop logo,
brief instructions and one active «Αλκάνια» card. The card introduces four topics
and starts «Ποιοι άνθρακες μετρούν εδώ;». Progress is1–4. Results and the session
button return to the set welcome; cancelling confirmation preserves the current
answer, confirming resets the set. The header Exit still returns to Namelecule.
The screen sequence is in-memory; browser Back is not a new internal screen router.

## Scope and recovery

Exactly six runtime paths: js/namelecule-game-repair.js,
games/data/name-repair-alkanes.json, css/namelecule-games.css,
games/name-repair.html, mulermoc-nom-54.html (shared engine cache URL only),
design/welcome-proposal.html (entry wording/query). Baseline hashes and BEFORE
copies are in this directory. HEAD168e3cec01f941a84d40bbe0dc07156e7baa35d0/index
preserved. Extensive pre-existing changes are excluded from this contribution.

Only guided-parent was removed from game data. The remaining four authored
objects are byte/content-equivalent to their original versions. Questions,
feedback, names, images and grading remain. Shared mount/restore API is unchanged;
the common round renderer differs only in a standalone-only button label. The
embedded pilot JSON/controller/scenario engine and core52/54 match the baseline.
Unused rehearsal assets remain available in recovery/history; no images deleted.
No changes to other homologous series or React. No stage/commit/push/publication.

Actual professor HEAD/history/CHANGELOG checked2026-11-04T11:37:40Z: unchanged
from actual synchronized02dbcfaf79e23f1933a252e0b1f6671049d39b78, no new commits.

## Verification

Developer engine74, component60 and standalone hub40 assertions PASS in
JavaScriptCore; component/hub tests use DOM doubles, not a browser. Engine tests
adapt old87 checks to remove16 assertions for the removed question and add3
four-round schema guards. Historical tests/results were not overwritten.

Actual isolated Firefox:53 hub/game checks PASS,0JS exceptions. Main welcome
link→hub→all4exact missions with keyboard→results→hub→fresh replay; one wrong
submission counted as fifth effort; return Cancel/Confirm; viewports1500/768/550/
390/320; simulated-touch mission/Continue/return; first SVG failure disables
assessment and recovers with retry; external header Exit. Desktop/mobile
screenshots were visually inspected. Initial driver failure was a missing
`disabled` property on anchors; the test helper now normalizes it to boolean.
No application fix was needed for that test-driver error; raw run retained.

Embedded pilot replay:45 checks PASS,0JS exceptions. Includes wrong/correct
answers, same-tab refresh, unlock/Continue, URL/hash/history/keyboard gates,
image failure/recovery and supported mobile/portrait-return paths. The last
Escape-after-history step initially failed under programmatic focus only (same
sensitivity recorded before this hub unit). A real pointer click on navigation,
then focused Escape, passes and records its actual key event. No application
patch was made or root-cause fix claimed; the precise original focus route is not
fully established. Both raw runs are retained. Actual input is the stated final
verification condition, not a universal keyboard guarantee. Scope-specific
syntax/whitespace/exact-question/hash guards PASS. A full337step replay is not
repeated: core/viewer/scenario modules and pilot data are unchanged; the shared
round boundary and mandatory pilot flow receive direct coverage.

Fresh independent Reviewer /root/review_workshop_hub found no actionable P0–P3.
Independently verified7target/42evidence hashes, ran74+60+40 in-memory assertions,
read actual diff/dependencies and assessed supplied Firefox results/screenshots.
Browser execution was Developer evidence, not independently repeated. The focus
limitation remains explicitly unresolved. See review-report.md. After review only
factual records/cleanup evidence changed; six runtime hashes are unchanged.
Six final served-runtime files returnedHTTP200 with exact reviewed SHA256 bytes.
Owned Firefox38292/9244 stopped and profile removed; normal userFirefox/server8013
retained. Updated workshop open command to normalFirefox returned exit0.

## Limits

Local Firefox only; touch simulated, Safari/physical-device/assistive technology
not executed. Existing CDN/PubChem/CIR dependencies of Main54 remain. The new
hub does not add progress storage or cross-device sync; explicit return warns
before clearing the current set. Existing same-tab checkpoint storage remains
separate. No offline or conference-machine readiness claim.

No core files changed in this unit. Previous core54 integration is pre-existing.
