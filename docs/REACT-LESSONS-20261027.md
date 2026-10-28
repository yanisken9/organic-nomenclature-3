# Shared React theory playback — 2026-10-27

Approved extension of the reviewed alkane pilot to the other11existing lessons.
All12library actions now use one React lesson route/component and one generated
native52host. No new lesson content or rendering engine was introduced.

## Scope and implementation

- `main.jsx` resolves only existing catalog lesson links to
  `#/lesson/<id>/step/N`. Shared route validation rejects unknown IDs and
  malformed/out-of-range steps. Headings and standalone fallback URLs come from
  the existing catalog; source content.json is unchanged.
- `LessonPreview.jsx` uses the selected lesson's ID/count/path and a keyed
  remount for course changes. Each host gets a fresh session. Within a course,
  latest-request/ACK guards, Previous/Next, history, loading/retry and Exit remain
  the reviewed mechanism. Old-course/session messages cannot apply to a new one.
- `build-lesson-host.py` generates an allowlisted12-lesson registry from the
  actual source JSONs and catalog, validating unique IDs, paths, counts and
  per-step titles. `lesson-host-bridge.js` accepts only its requested catalog
  ID/scenario pair, plus the existing message source/origin/session/ID checks.
- Authored pixel heights retain the pilot's native budget fitting. The alkene
  lesson has Auto heights: these now use an independent bounded outer viewport,
  preserving native internal scrolling instead of deriving a height from their
  own auto-sized viewers. A validated viewport message handles height-only
  parent resize. Native fitter/coordinates are reused; step changes reset the
  child's scroll position. No JSON height setting changed.
- The native validator still derives effective menu visibility from its stored
  molecule subset. Legacy `show.menu` flags are intentionally ignored by native52;
  this extension does not replace that behavior.
- Notes, rule tables, name parts, common/IUPAC naming, highlights, numbering,
  native menus and2D/3D remain the original52scenario/player behavior. This is
  integration into React navigation, not a full React renderer rewrite or a
  security sandbox. No dependencies, CSS, package/lock or molecule-viewer code
  changed in this extension. Main/core/MOL/SDF/scenarioJSON remain unchanged.

## Existing lessons retained

| Catalog lesson | Steps |
|---|---:|
| Αλκάνια |21|
| Αλκένια |22|
| Αλκίνια |22|
| Αλκαδιένια |23|
| Αλκενίνια |23|
| Κορεσμένες μονοσθενείς αλκοόλες |20|
| Άλλες αλκοόλες |22|
| Κορεσμένοι μονοαιθέρες |27|
| Κορεσμένες μονοσθενείς αλδεΰδες |24|
| Άλλες αλδεΰδες |26|
| Κορεσμένες μονοσθενείς κετόνες |25|
| Άλλες κετόνες |28|
| **Total** |**283**|

## Developer verification actually performed

- Standard build passed:26modules, JS315.71kB/89.00gzip, CSS9.97kB/2.25gzip.
  The existing tert-butyl-ether stored-chain diagnostic remains unchanged.
- Actual Firefox: all12React library actions,283forward step transitions,
  source notes/modes/name visibility, correct course headings/counters, initially
  closed rule containers and reverse boundary transitions.12mobile390px layouts
  fit parent/child widths. Six representative screenshots were captured; ethers
  and complex-ketone desktop/mobile views were visually inspected.
-283/283exact state/text/rules/name/hidden/highlight/numbering/SVG comparisons
  with standalone main at matched per-step viewport and host layout CSS applied
  only in browser memory. All12final actual3D atom/bond/main-chain snapshots
  also matched. This is controlled source parity, not new chemical certification.
- Ether lesson preserves9common and18IUPAC steps. All authored alkoxy-reference
  steps remain closed on entry; manual main alkoxy table at step5 opens and the
  next reference closes. Existing generic/supplemental table DOM is preserved.
- All12cross-course session/bounds checks passed, including stale/wrong-course/
  wrong-source replies, malformed/prototype/encoded routes, manual rule tables,
  cross-course Back/Forward/reload and late-callback isolation.
- Auto viewport1000→700→1100height-only changes, invalid viewport packets and
  internal scroll reset passed. Actual wrong3Dmodel timeout15.23s in Other
  ketones, correct course/step retry, pending3D→ether course change and Exit passed.
- Existing viewer transition suite passed with only test port/output-path
  substitution: ordered zoom ACKs, pending guard, actual wrong-model timeout
  9.28s, retry/remount. Existing20Greek library-search cases passed.
- Main283-step run recorded0JavaScript errors. Lifecycle run recorded1known
  native CDN `setDisplay`/null-viewer teardown error; its full raw event is kept.
  Historical native51/52control reproduces the signature. Unexpected errors0.
  Viewer transition run recorded0errors. No runtime error handler was suppressed.
- Static task baseline1420paths:1412protected files unchanged,1391outsideReact
  and the two journals. All source lesson/catalog/molecular/core/lock bytes stay
  protected. Registry/source parity, host/content checks, syntax and diff checks
  passed. HEAD and stable branch refs unchanged.

The first Auto-height parity run exposed the old content-size feedback and was
discarded after the bridge fix; the new runtime was tested afresh. Later harness
corrections used the native validated menu visibility and null-safe optional
rule DOM, including the separate alkoxy container. Completed5then7lesson chunks
were resumed only after checking identical runtime fingerprints. All final283
comparisons and12scenes belong to the same final runtime, not mixed code versions.

## Evidence, independent review and limits

`checks/react-lessons-before-20261027.json`, `test-react-lessons-*` and final
browser/lifecycle/viewer-transitions/static JSON results; compressed283-step
capture contains runtime fingerprints, actual snapshots,12scenes and all raw
recorded JavaScript errors. Actual screenshots and before bytes remain temporary
under `/tmp/namelecule-react-lessons-20261027/`. The read-only frozen manifest is
`checks/react-lessons-reviewed-target-20261027.json`; final Reviewer identity,
findings and disposition are recorded in SESSION-NOTES/YANNIS-CONTRIBUTIONS.
Build/browser/fault execution above is Developer evidence, not independent rerun.

No commit, push, publication or new backup ZIP. No Safari, screen-reader, Drupal,
offline, exhaustive exploratory interaction in all126molecules, new IUPAC audit
or conformer generation. Native intermittent JSmol teardown remains unresolved;
zero errors in the large parity run does not prove it fixed. Every-frame animation
timing and every supplementary-rule interaction are not claimed by snapshot parity.

Upstream read-only check: HEADa40beec0cc89d40fb90ef84c6d619963ebca136b, preceding
2adb973splits suffix locants/forces single-line components; a40beec enlarges the
author handle. No core update. Last actual sync remains93b759f; these changes
overlap name/teaching behavior and remain deferred with prior updates to preserve
main. CHANGELOG SHA256756304901ecad7fa29e432e6dc1a6ef68058756f8f93c45cbcd2828e1ed03f54.
Core52 SHA256 remains72ac4b4ae3c9bfaa90fde650bf588ed6430acec9ad3ceef72a94a27ad6750e3a.
