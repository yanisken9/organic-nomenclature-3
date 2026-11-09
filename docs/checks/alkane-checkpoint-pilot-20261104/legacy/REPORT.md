# Original lesson regression — 2026-11-04

Developer execution for the approved isolated alkane checkpoint pilot. This is supplied browser evidence, not independent review. No application/source/journal edits, dependency installs, commits, or publication were made by this agent.

Commands, from repository root:

```sh
python3 docs/checks/alkane-checkpoint-pilot-20261104/legacy/test-lessons-browser.py > docs/checks/alkane-checkpoint-pilot-20261104/legacy/run.log 2>&1
python3 docs/checks/alkane-checkpoint-pilot-20261104/legacy/test-model-paint.py > docs/checks/alkane-checkpoint-pilot-20261104/legacy/model-paint.log 2>&1
```

Firefox used port9245, headless1500×1000, PID36989, isolated `/tmp/namelecule-checkpoint-legacy-20261104-ff`. Its exact arguments and verified cleanup are in `firefox.json`. The owned process stopped, port9245 closed and own profile was removed. Root port9244, normal Firefox and server8013 were not touched.

- All14 original lessons/337steps completed:9780 functional assertions,0 failures. Verified authored molecule,mode,naming,selected components,visibility,2D SVG,style,heights,zoom and language state; no checkpointUI on any ordinary step and Next enabled before each final step.
- All14 export/validate roundtrips and previous/next/Exit-to-library journeys passed.
- Each lesson's final3D model was checked by actual JSmol model source, expected atom count,live state and nonzero canvas dimensions, independent of pending flags.
- Separate cold alkane step21 capture confirms the32atom model and painted canvas:538 nonwhite samples of16223. `actual-3d-cold-alkane-last.png` was visually inspected and contains the3D molecular drawing. This probe exited0 with0 JSerrors.
- All33 guarded source hashes remained unchanged across replay and paint capture. The full start/end manifest is in `lessons-browser.json`; selected exact hashes appear below. No core changes were made by this agent; core54 is also unchanged across both runs.

The replay process exited1 despite completing all functional checks: the inherited generic harness treats4 external Cactus/CIR CORS404 logs as JSerrors. There were0 application-code exceptions,12 ether atom-mismatch warnings and2 associated IUPAC-EN lookup warnings. Every diagnostic text already appears in pre-pilot `docs/checks/v54-sync-20261104/shell/lessons-browser.json`; `classification.json` records the comparison. These diagnostics were retained, not hidden.

The3 routine `lesson-*-last.png` captures were taken immediately after Prev→Next and may show3D reloading; they are not evidence of completed painting. Use the explicitly awaited cold screenshot for that evidence. Full step replay mostly calls the real `fScenarioGo` entry point; Prev/Next/Exit use the real DOM button handlers. This is a desktop proportional regression check, not exhaustive pointer/keyboard/mobile/geometry coverage, offline assurance, or conference-machine validation. JSmol j2s CDN and CIR remain external dependencies.

Selected SHA256 hashes (identical start/end):

- `mulermoc-nom-54.html`: `a2c9874acfa165907060fbb666154189196f1c1f7534df01dc77b7c90773bdd6`
- `js/mulermoc-nom-scenario-54.js`: `e8ab12d6bf7671a93d7b5b9c21506d98959f3133a6df425e3787d0408becaa9a`
- `js/mulermoc-nom-core-54.js`: `73e28373c8128b3db48a65084ac07bd19c5f4887b236ba4896a3c5a29330fe6c`
- `js/namelecule-quiz-checkpoints.js`: `d8cfa65c2e04f3b3a6e15e0b4dc8673b50e3defd3899feec96e8982f86d9b6bf`
- `js/namelecule-game-repair.js`: `63cd84e7a2f5091d0f74274e5217b3d666dcc3baf0408a541ee0efc1aa63a3fe`
