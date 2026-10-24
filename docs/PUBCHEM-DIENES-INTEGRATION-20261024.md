# PubChem 3D integration — 2026-10-24

Approved replacement of five new diene 3D models with the previously downloaded,
chemically checked PubChem records. See PUBCHEM-DIENES-AUDIT-20261024.md for
retrieval evidence, CID list and the rejected allene geometry.

Source and runtime SDFs are byte-identical downloads, with CID, URL, retrieval date,
SHA256 and graph-derived heavy-atom mapping in each provenance JSON. Only their
mainChain3D arrays change in application data; all 2D assets and embeds are preserved.
The 1,2-butadiene RDKit SDF/provenance remain unchanged. Stereochemistry stays
unspecified in names: a downloaded conformer illustrates geometry rather than an
assigned R/S or E/Z identity. CID549148 specifically has one undefined stereocenter.

The generator preserves existing PubChem 3D records after checking source/runtime
hashes, instead of silently replacing them with RDKit. Chemical and browser checks
now account for graph-preserving 3D atom renumbering and equivalent terminal methyls.

Developer checks: 24 molecular forms pass formula, graph, valence, explicit H,
coordinates, crossings (2D), bond length (3D), provenance hashes and allene geometry.
36 naming cases pass across three representations and two chain modes.
Developer browser checks: all 36 combinations (six molecules, three forms, two
chain modes) pass displayed names, actual JSmol atom counts, component clicks,
branch carbons and attached hydrogens, without JavaScript errors. Screenshots
for the largest PubChem molecule and retained allene were visually inspected.
An isolated /tmp generator run preserved all five PubChem SDF/provenance pairs
and generated the local allene without touching repository assets.

Independent Reviewer /root/review_pubchem_dienes (fresh real reviewer role) checked
21 frozen hashes, all five raw-download identities/CIDs, 701 unchanged baseline
files, only five mainChain3D data changes and preservation of core/viewer/2D/allene.
It independently ran the 24-form chemical and 36-case naming checks, all passing.
Browser/generator/visual results above are Developer evidence, not independent
execution. No new network retrieval or independent browser/visual certification.
One P3 finding: stale generator documentation said no PubChem data was used.
Corrected to describe preserved PubChem records and local RDKit fallback;
docstring-only independent re-review resolved P3: all21 hashes match, other20
files unchanged, generator differs solely in opening documentation. No remaining
actionable findings within reviewed scope. No blocking or functional/chemical findings.
Freeze: checks/pubchem-freeze-20261024.json. No enforced reviewer filesystem
isolation claimed; reviewer obeyed the behavioral read-only instruction.

No core or viewer changes in this follow-up. Earlier core50 naming changes predate
this task. Local working tree only; no stage, commit, push or publication.
Baseline backup: /tmp/namelecule-before-pubchem-20261024-010224
