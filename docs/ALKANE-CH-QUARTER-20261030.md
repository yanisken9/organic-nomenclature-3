# Additional C–H25% MOL experiment — 2026-10-30

## Approved behavior and sources

The user explicitly preferred modifying MOL distances first. After clarification
that the existing files already used50% of the original C–H distances, the user
approved a further25% reduction of current values in all8expanded alkanes:
methane,ethane,propane,butane,pentane,methyl_2_pentane,dimethyl_2_3_butane,
ethyl_3_dimethyl_2_5_hexane. Nominal result:37.5% of original pre-experiment
C–H atom-center distances. It is a coordinate experiment, without a guaranteed
proportional screen-pixel reduction.

`Hnew=C+0.75(Hold−C)` is applied to the90explicit carbon-bound H from a new
immutable immediate-before snapshot. Only x/y of H change in8embedded Expanded
strings of js/jsme-nick-nomeclature-moc2-data_52.js and3existing physical MOL
copies (two new_molecules and one historical source-2d). Four decimals retain
V2000 precision. Carbon positions, C–C, directions, atom fields/z/IDs, bonds,
headers, metadata and each file's own atom order remain. Other forms/records,
3D, viewer, core, HTML, scenarios and React are unchanged. Re-running the
fixed-baseline generator cannot accidentally multiply the reduction again.

## Actual checks and observations

Developer static PASS:90H×0.75 within0.00005 coordinate rounding; carbon and
indexed graph unchanged;133other records, condensed/skeletal strings, metadata
and all other data-file code identical. 1,879 protected existing files retain
their snapshot hashes. Data JavaScriptCore syntax and3new Python ASTs PASS.

Chemistry Validator /root/validate_alkane_ch_quarter,
ROLE_ID NAMELECULE_CHEMISTRY_VALIDATOR_V1_20261023, independently checked the
four hashes,90vectors/directions (including nominal original×0.375), all unchanged
fields/bond orders, C4/H1 valence and neutral charges. Formulas CH4,C2H6,C3H8,
C4H10,C5H12,two C6H14,C10H22 unchanged. It checked carbon-tree isomorphism of
expanded/available condensed/skeletal and all8runtime SDF, independent of atom
ordering/explicit H; source/embedded correspondence and historical ordering
are retained. No chemistry finding. Methane lacks a skeletal MOL as before.

Real isolated Firefox only on affected expanded forms:64before/after cases
(8molecules×2phases×2zooms×2widths1500/390), plus3branch highlights. No glyph
overlaps, clipping or JS errors; full center/edge raster gaps remain clear.
The runtime readability flag is FALSE: six after-cases, the3branched molecules
at absolute zoom0.5 and both widths, have28short C–H instances below1pixel.
Shortest remaining stroke is0.13px in the largest molecule (before1.48px).
2-methylpentane:0.32px (before1.57px); dimethylbutane:0.42px (before1.72px).
These short strokes are a known limitation, not a passed readability check.

At normal desktop zoom, atom-center C–H screen ratios after/before are:
methane1.000,ethane0.923,propane0.901,butane0.890,pentane0.873,
2-methylpentane0.790,dimethylbutane0.810,larger branched alkane0.791.
Native JSME normalization still changes C–C screen scale: approximately1.053–
1.232 despite fixed stored C coordinates. Methane remains visually unchanged.
Font policy is unchanged; framing may still alter actual displayed font size.
Screenshots are evidence for2D only: programmatic selections can leave sidebar,
radio or3D on a previous state; no3D runtime verification is claimed.

The existing lesson's only expanded step18 passes at1500px. At390px it FAILS
its>1px readable-stroke requirement (one captured C–H stroke0.53px). The raw
lesson result records completed:false and the exact failing bond. Scenario JSON
is untouched. Responsive emulation only, not a physical mobile device.

## Review, limits and next decision

Independent consolidated fresh-context Reviewer /root/review_alkane_ch_quarter,
ROLE_ID NAMELECULE_REVIEWER_V1_20261023, completed the17-path frozen review
(manifest9784eeac11b251989605e32c71348a1d4b5d4e708cc4a4d83e3e0af80896c4df).
It independently verified hashes,90vectors/3copies, preserved fields/graphs/code,
1879protectedfiles, exact diff,3AST and141molecule registry evaluation, and read
the supplied screenshots/runtime evidence. Browser observations remain Developer
evidence. One P2 remains OPEN: ACQ-R1 at data52.js5981 (also5261/5345), short
C–H visibility at minimum zoom and narrow lesson step18, as detailed above.
No other actionable finding. No second full review was run. The experiment is
verified at the data level; visual acceptance remains unresolved. Follow-up
restoration or display correction awaits the user's decision. No correction
outside the approved MOL-only scope has been made. The molecular modification is applied
locally for the approved experiment; visual acceptance remains open because of
minimum-zoom/narrow-lesson readability. Viewer/core changes are not authorized
by this MOL-only plan. No new display adjustment has been made. A broader visual
fix or restoration of the before-experiment data requires a concrete follow-up
decision; the immutable current-before snapshot enables exact restoration.
No claim of universal display improvement or production readiness is made.

Sources/evidence: docs/checks/alkane-ch-quarter-*;
reduce-alkane-ch-quarter-20261030.py (--before snapshot, --apply),
check-alkane-ch-quarter-20261030.py (--before snapshot, --output),
test-alkane-ch-quarter-browser-20261030.py (--output under /tmp).
The unchanged test-alkane-clearance-v2-lesson-20261030.py supplies the lesson
check. No redundant whole-library runtime pass, export test, full3D, Safari or
React build. No core change today, no commit/push/publication.
