# Uniform expanded bonds in the final alkane — 2026-10-30

The user explicitly approved extending the completed 2,3-dimethylbutane
prototype to only the expanded 3-ethyl-2,5-dimethylhexane, the last alkane in
library order. Its22C–H now all measure0.3094MOL units;9C–C all measure0.6188,
including both horizontal parent and vertical branch bonds. Carbon positions
scale uniformly by0.6188/0.825; H positions follow their original directions
at the approved common distance. Indexed graph, IDs/order, atom fields/z,
header, bond orders and all other MOL fields are retained. Embedded and physical
Expanded source are identical.

Changed application files: js/jsme-nick-nomeclature-moc2-data_52.js,
mols/new_molecules/ethyl_3_dimethyl_2_5_hexane_2D_Expanded.mol,
js/mulermoc-nom-molview-52.js and mulermoc-nom-52.html. The viewer change only
adds this key to the existing expanded-prototype gate; calibration2.6175,
centered glyphs, square masks, fit and numbering reuse the prior implementation.
HTML changes only two cache URLs. Other140records, including the previous
prototype, other target forms, core,3D, scenario JSON and React remain unchanged.

Developer static checks PASS: uniform22CH/9CC, directions/carbon scale,
indexed graph and fields; byte equality outside the one embedded literal;
1,912protected existing file hashes;2JS syntax/3Python ASTs. A separate
Chemistry Validator /root/validate_alkane_ch_quarter,
ROLE_ID NAMELECULE_CHEMISTRY_VALIDATOR_V1_20261023, independently verified
both molecular hashes/coordinates, C10H22, neutral charges, C4/H1valences,
indexed bonds/order and unchanged140records. No chemistry finding. Unchanged
SDF graphs were not redundantly revalidated.

Developer isolated Firefox:12before/after cases (1500/390px, zoom0.5/2/2.5),
5identical-SVG guards including the previous dimethyl prototype,4number/highlight
interactions with six parent numbers and actual-ink collision checks, and
PNG/SVG export smoke PASS. Allafter cases have C–C/font≈2.6175, equal C/H fonts,
no recorded clipping/overlaps/JS errors, minimum remaining stroke1.45px and
sampled white gap0.658px. Largest captured same-type stroke variation across
orientations0.067px from native rounding; no pixel-perfect equality claim.
Normal desktop font22px; narrow fitting can reduce it to preserve full drawing.
The existing lesson's expanded step18 PASS at both widths,32atoms visible,
without editing its JSON. Three screenshots are2D evidence only; scripted
main selection can leave sidebar/radios/3D on an earlier state.

Independent consolidated fresh-context Reviewer /root/review_alkane_large_uniform,
ROLE_ID NAMELECULE_REVIEWER_V1_20261023, verified all15hashes, exact diff,
MOL/source/graph/valence/coordinate/scope invariants,1,912protected hashes and
2JS/3Python syntax checks, and inspected the three suppliedPNG/runtime records.
No actionable P0/P1/P2/P3 findings; no corrections required. Browser results
remain Developer evidence, not independent runtime execution.
Frozen15-path manifest docs/checks/alkane-large-uniform-review-target-20261030.json,
SHA25633b867bcccd034a39b4daee896bc61e5b1f45fdbb683519f49dc0b37cc4b8e69.
Immediate baseline/diff/static/browser/lesson results and screenshots use the
alkane-large-uniform-* prefix under docs/checks. Reproducible scripts:
check-alkane-large-uniform-20261030.py,
test-alkane-large-uniform-20261030.py and
test-alkane-large-uniform-lesson-20261030.py.

No new naming rule or learning sequence; Learning Designer N/A. No Safari,
physical-device, full3D, all-lessons or React run. Earlier ACQ-R1 remains outside
the two updated prototypes; this captured largest-alkane case/lesson now passes.
No universal library display fix is claimed. Local only, no commit/push/publication.
No core file changed this session. Final source/evidence hashes remain identical
to the reviewed target. Isolated testFirefox9284 was stopped; userFirefox and
server8013 were left untouched. Next: user refreshes Firefox (Cmd+Shift+R) and
evaluates this expanded molecule before any extension to additional molecules.
