# Two unbranched enynoic acids — 2026-10-28

User approved the bounded plan after read-only investigation. Added two previously
absent molecular graphs without repeating earlier additions. Main inventory is
now136; the134previous records, embedded/source assets, core52, scenarios and
React catalog remain unchanged.

| Greek school name | Formula | Graph | Parent C |
|---|---|---|---|
| 2-πεντεν-4-ινικό οξύ | C5H4O2 | HOOC–CH=CH–C≡CH | 5 |
| 2-εξεν-4-ινοδιικό οξύ | C6H4O4 | HOOC–CH=CH–C≡C–COOH | 6 |

Keys: penten_2_yn_4_oic_acid and hexen_2_yn_4_dioic_acid. The monoacid numbers
from COOH; the diacid tie {2,4} gives the double bond position2 rather than4.
No new naming rule or stereochemical assignment was introduced.

## Files and behavior

- Two nameExamples records and six embedded MOLs in data52, preserving every old
  record, its order and existing MOL strings. Source files: six2D MOLs, two3D
  SDFs and two provenance JSONs under mols/new_molecules. Two byte-identical SDFs
  under mols/nomeclature-moc2 are used at runtime.
- Existing horizontal condensed/expanded COOH conventions, all explicitH in
  expanded, regular skeletal geometry and linear sp centers. The existing shared
  skeletal display pipeline automatically orients the numbered parent left→right
  and frames the rendered structure. That geometry implementation is unchanged.
- Viewer52 adds only the two keys to the existing progressive analysis-numbering
  list. Main HTML refreshes data/viewer cache URLs. No core, 3D behavior, lesson,
  React catalog/host or old molecular-source changes.
- Local RDKit2025.09.2 ETKDGv3/MMFF94s illustrative conformers, seed20261028,
  lowest converged among24sampled conformers; explicit source/method/hash/atom
  mapping. Approved local generation, no external structure lookup. No claims of
  PubChem source, experimental geometry, R/S or E/Z specificity.

## Verification

Developer used the existing RDKit environment and real core/viewer JSC harness.

- check-two-enynoic-acids-20261028.py: six2D and two3D graphs/formulas/valences,
  explicitH, atom and bond clearance/crossings, planar2D, carbonyl/sp3D angles,
  bond lengths, provenance hashes/mappings and runtime/source equality. All134
  old records/MOLs/order and1625protected files match the baseline. Neither new
  graph duplicates the other or any of the19old acids.
- test-two-enynoic-acids-naming-20261028.py:36new cases (three forms ×twochain
  modes plus12atom-order permutations per molecule) and802old-library cases
  unchanged. 2D/3D numbered-chain signatures agree. Existing core already handles
  both names; core SHA256 remains7e944c6f30abd4cae66a4c1ee0f413f21582b2058b7d3c7679a7a1a463d8a998.
- Actual Firefox:12form/viewport cases (two ×threeforms ×1500/390), twoactual3D
  models with matching atom/bond counts, no overlaps/clipping, fourvisibleH per
  expanded molecule, progressive parent numbering. Actual clicks on double,
  triple and acid-suffix boxes verified native JSME atom selections and actual
  JSmol selections against source graph/provenance, including COOH hydrogens.
  Zero JavaScript errors. Selected screenshots visually inspected.
- Three JS syntax checks, fourPython AST checks and source-diff whitespace checks.
  Browser artifacts under /tmp/namelecule-two-enynoic-acids-20261028; numeric
  evidence/baselines/specs under docs/checks/two-enynoic-acids-*20261028.*.

Chemistry Validator /root/two_acids_chemistry independently checked graph/formula/
valence/H, parent direction, provenance/mappings, no old-acid duplicates and source/
runtime bytes. Skeletal sp angles≥179.9953°; SDF angles179.7772°/179.9115° (mono)
and179.8965°/179.8086° (di). No actionable chemistry findings. No browser was run
by the specialist. Consolidated independent Reviewer outcome is recorded in the
current session/contribution notes; Developer checks are not independent review.

No new lesson or general chemical-support claim. PNG export and every unrelated
navigation path were not rerun for this data addition. Earlier known JSmol page
teardown/long-name PNG-strip limits are outside scope.

Core unchanged in this task. All changes local; no commit, push or publication.
