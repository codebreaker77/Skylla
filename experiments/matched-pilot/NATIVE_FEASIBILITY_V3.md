# Native feasibility runtime correction

Preserve run-001 and run-002, their methods and implementations. Version 2 is
preserved in Git commit 07a7aae. It restored shell reads/writes and produced
two production patches that pass the selected clean-evaluator target/class
checks. Luigi completed in 60.6 seconds; Tornado timed out at 120 seconds and
does not qualify as an in-budget completed repair under the frozen rule.

The virtual-environment launcher cannot start its user-profile base interpreter
under the native Windows sandbox. Copy the already installed Python 3.9 runtime
to ignored artifacts/runtime/python39; record every copied file hash, use explicit
standard-library/study-package paths, restore workspace source imports and
disable pytest plugin autoload as in the host evaluator. No interpreter/model
download, CPU model inference or package-version upgrade is involved.

A direct sandbox version/import check passed. An initial unbounded direct
project test invocation stalled and was stopped by terminating its verified
owned process tree. A separately recorded 30-second-bounded check, with
explicit plugin autoload disabled, ran the patched solver's five original
class tests successfully in about 2.3 seconds. This does not isolate the sole
cause of the earlier stall; it validates the corrected invocation.

Future native episodes use this sandbox-readable interpreter in their prompt,
and record its manifest hash alongside the corrected implementation. Keep
120-second caps, original issues and evaluator rules. No v3 coding episode has
run yet. Prior case and patch exposure remains development contamination.
The positive interpreter check is not another agent repair or comparison arm.
