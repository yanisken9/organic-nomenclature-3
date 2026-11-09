# Four unsaturated carboxylic acids — 2026-10-28

Resumed the previously approved interrupted addition. At resumption the library
contained130entries, including the four completed saturated acids. None of the
four pending keys had a registry record, embedded MOL or runtime SDF. Temporary
assets already existed; core52 had an incomplete bounded extension. No completed
addition was repeated. User authorized continuation within that approved scope.

| Greek school name | Formula | Parent C |
|---|---|---|
| 2-μεθυλο-2-προπενικό οξύ | C4H6O2 | 3 |
| 2-αιθυλο-3-μεθυλο-2-πεντεν-4-ινικό οξύ | C8H10O2 | 5 |
| 3-αιθυλο-2-ισοπροπυλο-4,5-διμεθυλο-2,4-εξαδιενοδιικό οξύ | C13H20O4 | 6 |
| 2-αιθυλο-3-ισοπροπυλο-6,6-διμεθυλο-2-επτεν-4-ινοδιικό οξύ | C14H20O4 | 7 |

## Changes and boundaries

- Four records and12embedded MOLs in data52, with the existing schema/order.
  Three2D MOLs, one3D SDF and provenance per molecule in mols/new_molecules;
  identical runtime SDFs in mols/nomeclature-moc2. Final inventory134, unique keys.
- The previously started core52 extension handles acyclic C/H/O unsaturated
  mono-/diacids, terminal COOH direction, alphabetical ties and the requested
  branched C3double-bond locant. Original saturated-monoacid guard unchanged.
  During resumption, explicit-H validation was corrected to use full bonds:
  analysis adjacency deliberately omits H. Off-parent C–C multiple bonds now
  decline alkyl-prefix support, avoiding vinyl/ethynyl mislabeling as alkyl.
- Viewer52 extends existing sequential analysis numbering to the four keys and
  Main-only three-prefix boxes to the two large diacids. Core component schema,
  teaching/scenario code, old molecules, scenario JSON and React stay unchanged.
  HTML cache URLs refresh data/core/viewer. No new rendering method introduced.
- Esters, mixed functions, rings and general alkenyl/alkynyl substituent naming
  are outside this extension. Existing unsupported off-parent unsaturation can
  still produce invalid parent names such as0,3locants; this pre-existing
  limitation is not treated as supported naming. No general IUPAC certification.

## Sources and molecular conventions

All four SDFs are locally generated RDKit2025.09.2 ETKDGv3/MMFF94s conformers,
seed20261028, selected among24sampled conformers. The fourth selects among
converged conformers satisfying both sp angles>175degrees. Provenance records
the method, hash, graph mapping and unspecified stereochemistry. No experimental
geometry or assigned R/S/E/Z is claimed. The earlier PubChem transmission was
blocked before execution and was not retried. No absence from PubChem is claimed.
MOL school display flags follow existing conventions; structures retain bond orders.

## Verification

Developer evidence uses the existing RDKit environment and real JavaScriptCore
core/viewer harness, not a rewritten naming implementation.

- check-other-acids-20261028.py:12MOL/4SDF identity, formulas, explicitH, bond
  orders, planar2D, clearance/crossings,3D bond lengths/sp/carbonyl angles,
  provenance/hash/mapping, runtime/source identity and all130old records/MOLs.
  Resume baseline: checks/other-acids-resume-before-20261028.json; original
  pre-extension source bytes: checks/other-acids-before-source-20261028.json.gz.
- test-other-acids-naming-20261028.py:72new cases across three forms, algorithmic/
  authored chains and12heavy-atom permutations each;778old-library cases.
  Original guard boundaries plus new implicit/explicit-H exclusions and a vinyl
  sidebranch support rejection. Saved React inventory frame is compared with
  that same inventory; Main inventory additions may change its computed frame.
- JS syntax parsing for data/core/viewer and Python AST checks passed.
- Real Firefox test-other-acids-browser-20261028.py passed24form/viewport cases
  (four molecules ×three forms ×desktop1500/narrow390), four actual3D models,
  all applicable prefix selections including the third group and their explicit
  3DH selections, progressive parent numbering, zero JavaScript errors.
  Evidence: checks/other-acids-browser-20261028.json; screenshots in
  /tmp/namelecule-other-acids-20261028. Developer visually inspected selected
  condensed/expanded/skeletal captures. Initial browser failures exposed the
  explicit-H core bug and stale script cache; subsequent test-only corrections
  used native carbon-anchor masking (including reverse HOOC) and the real
  third-prefix DOM ID acidPrefixNumber3. These are not runtime fixes.
- Asset checks also reject duplicate new graphs against all15old acid entries.
  Final naming suite includes29guard/boundary probes.
- Consolidated independent Reviewer /root/acid_review completed the frozen42-file
  target with no actionable P0/P1/P2/P3 findings. Independently reran read-only
  asset/naming checks and24additional full-H atom/bond permutations, inspected
  the diff/dependencies and five saved screenshots. Firefox execution remains
  Developer evidence; the Reviewer did not launch a browser. Node was unavailable;
  real sources parsed/executed through JavaScriptCore. PNG export, every viewer
  transition and unaffected educational flows were not rerun. This status-only
  paragraph was added after review; implementation and test files stayed frozen.

Chemistry Validator /root/acid_chemistry independently checked actual names,
full graphs/mappings and chain indices. CV-01 P1 explicit-H failure independently
closed after correction:24integrated cases plus24explicit-H/SDF permutations.
CV-02 P2 false alkyl sidebranch support closed after four targeted vinyl/ethynyl
probes and24requested cases on final core SHA256
7e944c6f30abd4cae66a4c1ee0f413f21582b2058b7d3c7679a7a1a463d8a998.
No browser/classroom validation was performed by the specialist.

No commit, push or publication. No new lesson. No external message sent.
