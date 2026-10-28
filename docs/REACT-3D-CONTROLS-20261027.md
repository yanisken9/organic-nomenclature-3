# React — native 3D controls, 2026-10-27

Approved scope: expose existing C–H visibility, atom symbols, three molecular
representations and rotation in the React molecule viewer. The main conversation
implemented the change. No chemistry/teaching changes or specialist agents.
Independent final review targets are frozen separately; its outcome is recorded
in SESSION-NOTES and YANNIS-CONTRIBUTIONS after review.

## Behavior and files

- `react-preview/src/MoleculePreview.jsx`: 3D-only native select/checkboxes,
  expected controls state and reply validation. Controls are disabled until the
  latest ordered model/script ACK; old controls cannot queue behind a mode/zoom.
- `react-preview/public/viewer-host-bridge.js`: validated model/view-bound
  commands, rechecked at execution, invoke original native52 UI handlers:
  `#hydrogensCheck`, `#atomSymbolsCheck`, `#rotateCheck`, `#dropLi0/1/2`.
  No replacement Jmol styling logic. Existing v4 session/origin/source/ID,
  actual model graph and script completion gates remain.
- `react-preview/src/preview.css`: wrapping control row and bounded select.
- React README, generated viewer host/dist and scoped evidence/docs.

C–H hiding keeps O–H hydrogen visible; no atoms/bonds/coordinates are removed.
Preferences persist across molecule/naming/view changes according to the native
engine. Retry/remount starts with H/symbols on, ball-and-stick, rotation off.
The original 2D forms, CHn, numbering, names, rules and PNG workflow remain.
React remains an interface around the original renderer, not a complete renderer
rewrite or independent/offline distribution.

## Verification actually performed

- Build passed:26modules, JS317.30kB/89.44gzip, CSS10.20kB/2.27gzip. Existing
  `tert_butyl_isopropyl_ether` calculated/stored-chain diagnostic retained.
- Real Firefox:42/42 exact native main52 render comparisons at equal viewport.
  Ethanol, ethyl-isopropyl ether and the complex branched unsaturated diketone:
  all3styles × H on/off × labels on/off plus numbered-chain label states.
  Compared actual atom identities/xyz/visibility/colors, bond graph/orders/
  visibility/colors/radii, sphere sizes, actual labels, selected atoms, chain,
  numbering echoes and explanation; ignored only echo screen bounding boxes.
- Actual ethanol:5 C–H hydrogens hidden, O–H hydrogen visible. Rotation changes
  camera quaternion, stops on request and leaves xyz unchanged. Native2D SVG/
  name/chain snapshots identical before/after controls for all3representatives.
- Preferences across methane/ether/common-name/2D/zoom; keyboard Space;
  invalid/stale/wrong-model/2D commands and malformed/mismatched ACKs rejected.
  Delayed real model gate disables duplicate controls and style behind zoom;
  pending control→new molecule completes on latest state.
- Real wrong-model failure after9.09s; retry resets native defaults. Leaving
  rotating viewer removes its iframe; re-entry creates a fresh default session.
-1500/390px controls fit without page overflow; both screenshots inspected.
  These tests preserve the existing camera/zoom policy, not new mobile framing.
- Existing viewer transition suite passed: ordered zoomACKs, pending3D→2D guard,
  wrong-model9.25s failure/retry and unmount/remount; PNG pending-unmount passed.
  Additional smoke downloaded a valid native1200×733PNG after3D→2DCHn,
  confirmed12library links and executed other-ketone lesson steps1→2.
-1440-file task-start baseline:1426 protected files unchanged, including1403
  outside React/journals. All core/Main/MOL/SDF/scenarioJSON/catalog/lesson-host/
  dependency files unchanged. HEAD168e3cec and stable thesis-work3673c390 unchanged.
  Generated host checks, content check, PythonAST, bridgeJS syntax and diff passed.

Browser scripts and raw results: `docs/checks/test-react-3d-controls-*.py`,
`react-3d-controls-*.json`, compressed capture. Before source bytes and screenshots
are under `/tmp/namelecule-3d-controls-20261027/` (temporary). Existing transition
and PNG-lifecycle logic reused unchanged; temporary copies only adapt Firefox
port/output destinations. No283-step rerun: lesson runtime/content unchanged,
protected by byte hashes, with a focused live lesson smoke instead.

## Diagnostic history and limits

Initial strict-zero-error run completed all42 comparisons and functional checks,
then failed its final error assertion on one previously documented external
JSmol `setDisplay`/null-viewer resize/lifecycle error. Its raw failed report is
retained as `react-3d-controls-browser-initial-strict-20261027.json`. The test
classifies only that exact known CDN error separately and keeps unexpected
errors blocking; no production error suppression or lifecycle fix was added.
The full repeat used identical runtime hashes and passed with0JavaScript errors.
Existing transition/PNG smoke/lifecycle runs also had0errors. A clean repeat does
not prove the intermittent library issue fixed. Historical native51/52 controls
and earlier shared-lesson tests already recorded the same signature.

Not tested: Safari/real touch/assistive technology/offline/Drupal/every126molecule
control combination. No new molecular-accuracy or conformer-quality certification.
The42comparisons establish reuse/parity, not independent chemical validation.

UpstreamHEAD a40beec0cc89d40fb90ef84c6d619963ebca136b and CHANGELOG rechecked,
unchanged from last check. Last actual sync93b759f. Previously reviewed pending
upstream updates remain deferred to preserve Main; no fetch/merge/ref changes.

No core file changed. Core52 SHA256:
`72ac4b4ae3c9bfaa90fde650bf588ed6430acec9ad3ceef72a94a27ad6750e3a`.
No commit/push/publication/dependency install. Open locally:
`http://127.0.0.1:8013/react-preview/dist/?v=3d-controls-20261027#/viewer`.
