# PubChem-first 3D audit — 2026-10-24

User agreed PubChem as first source when suitable; validate before replacement,
use local RDKit when absent/unsuitable. READ-ONLY application audit; no assets,
core/viewer/data changed. Actual6name queries/3DSDF requests allAPI200; files only
/tmp/namelecule-pubchem-dienes-20261024. lookups.json/validation.json containURLs,
status,rawSDFSHA256 and preliminarygraph/formula/H/bond/geometryresults.

CID7845butadiene1,3;11535butadiene1,2;11587pentadiene1,4;20682methyl3pentadiene1,3;
137118dimethyl2,3pentadiene1,3;549148ethyl3dimethyl4,5hexadiene1,4.
All6graphs/formulas/explicitH/finitecoords/valence/bondlengthspass preliminarychecks.
Cachedweb11535saysQCgenerationfailed but actual3DAPIreturnedSDF; inspectedactualfile.

Independent ChemistryValidator /root/validate_methylpentadiene_plan confirmed
PubChem11535allene unsuitable:axis179.955deg but endplanes~0.074deg (coplanar),
local179.959deg/endplanes~89.93deg. Developer independentplane-normalcalculation
0.089deg vs89.9997deg; smallmethodvariation, same conclusion. RetainlocalRDKitallene.
Other5onlyboundedchecks,notfullgeometry/visualcertification. CID549148metadata
undefatomstereo1/defined0; illustrative3DmayparseC@ withoutdefininggenericR/Sidentity.
No claimPubChemgloballyinferior/superior; currentrecord geometrydeterminesfitness.

Proposed scope awaitingapproval:replace5source+runtimeSDF/provenance withPubChem,
keepalleneRDKit;update5mainChain3D mappings via graph notatomorder,tests forchanged
indices andbrowserhighlight/camera;preserveall2Dlayouts/names/core/viewer;independent
finalReviewer. No commit/push/publication. No corechange in thisaudit.

butadiene_1_3 CID7845 sourceSHA256 43732aa4850eec220cbc316f8b8373702ed7d400fcb8097c56d3240b933e4b1e candidateMainChain3D [3, 1, 2, 4]

butadiene_1_2 CID11535 sourceSHA256 93575de1907ff4672416098254fc0cdfb80294e8add837977b64958294663803 candidateMainChain3D [4, 3, 2, 1]

pentadiene_1_4 CID11587 sourceSHA256 2a8c49abdf96156b572d9cfec7f11b65fc9f46b5740b571f30437998ad3fd921 candidateMainChain3D [4, 2, 1, 3, 5]

methyl_3_pentadiene_1_3 CID20682 sourceSHA256 a430bcf151ab4ce8e00fbe283ead33c01805a890a2881a58cfd0e6e9a5620de3 candidateMainChain3D [6, 5, 1, 2, 4]

dimethyl_2_3_pentadiene_1_3 CID137118 sourceSHA256 2e54e431165f62f79a11fb964055b1355b42ecfa1f67681ca6b2e79fc3efee8a candidateMainChain3D [7, 2, 1, 4, 6]

ethyl_3_dimethyl_4_5_hexadiene_1_4 CID549148 sourceSHA256 5621b1f9c870a40be0bebc5cb8ccc3d545fffefb0f4964d661ee7f87d3280f9d candidateMainChain3D [10, 5, 1, 2, 4, 8]
