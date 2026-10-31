# Propene Expanded label clearance — 2026-10-31

## Approved scope and conference criterion

After declining an initial change and requesting comparison, the user explicitly
moved past that comparison and requested a safe correction. This renews approval
of the previously presented propene-only Expanded viewer/cache plan. It does not
authorize expansion to all alkenes, a core change or publication. The professor's
observed gap is accepted; its runtime difference remains unresolved. The fix does
not claim to explain that observation. See PROPENE-GAP-INVESTIGATION-20261031.md.

The user instructed all agents to prioritize reliable presentation at ENEPHET in
April2027. Official https://synedrio2027.enephet.gr/ confirms23–25April2027,Volos.
A permanent section at the top of AGENTS.md records scoped/reversible work,
affected interaction/scenario checks, review and recovery, honest limits and a
future machine/browser rehearsal. It does not claim a tested offline fallback,
a freeze/release already prepared, guaranteed uptime, or authority to publish.

## Implementation

Only the existing fPadExpandedAlkaneLabels gate is extended to selectedMol=propene
in Expanded. Reuses its already present real-glyph measurement/padding branch;
alkane fixed-square masks and every other algorithm are byte-identical. Updates
only existing C/H backplates, preserving their fills and native atom centers,
labels, SVG bond lines, names and fit. The HTML changes one viewer cache URL.
Other alkenes/modes remain excluded. No new dependency or renderer is introduced.

Baseline docs/checks/propene-gap-before-20261031.json.gz contains exact pre-change
AGENTS/viewer/HTML and770protected runtime hashes. Source HEAD168e3cec01f941a84d40bbe0dc07156e7baa35d0;
last full checkpoint5230897ad5623ef1f4f3810ce0a6032123a8242d is also retained.
Snapshot scope is the immediate working tree, not a claim of a clean branch.
Core52 SHA d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2 unchanged.
No MOL/data, topology/IDs,3D,scenarioJSON,teaching,core or React source/build changes.

## Developer verification

- Static: exact5-line viewer gate/comment change, one HTML viewer cache URL;
  unchanged770runtime hashes and original Git index. JavaScriptCore syntax and
  two Python ASTs PASS. One initial static assertion expected both existing cache
  keys to change; corrected the test to the approved viewer-only URL, not the app.
- Real Firefox: all422available2Dforms/141molecules before/after. Only propene
  Expanded SVG differs. Every form's bond lines, text markup and viewBox are
  identical;421completeSVGs are identical, including all8expanded alkanes.
-24before/after raster cases at viewport1500/390CSSpx, DPR1/2 emulation and zoom
  0.5(min)/2(default)/4/6(max). The7single bonds, including all6C–H, are mapped via
  svgBondList (C=C emits two lines). All after cases have positive raster-verified
  endpoint clearance; minimum0.825CSSpx, minimum remaining stroke7.783CSSpx.
  Initial minimum before gap−2.408CSSpx. Double-bond lines are invariant under the
  whole-library guard; the endpoint raster probe intentionally measures singles.
-6actual name-component interactions (chain numbering and double-bond highlight)
  pass endpoint checks; each numbering set has3items. Real menu/mode/zoom controls,
  molecule switches and mask reapplication are checked. Mask helper idempotence
  PASS. This is not a claim about all existing full-fit oscillation conditions.
- Existing alkene lesson replay:12step visits across desktop/narrow (steps1,5,19,
  21,20,21); selected molecules/modes/presentation state match saved JSON. On step21,
  select the already allowed propene, switch Expanded, verify gaps, navigate away/
  back and verify restoration. No new step/preset or educational text was added.
- PNG export blob>1000bytes and parseable SVG PASS. Not a pixel comparison of the
  downloaded PNG. Screenshot3 visually inspected. Geometry-only before/after
  screenshots use direct2D loads and can retain methane3D/radio UI from initialization;
  the presentation screenshot and later real controls show actual propene UI.
- Zero recorded JavaScript errors in this bounded run. Initial test invocation
  of the earlier comparison harness once ran before Firefox was ready; current
  implementation launcher awaits its port. No claim about earlier JSmol rapid-
  switching diagnostics being fixed or universal service/console cleanliness.

Sources: check-propene-gap-20261031.py/test-propene-gap-20261031.py and
propene-gap-{static,browser,source,before,after,presentation}-20261031 artifacts.
Browser/raster evidence above is Developer evidence, not independent execution.

## Limits and review state

This run uses isolated actual Firefox; narrow/DPR2 are emulations, not a real
phone/projector/retina-device rehearsal. No Safari/Chrome, general3D regression,
all337lessonsteps, network-loss or conference-machine run was performed. Online
JSmol/CDN dependencies and previously recorded rapid-switch uncertainty remain.
No conference-ready certification is claimed. Pure mask display change: Chemistry
Validator/Learning Designer/Planner are not activated; chemical/pedagogical data
and learning sequence are invariant. Independent consolidated Reviewer completed without actionable findings; details below.

Local only. No commit, push, publication or upstream synchronization. UserFirefox
andserver8013 retained; isolated test processes are owned by this unit.

## Independent review and supplemental navigation — final status

Fresh Reviewer /root/review_propene_conference_20261031,
ROLE_ID NAMELECULE_REVIEWER_V1_20261023: no actionable P0/P1/P2/P3 findings.
Frozen13paths manifestSHA68ed8ee6e279768f83cce6eb7c6b4c89b968bfbcff63806c6fa2aa507405923f.
Independently verified all hashes, exactdiff/gzip/base64,770protectedruntimefiles,
index, JSCsyntax andPythonAST, surrounding code/test dependencies and3screenshots.
Browser observations are Developer evidence, not independent runtime execution.
No full repeated review; sourceAGENTS/viewer/HTML and previous test evidence stayed
frozen. Only this status section and project records are updated after review.

Supplemental Developer test after review:6real scNext/scPrev clicks at1500/390px
reached expected steps/molecules/modes; real scExit returned to14lessonlibrary.
Combined navigation+next-scope audit logged38nativeJSmol null-viewer errors
(2setDisplay,36updateJS), not yet localized to a phase or causally explained.
Do not describe this supplemental run as console-clean or declare conference
readiness. The earlier bounded422/24/12 run remains accurately recorded as0errors;
this later evidence is separate. No JSmol fix, source change or cause claim.
A separately scoped baseline/current lifecycle diagnosis is the next step for
that uncertainty, not repeated unchanged tests.

Latest user asks the same inspection/fix for ALL alkenes. Read-only audit found
7eligible expanded forms;6uncorrected forms show contact at C/H;propene passes.
Both double-bond line primitives were included in this new audit, which is not
a claim that the earlier single-bond probe covered them. The implementation
remains propene-only until the category extension's concrete plan is approved.
Evidence/source: alkenes-gap-audit-and-navigation-20261031.py/.json.
