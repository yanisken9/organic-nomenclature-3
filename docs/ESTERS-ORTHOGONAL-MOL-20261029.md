# Orthogonal expanded ester MOL correction — 2026-10-29

## User authorization and permanent convention

The user explicitly requested correcting the MOL files after rejecting diagonal
C–H fans: expanded drawings must use horizontal or vertical bonds. Resolving
crowding by introducing diagonal H bonds violates this educational convention.
The prior fan choice was a Developer error, not a JSME setting.

Scope: only the five NEW expanded2D source MOLs, corresponding embedded strings,
their reproducible generator and data-script cache key. Old esters and other
representations are preserved. No viewer workaround or core changes are included.

Files under `mols/new_molecules/`:

- `sec_butyl_ethanoate_2D_Expanded.mol`
- `butyl_propanoate_2D_Expanded.mol`
- `tert_butyl_methanoate_2D_Expanded.mol`
- `isobutyl_2_methylpropanoate_2D_Expanded.mol`
- `isopropyl_2_3_dimethylbutanoate_2D_Expanded.mol`

## Implementation

Removed the45degree H-fan exception from
`docs/checks/generate-esters-20261029.py`. Expanded heavy coordinates are rebuilt
along the authored orthogonal directions of the connected tree. C–C and carbon
branch spacing1.80, ester C–O/O–C1.21, C=O1.10, C–H.825 drawing units.
All explicit H use free cardinal directions. Opposite-side adjacent acid methyl
branches remain opposite. Tert-butyl methanoate formyl H8 is authored LEFT of C1
in the source itself. The existing viewer override now requests that same position.

These unequal drawing lengths and90/180degree angles are school connectivity
diagrams, not physical bond angles or conformations. Condensed/skeletal outputs
from the modified generator are byte-identical to their saved versions.

Updated only the five expanded strings in
`js/jsme-nick-nomeclature-moc2-data_52.js`; metadata and every other embedded form
remain identical. HTML data cache key becomes `esters-orthogonal-20261029`.
No JSME vendor/settings, SVG geometry/spacing, viewer or core edits.

## Developer checks actually completed

- All110bonds across five expanded MOLs are exactly horizontal or vertical with
  nonzero length. Indexed atom records excluding x/y, z/charges/stereo and every
  bond/H-neighbor identity match the exact pre-change source. Source/embedded match.
- No unrelated bond intersections or atom-on-unrelated-bond contacts; minimum
  nonbonded atom-centre distance exceeds1.0drawing units in all five structures.
- Other136embedded molecule records and all other forms of the new five are
  unchanged. Hash verification preserves all non-target molecular files,
  core/viewer and all3D/provenance. All515molecular files were monitored; exactly
  the five approved expanded MOLs changed.
- RDKit chemical/provenance suite:15forms/5SDFs PASS, including formulas, graph,
  explicit H counts, neutral valences, stereochemistry and2D→3D maps.
- Actual JavaScriptCore:110new naming/parent/permutation cases,814old regressions,
  16guard cases PASS; legacy library frame invariant.
- Actual Firefox/JSME:30expanded cases (five molecules ×1500/390px ×absolute
  zoom1/2/4), zero diagonal SVG lines, zero label overlaps, zero clipped labels,
  correct names, acid-left and complete H counts. Tert formylH remains horizontal
  left. Five highlight replays preserve indexed MOL content (only JSME export
  timestamp ignored), directions and readability. Zero JavaScript errors.
- All five actual expanded images inspected. Initial viewport-clipped capture
  artifacts were replaced with full-page screenshots; an additional settled
  full-page/bounding-box check on the largest ester confirmed complete top/bottom H.
- Three Python files compile in memory; no dependency installation this phase.

Developer evidence in `docs/checks/esters-orthogonal-{static,assets,naming,browser}-20261029.json`.
Exact before-source gzip/diff and review target are in the same directory.
Full-page screenshots are under
`/tmp/namelecule-esters-20261029/orthogonal-mol/browser-verified/`.

Browser actions are programmatic;390px is desktop layout emulation, not physical
mobile. Other browsers/fonts and export are untested. This bounded correction
makes no new claim about the unchanged old isopropyl-ethanoate expanded overlap,
previously disclosed. Existing four viewer fixes remain unchanged.

## Independent roles and review

Read-only Chemistry Validator `/root/ester_orthogonal_chemistry`,
ROLE_ID=NAMELECULE_CHEMISTRY_VALIDATOR_V1_20261023, confirmed the orthogonal-school
convention and proposed spacing, formyl-H direction and preservation criteria.
It independently simulated nonbonded distances, not visual runtime.

Completed by `/root/ester_orthogonal_review` in fresh context,
ROLE_ID=NAMELECULE_REVIEWER_V1_20261023. No actionable P0/P1/P2/P3 findings.
All18target hashes and the exact eight-path source diff independently verified;
520monitored paths confirm only the approved eight source paths changed.

Independent in-memory checks confirmed all110orthogonal bonds, indexed fields/
H-neighbors, source/embedded identity, no proper crossings/atom-on-bond contacts,
minimum nonbonded separation≈1.166726 and formylH8at(-.825,0). Generator functions
were executed in memory: all15forms match saved MOLs byte-for-byte. Independent
RDKit verified graph/formula/neutral charge across15forms plus SDF hashes,
3Dgraphs and provenance mappings. Three Python scripts compiled in memory.
Reviewer inspected supplied full-page largest-ester/tert-formate screenshots;
no independent browser launch or naming-suite rerun. Browser/naming results
remain Developer evidence. No files were written by Reviewer. Only this
report's review status was finalized afterwards; other target hashes remain
unchanged. Publication authorization remains separate.

## Core and save state

Core52 unchanged in this correction, SHA256
`d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2`.
Viewer52 unchanged, SHA256
`9c45d5c4180aaf15dd7a68db50561f5664efb14bf9d2e8d133462261d7b8e5a8`.
Earlier approved core ester naming changes remain local. No commit, push,
publication or professor synchronization performed.
