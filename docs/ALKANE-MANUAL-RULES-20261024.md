# Alkane rule tables open by request — 2026-10-24

User-approved follow-up supersedes automatic opening in ALKANE-AUTO-RULES-20261024.md.
In the existing alkane theory presentation the corresponding rule title remains
visible on component/alkyl selection, but the table starts collapsed on step entry
and component changes, even when the previously viewed table was open. The user
opens/closes it by clicking its title. Other lessons preserve previous behavior.
Exact-title/presentation scope and existing rule text/table/highlight rows retained.
No lesson JSON, Desktop JSON, chemistry, molecule or core edits.

Production changes: existing helper renamed fScenarioShowComponentRule in
scenario/viewer/teaching50; viewer forces pilot table collapsed on rendering;
existing visibility-based title toggle retained; three HTML cache queries updated.
Before snapshots /tmp/alkane-manual-rules-before, base2de69f4.
Four production hashes /tmp/alkane-manual-freeze.json.
Independent Reviewer /root/review_alkane_manual_rules freshcontext inspected all
four diffs and hashes with AGENTS/checklist, no actionable P0–P3 findings. No
independent browser execution. Browser results are Developer evidence.
No commit/push/publication.

Developer actualFirefox21step replay verified selected tables initially collapsed
with corresponding titles/selected rows. Five component types each remained
collapsed on selection and opened via title. Manual closing plus transition from
an opened table to next step collapsed correctly. Four other lessons and free
exploration isolation passed. Evidence checks/alkane-manual-rules-20261024.json;
script checks/test-alkane-manual-rules-20261024.py. No classroom efficacy or
new molecular validation claimed; unchanged chemistry assets.

Run recorded three external JSmol viewer=null errors during multi-page navigation;
functional assertions passed. Same external error family was reproduced on pre-pilot
baseline in prior task (ALKANE-AUTO-RULES-20261024.md). No error-free run claimed.
