# Common expanded alkane presentation completed — 2026-10-30

The user approved the same final settings for the remaining methane, ethane,
propane, butane and pentane. All eight current expanded alkanes now have source
C–H=0.3094 and C–C=0.6188 where present (90C–H and29C–C altogether).

Only four embedded Expanded MOLs change in this unit: ethane–pentane.
Their10C–C change0.825→0.6188;36C–H translate with the same carbon and retain
their0.3094relative vectors. Carbon coordinates use round(oldxy×0.6188/0.825,4).
Indexed graph, atom IDs/order, headers, z, atom fields and bond records remain.
The methane MOL is byte-identical, including its four0.3094C–H. There are no
separate physical Expanded MOL sources for these keys; none are created.
Other137records, including the three previously reviewed branched prototypes,
target condensed/skeletal, metadata, core,3D, scenarios and React stay unchanged.

Application paths: js/jsme-nick-nomeclature-moc2-data_52.js,
js/mulermoc-nom-molview-52.js and mulermoc-nom-52.html. The existing display
helper now accepts all eight known keys. Its original C–C/font calibration2.6175
remains. Methane has no C–C, so its font calibration uses twice the native C–H
length, equivalent to C–H/font1.30875. This is a numeric calibration only; native
bond/atom anchors are not moved. Centered glyphs, equal square masks, numbering
and framing reuse the existing pipeline. Two HTML cache URLs change.

Developer static PASS: four exact coordinate/field/graph deltas, data byte equality
outside four literals, all eight final source lengths,1,938protected existing
file hashes and2JS/2Python syntax checks. Chemistry Validator
/root/validate_alkane_ch_quarter, ROLE_ID NAMELECULE_CHEMISTRY_VALIDATOR_V1_20261023,
independently verified the data hash,10CC/36CH, unchanged H vectors, CnH2n+2,
neutral C4/H1valences, indexed graphs/fields/directions and unchanged methane
and all other data. No finding; unchanged SDF work was not repeated.

Developer isolated Firefox PASS:60before/after cases (five targets×1500/390px×
zoom0.5/2/2.5),12identical-SVG guards (nine available other forms plus three
previous expanded prototypes),10parent numbering/highlight interactions with
1–5numbers and actual-ink collision checks, preparation idempotence and PNG/SVG
export smoke. No recorded overlaps, clipping or JS errors. After C–C/font≈2.6175
and C–H/font≈1.30875, common C/H font sizes, remaining stroke≥1.4499px,
sampled white gap≥0.6833px, max same-type stroke variation0.0668px. Native
rounding prevents a pixel-perfect equality claim. Responsive framing can reduce
font size when space is limited. Four screenshots cover methane/pentane before
and after, as2D evidence only; scripted selection can leave otherUI/radios/3D stale.

Independent consolidated fresh-context Reviewer /root/review_alkane_all_uniform,
ROLE_ID NAMELECULE_REVIEWER_V1_20261023, verified all13hashes, exact diff,
MOL/graph/valence/direction/field/scope invariants, registry/order,1,938protected
hashes and2JS/2AST syntax checks. All eight source-length totals independently
confirmed. Four suppliedPNGs, browser script/dependencies and results inspected.
No actionable P0/P1/P2/P3 findings; no corrections required. Runtime remains
Developer evidence, not independent Reviewer execution. Frozen13-path manifest
SHA256cc706cc33bfe2f07c45026120e4e98cca52d439e254053e89609b5236fb75a9b,
docs/checks/alkane-all-uniform-review-target-20261030.json. Immediate baseline,
exact diff, static/browser results and screenshots use alkane-all-uniform-*.
Reproducible check-alkane-all-uniform-20261030.py and
test-alkane-all-uniform-20261030.py reuse existing raster/number probes.

No naming rule or learning sequence changed; Learning Designer N/A. Existing
lesson presets for these five remain condensed; its only expanded step uses
the unchanged larger branched prototype. No redundant lesson,3D, physical-device,
Safari or React run. The old ACQ-R1 captures describe the superseded branched
experiment; those three were addressed/tested/reviewed in earlier prototype
units, including step18. This unit verifies five new cases and preserves the
three existing ones; it does not claim fresh whole-app certification.
Local only, no commit/push/publication. No core file changed this session.
Final13target/1,938protected hashes remain identical after review.
Only isolated testFirefox9954 was stopped; userFirefox/server8013 remain.
Next: user refreshes Firefox (Cmd+Shift+R) and evaluates all eight expanded
alkanes before any new scope.
