# Namelecule React — ether naming, 27/10/2026

Approved scope: add the existing IUPAC/Κοινή choice to the React name panel for
the11existing ethers, preserving their names, components, explanations and2D/3D
highlights. The user requires the main edition to remain unchanged and available
as an alternative. No new chemistry, molecules, educational content or dependencies.

## Implementation

Only four runtime sources change: React `NameAnalysis.jsx`, `MoleculePreview.jsx`,
`preview.css` and `public/viewer-host-bridge.js`. Native radio inputs appear for
ethers only. A naming command invokes the existing main52 handler
`#radioEtherNaming .etherNamingRadio`; React does not compose another common
name or calculate another atom/group mapping. The original systematic catalog
title remains above the viewer, while the analysis follows the selected naming
variant, matching the main application's distinction.

The existing v4 adapter additionally carries the bounded `naming` preference.
Both enum values and the latest requested preference are checked before an ACK
can update React. Naming commands require the actual current ether and matching
molecule ID; the target is checked again when the queued command executes.
Source/origin/session/request/model validation and ordered queue remain intact.

The preference persists across molecule switches as in the main engine; non-ethers
never display the switch. A fresh/retry/remount session starts with IUPAC. A
pending naming change clears old components and hides the graph until the model/
script ACK; radios and zoom remain disabled during that interval. The existing
main handler clears previous highlights and supplies the new explanation/content.

All main HTML/CSS/JS/core/data/MOL/SDF/scenario files are untouched. No core
changed. The existing generated host/bundle is rebuilt locally; no commit,
push or publication. Main files and the remaining React sources are protected
by `checks/react-ether-naming-before-20261027.json` (1350task-start files).
Exact prior React bytes for an independent diff are also retained under
`/tmp/namelecule-react-ether-naming-20261027/before/`.

## Verification status

Build passed:22modules, JS305.60kB/85.98kB gzip, CSS5.63kB/1.45kB gzip. Static
preservation passed for1343baseline files outside the five permitted React
paths and two journals;1328of them are outside React. The126molecule catalog,
12lessons and their original assets remain unchanged. Content/host `--check`,
molecule-filter checks, JS syntax, Python AST and Git whitespace checks passed.

Actual Firefox validation passed444exact comparisons across all11ethers, both
variants, three2Dforms,
all visible component selections and3D states with the unchanged main52 at equal
canvas size. There were zero JavaScript errors in the completed run. The test also exercises
native keyboard input, preference through
non-ethers, invalid/stale/wrong-target messages, pending model gates and mobile/
desktop layout. Completed captures are checkpointed for comparison on the same
runtime hashes. An initial fault-injection harness attempt incorrectly compared
the legitimate ACK sequence against deliberately oversized rejected command IDs;
only the harness was corrected, not application behavior.

Lifecycle checks also passed: a pending naming change followed by a non-ether
selection finishes on the latest model with the proper preference; controlled
iframe-error/retry and unmount/remount restore ethanol/IUPAC. These are controlled
fault injections, not an actual CDN outage. Zero JavaScript errors.

The existing transition regression also passed on this build: ordered zoom ACKs,
pending3D-to2D zoom protection, actual incorrect-model failure at9.23s, retry
and unmount/remount, with zero JavaScript errors.

Final browser/lifecycle/transition results and the independent frozen-target
review are recorded in session/contribution notes and `checks/react-ether-naming-*`.
Browser/build execution is Developer evidence; do not infer independent browser
execution or a completed review until the explicit final record exists.

Known legacy JSmol lesson-lifecycle behavior remains outside this scope. No new
universal IUPAC/conformer certification, full283lesson-step run, Safari, AT,
real mobile touch, actual CDN outage, clipboard or Drupal test is claimed.
The app still uses the established renderer/engine in a same-origin iframe.
