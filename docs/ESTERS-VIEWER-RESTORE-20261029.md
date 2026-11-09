# Restore shared ester rendering — 2026-10-29

## Approved request and changes

The user approved removing the added ester-specific automatic orientation for
all nine esters, using the previous common renderer, then checking all three
forms. New MOL edits were explicitly deferred until after observing the result.

Removed `esterOrientationApplied`, `fEsterAcidLeftMol`, `fApplyEsterOrientation`
and its call inside `fUpdateSVG` in `js/mulermoc-nom-molview-52.js`. The existing
`fApplySkeletalLayout` pipeline remains as in the pre-ester snapshot. Retained
acid-parent naming/highlight helpers and count explanations; these are separate
from depiction. Updated the viewer cache key in `mulermoc-nom-52.html`.

No MOL, SDF, provenance, embedded data, core, JSME setting/vendor or SVG spacing
logic changed in this restoration. This does not undo the previously approved
core naming extension. The naming harness no longer calls the removed display
helpers; its chemical/naming/parent-map/legacy-frame checks remain active.

## Actual Developer checks

- All monitored molecular files, core and embedded data hashes unchanged.
  No occurrences of the three removed display identifiers remain in the viewer.
- Actual JavaScriptCore:110new naming/chain/permutation,814old regression,
  16guard cases pass after removing obsolete rotation-only test assertions.
- Actual isolated Firefox compares the task-start four-file snapshot against
  the restored app at1500/390px and zoom1/2. Four old esters ×3forms ×2widths
  ×2zooms =48comparisons have byte-identical SVG and identical names.
- All9esters ×3forms ×2widths ×2zooms =108restored render captures; together
  with48baseline captures,156cases, no recorded JavaScript errors. Labels were
  checked for viewport clipping; this is not a bond-to-label correctness test.
- Programmatic DOM activation;390px is desktop layout emulation. Browser output
  is Developer evidence. No physical-mobile, export or all-zoom verification.

The baseline serves captured pre-ester data/core/viewer/HTML with unchanged
supporting dependencies. It is the immediate task-start snapshot, not a claim
about every older release or the professor's current upstream appearance.
Evidence under `docs/checks/esters-viewer-restore-*20261029*` includes browser,
naming, preservation, source diff and compressed before-source snapshot.

## Remaining issues: do not declare the original visual complaint fixed

For methyl methanoate condensed, removing the hook produces the same image as
the immediate pre-ester snapshot. It does not establish the cause of the user's
screenshot; the exact screenshot molecule/environment has not been confirmed.
The rendered drawing includes a visible formyl H and a CH label, which warrants
separate hydrogen-label investigation. No extra chemical source H was added.

At default desktop view the restored skeletal renderer places the acid fragment
on the right for three of four old esters and four of five new esters; methyl
methanoate/tert-butyl methanoate are exceptions. Condensed/expanded acid-left
holds for all nine. Earlier orientation-specific browser assertions therefore
no longer describe this restored target and have not been relabeled as passing.
The approved removal is implemented; the earlier acid-left requirement and the
user's original visual complaint remain unresolved. A new concrete plan and
approval are required before further code/MOL changes. In particular, do not
assume changing source orientation alone overrides the common skeletal pipeline.

## Independent review

Completed by `/root/ester_restore_review`, fresh context,
ROLE_ID=NAMELECULE_REVIEWER_V1_20261023. No actionable P0/P1/P2/P3 findings
within the approved removal scope. All12frozen hashes and the exact scoped diff
were independently verified. Reviewer re-executed110new/814old/16guard naming
cases with output in memory and confirmed current core/data hashes. Browser
156records/48SVGcomparisons and preservation of515molecular files were supplied
Developer evidence, not independently rerun. The Reviewer explicitly confirmed
that baseline equality does not resolve the original visual complaint;7of9
skeletal acid-right cases and possible formyl-H/CH issue remain open. No files
were created/edited/staged by Reviewer. Only this report's review-status text
was subsequently updated; implementation hashes remain unchanged.

## Core/save state

No core file changed during restoration; core52 SHA256 remains
`d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2`.
Earlier five-ester naming changes remain local. No commit, push or publication.
