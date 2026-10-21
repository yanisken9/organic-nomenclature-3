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
