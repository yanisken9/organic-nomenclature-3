# Two-part alkane lesson — 5 November 2026

Local implementation of the approved twelve-step lesson. The two theory parts
end in generated Workshop sets with three repairs each. A set unlocks its next
part only after all three repairs have been submitted correctly. Repeated
attempts and return to theory remain available. The final step exposes all eight
existing alkanes, their 23 available 2D forms and eight existing 3D models.
Methane has no skeletal form.

The new JSON replaces the current library link; the original 21-step JSON and
single-question authored pilot remain available. The library still has fourteen
active lessons, now 328 steps. Generation uses the previously reviewed structure
catalog, chemistry client, Worker, generator and actual unchanged core54. Saved
seeds/answers are reconstructed and rechecked before accepting completion.
Difficulty in this lesson is Basic; question families are sampled, not guaranteed
to cover every rule in each three-round set. Completion is formative practice.

## Scope and recovery

Eight initial runtime paths are listed in `runtime-review-target.json`. The final
two-file R1 correction is pinned in `targeted-review-target.json`; the combined
final hashes are in `final-verification.json`.
The six pre-existing files have copies under `before/`; `baseline.json` records
the pre-task HEAD/index and nine protected source hashes. Earlier dirty working
files are outside this contribution. Source HEAD is
`168e3cec01f941a84d40bbe0dc07156e7baa35d0`.

No core/core-version, molecular data/MOL/SDF, generator, chemistry client/Worker,
v52 or React file changed. Nothing was staged, committed, pushed or published
for this unit. The previous verified November 4 recovery/publication point is
retained. Current professor upstream was checked earlier in this session through
`f49b810c`; actual synchronization remains `35d791ee`, with the separate drawing
pipeline overlap unresolved.

## Verification completed

- Chemistry Validator `/root/validate_compact_alkane_lesson` independently checked
  23 2D graphs, eight SDF graphs, 35 actual core analyses and 23 complete atom maps.
  Text, selected parents, numbering, highlights, formulas and all eight IDs agree.
- `adapter/test-generated-checkpoint.py` passed 51 assertions with eight actual
  core analyses. Transport, DOM and WebCrypto were simulated in that harness.
- `check-scenario-content.py` passed sequence/configuration/source-preservation
  checks. Original scenarios and both core hashes remain identical.
- Actual clean Firefox, 1500×1000 and 844×390, completed 128 functional checks in
  `browser/two-part-browser.json`: full twelve-step/six-repair replay, wrong and
  unsubmitted answers, exact active-answer restoration, both gates, blocked
  jumps, real chemistry-Worker failure/retry, all 23 2D forms and eight matching
  3D source paths, name clicks, zoom and resize.
- Recovery: 19 checks, zero JavaScript errors. Cancellation, content/card changes,
  catalog rejection, image failure/reload, zoom/Escape, malformed stored progress,
  unknown required type and unavailable storage were exercised.
- Compatibility: 60 checks, zero JavaScript errors. Export/import, page lifecycle,
  actual history return, and first/final/Prev/Next paths in all thirteen other
  lessons. This was not a new full replay of all 316 unaffected authored steps.
- Existing authored checkpoint: 45 actual Firefox checks, zero JavaScript errors.
  Original standalone two-set Workshop: 60 checks, zero JavaScript errors.
- Final R1 correction: 11 targeted Firefox checks, zero JavaScript/console errors.
  Cold preparation/error/retry retains the loading boundary with usable controls;
  actual Worker verification reveals the requested snapshot; warm viewer state
  and both cold Exit paths work. These narrowly verify the changed loading paths,
  rather than constituting a second full twelve-step replay.

Browser results are Developer evidence. They are distinct from the specialist's
independent chemical checks and the independent final Reviewer assessment.

## Observations and limits

The 128-check run also logged one uncaught native JSmol exception,
`bufferedImage / platform is null`, during asynchronous restoration of the first
completed gate. The subsequent flow and all models rendered, but this does not
establish the cause or prove future reliability. It is not classified as
pre-existing or fixed. The initial observed run is preserved separately. A bounded
normal-versus-deferred-loader diagnostic had one normal restoration with no
exception; the deferred variant failed its test wait, so it does not establish a
causal comparison (`browser/restoration-trace.json`).

The initial test profile 9245 showed hidden legacy controls even using exact
pre-task source copies. A new clean profile 9246 displayed and exercised those
controls normally. No app change was made for that environmental observation;
the old profile's precise cause was not established.

JSmol j2s resources and fonts currently include external-service dependencies.
No Safari, real touch device, assistive-technology certification, public release,
offline package or conference-machine/demonstration-sequence validation is claimed.

## Independent review

Fresh read-only Reviewer `/root/review_two_part_alkane_lesson` inspected the
frozen eight-file target, dependencies, source copies and supplied evidence.
R1 (P2) identified early release of the cold loading screen. It was corrected
in player54/CSS and **closed** after independent targeted hash/diff/syntax checks,
seven in-memory behavioral checks, and inspection of Developer's eleven actual
Firefox checks and screenshots. The Reviewer wrote no files. There are no open
P0/P1 findings; the native JSmol observation above remains approximately P2.
Details and exact target references are in `independent-review.json`.

No permanent JSmol cure or conference readiness is claimed. All code remains
local. No core/core-version file changed during this session.
