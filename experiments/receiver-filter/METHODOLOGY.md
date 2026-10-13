# Receiver-aware observation filter: development protocol v1

October 13, 2026. A follow-up on the already exposed Tornado case, not independent
confirmation or a repair study. Freeze before the new paired probe executions.

Import AsyncIOLoop from the pinned buggy snapshot in a separate process and
record its actual method-resolution order (MRO). Starting with the earlier eight
frozen AST proposals, retain every shared class container. Retain instance fields
declared in the receiver MRO, or assigned to the same self access path in the
receiver's scanned source. The latter avoids losing an access deduplicated under
an unrelated class in the original generator. Drop other instance declarations.

This is a cheap heuristic. Dynamic attribute injection, monkeypatching, helpers,
external source not scanned and changing receiver classes can defeat it. Scanning
nested method bodies may conservatively retain extra fields. Filter proposals
only: unavailable is never recoded as zero or bug absence. This known case cannot
establish the false-exclusion rate or blind discovery.

Generate/filter using buggy source and MRO only. The known registry, earlier
reference results and source selection have been exposed to the author, but
filter code does not receive a useful-observer label or reference outcome.
Freeze both filtered and unfiltered candidate sets, source identities, method
and implementation hashes before replay. Preserve all exclusion reasons.

Replay both candidate sets on buggy and reference source: one/ten close cycles,
three repetitions, fresh source copies/processes, same fixed order. Twenty-four
probe invocations when complete, plus the single MRO import process used during
freeze. Compare paired observations, unavailable accesses and full costs. Same
probe count means fewer field accesses is not fewer test calls. Fixed run order
and startup effects prevent claiming latency gains from small differences.

No patches, inference or new reference test runs occur. The earlier target and
neighbor tests are recorded separately in the observer study; source fingerprints
must still match those snapshots. Require valid project-bound payloads and keep
all outputs/failures. A discriminating field is not an independent repair-utility
label. Retaining it on this case does not establish general safety of the filter.

```powershell
artifacts/venvs/study/Scripts/python.exe tools/study/receiver_study.py freeze
artifacts/venvs/study/Scripts/python.exe tools/study/receiver_study.py run --name run-002
python tools/study/receiver_study.py verify --name run-001
```

Freeze only when files do not already exist; use a new run name. This experiment
tests whether a simple baseline removes observed unavailable fields before we
consider learned candidate ranking.
