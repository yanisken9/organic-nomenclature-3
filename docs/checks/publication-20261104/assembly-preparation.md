# Curated publication assembly preparation — 4 November 2026

Prepared `prepare-assembly.py` and isolated tests. No real freeze, assembly,
clone mutation, staging, commit, push, network operation or publication was run.
Read-only inspection found public clone HEAD `74a9e3ea395eb79ffa6d6d72bdcb6275e10c93a7`
on `thesis-work`, clean, with 2,686 tracked paths. The existing assembly seed lists
712 source paths. The preservation record lists 39 React paths and core52/main52
hashes. These observations do not substitute for the full hash checks at freeze.

The script retains every existing public path, including old releases. It
preserves every `react-preview/` path and every filename with `-52.` or `_52.`;
no source update may overwrite those files. It adds eligible 54 runtime files,
games/assets/data, the separate pilot, five current professor report files,
README/contributions, dated 3–4 November documentation and historical evidence.
The final curated count is determined when the source is actually frozen.

Live source instructions/configuration/session notes/plans/state and the entire
`docs/checks/publication-20261104/` folder are excluded from new publication
updates. Existing dated historical evidence remains eligible, including its
`before` snapshots and logs, as requested. Exclusion from new updates does not
delete files that already exist in the public base.

After final sync review, runtime/core checks and document updates, the main
Developer runs:

```sh
python3 -B docs/checks/publication-20261104/prepare-assembly.py freeze
python3 -B docs/checks/publication-20261104/prepare-assembly.py assemble
python3 -B docs/checks/publication-20261104/prepare-assembly.py verify
```

`freeze` reads state, source and the disposable public clone, and writes local
evidence only. It requires the established state fields plus
`syncReviewComplete: true`, an absent/false `upstreamSyncInProgress`, final
`core54SHA256`, unchanged `core52SHA256` (or older `coreSHA256` alias), and a
nonempty exact `sourceRuntimeHashes` map. It verifies the public clone's branch,
base, clean state, independent Git metadata and location inside the dedicated
job outside source. Baseline Git blob bytes are SHA256 hashed, then compared
against all checked-out public files and the 39-path React preservation record.

Outputs are:

- `curated-source-manifest.json`: canonical sorted-key compact JSON with newline;
  exact source paths/SHA256 values, UTC source cutoff, source HEAD/index/core54,
  all base path hashes, protected path hashes and local dependency hashes.
- `curated-source-manifest.json.sha256`: detached manifest SHA256.
- `curated-stage-paths.nul`: exact curated path list for the main Developer's
  later explicit staging step. Ignored historical logs require force staging.

Those files are excluded from publication inputs and contain no self hash. The
manifest and stage-list output names are exclusive: retain earlier outputs
separately before freezing a changed source again. No output silently replaces
an existing freeze. The script never edits state.

`assemble` checks the frozen canonical bytes/detached digest and all source
hashes again, scans all curated bytes for established token/private-key patterns
(including binary/large files), and copies exact bytes only into the disposable
public clone. It verifies the entire resulting public file set, all hashes, no
base deletions, all protected React/52 bytes, and dependency hashes. It writes
`curated-assembly-verified.json` as local evidence. `verify` repeats verification
without copying. Source HEAD/branch/index/runtime invariants are checked before
and after. A source change invalidates the frozen cutoff.

There is deliberately no publication-review gate before assembly. The main
Developer completes local checks, then hands the assembled clone, frozen source
manifest, helper and evidence to one fresh independent publication Reviewer.
The main Developer controls staging, commits, pushes and publication afterward.
The script performs none of those actions, and no source Git write exists.

The local dependency check covers active HTML links/scripts/images, relevant
CSS URLs, scenario query links, 14 active theory JSONs/337 steps, two alkane sets
with three questions each, standalone and embedded pilot SVGs, all 141 library
SDF paths, shared JSmol and init54. The data inventory includes both 136 initial
registrations and five later ester registrations. Inherited active dependencies
that differ locally fail unless explicitly protected React/52 content. External
references are recorded without fetching them.

14 isolated tests passed using fictional temporary files. They check exclusions,
preservation rules, canonical bytes, URL normalization, late molecule entries,
complete fixture dependency inventory, missing assets/unknown molecules, large
binary secret-pattern detection, frozen-digest enforcement, exact public tree
verification and exclusive output creation. No actual Git or clone operation is
called by those tests. Syntax and trailing whitespace checks also passed.

The static dependency check does not execute JavaScript or validate CDN/PubChem
availability, browser interactions, chemistry, JSmol rendering or remote Pages
deployment. Those remain the main Developer's runtime/live checks and independent
review scope. Pattern scanning is not a complete secret audit. No core file was
edited by this preparation task; the concurrent core54 sync belongs to the main
work session and must be reported separately.
