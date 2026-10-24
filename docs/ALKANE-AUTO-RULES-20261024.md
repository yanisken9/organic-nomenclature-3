# Alkane rule-table pilot — 2026-10-24

User approved automatically opening the existing corresponding rule table when
an alkyl group or one of the three principal name components is highlighted,
automatically or by click, initially only in the existing alkane theory lesson.

Implementation is gated by presentation mode and exact existing lesson title
«Αλκάνια-Ονοματολογία και διακλαδώσεις». Three principal components and both
alkyl groups/positions use existing rule text, tables and selected-row logic.
The local open override does not mutate ruleFlag. Scenario replay preserves the
pilot table visibility even when the stored show.rule is false. A scoped title
handler derives its state from actual visibility so manual closing stays coherent.
No new schema, molecules, rules or lesson steps; imported identical lesson title
receives the same pilot, renamed copies do not. Desktop JSONs need no update.

Changed production files: molview-50.js, scenario-50.js, teaching-50.js and their
cache queries in mulermoc-nom-50.html. No core changes. All other changes in
this dirty workspace predate this task. Baseline snapshots/full hashes at
/tmp/namelecule-alkane-rules-before-20261024, base2de69f439dc3b709fc4658624ad98ee8d6ffe47e.

Independent actual Reviewer /root/review_alkane_auto_rules, fresh context,
read AGENTS/checklist, inspected frozen diff and reported P3 manual toggle
state inconsistency. Developer corrected scoped teaching handler; independent
re-review of all four frozen targets resolved P3, no further actionablefindings.
Reviewer did not run browser tests. Freeze /tmp/alkane-rules-freeze.json.

Developer browser assertions traversed21steps, verified all automatically
selected rule tables/rows visible, clicked all five component types, checked
manual collapse and four other lessons plus free-exploration isolation. Screenshot
/tmp/alkane-auto-rule.png visually inspected. External JSmol viewer=null errors
were observed during multi-document navigation; recorded separately, without
claiming the complete browser run is console-error-free. No app engine fix for
these errors included. Node unavailable, so no node --check claim; actual
Firefox executes changed scripts. No commit/push/publication.

Final repeated focused browser run passed all functional assertions and recorded
zero JavaScript errors. Evidence checks/alkane-auto-rules-20261024.json (21step
states, fiveclickedcomponenttypes, fourotherlessons/freeexploration). Earlier
transient external errors are not erased or claimed fixed.

A read-only temporary HTTPserver served exact pre-task versions of the four
changed production files with all other assets unchanged. The baseline navigation
comparison reproduced30 external JSmol viewer=null errors (same setDisplay/updateJS
classes), evidence checks/alkane-rules-baseline-jsmol-errors-20261024.json. Thus
the external failure is reproducible without this patch; finalpatch run was clean.
