# Welcome/game and preserved React — Developer browser evidence

2026-11-04. Root delegated evidence-only browser checks. Only files in this
directory were written. No app/core/React source edits, build, installation,
commit, publication or additional agent activation.

The local user server was `http://127.0.0.1:8013/`. Tests used an independently
started headless Firefox with port `9246` and profile
`namelecule-v54-nav-20261104-ceya7owx`. This is a separate browser profile,
not an assertion of filesystem isolation. These are Developer checks, not
independent Reviewer execution.

## Actual commands and results

```text
python3 docs/checks/v54-sync-20261104/navigation/test-navigation.py
python3 docs/checks/v54-sync-20261104/navigation/test-react-preserved.py
```

Both final commands exited 0. They use the existing Python-stdlib Firefox BiDi
helper and actual input actions, served application documents and loaded models.
Local socket/browser permissions required the authorized tool escalation; there
was no automatic-approval rejection.

`navigation-browser.json`: **94 checks, zero application JavaScript errors and
zero page warning/error diagnostics**. At widths 1500 and 390:

- The welcome game card is a direct game anchor and opens the game page.
- Keyboard Enter at 1500 and simulated touch at 390 complete all five rounds.
  Both show exactly `[4, 4]`: four scored challenges and four submitted repairs,
  with the guided example excluded. Success explanations agree with game data.
- Intro and mission logos decode the accepted 3D PNG; no page overflow in the
  measured welcome/intro/round/results views.
- Existing theory-library route, teacher/login dialogs, link visibility and
  close controls work. This check did not assert Main54 theory activation.
- Results, mission Exit and brand return to welcome; browser Back returns to
  the game document and Forward returns to welcome.

`react-browser.json`: **17 checks, zero application JavaScript errors and zero
page warning/error diagnostics**. The preserved React build exposes 126 catalog
molecules and 12 lessons. Actual ethanol 2D SVG and nine-atom JSmol model load;
expanded mode works; selecting `comp5` selects its real iframe component and two
JSmol atoms. Actual 3D controls/view display, then methane loads with 2D SVG and
five atoms. The loaded iframe scripts retain the two
`preserved-main-20261030` data52/viewer52 URLs and original core52, with no core54
reference. The monoalcohol lesson renders actual 2D SVG; pointer Next reaches
step2, Previous returns step1, and Exit returns the library. No React rebuild.

Inspected screenshots include mobile game intro, desktop results, React 3D
component selection and lesson step1; screenshots are not substitutes for the
interaction/model checks above.

## Failures and limits retained

- The first navigation attempt used a nonexistent capitalized theory substring;
  corrected the test to the actual library heading/link contract and reran all
  94 checks. The first React attempt had a quoted-selector SyntaxError in the
  test expression; corrected only that expression.
- A subsequent React attempt passed 15 checks, including actual models and
  lesson Next, but rapid keyboard Enter on Previous stayed at step2 for 90s.
  The screenshot showed a healthy step2, and there were no app JavaScript
  errors. The complete later pointer replay passed. The cause of that keyboard
  attempt was not established; it remains an activation/focus/automation
  uncertainty, not a proven new regression or a claimed fix.
  `react-keyboard-previous-attempt.json` and its labelled PNG retain the evidence.
- The React network capture recorded one `favicon.ico` HTTP404. No failed
  molecular/CDN dependency response was observed. JSmol uses its existing
  external CDN configuration; this run does not establish offline operation.
- `firefox.log` contains Firefox RemoteAgent internal WeakMap warnings from
  iframe/network instrumentation. They are browser-protocol diagnostics, not
  application JavaScript errors, and are disclosed rather than silently removed.
- Touch is simulated pointer input, not physical hardware. Safari, assistive
  technology, all React lessons, arbitrary navigation timing and a conference
  demonstration sequence were not comprehensively tested.

## Hashes and process cleanup

`baseline.json` and `end-hashes.json` cover 47 relevant target files, including
React sources/build, game files, welcome/theory documents and core52/core54.
**No target hash changed during this evidence-only subtask.** The previously
implemented core54 stays frozen at
`10f3e1ed4ea566be50c4797d523d6cfe83e86a41cab761b0c18281f9113a061f`.
No additional core edits were made here; root reports the earlier migration in
the complete session core report.

The first detached browser launch ended before tests connected; the subsequent
launcher stayed alive for the owned browser. Final browser PID was **33397**.
Before cleanup, `/bin/ps -p 33397 -o command=` was checked against both the exact
owned profile and `--remote-debugging-port 9246`; only that PID received SIGTERM.
Its exit was confirmed. `cleanup.json` records the identity and result. The user
server, normal browser, and other agents' ports9244/9245 were not stopped.
