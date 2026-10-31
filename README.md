**Namelecule — 31/10/2026:** Διόρθωση γραμμάτων 2D, ελεγχόμενη διόρθωση κύκλου ζωής JSmol και ομοιογένεια 47 ανεπτυγμένων τύπων. Παραμένουν 141 μόρια / 14 μαθήματα / 337 βήματα. Καμία σημερινή αλλαγή core ή δημόσιας React.
[Αναφορά καθηγητή](https://yanisken9.github.io/organic-nomenclature-3/docs/professor-20261031/update.html), [σελίδα υποδοχής](https://yanisken9.github.io/organic-nomenclature-3/design/welcome-proposal.html?v=release-20261031). Τα όρια και η ανοικτή διερεύνηση του κάδρου αναφέρονται στην αναφορά.

**Namelecule — 30/10/2026:** Ενιαία παρουσίαση των οκτώ ανεπτυγμένων αλκανίων,
με C–H0,3094 και C–C0,6188 στα MOL, κοινή πολιτική χαρακτήρων/κενών και
ελεγμένη αρίθμηση. Διατηρούνται141μόρια,14μαθήματα/337βήματα και προηγούμενα
σημεία επαναφοράς. Καμία σημερινή αλλαγή core ή React build.
[Αναφορά καθηγητή](https://yanisken9.github.io/organic-nomenclature-3/docs/professor-20261030/update.html),
[σελίδα υποδοχής](https://yanisken9.github.io/organic-nomenclature-3/design/welcome-proposal.html?v=release-20261030).

**Namelecule v52 — 29/10/2026:**141molecules, including nine esters;
14active lessons/337steps. [Main welcome](https://yanisken9.github.io/organic-nomenclature-3/design/welcome-proposal.html?v=release-20261029),
[professor report](https://yanisken9.github.io/organic-nomenclature-3/docs/professor-20261029/main-esters-update.html).
The five new expanded MOLs use orthogonal bonds. Known rendering limits are
listed in the report. React build/catalog remains the previous126molecule release.

**Local expanded MOL correction — 2026-10-29:** The five new esters now have
only horizontal/vertical bonds in their expanded source MOLs and embedded data.
Crowding is handled with spacing, not diagonal C–H fans. The generator preserves
this convention. Other2D forms, old esters,3D, core and viewer are unchanged by
this correction. Local, not committed/published; see [orthogonal MOL report](docs/ESTERS-ORTHOGONAL-MOL-20261029.md).

**Local ester display fixes — 2026-10-29:** Main v52 has141molecules.
The approved viewer fixes avoid duplicate formyl H, place ester acid fragments
left in skeletal mode, suppress skeletal carbon-bound H with their strokes,
and put tert-butyl formate's formyl H left in condensed/expanded views.
Source MOL/SDF, embedded data and core remain unchanged by these display fixes.
Local, without a commit or publication; checks, review status and one unchanged
legacy expanded-label overlap are recorded in [display report](docs/ESTERS-DISPLAY-20261029.md).

**Public review release - 2026-10-28:** [Main v52 welcome](https://yanisken9.github.io/organic-nomenclature-3/design/welcome-proposal.html?v=release-20261028) and
[React trial welcome](https://yanisken9.github.io/organic-nomenclature-3/react-preview/dist/?v=release-20261028#/). Main136molecules/14lessons337steps;
React126molecules/12lessons283steps. Reviewed runtime/build retained, without
rebuild or chemistry changes. Known limits are disclosed in
[professor reports](docs/professor-20261028/main-v52-update.html).

**Corrected theory scope — 2026-10-28:** «Άλλα καρβοξυλικά οξέα» now uses only
7 existing unsaturated mono-/dicarboxylic acids with C=C or C≡C and no other
functional groups, in 26 progressive steps. The library has 14 active lessons /
337 steps. Removed examples remain in the general molecule library. No core,
player, viewer or molecular data changes. Local, not committed or published.
See [corrected lesson record](docs/UNSATURATED-ACIDS-SCENARIO-20261028.md).

**Local addition — 2026-10-28:** 2-πεντεν-4-ινικό οξύ (C5H4O2) and
2-εξεν-4-ινοδιικό οξύ (C6H4O4) bring the Main library to136molecules.
Three2D forms and graph-matched explicit-H RDKit3D sources use existing
conventions and the shared skeletal geometry pipeline. Existing134records,
source assets, core52, scenarios and React catalog are preserved. Local,
without commit/push/publication. See [checks](docs/TWO-ENYNOIC-ACIDS-20261028.md).

**Local addition — 2026-10-28:** four unsaturated mono-/dicarboxylic acids
bring the Main library from130 to134molecules. The interrupted addition is
completed with bounded core52 alkyl-prefix support, three2D forms per molecule
and graph-matched explicit-H RDKit3D conformers with provenance. Existing130
records/MOLs,13active lessons and React source are preserved. These conformers
do not specify R/S or E/Z. See [scope, checks and review](docs/OTHER-ACIDS-20261028.md).
This addition is local, without commit/push/publication.

# MuLERMoCs — Organic Nomenclature Learning Platform

A Greek-first interactive learning platform for organic nomenclature, built around molecular structure, naming logic, and multiple representations. It is a no-build static web app (JSME, JSmol, Snap.svg, jQuery, vanilla JavaScript) intended to be embedded in Drupal.

Desinged and developed by Nickolas Charistos

**Local theory addition — 2026-10-28:** «Κορεσμένα μονοκαρβοξυλικά οξέα»,28
progressive steps using all8eligible existing molecules, is linked from the acid
card. The Main library now has13active lessons/311steps. Optional rule tables
start closed; the last3D step is optional. Player52 supports replay of the
existing third-acid-prefix boxes. Previous12scenarioJSONs, core52, molecular
assets and React files remain unchanged by this lesson. Local, not published.
See [lesson record](docs/MONOACIDS-SCENARIO-20261028.md) for verification status.

**Local addition — 2026-10-28:** four saturated monocarboxylic acids bring the
Main library to130molecules. Bounded core52 alkyl-prefix support, three2D forms
and graph-matched explicit-H3D follow existing conventions. All126oldrecords
and12scenarioJSONs remain unchanged; React is preserved without a rebuild.
See [acid addition and checks](docs/ACIDS-20261028.md). Local, not committed/published.

**Current local integration — 2026-10-27:** v52 from professor upstream
`93b759f5891d7b5a1172646032d83215d60b7604`, with Namelecule layout, all126molecules
and12lessons/283steps retained. The previous v51 remains runnable. Welcome/library
and the React trial now target v52; stable/published Git checkpoints are unchanged.
No commit or publication is implied. See [v52 integration and checks](docs/V52-SYNC-20261027.md)
and the current resume point for validation/review status. Older entries below
describe their original implementation stages.

**Current source snapshot — 2026-10-26:**126molecules,12active theory lessons,
283steps. The [consolidated professor update](docs/UPDATE-20261025-26.html)
covers work from the25October MOL-only double-bond/function removal through
v51 integration,28molecule additions,five new lessons and the final skeletal
alignment. Earlier dated local-only/release notes below are historical snapshots;
see `docs/SESSION-NOTES.md` for actual save/publication verification.

**Saved checkpoint — 2026-10-26:** runtime commit
`74e381c7decc839b05719400ffdeab59303917b6` is saved on `origin/thesis-work`
and verified on the personal GitHub Pages site, with121molecules and11lessons
(255steps). All121runtime3Dfiles and11scenariofiles matched the committed bytes.
The dated local-only statements below describe implementation stages before
this save. See `docs/SESSION-NOTES.md` for current publication and backup status.
The consolidated professor report is deferred until after the next work period.

**Additional local lesson — 2026-10-26:** «Άλλες κετόνες»,28progressive steps,
all7existing eligible molecules, no quiz/isomerism; the dual ketone card now has
two active lessons. Local total126molecules/12lessons/283steps. Prior11scenarios,
core51 and molecule files unchanged by this lesson. Not yet published.
See [lesson checks](docs/OTHER-KETONES-SCENARIO-20261026.md).

**Additional local molecule — 2026-10-26:**
4-ισοπροπυλο-3,6-διμεθυλο-3-οκτεν-7-ιν-2,5-διόνη (C13H18O2) brings the local
library to126molecules. Existing core51 names it without changes. Three2DMOLs
and an explicit-H RDKit3D conformer follow the checked ketone conventions.
See [single ketone checks](docs/FIFTH-KETONE-20261026.md). Local, not published.

**Local addition — 2026-10-26:** four other ketones bring the local library to
125 molecules. Bounded acyclic mono-/diketone naming preserves distinct C=C,
C≡C and carbonyl locants and existing 2D/3D conventions. Two 3D sources are
PubChem; two are documented RDKit conformers. Previous molecule records and
all eleven scenarios remain unchanged. This addition is not yet published.
See [other ketone checks](docs/OTHER-KETONES-20261026.md).

**Current baseline:** local v51, integrated from professor upstream
`6e29bd5c89872665ec9cd45f9f80fd2d9bd91d6e` on 2026-10-26.
Core51 now includes the approved local branched-ether naming extension. Namelecule preserves
its welcome page, theme, eleven theory lessons (255 steps), all 98 pre-existing molecule records,
2D MOL coordinates/explicit hydrogens, original 3D sources/provenance and cameras.
The v51 viewer uses the upstream native SVG renderer and rich-note support while
retaining local fitting, label spacing, highlights, manual rule panels and library Exit.
The approved MOL-only double-bond correction is retained; its SVG override is absent.
The previous customized v50 remains runnable and is unchanged by this migration.
This v51 integration is local and has not been committed or published.
See the [v51 integration record](docs/V51-SYNC-20261026.md) for checks and limitations.

Seven ethers were added locally on 2026-10-26, taking the library to 105 molecules.
Each uses the existing common/systematic naming toggle, three 2D MOL forms and
an explicit-H, graph-matched PubChem 3D source. The core/viewer extension handles
branched C4 alkyl groups, parent methyl prefixes and complete group highlights.
The previous 98 molecules and all theory scenarios are unchanged by this addition.
See [ether checks](docs/ETHERS-20261026.md). The approved follow-up arranges
ethers horizontally around O and uses a common default atom-label scale across
the 2D library; see [2D layout/typography checks](docs/2D-LAYOUT-TYPOGRAPHY-20261026.md).

A 27-step saturated monoether theory lesson uses all 11 existing ethers in ascending
carbon count, teaching common and school systematic naming through progressive
disclosure. See [lesson record](docs/MONOETHERS-SCENARIO-20261026.md).

Five aldehydes were added locally on 2026-10-26, taking the current library to110
molecules. Methanal detection and existing alkyl-prefix handling were extended
within the approved saturated acyclic monoaldehyde scope; its twoH are preserved
in the condensed viewer. Four3D sources are PubChem and one is documented RDKit.
See [aldehyde checks](docs/ALDEHYDES-20261026.md).

A25-step saturated monoketone theory lesson uses all seven existing eligible
molecules, progressive disclosure, optional closed rules and final3D.
The new double KETONES card reserves other ketones for a future lesson.
See [ketone lesson checks](docs/MONOKETONES-SCENARIO-20261026.md).

Four saturated monoketones were added locally on2026-10-26, taking the library
to121molecules. Bounded core51 support preserves carbonyl locants and alkyl
prefixes, selects equivalent parents by the approved naming rules, and reuses
existing2D/3D highlights. Three3D sources are PubChem and one is documented RDKit.
See [ketone checks](docs/KETONES-20261026.md).

Seven other aldehydes were added locally on 2026-10-26, taking the library to117
molecules. The approved core51 extension handles alkyl prefixes for acyclic
mono-/dialdehydes with C-C unsaturation and numbering with two terminal CHO groups.
All previous molecules and scenarios remain unchanged. Five3D sources are PubChem,
two are documented RDKit conformers. School parent-chain naming is retained for
4-ethylpent-4-en-2-ynal, distinct from current preferred IUPAC chain selection.
See [other aldehyde checks](docs/OTHER-ALDEHYDES-20261026.md).

A 24-step saturated monoaldehyde lesson uses the nine existing saturated aldehydes,
with the established progressive disclosure, C1 numbering and optional final3D.
The double aldehyde library card also offers the26-step other-aldehyde lesson,
using all eight existing unsaturated/dialdehyde examples through progressive
disclosure, optional closed rules and final3D. No quizzes or isomerism teaching.
See [other aldehyde lesson checks](docs/OTHER-ALDEHYDES-SCENARIO-20261026.md).
See [lesson record](docs/MONOALDEHYDES-SCENARIO-20261026.md).

Six new alkadienes were added locally on 2026-10-24, with three 2D forms and
explicit-H 3D assets: five validated PubChem conformers and one RDKit fallback
(1,2-butadiene, after rejecting unsuitable PubChem allene geometry). See [diene checks](docs/DIENES-20261024.md).
A fourth 23-step alkadiene theory lesson follows the same naming and branching
progression, using the eight existing dienes. See [lesson record](docs/ALKADIENES-SCENARIO-20261024.md).
Three branched enynes were added using the existing representations and data format.
See [enyne validation](docs/ENYNES-20261024.md) for formulas, provenance and checks.
A fifth 23-step theory lesson, «Ονοματολογία Αλκενινίων», uses the seven existing
enynes and the same stepwise library format. See [lesson checks](docs/ENYNES-SCENARIO-20261024.md).
**Entry point:** [index.html](index.html) → [Namelecule welcome](design/welcome-proposal.html)
→ [v51 molecule exploration](mulermoc-nom-51.html).
The prior [v49](mulermoc-nom-49.html) remains runnable with its local P2 fixes.

The previous [v48](mulermoc-nom-48.html) remains runnable with its original files.
The library offers the exact user-authored 22-step alkene lesson and a matching
21-step alkane lesson, with rules, branched examples and 2D/3D exploration.
A new22-step alkyne lesson starting with ethyne is ready for review at
[its direct presentation link](mulermoc-nom-50.html?scenario=scenarios/alkynes-nomenclature-branches.scenario.json&present=1&from=theory-library);
it is listed as the third card in the theory library. See [lesson details](docs/ALKYNES-SCENARIO-20261022.md).

| Layer | File |
|---|---|
| Core engine | [js/mulermoc-nom-core-51.js](js/mulermoc-nom-core-51.js) |
| Viewer | [js/mulermoc-nom-molview-51.js](js/mulermoc-nom-molview-51.js) |
| Teaching | [js/mulermoc-nom-teaching-51.js](js/mulermoc-nom-teaching-51.js) |
| Scenarios | [js/mulermoc-nom-scenario-51.js](js/mulermoc-nom-scenario-51.js) |
| Molecule data (121 molecules) | [js/jsme-nick-nomeclature-moc2-data_51.js](js/jsme-nick-nomeclature-moc2-data_51.js) |
| Theme | [css/namelecule-51.css](css/namelecule-51.css) |

The sections below describe the historical v44 feature baseline and broader
project plans; the current migration status is recorded above.

---

## Repositories and versions

| Site | Serves | Status |
|---|---|---|
| [organic-nomenclature-2](https://nick-charistos.github.io/organic-nomenclature-2/) | v42 | frozen — emergency hotfixes only |
| [organic-nomenclature-3](https://nick-charistos.github.io/organic-nomenclature-3/) | v44 | active — all new work happens here |

Root holds the files of the current release (`*44*`; `mulermoc-nom-42/43.html` are kept alongside). Older file sets live in [archive/](archive/README.md) (non-runnable museum). Runnable history via git tags `v41`–`v44`.

Not tracked on GitHub (not needed to run): RDKit experiments, most of `imgs/` (only `image-svgrepo-Industrial-Sharp.svg` is kept; other icons are inlined/served by `js/ui-icons.js`), PDFs, `mols/branched/`, third-party libs served via CDN (see [.gitignore](.gitignore)).

---

## What works now (v44)

### Chemistry engine
- Greek IUPAC naming for alkanes/alkenes/alkynes, branched chains, halides, alcohols, aldehydes/ketones, carboxylic acids (incl. hydroxy/amino/oxo/keto), nitriles, amines, ethers (systematic + common names), esters (two-word names).
- v44 hardening: bond-order N-table (tertiary R3N fixed), principal-functional-group rank, halogen N-way handling.
- Name analysis: per-fragment highlight and numbering in 2D and 3D, branch highlighting (incl. expanded hydrogens), rule-theory panel.

### Viewer and UI
- 2D (JSME) and 3D (JSmol) views; condensed, expanded, skeletal and annotated-skeletal modes; `[2D][3D]` visibility toggles; PNG export.
- Menu groups: homologous series (default sort by carbon count), chemical classes, rules, flat `Όλα τα μόρια`.
- Name panel: IUPAC/COMMON toggle, per-component eye toggles (hide name parts), Greek TTS narration that follows visibility.

### LEARN layer: didactic scenarios
- Authoring behind the `Σενάρια` handle: up to 3 scenarios, steps per scenario with per-step molecule/menu/chrome settings, rich step text (`B I sup sub`, size/width/columns), icon buttons, drag-reorder, step drawer, Import/Export JSON.
- Presentation mode (`#pageContainer.presenting`) walks the steps; Exit restores the full app chrome.
- Details: [docs/didactic-scenario-plan.md](docs/didactic-scenario-plan.md).

### Known gaps
- Unsaturated ethers/esters and wider ester coverage; rings and aromatics not supported.
- v44 engine fixes pending browser verification (see CHANGELOG).
- Scenario library (beyond `ethene`) and EPAL/Lyceum two-level notes still to be written.

---

## Four layers (LEARN-first)

All layers reuse the same v44 engine, embedded as a static app in Drupal:

| # | Layer | Contract | State |
|---|---|---|---|
| 1 | **LEARN** | teacher-authored linear scenarios; presentation + self-paced learning | working scaffold (authoring + presentation); first stored scenario `ethene` |
| 2 | **EXPLORE** | free browsing of all molecules (left menu) | working (64 molecules); next: bounded EXPLORE-lite (~15 mols) + menu search |
| 3 | **PRACTICE** | exercises with corrective feedback (3 types v1) | not started — see [LAYERS-PLAN](docs/LAYERS-PLAN.md) |
| 4 | **PLAY** | gamified quizzes; responses + times logged for research statistics | not started — Drupal owns auth/session/logging; see [LAYERS-PLAN](docs/LAYERS-PLAN.md) |

Out of scope for now: quiz SPA, participant logging, CSV export, server-side classroom management, rings/aromatics, reactions, isomerism (reserved in schemas), English UI (conditional later phase).

---

## Vision (twofold+1)

1. **A useful tool for chemistry learning** with real impact (teachers + students, Greek-first organic nomenclature).
2. **Ongoing research** about and from this project (learning + motivation effects, EPAL vs Lyceum, publications).
3. **Conditions for new developments** — technology and knowledge reusable for isomerism, reactions, and beyond.

### Architecture
- **Embedded static:** the chemistry app stays dependency-free static (no build); Drupal embeds it and owns scenarios, exercises/quizzes, users/sessions, logging, and exports.
- **Stats primary for research:** response + time logs designed for publication (pseudonymous participants, condition/layer flags; no PII in the static app).
- **Extensible:** scenario `menuSubset`, exercise `itemType`, log `domain` fields reserve `nomenclature | isomerism | reactions`.

### Team

| Who | Role |
|---|---|
| P1 — supervisor (computational chemistry) | app code (hand-written + AI-assisted), engine ownership |
| P2 — Drupal / educational research / statistics / eye-tracking | Drupal embedding, logging API, dashboards/CSV, research design |
| P3 — MSc student, chemistry teacher | scenarios, questions, exercises, quizzes; small-class pilots (with P4) |
| P4 — undergrad chemistry | `.mol`/`.sdf` molecule production (with P3) |
| P5 — MSc student, chemistry teacher | school research: learning + motivation, EPAL vs Lyceum |
| P6 — MSc graduate, chemistry teacher | co-supervision, project memory, educational research |

---

## Documents

- [CHANGELOG.md](docs/CHANGELOG.md) — authoritative history, incl. `[Unreleased]` v44 working copy
- [didactic-scenario-plan.md](docs/didactic-scenario-plan.md) — scenario schema and authoring flow
- [LAYERS-PLAN.md](docs/LAYERS-PLAN.md) — layer contracts, exercise types, research logging schema
- [DEVELOPMENT-PLAN.md](docs/DEVELOPMENT-PLAN.md), [PROJECT-PLAN.md](docs/PROJECT-PLAN.md), [PROJECT-PLAN-GR.md](docs/PROJECT-PLAN-GR.md) — product/research plans (may lag the code)
- [FLOWCHART.md](docs/FLOWCHART.md), [SESSION-NOTES.md](docs/SESSION-NOTES.md) — engine flow and working notes

---

## Status summary

- Baseline: **v44** (+ working copy); v43 frozen at tag `v43`, v42 frozen in repo2
- Focus: **LEARN pilot (stored scenarios) + bounded EXPLORE-lite**
- Near-term: **scenario library verification on v44**
- Rules: secondary explanatory layer; homologous series = database order
- Research layer: active design (schema v1 in LAYERS-PLAN)

## New teaching scenario — 2026-10-19

[Αλκένια–Αιθένιο](scenarios/Αλκένια-Αιθένιο.scenario.json): seven steps,
ethene naming and four-alkene 2D/3D exploration. Import through Scenarios.
Updated title clearance requires re-importing the latest file. Desktop
scenario deliverables are saved in `/Users/yannisskendros/Desktop/αρχεία  json`.

## Local molecule trial — 2026-10-19

The local v48 now includes **2-methylpropene**, bringing its data to 70 entries.
This addition is included in the current publication snapshot. See [trial review](docs/METHYLPROPENE-TRIAL.md)
for full-app checks and removal instructions.

Local v48 also includes 3-methyl-1-butene (71 total working entries), with
KingDraw-reference layout and an approved naming fix retaining the -1- locant.
Browser checks passed; user visual acceptance remains pending. Published as part of snapshot `4919f99`.
See [draft review](docs/METHYLBUTENE-TRIAL.md).

Local working data also includes 3-ethyl-2,5-dimethylhex-2-ene and grouped
alkyl highlights (72 entries). This and the 2026-10-20 upstream sync are part of the accepted snapshot. See [large-alkene review](docs/LARGE-ALKENE-TRIAL.md).

Long molecule names now stay on one line using adaptive font fitting.
Short names keep their original size. See [font fitting](docs/NAME-FONT-FIT.md).

New local lesson: [Alkene nomenclature with branches](scenarios/Αλκένια-Ονοματολογία-Διακλαδώσεις.scenario.json),
23 steps from ethene to the three branched alkenes, with 2D/3D exploration.
Import the JSON; this lesson has not been published yet.

## Theory lesson refinement — 2026-10-24

The five theory lessons use progressive disclosure without quizzes. Current step
counts are alkanes 21, alkenes 22, alkynes 22, alkadienes 23 and enynes 23, including
a separate optional final 3D observation. Naming synthesis stays in 2D.

## Four alcohols — 2026-10-24

Added 2-butanol (C4H10O), 4-methyl-2-pentanol (C6H14O),
2,2-dimethyl-3-pentanol (C7H16O) and
4-isopropyl-3,5-dimethyl-2-heptanol (C12H26O). Saturated acyclic monoalcohol
branch prefixes and corresponding highlights are supported by the scoped v50
extension. Expanded and 3D include all H, including O–H. Three PubChem SDFs
and one explicitly documented RDKit fallback; no stereoisomer identity assigned.

## Five other alcohols — 2026-10-25

Added one branched diol and four branched unsaturated alcohols (C4H10O2,
C5H10O, C6H10O, C6H8O, C9H14O), using existing 2D/3D asset conventions.
Pure acyclic alcohol branch prefixes and distinct en/yne/OH locants are supported.
Four raw PubChem 3Ds and one documented RDKit conformer; stereochemistry is
unspecified. No locant-omission policy change.
