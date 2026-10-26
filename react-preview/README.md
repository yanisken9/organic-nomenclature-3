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
