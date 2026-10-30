# Namelecule React — existing126molecule catalog, 27/10/2026

The user approved expanding the React viewer from three to all126existing
molecules, with an explicit condition: preserve the main edition as a fully
available alternative. No main runtime, core, molecule asset or scenario is edited.
Task-start baseline: `checks/react-catalog-before-20261027.json` (1336files).
Git base168e3cec01f941a84d40bbe0dc07156e7baa35d0, branch react-library-pilot;
stable thesis-work remains3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab.
Earlier uncommitted3D/v52 work is pre-existing, not newly authored by this task.

## Behavior and boundaries

`react-preview/tools/sync-molecules.mjs` runs the existing core52/data52 in a
trusted build-time Node VM, using only a fixed-column MOL graph-access adapter
for the four JSME methods the engine consumes. Existing naming, parent selection
and classification functions generate the metadata. It reads the main teaching
file's series labels, counts atoms in the existing explicit-H SDFs for formulas,
and produces `src/molecules.json`; no other naming or chemistry engine is added.
This is metadata generation, not chemical certification of the source library.
The engine's existing stored-chain warning for tert_butyl_isopropyl_ether is
retained; its generated name agrees with the actual main browser runtime.

The generated126IDs include the original case-sensitive Oxopropanoic_acid.
The catalog is ordered by carbon count with stable ties, then grouped in the
selector by19existing series. Greek name/common-name/formula search ignores
accents, case, final sigma and subscript-digit typography; words combine with
the series filter. Filtering never silently switches the current model: a
separate optgroup retains the current selection outside the results. Empty
feedback and clear/focus behavior are explicit. No persistent storage is added.

The same iframe and2D/3D/name-analysis bridge are retained. Both sides still
validate source/origin/session, requested molecule/view/form, model data and
request IDs. Default/retry remains ethanol. All377available2Dforms are exposed;
methane has no skeletal source, so its skeletal radio is disabled and switching
to it from skeletal falls back to condensed, matching the main application.
No replacement MOL, coordinates, camera, explicit H or double-bond function is
introduced. Main files are read by the build/runtime without editing them.

All three React welcome Explore links stay in the React viewer. Theory lessons
still navigate to the established standalone52player. This stage does not add
a React common/systematic toggle, optional theory-rule panels, speech, image
export, authoring or a native chemical renderer. Common names are search metadata.
The primary edition retains those existing controls. Both editions share legacy
assets/dependencies; this is not a standalone/offline/security-isolated release.

## Developer verification

- Build passed:22modules, JS304.83kB/85.76kB gzip, CSS5.30kB/1.40kB gzip.
- Actual Firefox: all126selections loaded their actual SDF; catalog titles,
  classification and React name components matched the existing engine. All377
  available2Dforms were captured in one unchanged iframe, including methane's
  disabled skeletal choice and fallback. Greek/formula/series/empty/clear/focus
  checks passed. Desktop1500px and mobile390px fit without page overflow; their
  screenshots were visually inspected.
- All377snapshots matched the unchanged standalone main52 exactly at the same
  viewport/internal canvas: canonical SVG geometry/text/styles/viewBox, names,
  common names, atoms/bonds, parent chain and visible component/explanation data.
- Actual visible3D and component selection/deselection/2D return passed for one
  existing representative of each of the19series. All126underlying SDF loads
  also passed the existing bridge's file/atom/bond/ordered-script readiness gate.
  This does not constitute detailed visual/conformer validation for all126.
- Actual welcome navigation: all three Explore links target React; a real click
  loads ethanol, and returning to the library retains all12existing lesson links
  and the main-version fallback.
- Existing transition suite passed on this final build: ordered zoom ACKs,
  pending3D→2D disables premature zoom, real incorrect-model failure after9.28s,
  retry and unmount/remount. No JavaScript errors in these browser runs.
- Read-only generators/host parity, JS syntax/Python AST, molecule-filter checks,
  20existing library-search cases and Git whitespace checks passed.
- All1316baseline files outside React and the two mutable journals are byte
  identical, including main entry/welcome/library, all core versions, molecule
  data/MOL/SDF and12scenarioJSONs. No new non-React/non-document runtime file.

The first harness attempts used premature assertions before async ACKs, an
unquoted numeric CSS attribute selector and a non-equivalent baseline canvas.
Only the harness was corrected. Completed126/377captures were retained and the
remaining comparisons resumed against the same source/build hashes, instead of
reloading all126again. `react-catalog-capture-20261027.json.gz` preserves those
snapshots and the runtime fingerprint; `test-react-catalog-browser-20261027.py`
runs the full check by default (`--resume` requires matching saved /tmp capture).
The capture fingerprint was attached after capture while verifying that runtime
sources/build had not changed; it is Developer evidence, not independent replay.

Artifacts are `checks/react-catalog-{browser,capture,static,transitions,routes,
before}-20261027.*` and corresponding test scripts. Transition evidence comes
from reusing `test-v52-react-transitions-browser-20261027.py`, not a new engine test.

## Limits and review record

No main application bug was repaired here. Known legacy JSmol lifecycle errors
in lesson transitions remain documented by the earlier v52 work; these zero-error
catalog runs do not establish their absence in other flows. The unchanged283
lesson steps were not rerun. No Safari, screen-reader, real mobile-touch, actual
offline/CDN-outage, OS-clipboard or Drupal test was performed. No new IUPAC or
pedagogical claims, molecules, lesson content or dependencies are introduced.

Final target and independent Reviewer outcome are recorded in SESSION-NOTES and
YANNIS-CONTRIBUTIONS after the frozen review. Browser/build runs above are Developer
execution. Nothing is committed, pushed or published. No core changed in this task.
