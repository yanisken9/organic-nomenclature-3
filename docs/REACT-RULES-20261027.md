# Namelecule React — optional rules, 27/10/2026

Approved scope: display the existing main52 naming-rule content in optional
React panels, initially closed, with manual opening. Keep the main edition
available and unchanged. No publication, commit, push, new chemistry, educational
method, dependencies or lesson-player/editor migration.

## Implementation and boundaries

Eight React runtime/build sources: NameAnalysis.jsx, MoleculePreview.jsx,
RulePanels.jsx, rule-data.js, rule-schema.json, preview.css,
public/viewer-host-bridge.js and tools/build-viewer-host.py. The README and
checks/documentation accompany the implementation. All other pre-existing source,
including the catalog and main/core/MOL/SDF/scenario files, is protected against
the task-start baseline. Existing uncommitted work is not attributed to this task.

The original fShowRule generates the title, explanation, table and selected rows.
The adapter reads that DOM without changing the engine or its rules. The shared
schema permits text and eight element types, an explicit class list and bounded
row identifiers. React validates exact node fields, a maximum of two panels,
12 levels, 600 nodes and 20,000 text characters per rule before rendering. No
HTML injection, DOM event attributes, styles or arbitrary elements are accepted.
Text-looking markup remains literal text; sub/sup and A/B row classes survive.

Each rule has an accessible native button with aria-expanded/aria-controls and
an initially hidden body. Component/molecule/naming changes close the panels.
A pending component command closes and disables the previous rule until the
latest valid ACK, preserving the existing molecular animation. Zoom/view/form
ACKs retain the current panel when the selected component is unchanged.

Only content actually supplied by the existing mechanism is shown. In free
exploration, commonAlkyl1/2 have no rule and the supplemental alkoxy table remains
scenario-gated. These pre-existing conditions were not silently changed. The
serializer/renderer can carry two existing panels if the source supplies them;
a synthetic fixture tests this contract without claiming real free-explorer
alkoxy availability or changing a scenario.

## Developer verification actually performed

- Build passed, 25 modules; JS308.15kB /86.90kB gzip, CSS8.65kB /2.02kB gzip.
- Actual Firefox: 237 exact source-DOM/React comparisons, including selected and
  deselected states and extra transitions. All visible components were exercised
  for a representative molecule from each of the19existing series. Covers five
  rule families, sub/sup, selected/A/B rows, initially closed panels, manual
  keyboard Space/Enter, rapid component selections, delayed ACK, molecule/naming
  reset and retention over zoom/view/form. Zero JavaScript errors.
- 1500px and390px layouts passed overflow checks; screenshots under /tmp were
  visually inspected. Both common/systematic ether paths retained source behavior.
- Controlled two-panel fixture: independent toggles, literal HTML-looking title/
  text and sub rendering passed. Invalid script-element message was rejected.
  This is explicitly synthetic adapter evidence, not a new lesson or source rule.
-29 data-contract cases passed, including allowed Greek row IDs, duplicate IDs,
  unknown tags/classes/fields, invalid children and node/depth/text budgets.
- Existing actual-browser lifecycle checks passed: pending naming then model
  switch, iframe-error/retry, unmount/remount. Existing transition regression
  passed: ordered zoom ACKs, pending3D-to2D guard, actual incorrect-model failure
  at9.18s, retry and pending-unmount/remount. Zero JavaScript errors in both suites.
- Content/host/catalog --check,126IDs/377forms/filter checks, JS/Python syntax
  and git diff --check passed. Catalog generation repeats the pre-existing
  tert_butyl_isopropyl_ether calculated-vs-stored-chain diagnostic; source catalog
  equality passes and no molecular/naming data were changed.
- Baseline1361files;1353protected paths byte-identical, including1339outside React
  and the journals. Both HEAD168e3cec01f941a84d40bbe0dc07156e7baa35d0 and stable
  thesis-work3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab unchanged. No core changed.

Evidence: checks/react-rules-*.json and test-react-rules-*; reused lifecycle and
transition scripts are recorded in their JSON outputs and session notes.
Baseline: checks/react-rules-before-20261027.json. Prior React bytes for diff:
/tmp/namelecule-react-rules-20261027/before/ (temporary, not a durable backup).
Frozen target: checks/react-rules-reviewed-target-20261027.json. Independent
Reviewer findings, identity and final disposition are recorded in current session
and contribution notes; browser/build execution above is Developer evidence.

## Limits

This remains a React UI around the existing same-origin engine/renderer iframe,
not a completed native-renderer or lesson-player migration. All126molecules were
not re-tested in every rule state; representative coverage plus unchanged engine/
assets is stated precisely. No fresh universal IUPAC, molecular geometry or full
283lesson-step certification is claimed. Safari runtime, real mobile touch,
assistive-technology behavior, Drupal and real CDN outage were not tested.
Known pre-existing JSmol lesson-lifecycle behavior remains outside this scope.
The current result is local only; publication remains explicitly deferred.
