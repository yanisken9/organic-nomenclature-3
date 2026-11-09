# Single-molecule bond-length prototype — 2026-10-30

## Approved scope and final behavior

Only the expanded 2,3-dimethylbutane (`dimethyl_2_3_butane`) is changed.
The first approved iteration restored the last C–H reduction, then the user
explicitly approved equalizing all14C–H at0.3094 in the embedded MOL and two
physical sources. A subsequent explicit approval reduces all5C–C by25%:
0.825 →0.6188 (four-decimal rounding of0.61875). Carbon coordinates scale
uniformly by0.6188/0.825; each H translates with its C, retaining its0.3094
relative vector. Horizontal/vertical directions, atom order/IDs, indexed bonds,
z, charges and other fields remain. Historical source atom ordering is retained.

The prototype viewer derives its font from native C–C anchors, centers the glyph
ink and uses equal square backplates. The first calibration was C–C/font3.49,
from the professor's original2-methylpentane. The newly approved reduction changes
that ratio to2.6175; otherwise fixed display calibration would undo the MOL change.
Number size, clearance and fit are scaled consistently. Every SVG update starts
from fresh native output; repeated mask/preparation calls do not accumulate.

Application files: js/jsme-nick-nomeclature-moc2-data_52.js,
js/mulermoc-nom-molview-52.js, mulermoc-nom-52.html (two cache keys), and
mols/{new_molecules,source-2d}/dimethyl_2_3_butane_2D_Expanded.mol.
Other140molecules, target condensed/skeletal, core,3D, scenarios and React are
unchanged from each immediate baseline. The other7alkanes retain the earlier
C–H experiment; its ACQ-R1 readability issue is not claimed fixed here.

## Verification and review

First iteration: static scope/syntax and1,891protected files; isolated Firefox
18cases,5SVGguards,4number/highlight interactions and PNG/SVG export smoke.
Chemistry Validator /root/validate_alkane_ch_quarter independently checked the
three molecular sources. Fresh-context Reviewer /root/review_alkane_fixed_cc,
ROLE_ID NAMELECULE_REVIEWER_V1_20261023, independently verified13frozen hashes,
exact diff, molecular/data/scope invariants, JS/Python syntax, and inspected
supplied2D evidence. No actionable findings. Historical frozen manifest:
alkane-fixed-cc-review-target-20261030.json, SHA256
bf41649bbea0bc997bc05c301639e88f00ec64c1724f864ade83c154976c800a.

Final25%C–C iteration: Developer static PASS,1,900protected existing files,
140other records and other forms/code preserved;2JS syntax and2Python AST checks.
Firefox12before/after cases (1500/390px; zoom0.5/2/2.5),5SVGguards,
4number/highlight interactions, actual-ink number collision checks and PNG/SVG
smoke PASS, without recorded clipping, overlaps or JS errors. At normal desktop
font22px, C–C after/before=0.749753 and C–H=0.999459 (native rounding).
Visible same-type bond strokes differ by<0.15px across directions. Minimum
remaining C–H stroke1.45px, minimum sampled white gap0.6666px. Responsive fitting
can change actual font/pixel dimensions when space is limited; the calibrated
C–C/font reduction is25% throughout. No pixel-perfect equality claim is made.

Chemistry Validator independently verified the final three hashes, all5C–C,
all14unchanged C–H vectors, carbon scale, C6H14/valences/indexed graph/fields,
and byte equality outside the one embedded literal; no findings. Targeted
final Reviewer verification by /root/review_alkane_fixed_cc independently checked
all13new hashes, agreement of baseline with the previously reviewed5application
hashes, exact source/MOL invariants,1,900protected files, exact diff and2JS/2AST.
No actionable P0/P1/P2/P3 findings. Supplied runtime/after PNG were inspected;
no independent browser execution. Actual largest captured directional stroke
difference was0.067px. No second full review was run.

Evidence and reproducible scripts: docs/checks/alkane-fixed-cc-* and
alkane-cc-quarter-*, check-alkane-cc-quarter-20261030.py,
test-alkane-cc-quarter-20261030.py. Final13-path manifest SHA256:
acd7ab5895fdfdc49f27a0e9091120940b79a215c155955a51a43909cf4e447c.
Runtime is Developer evidence, not independent Reviewer browser execution.
Screenshots substantiate2D only; scripted selection may leave sidebar/radio/3D
on a previous state. No Safari, physical-device, full lesson/3D or React run.
The lesson's only scripted expanded step uses the untouched larger alkane.

Local files only; no commit, push or publication. No core file changed in this
work session (core52 SHA256 d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2).
Target sources/evidence remained unchanged through review and final hash checks.
Only the isolated test Firefox8654 was stopped; user Firefox and server8013 remain.
Next: user evaluates the prototype in Firefox (Cmd+Shift+R) before any expansion
to other molecules.
