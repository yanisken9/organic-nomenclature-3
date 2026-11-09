# v54 draft/authoring Developer evidence — 2026-11-04

ROLE_ID=NAMELECULE_DEVELOPER_V1_20261023. Approved evidence-only scope. No app source, original52, React, commits or publication were changed by this UI task. Earlier core54 implementation is reported under ../core/. This is Developer evidence, not independent review.

Comparison base: source HEAD 168e3cec01f941a84d40bbe0dc07156e7baa35d0. baseline.json records 14 relevant files at task start. source-hashes-final.json records concurrent parent-owned corrections and final hashes.

## Verified behavior

- Master off hides New/Edit and rejects New through its handler. Actual Settings toggle exposes both. Empty input and a ring are rejected with Submit still usable.
- The real JSME editor received the documented nine-carbon drawing through readMolFile (drawing-input simulation). Submit used the real naming/rendering pipeline and inline 29-atom JSmol model. Live skeletal source and numbered parent were nine carbons while the selected template was ten. After the parent C9 correction, GR/EN were εννεάνιο/nonane.
- Draw → octane → stale Accept was blocked. Resubmit recomputed eight carbons/26 atoms; resubmitting nonane restored nine/29. Accept created custom_nonane, three forms and a selected menu entry. Deep comparison preserved all 141 original records and stored MOL2D forms.
- Same-molecule Edit updated the stable key/object, appended history and retained all slots. Changed-molecule Edit forked custom_octane and preserved the first record. Update/fork checks preceded the isolated C9 spelling correction; prediction and all forms were checked afterward.
- Each saved form expands to neutral C9H20 and retains nine C atoms/eight C–C single bonds. Real manual Save produced a Blob with valid one-record JavaScript/JSON. Blob.text interception wrote only an evidence copy. Fresh-context registration preserved 141 templates, selectable forms and inline 29-atom model.
- Three forms at 1500px and 390px retained names, parent9 and nine animated numbers. The shared glyph/frame/bond-gap probe found no clipping, ink within half a CSS pixel of bonds, or hidden lines. Actual portrait Continue was dismissed. Algorithmic-parent fallback and 2D/3D hide/show passed.
- Stored-template duplicate acceptance was blocked. A controlled null PubChem 3D response left Accept btnInactive; direct acceptance stayed blocked, records were unchanged and the UI explained the dependency.

## Findings and targeted verification

1. **Silent language-reload loss, corrected by parent.** quick-reload-loss.json records 142→141 records and custom_nonane→absent after GR→EN; a separate one-step authored scenario disappeared after EN→GR. Manual Save was valid. reload-guard-results.json: 10/10 passed, zero app JavaScript errors. An actual EN pointer click opened native Greek confirmation; BiDi Cancel preserved custom/scenario JSON, normalized drawing, URL and localStorage. Same-language no-op, closed author bar, scenario-only warning, explicit Continue with documented loss, and normal exploration without prompt passed. Suite used scenario9644d52e; unchanged guard retargeted successfully on final f1763a31 by the delayed suite.

2. **Late default preload overwrote active authored card, corrected by parent.** reload-guard-startup-race.json captured a new one-step card replaced by the stored seven-step scenario while network response completed. The cause was choosing fScenarioActive() after fetch; identical cause exists in original52, left unchanged. Final delayed-preload-results.json passed 10/10, zero app JavaScript errors, source hashes unchanged. Normal startup loads seven steps plus an empty card. Holding only default JSON, then creating/capturing a card, editing the original, deleting it, or opening/closing authoring preserved exact user state after release; all 141 templates remained.

3. **Inherited C9 spelling, corrected by parent.** Early evidence contains ενάνιο. After core73e28373/name-en8490121c, prediction/fresh import show εννεάνιο/nonane. Chemistry validation belongs to the parent handoff.

No unresolved product failure was found in final targeted checks. Continuing confirmation intentionally discards memory-only work; download/register remains the preservation path.

## Evidence and version boundaries

Counts overlap; they are not a unique-test total.

| Evidence | Result |
| --- | --- |
| first-harness-drafts-browser.json | 27 assertions passed; three later harness stage errors. Original create/update/fork, core10f3e1ed/viewer3b228b89 recorded. |
| quick-reload-loss.json | 15 passing assertions, two real pre-fix losses; corrected C9 visible. No own complete hash snapshot. |
| focused-drafts-results.json | Fresh registration, graph/formula, duplicate and guard evidence; wrong native-disabled assertion and numbering harness interruption. core73e28373/viewer3b228b89 recorded. |
| targeted-layout-no3d-results.json | Ten assertions passed including corrected no-3D checks; numbering stage interrupted by test toggle. language31545f05/scenario9644d52e recorded. |
| final-form-probes.json | 16 desktop assertions passed; mobile stage intercepted by normal portrait overlay. No own hash snapshot; relevant geometry/name hashes bracketed by neighboring recorded suites. |
| final-mobile-probes.json | Remaining 19 assertions passed, zero JavaScript errors. Run after final r2 handoff; no own full hash snapshot. |
| reload-guard-results.json | Settled native/logical confirmations: 10/10 passed, JS hash snapshot. |
| delayed-preload-results.json | Final HTML64e4f298/scenariof1763a31: 10/10 passed; 14 hashes unchanged start/end; loaded script URLs recorded. |

Final hashes:

- core54: 73e28373c8128b3db48a65084ac07bd19c5f4887b236ba4896a3c5a29330fe6c
- viewer54: 3b228b89b35db3da990ca0d75885b33221ae19793fb7ef2cd68b4f03e9363fb1
- language54: 31545f05a35020b6e603d9b10300848f72fc4b4d18ebbbbb4b695f469df10bf7
- scenario54: f1763a31567172e295cfee7afc936b0e592b3d5d6c0fddc60d7e68356b21a9c8
- HTML54: 64e4f298b393e5f1c6401f4fbca193bfe44d55ebf94cd8f18c4078af2669a6e3

## Reproduction and limits

Final bounded entry points: test-reload-guard.py, test-delayed-preload.py and test-final-mobile-probes.py. Run Python3 from repository root with server8013 and explicitly isolated Firefox BiDi9246. They use stdlib/tools/namelecule_bidi.py and end their own BiDi session. Historical broad harnesses retain initial failures; they are not a single passing rerun against the final app. The old silent-reload reproduction needs pre-fix source.

actual-browser-pubchem.json records successful unmodified browser lookup/SDF functions: PubChem CID8141, nonane, real29-atom SDF. Later calls explicitly replace fetch helpers with controlled asynchronous recorded responses. Nonane provenance is in the parent directory; authentic octane HTTP200 records/provenance are here. Mocks do not establish live service availability. Drawing input was simulated, not manually painted atom by atom. Fresh registration used the exported object as a preload, not an OS file picker.

Harness corrections: await async probes before serialization; settle pointer/handler setup; wait actual menu-handler registration; respect progressive numberingFlag instead of toggling partial counts; use btnInactive rather than native disabled; dismiss portrait overlay; normalize JSME-generated MOL timestamp. Historical errors are retained. Premature capture once returned null and caused a test-injected render exception; final readiness-gated suites have zero app JavaScript errors.

Observed full-flow HTTP failure was favicon.ico404. Firefox RemoteAgent WeakMap warnings are browser-internal. A transient draft warning compared live nonane with selected methane before restoration. Default remote mode uses chemapps JSmol/j2s resources. Offline startup, physical touch hardware, all novel chemistries, manual atom drawing, OS download/import and Beautify button were not verified. These checks do not guarantee service uptime or uninterrupted presentation.

Owned Firefox PID33683/profile namelecule-v54-drafts-20261104-25ac5x00/port9246 was identity-checked, SIGTERM-stopped and confirmed exited in cleanup.json. User server8013 and other browsers were preserved.
