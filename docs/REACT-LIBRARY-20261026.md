# Namelecule — structured React library, search and filters — 2026-10-26

User approved the proposed next steps: preserve the current app, save the trial
separately, normalize the library and add search/category filters. Molecular viewer
integration is deferred. Main conversation is Developer; final independent review
is required. No new dependencies, scientific rules, molecules or lesson content.

## Saved boundaries and upstream check

- Stable `thesis-work` remains3673c390c1fb1b7cbcc79411a6e1e3720e97f7ab.
- New **local** branch `react-library-pilot` holds the previous reviewed pilot and
  its already verified upstream image-picker sync in checkpoint
  e8d9bb406bc8172095a09cc8a46ba330dfb22922. The new structured-library changes
  follow that checkpoint after their own review. No push/publication is performed.
- Current upstream HEAD/main was read again:dc02933358a19f792c1a393fbdc2c15c2aba573f,
  equal to the last checked/content-synchronized revision. Its current changelog
  was fetched successfully and matched the Git object byte-for-byte (SHA256
  eb54faf3308c29c143d816b76399f1cd6ad373223de8a28f56b3b3253a875c0d).
  No additional release/port was needed. The current published site stays unchanged.

## Actual React structure

`tools/sync-content.py` still reads the existing source pages and scenario files,
but the library is now normalized into categories and lessons. Fields include
stable IDs, titles, descriptions, topic lists, formula text/subscript tokens and
restrictions, actual scenario step counts, action labels and unchanged player URLs.
The old generic library main DOM tree is no longer included in the generated JSON.

`LibraryPage.jsx` renders real `LessonCard`, `Lesson` and `Formula` components.
The welcome/shared header/footer bridge remains the earlier trusted node renderer;
this change is not a claim of complete app migration. Source HTML and scenario
JSONs remain the authoring authority, so there is no second manually maintained
curriculum. Rebuilding refreshes the generated snapshot, and stale snapshots or
inconsistent step badges fail validation.

The initial nine-card/twelve-lesson order, all titles/descriptions/topics/formulas/
restrictions/counts and lesson URLs are preserved. Dual categories remain grouped.
Header/lesson heading structure uses actual semantic headings. No molecular data,
coordinates, naming core or existing player behavior is changed in this stage.

## Search behavior

- Search covers category/lesson titles, descriptions and listed topics. It does
  not search all text in the283lesson steps, and is not a chemical/stemming engine.
- Greek accents, letter case and final sigma are normalized. All entered words
  must occur in the combined category/lesson summary; ordering stays unchanged.
- Category selection combines with search. A dual card displays only matching
  lessons and indicates a partial result, e.g.1of2; all category choices remain
  available regardless of the current results.
- A live result count, explicit no-results text, labeled search/select controls
  and Clear with focus returned to search support keyboard/screen-reader access.
- Filters remain during in-app welcome/library navigation. Full refresh or leaving
  for the existing player resets them; no account, local storage or progress log.
- Starting a lesson performs the same v51 navigation. Exit keeps the established
  library. The published entry and legacy welcome/library remain unchanged.

## Verification and evidence

- Vite production build passed (18modules; JS262.54kB/79.22kB gzip and CSS1.63kB/
  0.66kB gzip in the measured build). No new performance advantage is claimed.
  Pinned packages/lock and the previously verified portable Node remain unchanged.
- Read-only extractor `--check`, two Python ASTs, JS module syntax and Git whitespace
  checks passed. Catalog has9categories/12lessons/283steps; original welcome/panel
  snapshot and all12lesson links remain identical. No legacy main AST remains in
  the normalized library data.
- 1252 before-task file hashes remain unchanged after the final documentation
  entry, including core49/50/51, all molecule assets/data, lesson JSONs, existing
  app HTML/player/viewer and the old welcome/library. Expected changes are limited
  to the approved React files/build and related documentation/journals; new files
  are listed in the frozen review manifest. Stable thesis-work ref is unchanged.
- Twenty read-only Node behavior cases passed: Greek normalization, all-term
  search, category combinations, unmatched inputs, original ordering and no source
  catalog mutation. Results are based on the real catalog and explicit expected IDs.
- Actual Firefox1500px/390px checks passed: original library semantic field/formula/
  count/link parity, all9category choices, uppercase/unaccented/final-sigma queries,
  multiword topics, combined filters, partial dual card, result counts, no-results,
  Clear/focus, Enter-submit prevention, query treated as text, navigation retention,
  refresh reset, no document horizontal overflow and welcome dialog Escape.
- The existing Other-ketones lesson opened from a filtered result, with126molecules
  available; Next and existing Exit passed. This is a limited integration smoke,
  not a new execution of every lesson step or every molecular representation.
- React-preview console:0errors. During the legacy lesson transition,1known-type
  JSmol `this.viewer is null` event was captured, including its full stack. It was
  explicitly classified after the run;0unexpected errors. The saved browser script
  now applies that same classification to future runs. No retry was used to erase
  the event. The underlying cause remains unisolated and no JSmol fix is claimed.

Evidence in `docs/checks/react-library-{static,search,browser}-20261026.json`.
Read-only search cases: `node docs/checks/test-react-library-search-20261026.mjs`.
Browser script: `docs/checks/test-react-library-browser-20261026.py` (artifacts/tmp).
Build/open instructions remain in `react-preview/README.md`. Original pilot docs
and browser artifacts are historical records of checkpoint e8d9bb4, not a fresh
execution of those old checks against this new catalog representation.

Independent Reviewer identity, actual independent checks, findings/resolutions and
coverage limits are recorded in SESSION-NOTES and YANNIS-CONTRIBUTIONS. Browser
results/build output above are Developer evidence. Native OS picker, other browsers,
Drupal embedding, offline deployment, full viewer migration and learning outcomes
were not tested here. No chemistry/learning-design agent was needed for unchanged
scientific and educational content.

## Core and publication status

No core intervention in this stage. Core51 SHA256 remains
096d617853646de0dfd67bcbde3e32252aebcb98e7525b05e6f7e71ccb48a5fc.
The prior upstream picker integration belongs to the saved first checkpoint;
this phase does not modify the existing app/player source. Final reviewed work is
to be saved locally on the React branch after review; actual commit status is
recorded in the session notes. Local commits do not publish the preview.
The next decision is user inspection of the library; viewer migration remains
a separately planned later phase.
