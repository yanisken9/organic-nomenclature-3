# U35-GEOM01 — shared skeletal generator repair — 2026-11-04

User approved repair of `fZigzagMol` in `js/mulermoc-nom-core-54.js` after the
independent review found that deterministic-first acceptance selected flattened
ether chains. This worker owns only that function and this evidence directory.
Root Developer separately owns three numeric `sortedFunPositions` comparators.
The recorded repository base remains `168e3cec01f941a84d40bbe0dc07156e7baa35d0`.

Before measurements used the captured function/core (`before-fZigzagMol.js`,
`before-core54.js`). The real naming engine resolves each source's algorithmic
parent before generation. All 422 available source forms across 141 molecules
were exercised; methane has no saved skeletal form (423 theoretical slots).
The existing unsupported expanded `penten_3_yne_1` form contains literal `[H]`
labels and remains rejected by the supported-metadata guard.

Demonstrated cause and repair:

- The subtree queue copied its incoming direction to the first child. An ether
  bridge and off-parent degree-two carbons therefore formed straight 180°
  paths. Diethyl ether's actual parent is `[2,3]`; its O and two degree-two C
  angles were about 180°. Cumulated double-bond carbon centers were instead
  generated at 120°. Before sweep: 200 affected form outputs, 281 bad pivots.
- Endpoint branch placement also used a vector of length L as a unit direction,
  multiplying by L again. This produced approximately 1.3689 (=1.17²) bonds in
  36 form outputs. Every branch direction is now normalized before placement.
- The generator first builds its intended uniform L=1.17 layout. Invalid
  degree-two C/O pivots are then repaired by a proper rotation of a complete
  separable component about that pivot. Neutral O with two single bonds and
  non-sp C use the conventional visible 120° skeletal bend. Carbon with a
  triple bond or two double bonds uses 180°. Degree-two C with impossible bond
  order sum and unsupported degree-two O valence/charge are rejected.
- C1 and as much of the resolved parent as possible stay fixed. Both bend signs
  are tried, with guards against new/worse nonbond contacts, atom-on-bond
  contacts and crossings. A repair that cannot pass the guards returns null;
  it is not reported as a successful deterministic candidate. Ring closure,
  disconnected heavy graphs and duplicate/nonbonded parents fail closed.

This is generated geometry, not a display-only change. L=1.17 intentionally
replaces authored source lengths, as the existing generator contract specifies.
The local rotation stage preserves those generated lengths and all other local
angles; it does not drag individual atoms or mirror a fragment. Source MOL/SDF,
embedded data, old52, naming rules and the other generators were not edited by
this worker. All core bytes outside this function differ from the worker
baseline only in Root Developer's three authorized numeric comparators.

Executed Developer verification:

- `test-geometry.py --baseline`: 422 actual source forms; 421 transformed,
  one existing metadata skip; 200 angle-failing forms, 36 length-failing forms.
- `test-geometry.py --normalized`: isolates direction normalization before
  angle repair; 200 angle-failing forms remain, zero length/metadata/name
  failures. This baseline supports separate measurement of rotation invariants.
- `test-geometry.py`: all 421 supported forms transform successfully with zero
  angle, graph/metadata, name, determinism or uniform-length failures. All
  degree-two C/O targets are within 0.02° and generated lengths within 0.00015
  of L after MOL rounding. All 134 triple-bond sp and six double+double sp
  centers are linear. Heavy graph/order, charge, isotope/mass fields and SUP
  identities are preserved; regenerated SUP SBV vectors match new coordinates.
- `test-mechanics.py`: all 2,309 generated bonds retain normalized pre-repair
  lengths, 2,218 other local angles remain unchanged, and 1,922 oriented local
  angles retain their sign. 7,005 nonbond pairs, 14,010 atom/bond pairs and 4,506
  nonincident bond pairs show no new/worse guarded contacts or crossings.
  Five invalid/ring/disconnected/unsafe-valence fixtures fail closed. Hashes of
  all 456 recorded old52/data/MOL/SDF paths remain unchanged.
- `test-acceptance.py`: 228 assertions pass, reusing the existing actual
  acceptance/core suite and adding ten Accept/Update cases across diethyl and
  ethyl propyl ethers, 1-butyne, propadiene and 1,2-butadiene. Deterministic
  output wins and has correct C/O/sp geometry; update identity/history and
  engine/map state remain intact. Applets and PubChem preconditions are mocked.
- Existing `docs/checks/v54-sync-20261104/core/test-mol-properties54.py --output
  docs/checks/v54-upstream-20261104/geometry/mol-properties-results.json`:
  422 roundtrips, 1,684 generator graph/formula/charge cases, 13 deliberate
  metadata fixtures, 24 nitro derivations and negative butene map check pass.

Remaining limits: this evidence uses actual pure engine/acceptance code and
serialized coordinates, not a live JSME/PubChem/3D or visual browser. Root owns
those checks and independent Reviewer handoff. No additional supported-library
form required an unsafe repair skip. Future ring/disconnected/unsupported
metadata structures may use the existing applet/drawn fallback. Non-C/O
hybridization and all degree-three/four angle conventions remain outside this
bounded repair; existing local angles are preserved. Safety checks prevent
new/worse guarded conflicts, not every pre-existing crowding condition. No
conference-machine, offline or uninterrupted-operation guarantee is implied.

Frozen function SHA256:
`5a0e972822d76cfa541c193a2d4b827bde2f76864cddbc81c6cf99cb3ec875a7`.
Whole core54 SHA256 (also includes Root's numeric comparators):
`3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306`.
`manifest.json` records source/evidence hashes. Function is frozen for independent
Chemistry Validator/Reviewer inspection; no stage, commit, push or publication.
Root maintains the session/contribution notes and Greek core-change handoff.
