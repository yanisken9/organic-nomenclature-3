# Drawing portion of approved upstream 35d791ee sync — 2026-11-04

Owned runtime path: `js/mulermoc-nom-molview-54.js`. Only
`fMolDraftSyncBar` and `fMolDraftAccept` changed. The before snapshot is
`../before/js/mulermoc-nom-molview-54.js`; upstream base/head are
`02dbcfaf79e23f1933a252e0b1f6671049d39b78` /
`35d791ee9d6bdb8566d3adca1a1bdaba97efc5b8`. Repository base HEAD remains
`168e3cec01f941a84d40bbe0dc07156e7baa35d0`. Existing unrelated changes retained.

Beautify is visible only for school-form drafts while the editor is visible.
Acceptance chooses the deterministic built-in skeletal generator first,
including skeletal/annotated-skeletal edits. Each candidate must pass before
it wins; an invalid candidate continues to the next rung. Valid built-in fixed
points (including one atom at the origin) are accepted. Coordinate sums remain
diagnostic receipts only.

Candidate validation uses the existing finite-coordinate V2000 parser,
`fMolCanTransform2D` supported-metadata guard and `fBuildHeavyMap2D3D(false)`
exact heavy graph mapper. The mapper reads four engine lists, temporarily
replaced inside a synchronous try/finally transaction and restored by identity;
it does not mutate the existing map cache. Composite atom labels include
charge, mass difference and isotope fields; normal explicit H may be removed.
Tests prove those distinctions, graph/bond-order correctness, and list/cache
preservation. This does not certify arbitrary stereochemistry/query metadata:
unsupported transformations are rejected and the existing drawn fallback is
retained with warnings.

Only SMILES depiction fallbacks are checked for unchanged internal geometry.
All mapped pairwise distances are compared after normalization by extent, so
header changes, translation, rotation and uniform scaling cannot create a
fresh layout. Both real applet content and scale are captured before clearing.
Clear is checked for success before importing; every mutation path goes through
content and scale restoration in finally. A broken restoration API can still
fail; the candidate is then rejected and a warning is logged. One synchronous
retry only covers an immediately available repaint, not asynchronous completion.

Executed Developer checks:

- `python3 docs/checks/v54-upstream-20261104/drawing/test-drawing.py` — 188
  assertions passed, actual current core plus actual before/upstream/final
  acceptance functions, fault-injected mock applets. Reproduced upstream
  equal-sum rejection, invalid built-in blocking a valid later candidate, and
  translated echo false acceptance. Final cases cover equal-sum zigzag change,
  built-in identity/update, explicit H, single atom, invalid finite/count/type/
  graph/bond/charge/isotope/mass/collapsed candidates, per-rung continuation,
  formatted/translated/rotated/scaled echoes, clear/import/read/repaint errors,
  silent clear/import failures, immediate retry, applet restoration, stable
  engine lists/cache, custom update/fork, and stale/no-3D/pending/duplicate guards.
- `python3 docs/checks/v54-upstream-20261104/drawing/test-preservation.py` — 27
  assertions passed: whole-viewer JavaScriptCore compilation, actual SyncBar
  mode/editor behavior and exact byte preservation outside the two functions.
  Live-draft `skeletalLayoutSource`, shared geometry/framing, other mode policy,
  source assets and all other functions are unchanged by this worker.

Limits: these are executable pure-engine/mock fault checks, not browser/JSME,
PubChem/3D/network or visual checks. Root Developer owns real-browser affected
flows. Echo checking uses the existing mapper's one exact correspondence;
reordering equivalent atoms of a symmetric molecule with asymmetric geometry
can select a different automorphism and miss an echo. Universal geometric
isomorphism would require separate matcher scope. The built-in supported path
is independent of applet timing. No guarantee of conference/offline reliability
is implied. No core edits by this worker; no stage/commit/push/publication.

Frozen runtime/evidence hashes are in `manifest.json`; `viewer.diff` compares
against the recorded session baseline. Parent Developer owns independent review
and overall session/contribution records.
