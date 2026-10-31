Read-only Main-source JSmol investigation, 2026-10-31.

Main source/data/core/React are not edited by these diagnostics. Runtime pages
and Firefox profile lived under /tmp/namelecule-jsmol-lifecycle-20261031.
Servers: 8027 standard; 8028 /slow/ adds 0.5 s to SDF/SPT responses only.
BiDi port 9237 belongs to that isolated profile; user port8013 was untouched.

Scripts are archived diagnostic source, with the original absolute /tmp paths.
Do not run them against the user's browser. A rerun needs an explicitly created
isolated server/profile, the repository symlink app and these helper scripts.
No dependencies were installed. Python3 stdlib + Firefox + JavaScriptCore only.

observe.js is the final observer: later runs added more function wrappers,
atom-count observation and loadStruct callbacks. Earlier datasets consequently
contain fewer event kinds. The raw captures remain unchanged; no claim of
bit-identical timings or a single observer revision across every run is made.
The initial malformed preload failure is saved separately and excluded from
application-error totals. getVersion inspection failure is disclosed in report.

reproduction: 4 focused flows; faithful-exit: 6 with library Exit; slow-load:
3 delayed flows; slow-settle: 6 separate delayed follow-ups, 24 later samples.
controlled-teardown: 8 deliberately induced cases, not natural failure counts.
active-flows: 3 four-molecule sequences, actual hide/show, viewport resize.
Raw exceptions carry BiDi realm/context; LIFE logs carry epoch, URL, wall and
performance timestamps and applet state. Controlled cancellation does not
implement a reusable production fix.

summarize.py build() reads/recomputes evidence without writes. Direct execution
writes summary.json. External-source provenance records URLs/headers/hashes;
source-excerpts.json preserves relevant snippets. Native function string matches
are limited to those stated in the report; they do not pin every loaded j2s file.

The source snapshot, review scope and final verification are recorded separately.
Browser execution and screenshot are Developer evidence. No universal reliability
or conference-readiness claim follows from this investigation.
