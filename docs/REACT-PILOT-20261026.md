# Namelecule — React welcome/library pilot — 2026-10-26

Historical first-pilot record, preserved in local checkpoint e8d9bb4. The later
normalized catalog/search stage is documented in REACT-LIBRARY-20261026.md;
its current checks supersede this stage's library-rendering checks. References
below to uncommitted status describe the time this initial record was written.

User approved a separate trial after the proposed gradual migration. The main
conversation implements as Developer; the frozen result receives independent
Reviewer inspection. This is a local prototype, without commit/push/publication.

## Delivered behavior

- `react-preview/dist/` serves a real React welcome page and theory library,
  with the established content, styling, images, nine cards and twelve lessons.
- React owns rendering, hash navigation, modal state and reusable card/header/
  footer/dialog components. Native dialogs retain close/Escape and focus behavior.
- A deterministic build-time extractor reads the trusted existing page markup,
  CSS and panel data. Its generated node data is rendered as React elements,
  without raw HTML injection or execution of the original page script.
- Formula subscripts, limits, dual cards and all twelve lesson URLs are retained.
- Lessons navigate to the current v51 player. Its Exit still opens the established
  library; the player and molecular viewers have not been ported into React.
- The current published entry/welcome/library and all molecule/lesson files are
  byte-unchanged. The preview banner links back to the current welcome page.

This pilot deliberately uses a compatibility node renderer to preserve content
and avoid maintaining a second syllabus. It is not yet a normalized React content
architecture for the whole platform. Its value is a tested boundary around the
welcome/library; chemistry/player state and viewer integration remain future work.
There is no new quiz, login implementation, learning record, backend or tracking.

## Build and tooling

React/React DOM19.3.1 and Vite8.3.5 are pinned in the new folder's package/lock.
Python3.9+ extracts source content. A portable official Node24.22.1 was downloaded
to `/tmp/namelecule-react-tools`, with its archive SHA256 verified against official
SHASUMS256. No Node installation or configuration was made system-wide.
Npm install used `--ignore-scripts`; the reported audit was0 vulnerabilities.
This audit is a package-database snapshot, not a security certification.

Production build passed:16 transformed modules, JS267.13kB /78.08kB gzip,
CSS0.29kB /0.23kB gzip in this build. React adds payload versus the existing static
welcome/library; no speed improvement or measured performance claim is made.
Node/npm are build tools only; the generated preview runs on the existing static
HTTP server. Relative build paths assume `react-preview/dist/` under project root.
No custom web-server rewrite is needed for hash navigation. Output and node_modules
are locally ignored; bundled React/React DOM MIT notice is copied into the build.
See [build/open instructions](../react-preview/README.md).

## Required professor upstream check and routine sync

Last previously synchronized upstream:6e29bd5c89872665ec9cd45f9f80fd2d9bd91d6e.
Current HEAD checked:dc02933358a19f792c1a393fbdc2c15c2aba573f, one commit ahead,
`file selection window for images`. Both current changelog and actual GitHub
comparison/history were read; fetch updated the upstream remote-tracking ref.

Standing user authorization covers routine synchronization after review and
presentation of intent. The exact scenario51 runtime diff was ported cleanly:
raster image file picker (PNG/JPEG/GIF/WebP),512000-byte file cap,700000-character
data-URI cap, required alt text, separate URL action and asynchronous inline/modal
input synchronization. Existing Namelecule rules, title allowlist and library Exit
are preserved; active HTML scenario cache key updated.

Upstream rich-note plan/handoff were added. Existing local didactic plan/changelog
were preserved with additive records rather than replaced. Upstream session notes
were not copied over local continuity records. A combined docs patch did not apply
because one upstream plan was absent locally and the local scenario plan differs;
no partial patch was applied. Runtime-only patch applied cleanly and matching
upstream addition/deletion lines was verified. No merge commit is claimed.

This upstream authoring sync is separate from the React shell and introduces no
core, data, MOL/SDF or lesson-content changes. Last published site remains the
previous saved release until an explicit new save/publication instruction.

## Verification actually performed

- Production Vite build passed; npm package/lock versions agree. Python AST checks
  passed; Node syntax check passed for the modified scenario51 source.
- Extractor read-only `--check` verifies the generated snapshot against the actual
  welcome/library source and hashes. All twelve referenced JSONs exist /283steps.
- 1234 pre-existing tracked files match the baseline3673c390, including core51,
  molecule data, all molecular assets, both existing public source pages and all
  scenarios. The six changed tracked paths are the documented sync/runtime/docs
  and session/contribution records. New files are listed in the review manifest.
- Firefox1500px and390px: images decode, ethanol SVG viewBox preserved, no document
  horizontal overflow, nine cards/twelve links and exact card-text/URL parity with
  the source library. Three information dialogs open/close and restore focus;
  back/forward and hash-route refresh work.
- Actual navigation from React library into Other ketones, first Next and existing
  player Exit passed;126 molecules available. This is a limited integration smoke,
  not a fresh traversal of all283steps or proof of all viewer interactions.
- Eighteen read-only VM cases execute the actual upstream image-picker/URL functions:
  raster types, size/data caps, alt handling, cancellation, reader errors, input
  reuse, async input event and existing unsafe URL rejections.
- Browser test uses a genuine PNG File and native FileReader, checks data-URI/alt
  insertion, and confirms expanded-editor input updates the inline textarea and
  step state. Both file/URL controls exist. The native OS selection dialog itself
  was not automated, nor was a large image decoded visually.
- In the final focused Firefox run, no JavaScript errors were recorded. Earlier
  documented JSmol viewer-null issues remain unresolved; this limited run does not
  establish their absence on other lesson/viewer paths.

Developer evidence: `docs/checks/react-preview-{static,browser,upstream-picker}-20261026.json`;
scripts in `docs/checks/` and `react-preview/tools/`. Screenshots and build hashes
are retained under `/tmp` and the frozen review manifest. Independent review
identity, executed checks, findings and limitations are recorded in SESSION-NOTES
and YANNIS-CONTRIBUTIONS; browser evidence must not be labeled independent execution.

## Limits and current decision boundary

Only Firefox at the recorded viewports was exercised. No production deployment,
Drupal embedding, forced offline run, learner study or full React viewer migration
was performed. Node's temporary download and ignored build need rebuilding if
removed. Files are local, uncommitted and unpublished for this pilot.

Core51 is unchanged from this task's baseline
`096d617853646de0dfd67bcbde3e32252aebcb98e7525b05e6f7e71ccb48a5fc`.
Earlier approved core work remains part of the previously saved release; no new
core49/50/51 intervention is introduced here. No chemical or educational specialist
was needed because molecular/lesson content is unchanged.
