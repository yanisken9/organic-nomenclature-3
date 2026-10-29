# Expanded acid layout — 2026-10-28

User approved three changes together: vertical C=O and horizontal outward C–O–H,
shorter direct methyl stems, and clearance between carboxyl carbonyl labels and
native double-bond lines. Main v52 only; local, not committed or published.

## Implementation

- All15Expanded acid molecules /17COOH groups have vertical carbonyls and a
  collinear horizontal C–O–H, outward from the main chain at either end.
  Eleven groups in9old molecules needed reorientation. Carboxyl C stays fixed;
  local C=O/C–O/O–H lengths, atom IDs/properties, bonds and H counts are retained.
- Six vertical direct main-chain–methyl stems in the4new branched acids are
  shortened from2.34 to1.755 (25%). Each CH3 moves with its3H intact. Other
  branch stems, including the longer isopropyl attachment, are preserved.
  Existing source Expanded MOLs and coordinate specs match embedded data;
  the existing generator reproduces all12source2DMOLs exactly.
- Viewer52 pads only existing native white backplates of carboxyl C and carbonyl
  O. It measures rendered label bounds after final fitting, transforms them
  back to local coordinates and adds6%fontsize clearance. This also accounts
  for Firefox's difference between getBBox and rendered text bounds. Native
  bond lines are neither redrawn nor replaced. MainHTML cache URLs refreshed.

No core52, other2Dform,3D/SDF/provenance, molecule record, scenarioJSON,
React source/build/catalog or prior third-prefix behavior changes.
Core52 SHA256 stays97ae0466558eb954b810352d5f135fd4958e94a71c4a0cfef09fcf104085f78a.
The earlier28Oct approved core52 acid-naming extension is a separate contribution,
recorded in ACIDS-20261028.md; this task adds no core change.

## Developer verification

- `check-acid-layout-20261028.py`: RDKit graph/formula/valence and3Dgraph agreement
  for15acids, identical atom/bond properties and old indices, scope of moved
  atoms,17requested orientations/retained local lengths,6rigidCH3 translations,
  source/embedded/generator identity and1528protected baseline files unchanged.
- `test-acid-layout-naming-20261028.py`:130molecules,778before/after comparisons
  across available forms and algorithmic/data chain modes. Names, classification,
  components, numbered2D/3Dchain signatures and legacy viewport frame unchanged.
- `test-acid-layout-browser-20261028.py`: actual local Firefox; final48cases passed,0JavaScript errors.
  Checks all15acids at1500/390px,17COOHlabel gaps/native lines/all atom-label
  overlap/clipping;3representative molecules at both widths with main-chain
  selection and zoom in/out. Also actual mode/colour controls and PNG/SVG export.
  Screenshots in /tmp/namelecule-acid-layout-20261028; supplied Developer evidence.
- JavaScript syntax, PythonAST and git diff --check passed during development;
  final syntax checks passed; independent review pending.

Development iterations are not concealed: initial font-bbox padding was too small
and scale-dependent; final measurement uses rendered bounds after fit. One test
initially used a semantic mode as a DOM ID; corrected to the real `comp5` control.
A complete48case browser run already passed before adding colour/export coverage;
its narrow screenshot still included the existing portrait prompt. Final test
uses its normal dismiss button. No application change for that prompt.

## Scope and limitations

No new chemical naming rules or literature claims. Chemistry checks establish
identity preservation, not a new universal IUPAC certification. No Safari,
React rebuild, all283lesson-step replay or newacid scenario authoring is claimed.
The previously documented third-prefix scenario replay limitation is unchanged.
Independent review will be recorded in the session/contribution notes after the
frozen target is inspected; this document does not predeclare its verdict.
