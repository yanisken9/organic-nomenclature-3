# MuLERMoCs — Organic Nomenclature Learning Platform

A Greek-first interactive learning platform for organic nomenclature, built around molecular structure, naming logic, and multiple representations. It is a no-build static web app (JSME, JSmol, Snap.svg, jQuery, vanilla JavaScript) intended to be embedded in Drupal.

Desinged and developed by Nickolas Charistos

**Current baseline:** local v50, integrated from professor upstream
`2b616f6` on 2026-10-23. The v50 core preserves the three locally reviewed
v49 P2 fixes and the approved εξαδιένιο connector correction; it is not byte-identical
to upstream. All 89 local molecules,
their order, 2D assets, 3D files and lesson settings are preserved.
Namelecule welcome/library/theme, name fitting, loading and Exit behavior remain.
See [v50 integration report](docs/V50-SYNC-20261023.md) for checks and limitations.
This migration is local and has not been committed or published.
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
→ [v50 molecule exploration](mulermoc-nom-50.html).
The prior [v49](mulermoc-nom-49.html) remains runnable with its local P2 fixes.

The previous [v48](mulermoc-nom-48.html) remains runnable with its original files.
The library offers the exact user-authored 22-step alkene lesson and a matching
21-step alkane lesson, with rules, branched examples and 2D/3D exploration.
A new22-step alkyne lesson starting with ethyne is ready for review at
[its direct presentation link](mulermoc-nom-50.html?scenario=scenarios/alkynes-nomenclature-branches.scenario.json&present=1&from=theory-library);
it is listed as the third card in the theory library. See [lesson details](docs/ALKYNES-SCENARIO-20261022.md).

| Layer | File |
|---|---|
| Core engine | [js/mulermoc-nom-core-50.js](js/mulermoc-nom-core-50.js) |
| Viewer | [js/mulermoc-nom-molview-50.js](js/mulermoc-nom-molview-50.js) |
| Teaching | [js/mulermoc-nom-teaching-50.js](js/mulermoc-nom-teaching-50.js) |
| Scenarios | [js/mulermoc-nom-scenario-50.js](js/mulermoc-nom-scenario-50.js) |
| Molecule data (89 molecules) | [js/jsme-nick-nomeclature-moc2-data_50.js](js/jsme-nick-nomeclature-moc2-data_50.js) |
| Theme | [css/namelecule-50.css](css/namelecule-50.css) |

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
