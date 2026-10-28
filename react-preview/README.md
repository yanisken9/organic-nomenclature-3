> **2026-10-27 — 3D PNG:** the React PNG action follows the active 2D/3D view.
> 3D calls unchanged native52 `fSaveJmolPng`: original Save Image filename prompt,
> current representation/H/labels/highlights/camera, footer and1200×1200PNG.
> React reports only a requested download, not proof of disk storage. Cancellation
> returns a nonfatal status; encoding timeout fails closed and offers retry.
> Native save and prompt observers are confined to the generated React host;
> late saves after timeout/unmount are blocked. Ordered commands wait through the
> native delayed echo cleanup. 2D keeps its existing native exporter and8s bound;
> 3D allows90s for native prompt/encoding, parent100s. Main/core/data/lessons and
> dependencies are unchanged. See [PNG3D checks](../docs/REACT-3D-PNG-20261027.md)
> and session notes for actual verification and independent review status.

> **2026-10-27 — 3D controls:** the React molecule viewer exposes native52
> C–H visibility, atom symbols, ball-and-stick/spacefill/sticks and rotation.
> These controls invoke the existing handlers through the same ordered
> model/script readiness gate. C–H hiding preserves O–H hydrogens. Preferences
> follow the main engine across molecule/naming/view changes; retry/remount
> starts a fresh session with all H/symbols visible, ball-and-stick, rotation off.
> Controls wait for the latest ACK, and replies must match the expected flags.
> Main/core/coordinates/lesson data and lesson host are unchanged. This remains
> a React interface around the existing renderer, not a new chemical engine.
> See [3D control checks](../docs/REACT-3D-CONTROLS-20261027.md) for verification
> and the known external JSmol lifecycle limitation.

> **2026-10-27 — all theory lessons:** the12existing library actions now stay
> in React at `#/lesson/<catalog-id>/step/N`, reusing one generated native52host.
> Catalog IDs, scenario paths/counts and per-step source titles are validated at
> build time. Course changes remount with a fresh session; step changes retain
> the current host and request/ACK guards. Headings and fallback URLs come from
> the unchanged library catalog. No lesson content, main/core/molecular files,
> dependencies or viewer implementation are replaced.
>
> Authored pixel heights retain content fitting; authored Auto (currently the
> alkene lesson) follows a bounded outer viewport without self-sizing feedback,
> with native internal scrolling and scroll reset on step change. Height-only
> parent resizes use a session/course-bound viewport message. Earlier dated
> alkane-only descriptions below record the pilot stage. See
> [shared lesson verification](../docs/REACT-LESSONS-20261027.md) and current
> session notes for actual completed checks, limitations and independent review.

> **2026-10-27 — 2D PNG:** «Αποθήκευση PNG» requests the unchanged main52
> `fSave2DPng` export of the current 2D form, CHn, highlights, numbering and name
> boxes. The adapter binds the exact current context, waits for numbering and
> observes the native download-anchor click. It holds the queue through the
> native async callback, whose filename reads legacy globals. New actions cancel
> an export before its snapshot; after that, they wait for its download request.
> The UI says «Ζητήθηκε λήψη PNG», never that a file was saved. Sync export errors
> are nonfatal; an8s async timeout stops the host, blocks a late click and offers
> an export-specific retry to discard pending callbacks. 3D export is not added.
> The existing fixed-size name footer can crop very long names; this is confirmed
> byte-identical in standalone main exports, not changed silently in this adapter.
> Main/core/MOL/SDF/scenarios/dependencies are unchanged; see
> [PNG verification](../docs/REACT-PNG-20261027.md) and current session notes.

> **2026-10-27 — skeletal CHn:** the React 2D controls offer the existing
> «Σύμβολα CHn» checkbox. It invokes the unchanged main52 `#zigzagCheck`
> handler; annotated skeletal mode uses the same existing skeletal MOL, without
> new coordinates or atom mapping. The wire contract normalizes legacy
> `condensedZigZag` to `mode: skeletal, symbols: true`; symbols is a strict boolean
> checked against the latest requested state. The checkbox is available only in
> skeletal 2D after the latest command ACK. This avoids annotating a mode still
> queued behind another command. Its own change gates the graph until that ACK.
> Explicit mode selection clears CHn; model/naming/view changes retain it where
> supported, as in the main app. Methane falls back to condensed/unchecked;
> retry/remount starts ethanol/condensed/unchecked. Source/origin/session/model
> guards remain intact. No main/core/molecule/scenario/CSS/dependency change.
> See [CHn checks](../docs/REACT-SYMBOLS-20261027.md) and current session notes
> for actual verification and independent review status.

> **2026-10-27 — optional rules:** the React name panel now renders the rule
> title, text and table supplied by the unchanged main52 `fShowRule`, preserving
> sub/sup and selected rows. Panels start closed and open only on user action.
> Component/molecule/naming changes close them; ordinary zoom/view/form ACKs may
> retain the current open panel. Stale rules cannot reopen during a component ACK.
> A bounded shared schema carries text and whitelisted elements/classes, never raw
> HTML, styles or event attributes. No chemical/educational rules are invented:
> existing unavailable common-alkyl and scenario-gated alkoxy content remains so.
> Main/core/molecules/scenarios are unchanged; no dependencies or publication.
> See [rule-panel checks](../docs/REACT-RULES-20261027.md) and current session notes
> for completed checks and the independent review outcome. Historical absence-of-
> rule-panels statements below describe earlier stages.

> **2026-10-27 — ether naming:** the React name panel offers native IUPAC/Κοινή
> radios for the11existing ethers. They invoke the unchanged main52 handler;
> labels, explanations and2D/3D highlights are still produced by that engine.
> The ether naming preference persists across molecule switches as in the main
> app; retry/remount starts with IUPAC. No toggle is offered for other classes.
> The v4 adapter additionally carries a bounded naming preference, rejects
> mismatched replies and validates naming commands against the actual current
> ether. While the change awaits its model/script ACK, old graph/components are
> hidden and radios/zoom are disabled. No main source, molecule or scenario is
> edited. See [ether naming checks](../docs/REACT-ETHER-NAMING-20261027.md) and
> session notes for actual verification/review status. Older paragraphs below
> describe the historical stages; their missing-toggle statement is superseded.

> **2026-10-27 — full molecule catalog:** the React viewer now exposes all126
> existing molecules, grouped by the main engine's series labels, with Greek
> name/common-name/formula search. `tools/sync-molecules.mjs` generates metadata
> using the unchanged main52 naming/classification engine and explicit-H SDF
> atom counts. It does not maintain another chemical naming algorithm or copy
> coordinates. Build regenerates this catalog before generating the host.
> `node tools/sync-molecules.mjs --check` checks it without writing.
>
> The selector preserves the current model when filters exclude it; clearing
> returns focus to search. Selection/filters have no persistent storage. All377
> available2Dforms are retained; methane has no skeletal source, so that radio
> is disabled and switching to methane from skeletal uses condensed mode.
> Initial/retry selection remains ethanol. Existing uppercase IDs are preserved.
> Main2D/3D coordinates, explicit H, cameras and naming logic are reused unchanged.
> The React welcome's Explore links now stay in the React viewer. Theory lessons
> still use the existing standalone player. Common names are searchable metadata;
> this stage does not add a React common/systematic toggle or theory-rule panels.
> Earlier three-molecule paragraphs below describe historical implementation.
>
> This change is confined to React and its checks/documentation. The main app's
> files, entry point, molecule assets, scenarios and core are protected by a
> task-start byte-hash baseline. Both editions still share read-only legacy assets;
> this is not an independent/offline distribution or a native React renderer.
> See [catalog checks](../docs/REACT-CATALOG-20261027.md) for final verification.

> **2026-10-27:** the main application and generated React host/catalog now use
> the locally integrated v52. Earlier v51 paragraphs below describe prior stages.
> The same three molecules/2D/3D/name controls remain; no new React renderer.
> See [v52 sync](../docs/V52-SYNC-20261027.md) for compatibility and review evidence.

# Namelecule — isolated React pilot

Local welcome and theory-library preview. The current entry page, molecule
viewers, chemical core, molecular assets and all twelve lesson JSONs are kept.
No replacement of the published application is performed by this folder.

## Build and open

Requirements: Node.js24+ with npm, Python3.9+.

```sh
cd react-preview
npm ci --ignore-scripts
npm run build
```

Serve the **repository root**, not just dist (the preview links to existing
assets/player files outside its folder). For example, from the repository root:

```sh
python3 -m http.server 8013 --bind 127.0.0.1
```

Open `http://127.0.0.1:8013/react-preview/dist/`.
The existing development server can be reused if it already serves this root.
The library URL is `react-preview/dist/#/library`; hash navigation keeps refresh
working on a static server without special rewrite rules. The built files use
relative paths and assume this two-level location under the repository root.

## What is actually React

React owns the preview root, route state, modal state and rendering. The library
uses `LibraryPage`, `LessonCard`, `Lesson` and `Formula` components with semantic
categories/lessons/formula data, rather than a replay of the old library DOM tree.
`SiteHeader`, `SiteFooter`, `FeatureCard` and `PanelDialog` retain the original
welcome/shared-shell bridge. That bridge creates React elements from trusted
node data without raw HTML injection, iframes or execution of embedded scripts.

`tools/sync-content.py` extracts the checked source pages into `src/content.json`
at build time. The library catalog has stable category/lesson IDs, titles,
descriptions, formula tokens/restrictions, topics, player URLs and actual step
counts checked against the existing scenario JSONs. The legacy welcome panels
are parsed as a data literal, without executing JavaScript. Styles and source
hashes are retained. The snapshot is generated data: edit the established source
pages and lesson files, then rebuild. Do not maintain a separate React syllabus.
Read-only parity check: `python3 tools/sync-content.py --check`.

The catalog is the normalized part of this pilot; the welcome/shared shell still
uses the compatibility bridge. Existing app viewers/player remain outside React.
Starting a lesson performs normal navigation to the v51 application; Exit still
returns to the established library. No progress or account storage is added.
Current source scope: nine cards, twelve active lessons; no new educational content.

## Search and category filters

The library searches its titles, descriptions and listed topics, ignoring Greek
accents, letter case and final-sigma spelling. All entered words must match the
combined category/lesson summary. It does not search all lesson-step text.
The category selector combines with search. Dual cards show only matching lessons
and indicate a partial result; unfiltered cards retain the established summaries.
Counts, no-results feedback and a clear control support keyboard/screen-reader use.
Filters remain while navigating welcome/library inside the React app. Refresh or
leaving for the legacy player resets app state; no local storage/account is added.

Read-only behavior check, from repository root:
`node docs/checks/test-react-library-search-20261026.mjs`.

## Tooling and distribution

React/React DOM19.3.1 and Vite8.3.5 are pinned by package.json/package-lock.json.
This pilot used a checksum-verified portable Node24.22.1 under `/tmp`, without
installing Node system-wide. Its temporary location is not a permanent project
dependency; the requirements above describe rebuilding on another machine.

`node_modules/` and `dist/` are ignored locally. The React/React DOM MIT notice in
`public/THIRD-PARTY-NOTICES.txt` is copied into the build. Build output can be
reviewed locally; publication needs a separate user instruction.

The stable `thesis-work` branch remains at3673c390. The first reviewed pilot is
saved locally at e8d9bb4 on `react-library-pilot`; subsequent reviewed work stays
on that branch. No push/publication is implied by a local save.

Scope and verification: [structured library](../docs/REACT-LIBRARY-20261026.md).
The [first pilot record](../docs/REACT-PILOT-20261026.md) is historical.
## Three-molecule 2D integration pilot

The agreed names are **Namelecule — Κύρια έκδοση** for the established application
and **Namelecule React — Δοκιμαστική έκδοση** for this local branch.
Open `react-preview/dist/#/viewer`. The labeled molecule selector offers existing
ethanol, 2,3-dimethylbutane and propanone, with their Greek titles/formulas from
`src/molecules.json`. That small catalog is shared by React and the host generator;
it references existing molecule IDs and contains no new MOL/coordinate data.

React owns mode/zoom controls, selection, loading/error/retry and mount lifecycle.
The same iframe stays loaded across molecule changes. The bridge calls existing
`fSelectMol`, retaining mode and resetting zoom as the legacy application does.
While a molecule change is pending, the old graph is hidden; only a response for
the latest request ID, intended molecule and mode can reveal it. Controls remain
usable during a switch so rapid choices are processed in order. Retry/remount
starts again at ethanol, condensed mode and default zoom.

`MoleculePreview` sends only whitelisted molecule/mode/zoom messages to a dedicated
same-origin iframe. Both sides check origin, source window, protocol/session;
request IDs discard stale replies. Cleanup removes listeners/timers and unloads
the frame. This is lifecycle/DOM separation, **not a security sandbox**.

`tools/build-viewer-host.py` generates ignored `public/viewer-host.html` from the
unchanged `mulermoc-nom-51.html`, adds relative base/layout CSS and the classic
`public/viewer-host-bridge.js`, injects the catalog's allowed IDs into that script,
and strips analytics from this generated copy. Build the host before using it;
the standalone bridge source contains the build-time ID placeholder.
The original page, engine/viewer/data/teaching/scripts/MOLs remain unchanged.
The bridge uses the complete existing SVG post-processing pipeline; it does not
draw a replacement molecule. The generated page hides authoring controls but
retains JSME's text-measurement DOM. Do not hide all body children: doing so changes
atom-label metrics. Read-only parity: `python3 tools/build-viewer-host.py --check`.

This is **not a native React renderer or a 2D-only dependency bundle**. Legacy
startup still primes/loads JSmol and 3D resources before the bridge hides 3D;
molecule selection still uses its existing 3D loading path. Existing network/CDN
dependencies and possible legacy JSmol failures remain. Loading has a 90-second
deadline and commands a 10-second deadline, with explicit retry/fallback.
The legacy uniform atom-size/fit rules also remain; a small mobile molecule can
be enlarged with existing zoom. No offline, Safari/all-browser or full-library
viewer certification is claimed by this three-molecule pilot.

Current checks/report: [molecule selection](../docs/REACT-MOLECULES-20261026.md).
The [one-molecule viewer record](../docs/REACT-VIEWER-20261026.md) is historical.

## React name-analysis panel

`NameAnalysis.jsx` displays the existing name components beside the molecule
(below it on narrower screens). Labels, Greek euphony letters and explanations
come from the legacy engine's rendered name DOM; React does not assemble another
chemical name or author new theory. For these three molecules the explanation
texts are plain text. They are rendered as React text, without raw HTML.

A component button invokes the existing `.nameCompBox` click handler through the
v4 bridge, including toggle-off, highlight colors and the existing numbering
animation. The iframe renders the highlights/numbers itself; React adds no timer
or replacement atom mapping. Mode/zoom preserve the engine's current selection;
a new molecule, retry or remount clears it according to the existing behavior.
Component commands are bound to the current molecule and existing visible IDs.
The parent validates bounded component IDs/labels, unique IDs, at most one active
component and explanation text before accepting a message. Stale/malformed data
cannot replace current analysis. Native buttons expose `aria-pressed` and support
Enter/Space; the explanation is a polite live region.

Current verification: [name analysis](../docs/REACT-ANALYSIS-20261026.md).
Focused Firefox checks (repository root, local server8013/BiDi9237 required):
`python3 docs/checks/test-react-3d-regression-20261026.py`.
The optional `--layout-only` performs the six final desktop/mobile spacing checks.
The earlier one-/three-molecule reports describe their respective prior stages.

## Visible 3D pilot

The same three molecules now have React 2D/3D buttons. Native JSmol mouse/touch
interaction and existing 3D zoom are retained; name-component buttons invoke
unchanged legacy 2D/3D highlights and numbering. 2D form controls are disabled
while 3D is visible. Returning to 2D preserves its form/zoom and current analysis;
a molecule switch retains the chosen view/form and resets selection/zoom as before.

The v4 bridge verifies the actual loaded SDF URL, atom serials/elements and bond
edges/orders against the existing parsed 3D data. An ordered JSmol script marker
also confirms completion of queued loading/style commands. Adapter commands run
serially so native zoom cancellation cannot discard later commands. Until confirmed, the
frame is hidden and analysis disabled; stale replies cannot reveal an old model.
The generated host sets JSmol's existing `Info.script`/`defaultDirectory` to the
repository root, because JSmol resolves `load`/`script` relative to document
location rather than HTML base. Original HTML, JS, MOL/SDF and cameras are unchanged.

A ResizeObserver keeps the public JSmol canvas size aligned to the host. This is
still the complete legacy runtime inside a same-origin frame; no native React
chemical renderer, independent chemistry engine, offline support or replacement
of the main application is claimed. Both views require the legacy dependencies
and verified 3D startup. Existing load/command deadlines and retry apply.

After a rebuild, use a fresh query URL if a local browser cached the previous
index: `react-preview/dist/?v=3d-20261026#/viewer`.
Focused checks: `docs/checks/test-react-3d-browser-20261026.py`,
`test-react-3d-regression-20261026.py`, `test-react-3d-transitions-20261026.py`
and `test-react-3d-static-20261026.py`.
See [3D implementation and verification](../docs/REACT-3D-20261026.md).

Review correction (2026-10-27): both zoom buttons remain disabled throughout any
pending view/model transition, including 3D to 2D during a molecule load.
> **2026-10-27 — alkane lesson pilot:** the alkanes library action now opens
> `#/lesson/alkanes/step/1` within React. React owns Previous/Next, step count,
> history/deep links, loading/retry and Exit; the21unchanged source steps are
> still rendered by the native52scenario player in a separate generated host.
> Text, optional closed rules, progressive name visibility, numbering, final
> menu exploration and3D use that existing engine. This is incremental playback
> integration, not a rewritten React lesson renderer. The other11lesson links
> remain standalone. No main/core/molecule/scenario/dependency change.
> Build additionally generates `public/lesson-host.html`; read-only parity:
> `python3 tools/build-lesson-host.py --check`. See
> [lesson checks and limitations](../docs/REACT-LESSON-20261027.md) and current
> session notes for actual verification and independent review status.
