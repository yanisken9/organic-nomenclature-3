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
  Reviewer is inspecting it. Any later target changes require review again.
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
- Report actionable findings with severity, exact file/line, violated
  requirement, observed behavior, impact, and reproduction/evidence. Separate
  existing issues from regressions introduced by the change. Do not invent
  findings to fill a quota or treat style preferences as functional defects.
- The Developer addresses findings and returns changed content for independent
  re-review. Unresolved blocking/high-severity findings prevent declaring the
  change ready to publish; disclose any other residual findings and limitations.
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
