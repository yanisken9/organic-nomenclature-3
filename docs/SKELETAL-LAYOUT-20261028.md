# Permanent skeletal geometry and framing — 2026-10-28

Approved continuation of the global-layout plan with the user's two-stage
clarification: optimize chemical geometry, then frame the whole rendered drawing.
Priority is chemical correctness, horizontal parent development, readability and
centering. The named example is
2-αιθυλο-3-ισοπροπυλο-6,6-διμεθυλο-2-επτεν-4-ινοδιικό οξύ.

## Why earlier changes were inconsistent

The previous common core preference chose between chemically equivalent numbered
parents; it did not rotate the molecule. Later tools rotated selected molecule
batches using different criteria: parent endpoints, principal axes, selected bond
axes or minimum parent height. The viewer loaded each skeletal MOL as supplied.
Principal-axis alignment alone does not minimize vertical parent spread.

The original fFit2DSVG already centered the combined bond/label bounds. An initial
Firefox sample of nine molecules ×two viewports found no clipping and at most
0.267px horizontal center error. The missing common step was molecular geometry,
not a first-atom-based centering algorithm.

## Two reusable stages

1. Viewer52 resolves the parent through the existing naming pipeline on the
   original input. fSkeletalLayoutMol builds a transient V2000 display copy.
   It chooses a proper whole-molecule rotation minimizing the parent’s vertical
   extent, with C1→last-C progressing left to right. Ties prefer lower whole-shape
   height, then the smallest rotation. Single-C/degenerate parents retain their
   orientation. No zigzag is flattened or molecule reflected.
   A rotation cannot repair an invalid bond angle. A bent degree-two sp carbon
   therefore gets a local repair only when an entire side is separable: that
   side rotates about the sp center, preserving bond lengths and other angles.
   Ring-connected sides are rejected. Worsening close nonbonded atom pairs/new
   proper bond crossings and nonincident atom-to-bond contacts reject and roll back a proposed local correction.
2. JSME generates upright labels from the resulting geometry. Existing
   fFit2DSVG then fits/centers the whole visible bond/text/path bounds, with
   label/numbering margins, in the actual viewport. No new centering algorithm
   was required. Existing resize/zoom paths rebuild and refit the final drawing.

Geometry always derives from the original loaded source and the live numbered
parent; source coordinates never accumulate transformations. Chain changes
invalidate the applied-parent cache. Highlights/zoom/resize do not reread/reset
an already applied geometry. Saved records, source/embedded MOLs, atom IDs,
scenarios, core52 and all3D files remain unchanged. Condensed, expanded and
annotated-zigzag modes retain their original behavior.

The shared hook covers all133 available skeletal forms in the134-entry library
and future forms loaded through it. Methane has no skeletal form and keeps its
existing fallback. Both embedded hosts load the same viewer; only their viewer
cache URL changed. Regenerating those hosts from the current Main template would
also import unrelated font/settings changes, so those were deliberately preserved.
Permanent rules are in AGENTS.md and docs/REVIEW-CHECKLIST.md.

## Evidence and before/after

- test-skeletal-layout-20261028.py —802 real-core naming cases unchanged,
  266 skeletal geometry cases (133 × algorithmic/data),84 sp-angle checks;
  minimum final sp angle179.97977°. All bond fields, indices, charges, stereo
  fields, z and non-coordinate MOL records remain identical. Bond lengths and
  other local angles remain within four-decimal rounding tolerance.
- 43 available forms have reduced parent height in both chain modes. The user’s
  acid requires no local change: proper rotation178.14569° gives parent height
  0.9529→0.84309coordinate units and C1 on the left. Its triple-bond geometry
  remains intact. Only butanenitrile C1 needed local repair,120° → 180° in the
  transient display; its stored MOL and3D remain unchanged.
- test-skeletal-layout-guards-20261028.py —9 synthetic probes cover valid/bent sp,
  ring rejection, crossing/contact rollback (including collinear overlap), malformed input and invalid parents.
- Firefox test-skeletal-layout-browser-20261028.py —266 library/viewports cases
  (all133 forms at1500/390),18 representative before/after comparisons,9 other-mode
  invariance cases, real selection/highlights/numbering and resize. Zero observed
  label overlaps; minimum measured frame margin15.6167px and maximum horizontal
  center error0.375px. All labels/drawings stayed inside the frame. NoJSerrors.
- After the local-repair safety guard was added, all 266transformed outputs were
  compared with the browser-tested outputs and remained byte-identical. The
  later follow-up exercised the selected molecule and embedded hosts.
- Firefox test-skeletal-layout-interactions-20261028.py —four zoom steps preserve
  geometry/name/2D3D parent state and selection; alternative-chain roundtrip
  restores identical geometry. Real2D PNG exporter produced a nonblank1200×692
  PNG (51,939bytes), with the expected acid name. Downloads were intercepted.
  Viewer/lesson hosts load the helper and retain their original sizing flags.
  Separate-tab final run had zeroJavaScript errors.
- An earlier same-tab page-navigation run exposed four external JSmol viewer-null
  errors during page replacement. Similar errors pre-exist in dated browser
  artifacts (including main-2d-scale-browser-20261027.json). They are preserved
  in skeletal-layout-interactions-page-navigation-20261028.json, not silently
  discarded. This work does not fix JSmol page teardown.
- 520 molecular/scenario/core/data files matched the session baseline. JS syntax,
  Python AST and source diff whitespace checks were performed.

Developer screenshots/export remain under /tmp/namelecule-skeletal-layout-20261028:
user-acid key ending hepten_2_yn_4_dioic_acid-before.png / -after.png,
butanenitrile-before.png / -after.png and selected-acid-export.png.
Numeric evidence and baselines are under docs/checks/skeletal-layout-*20261028.*.

Chemistry Validator /root/skeletal_chemistry independently checked all133 authored
forms, proper rotations, signed angles, bond fields, orientation and520protected
hashes. Follow-up independently passed the initial 7 geometry guards on pre-contact-guard viewer SHA256
2f5b19e9a6b96cd153da7ec50d51e5d091f5d9c486ea3f695bd8ae02fa1a01f1.
Consolidated Reviewer /root/skeletal_review reported SKEL-01 P2: the initial
proper-crossing guard missed an endpoint landing on an unrelated bond. The
correction checks nonincident atom-to-segment clearance, rolling back endpoint
contacts and collinear overlap; two regression probes were added. Targeted
independent verification by the same Reviewer closed SKEL-01 on final viewer
SHA256 fee628ac0ff28d4df9cfbb5d695d09717f43b459c8c2594587531c70ddb12493:
9 probes passed, the exact reproduction rejected/rolled back, and all266final
outputs independently recomputed identical to the browser-era outputs. No
additional actionable findings. Browser execution remains Developer evidence.
The current-library outputs were compared again after this correction; browser
evidence is retained only where those outputs remain byte-identical.

## Limits and state

The local guard is bounded: it rejects new or worsened close nonbonded atom
pairs, proper crossings and nonincident atom-to-bond contacts. It does not prove
freedom from all future rendered label collisions. Current-library labels
were checked in Firefox; rigid rotations preserve existing crossings. Unsafe
future sp repairs are skipped rather than tearing rings or forcing geometry.
No claim of universal optimal layout, new chemistry support or IUPAC certification.
No classroom test. The existing external JSmol page-teardown issue remains.
Visual inspection of the actual exported PNG also found clipping of the very long
acid name in its name-box strip. The molecule is framed; the name-strip exporter
is unchanged by this task. This pre-existing export limitation remains outside
skeletal geometry/framing scope and is not counted as a new regression.

No core changes in this task. No commit, push or publication.
