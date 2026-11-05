# Engine-backed Workshop alkane pilot — 5 November 2026

Status: implementation, Developer verification and independent review complete.
Local work only. No commit, push or publication is authorized by this pilot.

## Approved behavior

The standalone Workshop has an opt-in `games/name-repair.html?source=engine`
entry. It retains two sets (unbranched/branched), three repairs per attempt and
the existing round UI. The original fixed sets remain the default. The lesson
checkpoint remains authored, with its original scenario and gating behavior.

Actual unmodified core54 analyzes each structure at runtime. A separate factory
uses its name/components, numbered parent, branches and root vocabulary to
introduce one eligible incorrect repair unit. The answer is derived from the
engine before the round starts; the shared game assessor compares the student's
repair to that generated solution. No molecule-specific correct-name/answer
table is loaded by the engine pilot.

Existing molecular structures are sampled, not newly invented. The pool is five
unbranched and three branched alkanes. Each set uses three distinct molecules;
repeated attempts may reuse structures or even coincide by chance. The generator
varies the fault, question order and choice order using a recorded seed.

`Βασικό` supplies a feature-level initial direction; `Πρόκληση` asks the student
to identify the relevant feature. Both use the same diagrams and eligible rules.
This is a guidance setting, not a validated adaptive difficulty model. There is
no claim of measured learning gains or comparable scores between random sets.

## Runtime boundary and recovery

- A fresh one-shot Worker imports the unchanged naming core for each analysis;
  it has no viewer, JSmol, lesson or Main-page state. All completion/error/timeout/
  cancellation paths terminate the Worker.
- The client measures the local core SHA-256 against the catalog's expected
  engine version. The exact measured bytes are retained as an immutable Blob;
  each Worker imports that snapshot, rather than rereading a potentially changed
  network file. Per-analysis Blob URLs are revoked on every completion path.
  HTTPS or localhost, Web Crypto/Workers and same-origin Blob imports are required.
- The structure-only catalog is reproducibly extracted from actual data54
  expanded MOL literals. Its source/engine hashes and revision accompany it.
  `python3 tools/build-alkane-game-catalog.py --check` detects source drift.
- Session storage keeps the recipe, difficulty, active question, legal answer
  state and attempts. Refresh recomputes the same engine-derived questions before
  restoring progress. Generator/catalog/core changes invalidate old receipts;
  malformed seeds and attempts to skip unsolved questions recover to the hub.
- If analysis cannot load, the UI offers retry and the original sets. It does
  not silently replace generated questions with authored ones while claiming
  an engine-backed result.

Fault eligibility is bounded: root alternatives keep every branch locant inside
the hypothetical parent and stay within the catalog's largest carbon count
(C10). C–C bond-type faults use only C2/C3, avoiding methane and extra missing
locants in larger unsaturated names. A symmetric reversal is not a fault.
Alphabetical order moves complete locant/group units and ignores multiplicative
prefixes. Multiplicity uses actual identical branches.

## Source changes and preserved baseline

Existing files changed: `js/namelecule-game-repair.js`,
`games/name-repair.html`, `css/namelecule-games.css`.

New runtime files: `js/namelecule-chemistry-worker.js`,
`js/namelecule-chemistry-client.js`, `js/namelecule-repair-generator.js`,
`games/data/alkane-structures.json`, and methane/propane SVG exports in
`games/assets/name-repair/`. New extractor: `tools/build-alkane-game-catalog.py`.
The two SVGs use the existing Main54 rendering/label/framing pipeline, not a
second renderer. Export provenance and screenshots are in `browser/`.

`baseline.json` records session HEAD168e3cec and exact pre-change hashes; `before/`
contains the three pre-existing edited files. The working tree was already dirty
and these application files were untracked at HEAD. Review compares this baseline,
not the entire repository history. The known verified public/recovery snapshot
remains the completed 4 November release; this local pilot is not published.

Core54 SHA256 remains
`3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306`;
core52 remains
`d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2`.
No core change was made in this session. Data54, stored MOL/SDF, Main54 HTML/viewer,
scenario JSONs, original game JSON/SVGs and React are outside the implementation.
The previously checked professor f49b810 changes remain unsynchronized; the last
actual sync is35d791ee. This pilot does not resolve that separate designer overlap.

## Verification actually performed

- Read-only feasibility: real core alone named all23available alkane forms without
  DOM/data54/JSmol in the naming scope; eight names independently checked.
- Adapter headless checks: eight catalog structures,23forms,eight permuted graphs,
  22malformed/unsupported inputs and62controlled client lifecycle checks. All nine
  simulated Workers terminated and ten Blob URLs were revoked. A network-change
  mismatch was reproduced before binding execution to the exact verified bytes;
  the corrected tests confirm later network changes cannot replace that snapshot.
  Three forbidden source-URL cases were also rejected. Exact final counts/hashes
  are in `adapter/adapter-report.json`; the before-fix reproduction is separate.
  These client doubles are distinct from the actual browser checks.
- Generator:512games,3072rounds,38644exhaustive legal repairs and6144state-restoration
  checks. Independent expected names, one correct repair, reproducibility,
  enumeration/input invariance, engine-output sensitivity, all five fault families
  and invalid inputs. `generator/results.json` records final hashes/counts.
- Chemistry Validator independently checked the actual23forms/eight SDF graphs,
  formula/parent/branches and exact catalog provenance. P2GEN-CHEM01 (unparseable
  shorter-parent distractors) was corrected and independently closed on generator
  hash11830448. Final targeted512games/3072rounds checked6992root values, withinC10.
- Developer actual Firefox: first full engine run passed71checks without JavaScript
  errors; actual Workers matched all eight independent names. Covered two complete
  sets, wrong/correct submissions, retry/cancel, refresh before/after success and
  results, keyboard focus, zoom,320–1500px layout and repository-prefix URLs.
  The final revised-code run passed72checks,0JavaScript errors, including actual
  verified-byte Blob imports, obsolete/corrupt progress recovery and prefix URLs.
  Additional final run passed21checks,0JavaScript errors: all five fault families,
  two new SVGs' actual decode/22px glyph/frame measurements, engine unavailability,
  retry and prevention of saved-progress jumps. Its deliberate unavailable-Worker
  test produced one expected console diagnostic, recorded separately from JS errors.
- Developer actual Firefox original fixed game:60checks passed,0JavaScript errors.
  Original embedded lesson pilot:45checks passed,0JavaScript errors, including
  viewer-state preservation, keyboard/history gating, mobile landscape and image
  failure/retry. These replay existing assertions with only endpoint/artifact
  location changed; prior evidence files were not overwritten.

Browser scripts and JSON evidence are in `browser/`. Reports distinguish intended
failure diagnostics from uncaught JavaScript errors. A passed local run is not a
guarantee of uninterrupted conference operation.

One intermediate test-harness run asserted the destination URL immediately after
clicking its link and failed before navigation completed. Explicit navigation
waiting and context activation corrected the harness; no application code changed
for that correction. The final72-check run then passed.

## Review and limitations

Consolidated independent Reviewer: `/root/review_engine_workshop_20261105`, fresh
context, read-only. No actionable P0/P1/P2/P3 findings. All52frozen paths matched
manifestc76ab022, including a final recheck. Reviewer independently reran the
reproducible catalog check, adapter tests and generator checks through in-memory
AST extraction, excluding their report-writing entry points. Counts matched the
Developer reports:23forms/eight permutations/22rejections/62clientchecks and
512games/3072rounds/38644repairchecks/6144restorechecks. All9simulatedWorkers
terminated and10BlobURLs were revoked. FourJSsyntax checks, source/baseline hashes
and new SVG atom/bond counts passed; supplied screenshots were inspected.

The actualFirefox72+21+60+45checks are Developer-supplied evidence, inspected but
not independently rerun by Reviewer. Chemistry specialist findings remain
separately attributed. `independent-review.json` records this handoff/result.
After review only records/status text changed; runtime source remained frozen.

Not tested here: Safari, physical mobile devices, assistive technology, published
HTTP deployment, the intended conference machine/sequence or an offline package.
The pilot itself uses local assets/core rather than remote chemistry/3D services;
existing Main lesson dependencies retain their earlier limitations. Other
homologous series, new graph generation and generated mandatory lesson checkpoints
remain later work requiring their own scope and verification.
