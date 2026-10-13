# Native feasibility launcher correction

The [first protocol](NATIVE_FEASIBILITY.md) and run-001 remain unchanged. Its
implementation is preserved in Git commit 015121d. Both episodes were blocked
from shell execution; Luigi produced no patch, and Tornado exhausted the cap
without a patch. These are apparatus failures, not valid native baseline scores.

The access-only marker did not validate source-reading or writes. Ignoring user
configuration also removed the explicitly configured Windows sandbox setting.
Before this retry, a direct native workspace sandbox check successfully read its
working directory and wrote/read a marker in the disposable local smoke folder.

Use the same cases, issues, model, reasoning, tools, 120-second caps and
evaluators from the first protocol. Explicitly configure the existing elevated
Windows sandbox implementation and the built-in :workspace permission profile,
and disable web search. Preserve new results under run-002, never overwrite
run-001. This restores intended workspace operations without granting full
filesystem access. It does not prove a read-confidentiality boundary.

Record the corrected implementation hash and this amendment before generation.
The retry has previously exposed development symptoms and is not independent
confirmation. Total accounting must include the failed setup episodes; token
usage absent at a timeout remains unknown, never zero. No Skylla/Laya treatment
or comparative effect is measured by either feasibility run.
