# Controlled experiment repair: method v1

Development study, October 13, 2026. Freeze this document, programs, policies,
runner, and apparatus tests before the comparative cohort. This is a local
protocol freeze, not an externally preregistered or blinded study.

## Question and scope

Does checking provenance and collector sensitivity recover a fault-discriminating
probe more efficiently than search and normalization at an equal execution budget?

This tests a small mechanism from [the ideation proposal](../../docs/IDEATION.md).
It does not test an LLM, discover explanations, generate source-level probes, or
repair production code. The present/absent hypothesis factor is deferred: these
rule policies do not reason about hypotheses, so crossing it would duplicate
identical behavior. Natural trajectory review, independent human labeling,
coverage/mutation engines, and model-driven prompt baselines remain pending.
Those comparisons are not implemented here under substitute names.

## Cases

Four original Python microprograms have deliberately constructed faults:

- Omitted option: default formatting loses its return value.
- Retained state: an update fails to invalidate a cached value.
- Execution order: registering after close incorrectly retains a registration.
- Configuration precedence: file settings incorrectly override environment settings.

Each family has four hand-authored inputs, exactly one exposing the fault under
the result observer and workspace source. Separate reference implementations
satisfy explicit expected values in fixture specifications. All cases are visible
to the author and used for apparatus validation. They are not unseen or natural
bugs; the family examples also share the same structural search problem.

Cross each family with seven initial-probe conditions: adequate, wrong input,
wrong observer, wrong source, input plus observer, source plus observer, and
masked result. Cross again with fault present/absent. The absent condition runs
the reference workspace implementation as a negative control.

Seeds 101, 202, 303 permute opaque input identifiers and candidate order, identically
across arms in a cell. They measure order sensitivity, not independent bug samples.
This yields 56 family/condition/fault cells, 168 case-order combinations, and
840 episodes across five policies.

## Interface and information boundary

Every policy receives the same initial probe, four input handles, observation
fields `result` and `status`, sources `workspace` and `fallback`, and budget.
The 16 configurations are a supplied finite menu. Input invention, field discovery,
and automatic location of fault sites are not claimed.

The worker imports an actual program module and returns an observation, provenance
derived from its file, and a symptom flag from the explicit task specification.
That flag is common testing infrastructure, not a reference replay during policy
operation. Status is always `ok`, deliberately inadequate for observing the result.

Policies receive no family/condition/fault labels, implementation filenames/hashes,
or reference outcomes. The policy module has no fixture/evaluator imports. This
is an API boundary for fixed deterministic policies, not adversarial filesystem
isolation. The worker knows the constructed condition. Reference replay occurs
only after the policy returns.

Each episode has a fresh interpreter and unique working/home/temp directory.
Each target invocation loads a fresh module and constructs local program state;
calls within an episode share its interpreter. Statefulness exists within the
specified operation sequence, not between independent invocations.

## Calibration and stress case

A calibration triplet costs three invocations: unchanged replay, positive control,
and placebo. The positive control overwrites returned `result` with a known
sentinel before extraction. The placebo changes unobserved metadata. Sensitivity
means positive differs from clean while placebo equals clean. The receipt names
the perturbed field.

This narrowly checks the collector; it is neither full mutation testing nor a
causal-validity certificate. The masked-result wrapper substitutes the specification
value before the control overwrite. Calibration can therefore pass while the real
fault stays hidden. No menu action removes that wrapper. This is a deliberately
unsupported case for all arms, retained in the primary denominator.

Calibration observations never count as fault observations. A control supports
only the tested collector/input/source; later input sweeps make no global adequacy
claim from it. No policy rejects a causal hypothesis or declares the whole program
correct from a negative observation.

## Policies

| Arm | Behavior |
| --- | --- |
| blind_search | Initial probe, then seeded permutation of remaining configurations |
| input_sweep | Sweep inputs with current source/observer, then workspace source, then result observer |
| normalize_then_sweep | After initial probe, set workspace/result and sweep current and remaining inputs |
| always_calibrate | Repair source from receipt; always calibrate once; repair insensitive observer; sweep inputs |
| conditional_calibrate | Same routing, but return an already observed source-valid symptom before calibration |

All arms can access the same primitives. These are study heuristics, not
reproductions of published systems, native agents, or the shipped Skylla CLI.
Normalization is intentionally strong: the interface exposes a canonical source
and useful result field to all arms. Free configuration edits may let it dominate
routing. That limitation is a reason to retain and scrutinize the comparator.

## Budget, outcomes, and interpretation

Budget: eight target invocations per episode, including initial execution and
calibration. Start a triplet only with three calls remaining. Menu/configuration
edits have no invocation charge; their CPU time is included in policy wall time.
Record target, policy, subprocess, and study time without general performance
claims from these tiny subjects. Three episode workers run concurrently; summed
subprocess time differs from elapsed study time. Each episode times out at 15s.

A candidate can be submitted after observing a symptom at the expected source.
After policy completion, independently execute the reference for every ordinary
probe. A verified discriminator violates the specification in the current
workspace and satisfies it in the reference. Primary outcome: the proportion of
fault-present episodes submitting a verified discriminator within budget.

Secondary outcomes: invocation counts over all episodes and by fault presence;
false completions; calibration cost; masked-case control passes without fault
reproduction; per-condition and order outcomes. Count evaluator reference calls
separately from policy budget. Keep timeouts/infrastructure failures in the success
denominator. Do not silently retry or drop them.

Report counts and paired differences. Do not treat permutations or related
fixtures as independent natural bugs for significance tests. Diagnostic recovery
is not repair success, and no breakthrough claim follows from this cohort.

Design prediction: routing may help against blind search, while normalization
may match recovery at lower cost. A competing possibility is a useful calibration
advantage. Masking should expose the control's narrow scope. Apparatus tests
already exercise selected cases before freezing, so this is development evidence.

## Freeze and reproduce

Run apparatus tests, then `python tools/study/probe_repair/study.py freeze`.
`protocol.json` records UTC freeze time, dimensions, budgets, seeds, and SHA256
of the method and executable sources. Commit it before the first cohort. The
runner rejects changed frozen files. Method revisions need a new version.

```sh
python -m unittest discover -s tests -v
python tools/study/probe_repair/study.py run --name run-001 --workers 3
python tools/study/probe_repair/study.py verify --name run-001
```

Tracked records preserve complete structured episode traces, decisions, reference
outcomes, resource counts, hashes, and aggregates. Raw stdout/stderr/requests stay
under ignored local `artifacts/probe-repair/`, with tracked hashes. Verification
also works without those local logs and reports how many were available.

No paid inference, credentials, or third-party target code are used.
