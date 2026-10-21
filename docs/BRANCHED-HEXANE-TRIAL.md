# 3-αιθυλο-2,5-διμεθυλοεξάνιο — τοπική προσθήκη21/10/2026

## Εγκεκριμένη προσθήκη

User approved three2D MOLs, PubChem3D SDF, local alkane integration and checks.
Key ethyl_3_dimethyl_2_5_hexane, C10H22, PubChem CID521421.
Source https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/521421/SDF?record_type=3d

Source MOLs in mols/new_molecules/, runtime SDF in mols/nomeclature-moc2/,
exact SDF source copy in new_molecules.3D raw PubChem bytes preserved. Data48
metadata and MOL2D registry extended from72to73keys; HTML data-script version
refreshed. No core/viewer edits for this addition.

2D style derives from same-carbon-skeleton large alkene: change2–3bond to
single, add explicit H at C2andC3 in expanded. Condensed10C/9bonds; expanded
10C22H/31bonds, skeletal10C/9bonds. Carbon valence4/Hvalence1 verified,
all bonds single. No stereo teaching specification added. C1..C6stored chain;
ethyl8–9at3, methyl7at2and10at5. Graph isomorphism to PubChem verified,
stored3Dchain[6,3,1,2,4,8]. See checks/branched-hexane-20261021.json.

## Checks completed

Data JS syntax. Both core chain modes and three available2Dforms produce
3-αιθυλο-2,5-διμεθυλοεξάνιο. All72prior molecule names unchanged across
430available cases. Actual Firefox classified alkane and loaded local3D SDF;
four2D modes, correct disjoint ethyl/dimethyl carbon selections in2D/3D,
expanded branch H5/H6 and exact paint/Jmol atom selections. Stored-chain
highlight passed; prior alkene/halogen regression checks passed. Expanded
screenshot visually reviewed, expanded/skeletal assets saved.

## Outstanding core issue found in final alternative-chain audit

Default algorithmic and stored name correct. Algorithmic pool includes6paths.
Stepping all paths through fGuessName(true) yields:

- [1,2,3,4,5,10] and [1,2,3,4,5,6]:3-αιθυλο-2,5-διμεθυλοεξάνιο
- [6,5,4,3,8,9]:4-ισοπροπυλο-2-μεθυλοεξάνιο
- [6,5,4,3,2,7]:4-αιθυλο-2,5-διμεθυλοεξάνιο
- [7,2,3,4,5,10]:3-αιθυλο-2,5-διμεθυλοεξάνιο
- [9,8,3,4,5,10]:3-ισοπροπυλο-5-μεθυλοεξάνιο

Source fRankChainPool ranks multiple bonds/double bonds/length/FGanchors but
not branch count; fOrientChainPath needs orientation comparison for this graph.
This makes some offered alternatives non-equivalent choices for the preferred
parent/name. No core fix attempted yet: ask approval for concrete general
core change, preserve existing priorities for FG/multiple bonds, maximize
branch count only within tied eligible paths, orient using sorted locant sets.
Check2D/3D consistency and all73names/synthetic bonds after any change. This
is not a complete validated alternative-chain experience until fixed.

No commit/push/publication; user deferred all saves until end of session.
Core addition SHA unchanged from after today's earlier sync. At session end
report earlier core sync and any subsequently approved fix to professor.

## Update — approved parent-chain fix completed

User approved generic core correction and requested professor-facing record.
Implemented connected acyclic hydrocarbon guard, carbon-branch locants in
2D/3D orientation, saturated-parent maximum branches/lowest locant filter.
Pool now4equivalent correctly oriented paths, all proper name.20atom/bond
permutations and synthetic unsaturation tests passed. All73default names
unchanged in436available before/after cases. Firefox new/old large molecules
all4modes/all4paths,2D/3D/H/paint sets and stored/regression checks passed;
22-step lesson/rules/horizontal paths retained. See CORE-CHANGES-20261021.md
and patch/test artifacts. Earlier outstanding section is historical, resolved.
No commit/push/publication. Core change recorded for end-session reporting.
