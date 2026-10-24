# Independent custom Reviewer report — 2026-10-23

ROLE_ID=NAMELECULE_REVIEWER_V1_20261023

No actionable P0/P1/P2/P3 findings were identified within the reviewed scope.

**Target and independence**

Fresh review context; no Developer conversation history or prewritten verdict inherited. Read `AGENTS.md`, `docs/REVIEW-CHECKLIST.md`, README and current session notes.

Comparison base: `2de69f439dc3b709fc4658624ad98ee8d6ffe47e`. Inspected the actual core49/viewer49/HTML diff and all requested test/evidence files. Independently computed SHA256 values for all eight frozen files; every value matches `docs/checks/v49-p2-freeze-20261023.json`. Workflow documentation and pre-existing notes changes were excluded from attribution to these fixes.

**Assessment**

- Fragment membership now bounds propyl/isopropyl classification at all inspected core and viewer ether/ester call sites.
- Alphabetical tie handling is restricted to saturated acyclic hydrocarbons, with matching 2D/3D orientation and pool ranking.
- Three or more substituent types retain interleaved locant/name pairs within twelve slots. Inspected grouped explanations, rule selection, stable component IDs, hidden-field and narration paths.
- Rooted branch signatures distinguish equal-sized n-propyl/isopropyl highlights and support stepper matching across independent atom orders.
- The immutable red evidence meaningfully demonstrates all three original failures. Its historical execution is supplied Developer evidence, rather than independently reproduced here.
- No molecular data, authored scenarios, teaching files or v50 integration appear in the application diff.

**Independent checks**

Executed with:

```text
/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc <file>
```

All returned exit 0:

| File | Result |
|---|---|
| `docs/checks/test-alkanes-p2-v49.js` | 14 checks passed |
| `docs/checks/test-alkanes-p2-extended-v49.js` | 877 assertions passed |
| `docs/checks/test-core-parent-chains-20261022-v49.js` | 20 permutations, parent paths and three unsaturation controls passed |
| `docs/checks/test-v49-scenarios-20261022.js` | 22-step validation/export/import checks passed |

Additionally executed an in-memory extension of the extended harness: four substituent types with repeated methyl groups, expected name `4-αιθυλο-5-ισοπροπυλο-2,9-διμεθυλο-6-προπυλοδεκάνιο`, across 20 independently permuted 2D/3D graphs. Naming and stepper signatures passed.

Other actual inspections: `git status --short`, `git diff --` the three application files, `cat`, `head`, `sed`, `rg`, and `shasum -a 256`.

**Supplied evidence and limits**

The freeze manifest reports a successful Firefox/JSME/JSmol browser run covering three representations, two chain modes, component clicks, selections, rule rows, grouped explanations, hidden fields, mocked speech routing and stepper behavior. I inspected the browser harness but did **not** execute it or launch a browser. These results remain supplied Developer evidence. No independent visual, audible speech, resize/export or library-navigation assessment was performed.

Recursive substituent naming, unsupported chemistry and full IUPAC certification remain outside scope. Existing scenario checks cover 22 steps; they do not establish exhaustive validation of every lesson.

**Rights and file changes**

Actual reviewer role identity is stated above. Runtime instructions declare a read-only filesystem sandbox and approval policy `never`; the behavioral no-write rule separately prohibits mutations. Git’s macOS launcher emitted denied `/tmp/xcrun_db-*` cache attempts, providing evidence of those specific blocked writes, not proof of universal enforcement. No write probes, escalation, custom TOML inspection, agents or browser launches were performed.

I made no source, core, documentation, staging or other file changes. The reviewed Developer target includes local changes to `js/mulermoc-nom-core-49.js`.

The inspected frozen implementation satisfies the three approved corrections on the evidence examined. No corrective finding is raised; this scoped conclusion does not guarantee absence of other defects or authorize publication.
