# Conference presentation priority — April 2027

- User instruction (2026-10-31), applicable to every agent: Namelecule is intended
  for presentation at the ENEPHET conference, 23–25 April 2027 in Volos.
  Official reference: https://synedrio2027.enephet.gr/ . Treat reliable presentation
  flow as a continuing acceptance criterion for relevant changes.
- Prefer bounded, reversible changes with a recorded baseline. Verify affected
  user interactions and scenario replay, not only isolated output or syntax.
  For viewer changes, include relevant molecule/mode switches, zoom, resize,
  numbering/highlights and presentation navigation; scale checks to actual impact.
- Preserve chemical and educational correctness and the independent review
  protocol. Disclose failures, untested areas and external-service dependencies;
  do not equate a passing smoke check with a guarantee of uninterrupted operation.
- Keep a known verified recovery point. Before a conference release, validate the
  agreed demonstration sequence on the intended machine/browser, including cold
  startup and recovery. A stable release and an Internet-independent fallback
  require their own preparation and verification; do not claim either exists
  without evidence. This priority does not authorize unrelated refactors,
  automatic publication, or activating all agent roles for each task.

# Root-cause solutions and prevention of recurrence

- User instruction (2026-10-31), applicable to every agent: prefer durable fixes
  at the demonstrated cause of a problem. Do not present symptom suppression,
  cosmetic compensation or a passing narrow test as proof of a root-cause fix.
- Before proposing implementation, reproduce the failure and trace the relevant
  data, settings and processing stages to identify where expected and actual
  behavior first diverge. Separate measured facts, hypotheses and unknowns.
  A repository revision or local copy does not establish what another person
  saw in a different live deployment, browser or configuration.
- Fix the causal component using a supported setting or a shared mechanism
  where appropriate. Do not accumulate molecule-specific exceptions to hide an
  unexplained failure. If only a temporary mitigation is justified, explain its
  limits and obtain approval for that scope; do not silently call it permanent.
- Verification should reproduce the original failure before the change, confirm
  its resolution afterward, and cover relevant variations and affected flows.
  Preserve scientific correctness and add meaningful regression protection
  against recurrence, proportionate to the actual change and existing tests.
- State the verified operating conditions and remaining uncertainties. Reliability
  is established with evidence and independent review, not an unconditional
  promise that a solution will always work. Existing workarounds may need later
  reassessment; this instruction does not authorize automatic removal, broad
  rewrites or changes outside an approved plan. Keep the cost protocol in force.

# Session continuity

- At session start, read `README.md`, the current session notes, and relevant
  project/development plans. Inspect code structure and the code relevant to
  the task to understand the project's direction and evolution. Broaden the
  review when needed; do not claim to have read the entire project unless done.
- At the start of each session, read the current resume point at the top of
  `docs/SESSION-NOTES.md` and inspect `git status` and relevant diffs before
  asking the user to reconstruct previous work.
- Keep a dated current resume point at the top of `docs/SESSION-NOTES.md`.
  Update it after material changes or decisions and before the final response
  of a work session. Preserve older notes below it.
- Record the user's objective and decisions, changed files, verification
  actually performed, remaining work, and a concrete next step. Distinguish
  confirmed facts from assumptions; never invent unavailable conversation history.
- If interrupted, record the latest known state as soon as possible. These
  files preserve project context, not the complete chat transcript.
- Saving notes or source files does not mean creating a commit. Do not claim
  a commit or verification that has not happened.

# Plan before implementation

- User-approved workflow: before each code intervention, perform read-only
  investigation and present a concrete plan describing the intended behavior,
  affected files, and appropriate verification. Wait for the user's approval
  before editing code. This applies to fixes and refactors as well as features.
- Use Plan mode when available. If the current interface does not allow the
  assistant to switch modes, follow the same planning/approval sequence in chat
  and accurately state the mode; do not pretend a mode switch occurred.
- Approval of a plan authorizes its implementation and necessary checks. Ask
  again only for a material change of scope. Reading files and keeping project
  notes current do not require a separate code-change approval.

# Contribution record

- Maintain `docs/YANNIS-CONTRIBUTIONS.md` for Yannis's work with the assistant.
  Record the purpose, changed files, behavior, verification, pending work and
  actual commit references when available, so the collaborating professor can
  review and merge the work.
- Update it after material contributions and before ending a work session.
  Distinguish pre-existing changes from contributions made in the session.
  Attribute earlier work only when evidence supports it; do not invent history.

# End-of-session core change report

- User request (2026-10-21): at the end of EVERY work session, explicitly
  report whether any core.js/core-version file changed during that session.
- If changed, provide a short Greek message ready for the user to forward to
  the professor: exact core filename/version, concrete behavior changed, reason,
  checks actually performed and whether local/committed/published.
- If unchanged, explicitly state that no core changes were made that session.
- Compare against the session-start baseline, not only the latest task or
  uncommitted diff; distinguish upstream sync from locally authored changes.
- Preserve this record in session/contribution notes. Do not send messages to
  the professor; the user forwards the supplied text.

# Start-of-session professor changelog review

- User request (2026-10-22): begin EVERY work session by checking the current
  professor upstream docs/CHANGELOG.md against the last synchronized upstream
  revision recorded in session notes. Check current upstream HEAD/history too,
  since a changelog may omit code changes. Do this before new implementation.
- Report new entries/commits and overlaps with local customizations in Greek.
  Distinguish the last checked revision from the last actually synchronized one.
- Read-only comparison is authorized. Standing user authorization (2026-10-22):
  routinely synchronize with each professor release after review, preserving
  Namelecule customizations and validating the result. Present the intended
  changes before implementation; do not ask again for routine sync approval.
  Ask for approval for material new scope or unresolved conflicting behavior.
  Publishing/committing still requires the user's save/publish instruction.
- Record date, compared revisions, findings and any access failure in session
  notes. Do not claim the changelog was checked if the remote read failed.

# Developer and independent Reviewer

- User-approved workflow (2026-10-23): use two distinct roles for Namelecule.
  The primary agent acts as Developer; delegate independent review to a real
  Reviewer subagent. These roles supplement all existing instructions above.
- The Developer investigates, presents the plan, implements the approved scope,
  runs appropriate checks, resolves findings, and maintains project records.
  Plan approval covers necessary review and corrections within the approved
  scope; request new approval only for material scope changes. Commit/push and
  publication still require the user's authorization.
- Before handing off, stop editing the review target. Give the Reviewer the
  approved request, acceptance criteria, repository path, base commit, exact
  changed/untracked file list, and revision or content hashes being reviewed.
  Review the final working-tree content, including untracked deliverables;
  review does not require creating a commit. Do not edit that target while the
  Reviewer is inspecting it. Any later target changes require targeted verification under the protocol below.
- Start the Reviewer in a separate context without inheriting the Developer's
  conversation (use `fork_turns: "none"` when supported). Supply requirements
  and source references, not a prewritten verdict. The Reviewer reads this
  file and `docs/REVIEW-CHECKLIST.md`, then forms its own assessment from the
  actual diff, surrounding code/data and independently gathered evidence.
- The Reviewer must not edit, create, delete or stage files, update notes,
  commit, push, publish, install dependencies, or launch additional agents.
  It may run genuinely read-only inspections/checks and returns its report to
  the Developer. Checks that generate files, caches or browser artifacts must
  be left to the Developer or a separately authorized isolated environment;
  label supplied results as Developer evidence, not independent execution.
- Use the checklist proportionally. Documentation-only changes need no app
  runtime tests unless they alter a functional contract requiring validation.
  Chemistry or viewer changes need relevant molecular and browser checks.
  Always distinguish completed checks, supplied evidence, and untested areas.
- Report actionable findings with P0/P1/P2/P3 severity, exact file/line, violated
  requirement, observed behavior, impact, and reproduction/evidence. Separate
  existing issues from regressions introduced by the change. Do not invent
  findings to fill a quota or treat style preferences as functional defects.
- The Developer addresses findings and provides the changed content for targeted
  final verification under the protocol below. Unresolved P0/P1 findings prevent
  declaring the work complete or ready to publish; disclose other residual findings
  and limitations.
  User authorization for publication remains required even after a clean review.
- The Developer records the review target, Reviewer identity, findings,
  resolutions, checks and limitations in project notes or a review report.
  The Reviewer reports instead of writing these records itself. Respect an
  explicit user instruction forbidding even documentation writes.
- Separate context provides an independent assessment, not filesystem isolation
  or a guarantee of correctness. Subagents share this workspace and inherit
  parent permissions; the no-write rule is behavioral. If enforced read-only
  access is required, use a separately configured read-only session. If actual
  subagents are unavailable, disclose that fact and propose a separate review
  session; never describe Developer self-review as independent review.

# Namelecule Codex Cost Optimization Protocol v1.0

Adopted 2026-10-28. This protocol refines activation and review scope; it preserves
all five roles, approval boundaries, permissions and scientific requirements.
Where older workflow text implies a full review after every correction, use the
bounded review cycle below.

- Developer is the primary implementation role; the main agent may perform it
  without spawning a duplicate Developer. Never activate all roles by default.
- Activate Chemistry Validator when chemical rules, molecular structures or
  nomenclature are affected. Activate Learning Designer when educational scenarios
  or learning sequences are affected. Activate Planner only for complex
  architecture or design changes; ordinary planning stays with the Developer.
- Use Developer → one consolidated independent Reviewer after a logical unit is
  complete → Developer corrections → targeted final verification. The Reviewer
  starts in fresh context and inspects the relevant diff, new deliverables and
  directly affected dependencies. Expand only for concrete risks or evidence.
- Report actionable findings as P0 critical, P1 high, P2 medium or P3 low, with
  file/line, requirement, impact and reproducible evidence. Track resolution by
  finding ID; do not repeat resolved findings unless new evidence reopens them.
- Freeze each review target and identify the base, exact paths and hashes. After
  corrections, identify the new hashes and verify changed paths and their effects.
  P0/P1 fixes require independent targeted verification before work is complete;
  Developer verification alone is insufficient. For P2/P3, Developer checks may
  close isolated fixes; retain independent targeted re-review when correctness or
  chemical/pedagogical uncertainty requires it. Never describe self-checks as
  independent review. Disclose remaining findings and untested areas.
- A second full review is warranted only for substantial new changes or serious
  unresolved risks. Any target change needs verification, not automatic repetition
  of the entire checklist. No endless review/correction loops: record a persistent
  blocker and its next diagnostic step instead of repeating unchanged checks.
- Read only necessary files/sections and reuse verified context within the session;
  reread when content changes or uncertainty requires it. Keep handoffs and reports
  concise, with source paths and evidence instead of duplicated history. Keep the
  current resume point short and preserve historical records below it.
- Prefer bounded tasks and existing suitable tests. Repeat or broaden checks only
  for new changes, failures, affected dependencies or unresolved risks. Pure
  documentation changes need no application tests unless a functional contract
  changes. Agent loading tests are not routine checks for every instruction edit.
- Cost savings must not weaken chemical correctness, naming reliability,
  pedagogical quality, independent review of critical changes or documentation
  of significant decisions. General core changes still need broad relevant
  regression coverage. Record limitations and uncertainty; no savings percentage
  may be claimed without measurements. Do not change models/settings or introduce
  test quotas as an implied part of this protocol.
- For adoption of v1.0 only, the user explicitly waived all subagents, including
  Reviewer. Validate this documentation locally; this is not a standing exemption
  from independent review of subsequent work.

# Permanent skeletal geometry and framing rule

- Apply one reusable display pipeline to every available library skeletal form,
  including future imports and lesson/embedded viewers: chemical geometry first,
  horizontal parent development second, readability and complete-label framing.
- Resolve the numbered parent from nomenclature before changing display geometry.
  Prefer C1 towards the left and progression to the right, minimizing needless
  vertical spread. Try a proper whole-molecule rotation before local corrections;
  never flatten a zigzag, mirror a molecule or distort valid bond angles/lengths.
- Triple-bond sp centers must be linear. Where rotation cannot repair a bent
  degree-two sp carbon, rotate a complete separable side about that center;
  preserve topology, bond lengths and other local angles. Do not break rings or
  force unsafe geometry. Keep branch/functional-group labels readable.
- Keep saved records, embedded/source MOLs, atom IDs and 3D files unchanged for a
  display-only task. Rebuild transient geometry from original input, preventing
  cumulative rotations on molecule/chain changes, highlights, zoom or resize.
- After geometry and label generation, fit the bounding box of the entire visible
  molecular drawing, including labels, to the actual 2D viewport with margins.
  Center the whole structure, not C1 or the parent alone. Verify desktop/mobile,
  resize and molecule switches. Other representation modes and naming are invariant.
- Validate all available skeletal forms plus representative straight, branched,
  multifunctional and triple-bond cases. Report missing forms and unsafe skipped
  repairs explicitly; a central hook alone is not evidence of universal success.
