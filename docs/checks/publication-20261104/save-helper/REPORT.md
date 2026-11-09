# Save helper preparation — 4 November 2026

Scope: `communication/checkpoints/save-helper-20261104.py`, adapted from the
1 November helper, plus this evidence directory. The source application,
runtime/core files, active Git branch/HEAD/index and state JSON were not changed
by this preparation task. Other agents own the concurrent upstream sync/report.

19 isolated tests passed using temporary fictional files and mocked Git
responses. The test transcript and exact helper/test hashes are recorded in
`unit-tests.txt` and `tests-result.json`. No save, ZIP, bundle, checkpoint commit,
clone mutation, network operation or actual external save folder write was run.
Importing the helper performs no reads or writes apart from Python loading it.

## Execution prerequisites

The caller must finish the approved sync, checks, independent review, report,
public release and live verification before invoking the final save. The helper
reloads `communication/checkpoints/save-publish-20261104-state.json` at invocation.
It requires:

- Existing `stamp`, `job`, `checkpointClone`, `checkpointBranch`, `activeHead`,
  `activeBranch`, `indexSHA256`, `externalFolders` (two distinct absolute folders
  outside the source), and `clonesReady: true`.
- `core52SHA256` (or the older `coreSHA256` alias): unchanged core52 baseline.
- `core54SHA256`: **final reviewed synchronized core54**, not its older baseline.
- Nonempty `sourceRuntimeHashes`: exact relative-path → SHA256 runtime map.
  Every listed runtime file must match; the helper does not regenerate this map.
- `syncReviewComplete: true` and `upstreamSyncInProgress` absent or false.
- For final or any other non-initial generation: `publicLiveVerified: true` and
  the 40-character `publicReleaseCommit`.
- Only for an optional `initial` generation: explicit
  `allowPrepublicationSnapshot: true`. This still requires completed sync review;
  it does not bypass runtime/core invariants.
- Completed `docs/professor-20261104/` with `update.html`, `links.json`,
  `links.txt`, `message-to-professor.txt`; links JSON must supply HTTPS `report`
  and `welcome`. Relative report images must exist inside the source tree.
- Both existing React `dist` and `public` directories; the 14 active theory
  JSON files linked by the theory library must total 337 steps. The separate
  `scenarios/alkanes-name-repair-pilot.scenario.json` must exist and be inactive.
- Optional absolute `launcherPath`; otherwise the known project hierarchy
  resolves Desktop/Namelecule.app without environment variables. If present,
  the launcher must contain exactly 10 regular files (excluding `.DS_Store`).

The dedicated checkpoint repository must be clean, own its Git metadata, reside
inside `job` and outside the source, and be on `checkpointBranch`. Failed checks
abort; no source Git mutation, push or publication is implemented.

After execution is explicitly released by the main Developer:

```sh
python3 -B communication/checkpoints/save-helper-20261104.py final
```

Choose a new unique generation name for a retry after a partial failure. Existing
archive/bundle/generation-receipt names are never overwritten or deleted.

## Snapshot and receipt semantics

Tracked and nonignored untracked files, including new deliverables, enter the
source snapshot; React dist/public files are added explicitly. Source symlinks
are rejected. Every byte of source/recovery files is scanned for the established
token/private-key patterns, including large and binary files. Findings contain
paths only. This is a pattern check, not a complete secret audit.

All staged blobs in the disposable checkpoint clone must match source SHA256
values, including when Git attributes might transform content. The snapshot is
committed there; `checkpointSnapshotCommit` and `latestLocalCheckpointCommit`
identify that commit. Source ZIP contents have complete path/SHA manifests and
are checked by CRC and individual SHA256; the Git bundle is verified. A separate
communication recovery ZIP excludes older ZIP/bundle/log/hash files. Older
backups survive. ZIPs, bundles and copied artifacts use exclusive final names.

The source ZIP and checkpoint capture source bytes **before** receipt generation
and later bookkeeping. Their manifests state that cutoff. This avoids claiming
that a snapshot contains its own subsequently generated receipts. The helper
does not claim that core files were unchanged during the overall work session;
it records that the save helper itself changed no core file, core52 matched its
baseline, and core54 matched the reviewed synchronized hash.

Both external folders receive verified archives/hash files, the portable
professor report and its local images, links/messages/Webloc shortcuts, 14 active
theory JSONs/337 steps, separately labeled pilot JSON, the 10-file launcher when
present, notes and receipts. Every file copy is verified before the completion
state is written. `saveComplete` is written to the authoritative state file last.
Copies are individually atomic; multiple folders cannot form one filesystem
transaction. A failed multi-folder save may leave valid partial artifacts but
does not update the authoritative completion state. The caller must inspect any
failure and preserve those outputs when retrying with a unique generation.

For later authorized bookkeeping, import the module and call
`refresh_receipts(root, state)` after recording a distinct
`finalBookkeepingCommit` and any separately refreshed bundle metadata. That API
updates verified external notes and final receipts/state without committing,
altering the immutable snapshot commit, silently rebuilding a bundle, or pushing.
The caller remains responsible for the final bundle/bookkeeping procedure.

## Limits

Actual archive, bundle, checkpoint, report, launcher, public/live and external
copy verification remain for the main Developer after review. The tests cover
isolated helper behavior; they do not certify a real full save or restore.
Portable report hyperlinks can still need the Internet. A source backup is not
a verified conference offline package. No core file was edited by this helper
preparation; the main session's separately owned core54 sync must be reported.
