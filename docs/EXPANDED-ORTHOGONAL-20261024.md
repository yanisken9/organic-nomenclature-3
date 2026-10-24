# Orthogonal expanded diagrams — 2026-10-24

User approved horizontal main-chain/cardinalH/branches for the six new dienes,
following supplied teacher image. Diagrams show connectivity, not hybridization
angles or E/Z/R/S projections. Main conversation Developer. No core changes in
this follow-up; previous core50 εξαδιένιο fix is pre-existing. No commit/push/publication.
Backup/tmp/namelecule-before-expanded-20261024-003321 plus baseline manifest.
Final frozen13file target: checks/expanded-freeze-20261024.json.

## Final implementation

Six *_2D_Expanded.mol coordinate fields and matching data50embeds changed.
Atom IDs/order/explicitH/charges/connectivity/bond orders AND raw stereo fields
match baseline exactly. Parent horizontal, C-C1.17/C-H0.78, branches/H cardinal.
Generator orthogonal_expanded helper reproduces coordinates; full generator not
rerun so no3D/sourceSDF/runtimeSDF/provenance changes. Drawing preference recorded
for these six and future additions, not a bulk rewrite of old molecules.

Independent first review foundP2: changing unknown double stereo3->0 could make
RDKit inferZ for dimethylpentadiene. That attempt was REVERTED. RawMOL bondlines
including unknown3 restored exactly; new test rejects specific E/Z/CIS/TRANS after
RDKitparse. All six pass without that inference. Historical failed freeze hashes
retained in previousReviewFiles in finalmanifest for audit, not current deliverables.

User then explicitly APPROVED minimal viewer-only scope extension. Function
fDrawOrthogonalExpandedDoubleBonds runs only for expandedmode and sixselectedkeys;
uses svgBondList to redraw crossed pair as parallel horizontal SVG lines. Raw
applet graphics/MOL data are unchanged. Molecule graphs and source stereo identity
are preserved. Existing per-bondline count/order retained for highlight indexing.
HTML data/viewer cachekeys updated. Core/condensed/skeletal/3D remain unchanged.
Prior user rejection of allene skeletal centralC exception remains respected.

## Verification

- check-expanded-orthogonal-20261024.py:6pass parenthorizontal/cardinalbond axes,
  C-C/C-H lengths,formula/explicitH,sourceembed,generatorcoords; no inferredspecific
  alkene stereoisomer. SourceMOLdiff:onlyatom coordinatecolumns differ frombaseline.
- check-dienes-20261024.py:24forms graph/formula/valence/H/clearance/noncrossing/
  3D/allene checks passed; test-dienes-naming-20261024.py36cases passed.
- Actual Firefox6x3formsx2modes names/renderednames/components/branchC2D3D/H pass
  in previous run; finalSVG/PNGregression passed all36cases,parallelpairs aftercomponentclicks,
  PNGBlob/exportSVG and noJSerrors.
- Six finalexpanded previews usingactualmodeselector captured/visually inspected.
  No label overlap seen. SVG rawversusrendered debug confirmed originalcrossed pair
  remains in applet SVG while displayed pair is parallel with nonzero separation.
- Final test-expanded-browser-20261024.py extends existingdiene browserchecks with
  parallelSVGpairs aftercomponentclicks and realPNGBlob/exportedSVG verification.
- IndependentReviewer /root/review_expanded_layout re-review complete: initialP2resolved,no newactionable findings. See
  EXPANDED-INDEPENDENT-REVIEW-20261024.md.
- Core and all condensed/skeletal/SDF/provenance byte-identical to follow-upbackup.

No audible/classroom/exhaustive zoom/mobile/visual certification claimed.
PNG test captures generated blob/exportSVG with anchor interception, not real diskdownload.
Final frozenhash/diffcheck pass. Next:userrefresh and visualacceptance.
