# Ester hydrogen and orientation display fixes — 2026-10-29

## User-approved behavior

The user explicitly approved this combined plan after reporting three defects
and adding a fourth requirement:

1. First ester in carbon-count order, methyl methanoate condensed: retain its
   explicit H–C bond and show carbonyl C, not an additional CH label.
2. All nine ester skeletal views: acid fragment left, alcohol fragment right.
3. Skeletal ester views: omit carbon-bound H and their C–H strokes, keeping
   the underlying chemical graph and IDs intact.
4. Fifth ester, tert-butyl methanoate: HC(=O)O… in condensed form, with H left
   of C; expanded H–C(=O)–O… has a horizontal H–C bond to the left.

The fifth identity follows actual stable carbon-count sorting in teaching52:
C2methyl methanoate, C3methyl ethanoate, C4methyl propanoate, C5isopropyl
ethanoate, C5tert-butyl methanoate. This does not rely on insertion order alone.

## Bounded implementation

Only `js/mulermoc-nom-molview-52.js` and its HTML cache key change runtime.

- `fRemainingImplicitCarbonHydrogens`: core `carbonHydrogens` means total H,
  because core heavy valence omits H. Subtract actual explicit single C–H bonds
  locally in display, using `bondList`, not H-free connectivity. Invalid counts
  warn/skip insertion. Core semantics and naming remain unchanged.
- `fSkeletalLayoutMol`: optional acid/alcohol fragments choose the proper
  half-turn inside the existing pipeline. Preserve its geometry repairs,
  whole-molecule centering and other classes' C1 preference. Apply this
  preference only to guarded acyclic saturated monoesters. No second orientation
  pass or repeated JSME reload is introduced.
- `fFormylHydrogenLeftMol`: expanded tert-butyl methanoate starts from the saved
  source on every load, moving only its terminal formyl H transiently left,
  retaining C–H length and every indexed element/bond/stereo/z field. Main and
  original2D applets receive the same transient layout. Source MOL is untouched.
- Condensed tert-butyl methanoate label places H before C with measured H width;
  carbon keeps its native JSME x anchor. Other carbon labels keep their policy.
- `fHideEsterSkeletalCarbonHydrogens`: locate explicit C–H by chemical bond index
  and native SVG endpoints within its paired H backplate. This avoids assuming
  that skeletal text order equals atom order. Hide label, mask and bond stroke
  after wrapping/colors, retaining DOM nodes/indices. Fit ignores these hidden
  nodes. Heteroatom-bound H outside this ester policy remain untouched.

515molecular files (MOL/SDF/provenance), embedded data and core hashes are
unchanged. No JSME vendor/settings changes. SVG postprocessing is used for
label accounting/ordering and display suppression; the existing SVG spacing
policy is retained. This is not a claim that all work was a JSME setting change.

## Developer evidence actually executed

- Static actual JavaScriptCore:422available2D forms have correct remaining-H
  accounting;27ester forms checked. All131non-ester skeletal transformations
  exactly match the pre-fix implementation. Ester rotations preserve indexed
  atom/bond fields and all pairwise distances within V2000 rounding. Expanded
  formyl-H movement preserves C–H length and all other coordinates.
- Naming/parent correspondence:110new,814old and16guard cases PASS.
- Existing actual Firefox/JSmol suite:30form/chain cases, five3D models,
  12atom-color highlights,30layouts, no JavaScript errors. That suite preceded
  moving the H-suppression call after label wrapping; suppression does not affect
  its five new molecules (none has explicit skeletal H).
- Final actual Firefox:162current cases =9esters ×3forms ×2widths1500/390
  ×absolute zoom1/2/4, plus162pre-fix baseline cases. Asserted acid-left,
  no clipping, first ester C rather than CH with one explicit H, fifth HC with
  H geometrically left, horizontal expanded H–C, zero visible skeletal H and
  one hidden stroke per explicit C–H while retaining total stroke/index count.
- Nine resize/highlight replays on methyl/tert-butyl methanoate and sec-butyl
  ethanoate: indexed MOL content identical across repeats; only JSME's export
  header timestamp is ignored. H stays hidden and acid remains left.
- Condensed methanoic acid/methanal/ethanal controls captured and inspected;
  remaining-H values1/2/[1,3], labels HCOOH/HCHO/[CHO,CH3]. Their sources have
  implicit carbon H, so these controls retain their prior carbon-H label counts.
- Manually inspected actual screenshots of first/fifth ester required views,
  representative skeletal geometry and acid/aldehyde controls. Image inspection
  supplements, rather than follows from, label/clipping assertions.
- Two new Python scripts compile in memory. No project dependencies installed.

Evidence under `docs/checks/esters-display-{static,naming,new-browser,browser,preservation}-20261029.json`.
Exact runtime source diff and pre-fix snapshot:
`esters-display-source-20261029.diff`, `esters-display-before-source-20261029.json.gz`.
Immediate pre-fix copies for in-session reproduction are under
`/tmp/namelecule-esters-20261029/display-fix/before`.

An initial H-hide ordering issue was caught: the H wrapper replaced the hidden
text node. Hiding now occurs after label creation. Two harness corrections
compare pre-existing overlaps to actual baseline and ignore only export header
timestamps; final evidence comes from the passing run, not those initial runs.

## Residual issue and limits

Expanded isopropyl ethanoate has two overlapping H text bounds at both widths
and all three tested zooms (six cases). Its SVG is byte-identical to the exact
pre-fix baseline in each case. This is an unchanged older overlap, not repaired
by the approved four fixes. No other label overlaps were detected in these
ester cases. Do not claim universal perfect rendering.

Browser actions are programmatic DOM activations;390px is desktop layout
emulation, not physical-mobile testing. Other zoom/fonts/devices and export
were not newly tested. The old initial screenshot was not independently tied
to a specific user environment; the now-identified first-ester extra H was
reproduced and corrected as specified.

## Independent review

Completed by `/root/ester_display_review`, fresh context,
ROLE_ID=NAMELECULE_REVIEWER_V1_20261023. No actionable P0/P1/P2/P3 findings
in the approved scope. All13target hashes and the reconstructed scoped diff
matched. Independently re-executed actual JavaScriptCore static assertions in
memory:422forms/27ester forms/131other skeletal invariants, indexed fields,
rotation distances and expanded terminal-H movement PASS. Independently
confirmed517current core/data/molecular hashes match the preservation manifest;
historical provenance of that preservation remains Developer evidence.
Browser, naming and runtime3D suites were inspected as supplied Developer
evidence, not independently rerun. No independent physical-mobile, other
browser/font, export or original-user-environment verification. Reviewer wrote
no files. Only this report's review metadata was subsequently finalized;
implementation/test/evidence hashes remain unchanged.
Chemistry diagnosis was supplied by `/root/ester_display_diagnosis`,
ROLE_ID=NAMELECULE_CHEMISTRY_VALIDATOR_V1_20261023, with EST-H1/H2/O1 concerns
addressed by the implementations/tests above. Its supplied browser references
were Developer evidence; it did not independently execute a browser.

## Core and save state

No core file changed in this display fix. Core52 remains SHA256
`d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2`;
previously approved five-ester naming changes remain local. No commit, push,
publication or upstream synchronization was performed.
