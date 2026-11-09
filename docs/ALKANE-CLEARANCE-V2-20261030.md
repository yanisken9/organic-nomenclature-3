# Expanded alkane bond–glyph clearance — 2026-10-30

## Approved scope and result

The user reported that the previous vertical C–C mask adjustment still allowed
contact, supplied screenshots and explicitly included vertical C–H. After a
read-only investigation, the user approved clear gaps at both endpoints of all
C–C/C–H in the eight available expanded alkanes. This supersedes visual acceptance
of the earlier `ALKANE-LABEL-GAP-20261030.md` fix; its historical checks remain.

Only `js/mulermoc-nom-molview-52.js` and its cache URL in `mulermoc-nom-52.html`
change application behavior. `fPadExpandedAlkaneLabels` replaces the narrower
branch helper in the existing fit hook. It changes existing opaque backplates,
not native bond lines, glyphs, fonts, viewBoxes or atom anchors. At the final
screen font size, Canvas TextMetrics measure C/H ink extents, returned to native
SVG coordinates. Clearance is 0.08 em with a screen-pixel floor up to 1.5 px, plus any
visible text-stroke half-width. Below 8.34 screen-font pixels the floor decreases
proportionally (0.18 em), preserving short C–H strokes at minimum zoom. Square corners protect the complete stroke edge.
The helper is gated to expanded alkanes and recomputes from text on each call.

MOL/source/embedded data, the preceding C–H50% experiment, 3D, naming/core,
other categories/forms, scenario JSONs and React are preserved.

## Developer verification

- Scope/static checker: exact helper replacement, fit-call rename and HTML cache
  URL only; JavaScriptCore syntax and five Python ASTs PASS. 1,861 other existing
  files retain their pre-intervention hashes (the two journals are exempt).
- Before the small-zoom correction below, real isolated Firefox: 422 available forms over 141 molecules compared against
  the pre-intervention helper. All lines, texts and viewBoxes are identical;
  414 complete SVGs are identical. Only the eight expanded alkane masks change.
- 66 interactions over all eight alkanes at viewport widths 1500/390, including
  default/in/restored zoom and parent/branch highlights on all three branched
  examples. 2,256 bond endpoints checked; raster-measured ink-to-mask clearances
  1.30–3.18 px. Every visible bond segment remains >4.24 px; no label overlaps,
  clipping or JavaScript errors. Reapplying the helper alone does not accumulate.
- Raster checks use independently rasterized SVG text, not the application's
  TextMetrics as their oracle. Both the center and edges of each stroke are
  sampled within the gap; pixels match the opaque mask color, including green
  highlighted masks. All geometry is frozen before asynchronous image decoding
  to avoid stale detached SVG references after JSmol callbacks.
- Existing alkane lesson's only expanded step, step18, tested at both widths:
  124 endpoints PASS, gaps 1.33–2.50 px. Step/molecule/branch sequence unchanged.
- PNG blob >1000 bytes and parseable exported SVG smoke PASS. Main screenshots
  of 2,3-dimethylbutane and the larger branched alkane, plus lesson step18, saved.

Commands: `python3 docs/checks/check-alkane-clearance-v2-20261030.py`;
`test-alkane-clearance-v2-20261030.py`,
`test-alkane-clearance-v2-lesson-20261030.py`, and
`test-alkane-clearance-v2-fit-20261030.py`, each with `--output` under /tmp for
browser tests. Use the existing localhost8013 server and isolated BiDi9237 Firefox.
Baseline, exact diff, results and image evidence: `docs/checks/alkane-clearance-v2-*`.

## Limits and pre-existing behavior

390 px is responsive emulation, not a physical mobile device. No Safari/other
browser, full 3D runtime regression or React build is claimed. Scenario files
are unchanged; runtime coverage is the one existing expanded alkane step.

Full font-line boxes were rejected during development because they obscured
short C–H strokes at narrow widths; the final helper uses glyph ink instead.
The raster test sanitizes only its detached copy's pre-existing malformed
`black"` highlight attribute, already handled by the existing PNG exporter;
this does not alter live application content or broaden this fix.

A separate five-fit trace after highlight clearing/1.25 zoom reproduces an
existing viewBox oscillation, identically with old and new helpers. This is
outside the approved endpoint-clearance change and remains unresolved; no claim
of stable full-fit idempotence is made. The new helper's own idempotence passes.

## Review and save state

Independent fresh-context Reviewer `/root/review_alkane_clearance_v2`,
ROLE_ID NAMELECULE_REVIEWER_V1_20261023, reviewed the frozen18-path target
(manifest e5c49f7d9b200340a7f5c7c33351e2122455fdc670d4b67c8c9a31e55204c249).
It independently confirmed exact scope, 1861 protected hashes, JSC/4AST and
helper-gate/idempotence checks, read surrounding code and supplied screenshots.
It requested a bounded minimum-zoom check rather than another full review.

ACV2-R1 (P2): Developer's16 extra cases confirmed that the fixed1.5px floor
reduced some branched C–H strokes to0.45–0.72px at absolute zoom0.5. The
preceding helper left~2.05–2.30px. The correction makes only the small-font
pixel floor proportional; default-scale behavior and all other paths remain.
A targeted28-case run covers all8alkanes at minimum zoom, plus the3affected
at intermediate/default zoom, both widths. 1028endpoints PASS, no overlaps,
clipping or JS errors; reapplication is atomic/idempotent. Minimum retained
stroke1.48px (zoom0.5),4.21px (zoom1),4.24px (zoom2); minimum measured clear
raster gap0.78px at tiny zoom and>1.27px at the other tested zooms. No full422
rerun: source change is confined to the pixel-floor expression; existing
mode/category guards and mapping remain unchanged. The initial whole-library,
lesson and export results above are retained Developer evidence; final runtime
verification of the correction is the28 targeted cases.

Targeted independent verification by the same Reviewer CLOSED ACV2-R1 with
no residual actionable finding. Correction manifest SHA256
cba159553674b65057dc34f4647f6ec137449d9318330638be393e390ea6eb7c; final viewer
SHA256 ab8069a3618c510e1d6b0ff582e18c4003147d3692363af4edf6988f3f888217.
The Reviewer independently checked the exact small-zoom source correction,
all21 combined hashes, native JS syntax and both changed Python ASTs, and parsed
the28-case/1028-endpoint Developer evidence. No second full review was performed.
Only report/journal status changed after verification; application sources and
runtime evidence were rechecked against the reviewed hashes. Browser observations
above are Developer evidence, not independent runtime execution.
Chemistry/Learning Designer N/A: no molecular, chemical-rule, naming or learning
sequence change. No core file changed in this task or today's session. Local
files only; no commit, push or publication.
