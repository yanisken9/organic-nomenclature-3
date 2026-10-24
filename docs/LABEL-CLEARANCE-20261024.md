# Shared CHn label clearance — 2026-10-24

Approved request: remove unjustified visible C=C length differences across all
molecules, preserving shortening where actual H/labels occupy bond space.
Read-only audit:86molecules x4requestedforms,100C=Cviews in25molecules; eightdienes
have multipleC=C. Rawbutadienecondensed lines750/750, oldwhiteplatesleave330/100.
The shared fAddHydrogens2SVG shiftedCH2/CH3 text160units left and used unrelated
hardcodedplate widths/positions. This changes visible carbon anchoring.

Implementation viewer50 only: retain original JSME C text anchor, append H/subscript
as before; size carbon whiteplate to actual getBBox plus uniform6percentfontsize
clearance (20SVGunit fallback). Apply to condensed/condensedZigZag globally; no
molecule whitelist. Do not equalize actual segments or erase justified H-space.
Existing parallel-double helper, molecule geometry/stereo/3D/core remain unchanged.
HTML viewer URL cache revised. Source and runtime scientific files unchanged.

Developer checks
-86x4 requestedviews compare old/new function loaded in browser memory: identical
 names/textcontent and bondlinecoordinates. Actual expanded/skeletal unchanged.
 Methane unsupportedrequestedmodes use the pre-existing condensedfallback.
-691Canchors retain originalJSME x; symmetricexpandedbutadienedoublelengths equal;
 actualCH2 label occupation/platecoverage and highlight/zoom1/2/3 checked.
-Actual PNGBlob creation in condensed/condensedZigZag, exportedSVGanchorattributes
 match snapshot at exporttime; screenshots in/tmp visually inspected.
 Export test waits for scenario+JSmolactualmolecule, since earlyinitialization can
 race incomingmolecule. Intermediate test attempts failed from comparing export
 to asynchronouslyupdatedliveDOM and starting beforemoleculeloaded; corrected
 synchronization/expected snapshot, finaltwoexports pass withoutJSerrors.
-202protectedhashes preserve core,data,scenarios,sourceMOL/SDF/provenance and runtimeSDF.

Browser scripts docs/checks/test-label-clearance-browser-20261024.py and
 test-label-clearance-png-20261024.py; matrix evidence label-clearance-evidence-20261024.json.
Comparison test requires archived taskbackup/tmp/namelecule-before-label-clearance-20261024;
this is an archival regression comparison, not a portable standalonefixture.
SourcePNG/screenshot artifacts only/tmp. No full raster pixelcomparison claim.
Frozen5paths/hashes label-clearance-freeze-20261024.json; independent review completed without actionable findings.
Reviewer /root/review_label_clearance (fresh actual reviewer context) independently
verified5frozenhashes,202protectedfiles, renderer/rectmapping/functionalcompaction,
HTMLcacheURL, PythonAST and gitdiffcheck. Browser/PNG results remain Developer
execution; no full raster comparison or independently repeated browser run.
Reviewer inspected one Developer direct2D screenshot, which alone does not verify
wholeUI selection synchronization. Developer also inspected scenario lesson view.
No core changes thissession; local only, no stage/commit/push/publication.

Developer additional targeted hidden-SVG load/reopen-redraw check passed without JS errors; no frozen-target changes.
