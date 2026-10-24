# Theory progressive disclosure — 2026-10-24

Approved Phase B follows the Learning Designer Phase A assessment. The user
explicitly deferred quizzes. These lessons explain naming through observation,
progressive name-component reveal and worked examples, without learner scoring,
prediction or answer prompts. Existing schema, molecules and app engines retained.

| Lesson | Before | After | Old-step changes |
|---|---:|---:|---|
| Alkanes |22|21|Merge11+12 and19+20; split22|
| Alkenes |22|22|Merge13+14; split22|
| Alkynes |22|22|Merge13+14; split22|
| Alkadienes |22|23|Split6; merge19+20; split22|
| Enynes |22|23|Split6; merge19+20; split22|

All final steps separate guided2D naming synthesis from optional3D observation.
Alkane first-difference comparison is explained at the actual2,3,5 vs2,4,5 example;
2,3 either direction is described as equivalent. Alkene main-chain3 versus total4
wording corrected. Diene comparison is staged, pentadiene1,4 moves to synthesis,
two meanings of di remain distinct, and isomerism wording is removed. Enynes
teach all-multiple-bond locants before double-bond tie priority, separately from
en-before-yne writing order. First introductions of di in alkenes/alkynes remain
separate. Merged steps use one initial highlight, with other components clickable.

Changed deliverables: five canonical scenario JSONs, library counts/cache query,
README current summary; matching five existing Desktop JSON deliveries. Added
focused browser check and this record. Session/contribution records updated.
No molecules, scenario engine, core or viewer changed against session baseline.
Pre-existing working-tree changes are preserved and not attributed to this task.
Baseline snapshots and full file hashes are under
`/tmp/namelecule-theory-before-20261024`; base commit
`2de69f439dc3b709fc4658624ad98ee8d6ffe47e`.

Upstream read-only check: initial sandbox DNS failure, successful authorized
retry. HEAD remains `2b616f6cdc5b3c2d65b20d38b2e025e0d58ccfbb`, same as last
synchronized revision. Current complete CHANGELOG SHA256
`46de588394cf019759b0404838fa2f6505fa2ca4f27a8d150de78c087fdeb705`
unchanged from previous check; no new release to synchronize.

## Verification and review

Developer Firefox with actual JSME/JSmol traversed all111 final lesson steps.
First run completed the first four lessons (88steps) with DOM note, selected
molecule, representation, hidden fields, analysis mode, rule state and height
checks, plus validator/export/reimport without warnings. It then detected the
new unbranched enyne tie step used compBondPos, whose comp4 does not represent
its double locant. Corrected to compNumber1/comp0 and reran all23 enyne steps
successfully, validator/export/reimport passed and no JavaScript errors logged.
Enyne machine-readable results are in checks/theory-progressive-enynes-20261024.json.
Initial test-only uniform420height assumption was corrected to each stored
height; initial BiDi session exhaustion was avoided with an isolated temporary
Firefox profile on9231. No app engine modifications were needed.

Developer visually inspected final2D alkene/diene/enyne and3D alkane/diene/enyne
screenshots in /tmp. These are sampled visual checks, not an atom-by-atom check
of all highlights or a classroom trial. Static checks confirm sequential counts,
preexisting molecule references only and3D disabled before every optional finale.

Real independent Reviewer /root/review_theory_progressive, role
NAMELECULE_REVIEWER_V1_20261023, fresh context, read AGENTS/checklist, compared
seven targets with exact session snapshots and frozen hashes. No actionable
P0–P3 findings. A preexisting diene self-explanation prompt was replaced with
explanatory prose and re-reviewed. Enyne comp0 correction independently traced
through core/teaching/replay and re-reviewed with no findings. Reviewed test source
but did not execute browser checks. Runtime evidence belongs to Developer.
Reviewer confirmed Desktop identity and engine immutability. Freeze in
/tmp/theory-review-freeze.json. Record files are added after application freeze.
No classroom effectiveness claim is made; pilot teaching remains necessary.
No commit, push or publication authorized or performed.

Final browser navigation passed five library counts, actual enyne tie-locant
click explanations and Exit return to library. Desktop five deliveries byte-identical.

Firefox process log also emitted internal chrome://remote WebDriver WeakMap and
headless compositor warnings. These are distinct from the empty application-context
JavaScript error event log in the corrected enyne evidence. No browser-internals
error-free claim is made. The isolated test browser was closed after checks.
Ancillary records/tests/evidence independently reviewed with no actionable findings.
