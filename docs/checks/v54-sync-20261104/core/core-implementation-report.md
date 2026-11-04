# Main54 core migration — Developer evidence, 2026-11-04

Approved scope delegated by `/root`: create Main54 with all professor functionality
through `02dbcfaf79e23f1933a252e0b1f6671049d39b78`, preserve Namelecule chemistry,
keep original52/React/assets intact, verify the shared naming/generator/map paths.
Ownership was limited to `js/mulermoc-nom-core-54.js` and this evidence directory.
Source repository HEAD was `168e3cec01f941a84d40bbe0dc07156e7baa35d0`; actual
last synchronized professor base was `93b759f5891d7b5a1172646032d83215d60b7604`.
Root owns the consolidated session/contribution records and independent review.

## Frozen code and provenance

- Final core54 SHA256: `10f3e1ed4ea566be50c4797d523d6cfe83e86a41cab761b0c18281f9113a061f`.
- Exact upstream54 imported first, SHA256
  `75b69725e39ac5812566306a65150e1c26c6b5be09416ca2bb5160289dc17c46`.
- Original core52 SHA256 remains
  `d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2`,
  matching the session-start baseline. No existing core file was edited.
- The final core54 is a customized upstream import. Locally authored changes
  are fully identified by `local-core54-vs-upstream.patch`; it is not an exact
  upstream copy. No staging, commit, push, publication or dependency installation.

The normalized three-way core analysis had two conflicts. The first repeated
an ester guard already present later in upstream54; upstream's single copy was
retained. The second concerned ester acid length: upstream checks that the parent
starts at the carbonyl carbon and stays inside the acid fragment, preserving the
local acid-parent naming correction while avoiding an unrelated ranked chain.
All local52 acid/ester guards, branch priorities and locant corrections are
otherwise already present in upstream54.

## Demonstrated causes and bounded corrections

1. The new linearizer treated every off-parent neighbor as an orthogonal branch.
   A terminal nitrile N therefore bent C–C≡N to 90°. The shared placement block
   now continues the parent axis at a terminal degree-two sp carbon. No molecular
   exception list; topology and stored library coordinates are unchanged.
2. The new parser/writer discarded atom/bond fields and M CHG. Expansion then
   inferred a neutral oxygen valence for O− and added an erroneous O–H in the two
   supported nitro compounds. The tools now preserve atom/bond fields, z,
   CHG/ISO/RAD properties and supported SUP Sgroups through reindexing. Hydrogen
   inference uses supported charge-aware valences. SAL/SBL members follow atom/
   bond indices; new H join their parent's SUP group; SBV follows coordinates.
3. The new mapper's order-ignoring fallback incorrectly mapped 1-butene to
   2-butene. Translation now requires exact element/bond-order isomorphism.
4. The mapper cached by molecule key and atom counts. Thirty of 140 condensed →
   skeletal transitions reused an invalid map when equal-size graphs reordered
   atoms; some returned a contiguous but chemically wrong chain. Cache identity
   now contains the ordered 2D/3D graph inputs and original MOL/SDF text, including
   available charge/isotope/stereo source fields. A same-size graph mutation also
   invalidates the cache.

`upstream-linear-nitrile-reproduction.json`,
`upstream-property-map-reproduction.json` and `map-mode-switch-before.json`
record the observed pre-correction failures. These are measured engine results,
not screenshots or assumptions about someone else's browser deployment.

## Actual checks

Run from the repository root, using Python stdlib and the macOS JavaScriptCore
helper at `/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc`.
All three final result files identify the frozen final core SHA above.

```text
python3 docs/checks/v54-sync-20261104/core/test-core54.py --data54 js/jsme-nick-nomeclature-moc2-data_54.js --output docs/checks/v54-sync-20261104/core/core54-data54-results.json
python3 docs/checks/v54-sync-20261104/core/test-mol-properties54.py
python3 docs/checks/v54-sync-20261104/core/test-map-transitions54.py
```

All three commands exited 0. The tests execute the actual core functions. They
cover the 141-molecule library and all 422 available forms (methane has no saved
skeletal form):

- 844 names/parents/components/branches in algorithmic/data modes; 832 outputs
  identical to original52. Twelve expected upstream cases cover only the two
  new acid names `2-οξοπροπανικό οξύ` and `4-οξοβουτανικό οξύ` across forms/modes;
  their numbered parent signatures and branches remain unchanged. The former
  also moves from `ketoAcids` to `oxoCarboxylicAcids`.
- 844 naming calls before explicit naming-table initialization; 240 atom/bond
  permutations against approved local acid/ester specifications; 15 chemical
  guard boundaries; six malformed/empty-input checks.
- 1,263 generated linear/zigzag/expanded naming and graph checks; four terminal
  sp checks covering inverse parent direction and atom order. No newly bent sp
  centers in those generated results.
- 422 parse/write graph/formula/charge round trips and 1,684 generator graph,
  formula, formal-charge and SUP metadata checks; 13 deliberate charged,
  isotopic, parity, wedge, radical, query, unknown-property and Sgroup fixtures;
  24 explicit nitro derivations. Nitroethane has five C-bound H and nitropropane
  has seven; N+/O− survive, and no O–H is introduced. Interspersed explicit-H
  permutation verifies charge and SUP reindexing.
- 842/844 exact isolated 2D↔3D maps, 421/422 exact deliberately reordered maps,
  symmetry/distinct-pool-chain checks, four map boundary probes and chemical
  mismatch rejection. The raw-label exception below accounts for the remainder.
- 1,684 exact persistent-engine transitions across all 141 molecules, both
  parent modes and forward/reverse form switches, plus four explicit fail-closed
  raw-label cases. Reusing the same key/counts for 1-butene → 2-butene is rejected.

Syntax is exercised by compiling/executing the core in every JSC suite. The
upstream→custom `git diff --no-index --check` produced zero whitespace diagnostics
(exit 1 because the files differ). A whole-new-file `/dev/null` whitespace check
reported five trailing-space lines inherited unchanged from upstream54; these
formatting-only source lines were not altered during the frozen migration.
An initial literal-text idempotence assertion also detected only `-0.0000` versus
`0.0000`; the final test compares parsed geometry and graph, which is the relevant
invariant. Earlier narrow sweep results are explicitly labelled initial evidence.

## Limits and independent handoff

- One inherited expanded MOL (`penten_3_yne_1`) has the literal element label
  `[H]`. Raw-MOL engine tests do not silently coerce it. Exact mapping fails and
  all four generators reject it; the numbered parent signature fallback still
  agrees. Actual JSME normalization needs the root browser check. No source MOL
  was edited to hide this exception.
- `fGenExpandedMol` preserves input heavy coordinates. The inherited raw
  `butanenitrile` skeletal source has a roughly 120° nitrile center; expansion
  retains that input angle. The generated linear/zigzag forms are linear, and
  the existing viewer display pipeline is outside this worker's ownership.
- Ordinary explicit H can be stripped. Isotopic H stripping/layout is rejected;
  expansion retains it. Declared parity/wedge stereo, radicals, query/aromatic
  bonds, explicit valence/H declarations, unrecognized properties/group types
  and unsupported valence/element cases fail closed rather than invent chemistry.
  This bounded V2000 tool is not a universal chemical-file converter.
- Graph matching continues to use the upstream element/bond-order isomorphism.
  The cache includes complete source records, but this does not establish
  stereochemical correspondence for arbitrary new files.
- These are Developer engine checks. Browser visuals, physical device input,
  external PubChem/JSME/JSmol services, scenario replay and conference/offline
  readiness require the root's separate verification. No such guarantee is made.
- The frozen code was handed to Chemistry Validator `/root/v54_formula_conflict`
  for independent targeted P1 verification. Root performs the consolidated fresh
  Reviewer handoff and records their verdict; these tests are not independent
  review. Any subsequent code change needs targeted verification/new hashes.

## Core report for the professor

Προστέθηκε το `js/mulermoc-nom-core-54.js`, με τις λειτουργίες του upstream έως
`02dbcfaf` και διατήρηση των τοπικών διορθώσεων οξέων/εστέρων. Οι τοπικές αλλαγές
διορθώνουν τη γραμμικότητα C≡N στις νέες παραγωγές, τη διατήρηση φορτίων/ισοτόπων/
ομάδων SUP, την παραγωγή σωστών υδρογόνων στις νιτροενώσεις και την αντιστοίχιση
2D–3D κατά τις αλλαγές μορφής. Ελέγχθηκαν και τα 141 μόρια με τις παραπάνω
δοκιμές JSC· οι εξαιρέσεις αναγράφονται στην αναφορά. Το core52 έμεινε απολύτως
ίδιο. Οι αλλαγές είναι τοπικές, χωρίς commit ή δημοσίευση. Η ανεξάρτητη τελική
αξιολόγηση και οι έλεγχοι browser συντονίζονται από τον κύριο Developer.
