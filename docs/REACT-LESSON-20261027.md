# React alkane lesson pilot — 2026-10-27

Approved scope: integrate only the existing21-step alkane lesson into the React
shell. Main/source/core/molecules/scenarios remain unchanged; no quiz, new
educational content, dependency, commit, push or publication.

## Implementation and boundaries

- React `LessonPreview` owns Previous/Next,21-step counter, keyboard navigation,
  strict `#/lesson/alkanes/step/N` routes, browser history, loading/retry and
  return to the React library. Invalid/out-of-range routes show an error without
  starting an iframe. Library filters persist within the same React app session.
- The alkanes library link alone is redirected at render time. The source
  catalog and other11existing lesson links are unchanged.
- A separate generated same-origin `lesson-host.html` retains the actual52HTML,
  script order, DOM, native scenario validator/apply path, note sanitizer and
  scientific representations. Only duplicate shell/navigation chrome and
  analytics are removed/hidden. React does not reimplement teaching rules.
- The bounded lesson bridge calls the existing scenario functions and checks
  origin/source/session, lesson, command ID, step bounds and source titles.
  Parent ACKs must match the requested step; rapid route changes converge on
  the latest request. Pending content is hidden.90s startup/18s command parent
  limits and a15s host apply deadline fail closed with retry.
- The optional final3D readiness gate verifies the actual SDF file, atom types,
  connectivity/bond orders and an ordered Jmol script marker. Native exploratory
  menu/representation/name/rule controls remain native.2D sequential numbering
  remains visible as the existing animation rather than being replaced.
- The host measures native flow height, reserves the existing viewer pixel
  budget and invokes the existing fitter on height-only iframe resize. This
  prevents a longer note from shortening the following molecular viewport.
  The first parity run exposed this at expanded step18; the fix is only in the
  React host. Height messages are bounded420–12000px, not arbitrary CSS/HTML.
- Listeners, observers, timers and host overrides are cleaned up on unmount/
  pagehide. Escape in either context returns to the React library.

This is a same-origin compatibility adapter, not a security sandbox, native
React molecular/lesson renderer or completed migration. Main remains runnable.
The molecule-viewer component and its existing bridge are byte-identical to the
task baseline. Native legacy code still supplies every molecular drawing.

## Existing lesson content

Unchanged `scenarios/alkanes-nomenclature-branches.scenario.json`,21steps:
ethane, butane,2-methylpentane,2,3-dimethylbutane and
3-ethyl-2,5-dimethylhexane. Existing menus also allow the lesson's own selected
library examples. No molecule, formula, nomenclature, hydrogen, coordinate,
camera, rule, note or learning sequence was generated or edited here.

## Developer evidence

- Standard build passed:26modules, JS315.22kB/88.79gzip, CSS9.97kB/2.25gzip.
  The pre-existing tert-butyl-ether stored-chain diagnostic is unchanged.
- Real Firefox: all21steps via Next and20reverse transitions; same stored
  notes, modes, hidden name parts, selected components, numbering, menu and
  final3D. Optional rules start closed, open manually and close on next step.
-21/21 exact native main state/text/rule/name/visibility/highlight/numbering/SVG
  comparisons at equal per-step viewport and the same host-only layout CSS
  applied in memory to standalone main. Actual final3D atom/bond/main-chain
  snapshot also matched. This is controlled parity, not a comparison between
  different screen sizes or a new independent chemical certification.
- Reload/deep-link, Back/Forward within the lesson and across its entry,
  parent/iframe keyboard, malformed/stale/wrong-source messages, invalid routes,
  native controlled failure hook, retry, rapid routes, mobile390px, final menu
  selecting butane, pending unmount and clean remount passed.
- Actual wrong3D-model host timeout15.15s; correct retry at step21. Separate
  pending3D/remount/filter-preservation and route/viewer roundtrips passed.
- Existing viewer3D-transition suite passed unchanged logic on Firefox9238:
  ordered zoom ACKs, pending guard, wrong-model timeout9.15s, retry/remount.
  Existing20Greek library search cases passed.
- Final full browser/lifecycle/routes/viewer-transition runs captured zero
  JavaScript errors. Earlier completed21/21parity runs each captured one known
  native CDN teardown callback (`setDisplay` then `updateJS`, null viewer).
  Both raw runs are retained separately; no event was suppressed or repaired.
- Static baseline1401paths:1395protected files unchanged,1376outsideReact and
  the two journals. All main/core/MOL/SDF/scenario/catalog/lockfile bytes stay
  protected. Source/host checks, JS/Python syntax and whitespace checks passed.
- Desktop1500px and mobile390px screenshots were visually inspected. Both
  parent and child mobile documents fit their viewport widths.

Two initial harness corrections were needed: attach the iframe context before
querying it, and accept BiDi's discarded-context response when Escape removes
the target on keyDown before keyUp. Later error classification now derives exact
known CDN signatures from the existing v51/v52 control instead of an incomplete
one-message whitelist. No browser exception handler filters runtime errors.

## Evidence, review and remaining scope

`checks/react-lesson-before-20261027.json`, `test-react-lesson-*` scripts and
`react-lesson-{browser,lifecycle,routes,viewer-transitions,static}-20261027.json`;
compressed21-step capture and initial raw teardown runs are retained in checks.
Actual screenshots/before bytes are under `/tmp/namelecule-react-lesson-20261027/`.
The existing viewer transition script is reused with only port9237→9238 and its
temporary output path changed. Test artifacts are not production features.

The exact frozen review target is `checks/react-lesson-reviewed-target-20261027.json`.
Reviewer identity, independent findings and final disposition are recorded in
SESSION-NOTES/YANNIS-CONTRIBUTIONS; build/browser execution above is Developer
evidence. The Reviewer must inspect actual files without writes.

Known pre-existing JSmol teardown errors are documented in V52-SYNC and
`checks/v52-jsmol-lifecycle-control-20261027.json` (raw events retained). A final
zero-error run does not prove their absence in every navigation. Safari,
screen-reader testing, Drupal, offline mode and the other11lessons in React are
not claimed. No full283-step rerun or new chemistry/conformer validation.

Upstream checked c2aab76; last actual sync93b759f. Its Full-height/rails/tooltip/
play-bar and preceding author/date/Save-JSON changes are not integrated here,
because main must remain unchanged. Core52 SHA256 remains
72ac4b4ae3c9bfaa90fde650bf588ed6430acec9ad3ceef72a94a27ad6750e3a.
