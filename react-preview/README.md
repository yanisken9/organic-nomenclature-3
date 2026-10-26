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

React owns the preview root, route state, modal state and rendering. Shared
`SiteHeader`, `SiteFooter`, `FeatureCard`, `LessonCard` and `PanelDialog` components
render the existing page content. A small node renderer bridges trusted source
HTML to React elements; it does not use `dangerouslySetInnerHTML`, mount the old
pages in iframes, or run their embedded script.

`tools/sync-content.py` extracts the checked source pages into `src/content.json`
at build time, including formulas, text, CSS, links and source hashes. The legacy
welcome panels are parsed as a data literal, without executing JavaScript.
The snapshot is generated data: edit the established source pages, then rebuild.
Read-only parity check: `python3 tools/sync-content.py --check`.

This compatibility bridge is a pilot, not the final normalized content model
for a full React migration. Existing app viewers/player remain outside React.
Starting a lesson performs normal navigation to the v51 application; Exit still
returns to the established library. No progress or account storage is added.
Current source scope: nine cards, twelve active lessons; no new educational content.

## Tooling and distribution

React/React DOM19.3.1 and Vite8.3.5 are pinned by package.json/package-lock.json.
This pilot used a checksum-verified portable Node24.22.1 under `/tmp`, without
installing Node system-wide. Its temporary location is not a permanent project
dependency; the requirements above describe rebuilding on another machine.

`node_modules/` and `dist/` are ignored locally. The React/React DOM MIT notice in
`public/THIRD-PARTY-NOTICES.txt` is copied into the build. Build output can be
reviewed locally; publication needs a separate user instruction.

Scope and actual verification: [pilot record](../docs/REACT-PILOT-20261026.md).
