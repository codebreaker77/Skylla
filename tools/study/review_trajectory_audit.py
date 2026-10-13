"""Encode single-assistant review annotations; labels are judgments, not an oracle."""

from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/trajectory-audit"

# Each row refers to an exact source message. Text is original paraphrase.
# Format: message, intent, outcome, surface, exception visible, assessment, next check.
REVIEWS = {
    "scikit-learn__scikit-learn-14496": [
        (20, "validation", "no_visible_failure", "test_assertions", False, "Existing OPTICS tests pass; this does not establish coverage of fractional sample counts.", "Pair the fractional-input reproduction with integer-input controls."),
        (22, "reproduction", "symptom_observed", "exception", True, "Fractional sample count reaches project code and raises the reported neighbor-count type error.", "Repeat with fractional counts that round differently and verify effective neighbor count."),
        (46, "excluded", "not_applicable", "edit_script", True, "Edit-only script fails while decoding a source file; retain as an excluded operational event, not a diagnostic probe.", "Specify source-file encoding when applying the edit."),
    ],
    "django__django-15128": [
        (40, "excluded", "not_applicable", "version_check", False, "Version-only environment inspection does not execute the reported alias-collision scenario.", "Reproduce the query combination with the supplied model relationships."),
        (42, "validation", "no_visible_failure", "test_assertions", False, "Basic tests pass with skips; target alias behavior is not established by this suite result.", "Run a focused alias-changing query rather than use this as target evidence."),
        (48, "validation", "no_visible_failure", "test_assertions", False, "Existing query tests pass; no target reproduction is visible in this reviewed event.", "Observe alias maps before and after combining the reported queries."),
    ],
    "django__django-11276": [
        (6, "exploration", "no_visible_failure", "returned_value", False, "Standard-library escaping is observed; project wrapper equivalence is not executed here.", "Compare project and standard-library escaping on the same inputs."),
        (10, "validation", "setup_blocked", "command_error", False, "The requested pytest executable is unavailable.", "Use the project's documented test runner before interpreting test behavior."),
        (12, "validation", "setup_blocked", "exception", True, "The suite records an ASCII file-decoding error in a strip-tags fixture; target escape equivalence remains unestablished.", "Restore a compatible fixture-file encoding and rerun the focused escape tests."),
    ],
    "pytest-dev__pytest-7982": [
        (10, "excluded", "not_applicable", "docstring", False, "Runtime docstring inspection does not exercise symlink traversal.", "Construct a symlinked directory and inspect actual collection."),
        (32, "validation", "no_visible_failure", "test_assertions", False, "Existing path tests pass; the reported symlink scenario is not shown in this event.", "Compare collected node IDs for real and symlinked directories."),
        (40, "excluded", "not_applicable", "edit_script", False, "The Python command edits production code without running a diagnostic assertion.", "Run the symlink reproduction after the edit with unchanged fixture inputs."),
    ],
    "django__django-14787": [
        (10, "exploration", "no_visible_failure", "returned_value", False, "The agent checks wrapper metadata on a standard-library partial object.", "Check equivalent metadata through the project's decorator path."),
        (12, "validation", "setup_blocked", "command_error", False, "The requested pytest executable is unavailable.", "Invoke the project runner for the decorator tests."),
        (16, "validation", "no_visible_failure", "test_assertions", False, "Project decorator tests pass, but the issue-specific wrapper metadata is not independently compared.", "Run the supplied decorated-method example and observe wrapper attributes."),
    ],
    "pydata__xarray-3677": [
        (4, "reproduction", "symptom_observed", "exception_and_values", True, "The top-level merge succeeds while the method raises the reported attribute error; the script catches the exception and exits zero.", "Preserve the output comparison and add a target-specific assertion independent of exit status."),
        (20, "exploration", "unknown", "exception", True, "An unnamed array yields a printed validation exception despite zero exit status; relevance to the named-array issue is not established.", "Separate named and unnamed input contracts before accepting either result as target evidence."),
        (22, "exploration", "unknown", "exception_and_values", True, "The probe prints dataset iteration then raises on scalar-array iteration; this is auxiliary behavior, not the original merge symptom.", "Record which iteration precondition is required by the merge path."),
    ],
    "scikit-learn__scikit-learn-15100": [
        (10, "validation", "no_visible_failure", "test_assertions", False, "Existing text tests pass with expected failures; they do not establish the pre-normalized input contract.", "Run the actual project function on both normalization forms."),
        (14, "reproduction", "setup_blocked", "exception", True, "Printing a combining character fails under ASCII before the planned comparison; the script uses copied function logic rather than importing the project function.", "Use an encoding-safe observer and verify the actual project import."),
        (16, "reproduction", "setup_blocked", "exception", True, "Using repr still fails during ASCII output, so the revised observer does not yet expose the intended value.", "Use escaped code points or explicit UTF-8 output and rerun the project function."),
    ],
    "astropy__astropy-13398": [
        (34, "exploration", "unknown", "exception", True, "A missing-location transform prints an attribute error with zero exit status; its relation to the requested direct transformation is uncertain.", "Specify frame location and time preconditions explicitly."),
        (46, "exploration", "setup_blocked", "exception", True, "Coordinate construction rejects unitless angles before the intended time-propagation check.", "Supply explicit angular units, then verify the desired transformation ran."),
        (48, "exploration", "unknown", "exception", True, "After adding units, transformation reaches a missing-time attribute error; whether this is expected under the chosen frame contract is unresolved.", "Compare explicit target time with an omitted target time before interpreting propagation."),
    ],
    "sphinx-doc__sphinx-7757": [
        (16, "exploration", "no_visible_failure", "internal_state", False, "The agent directly inspects positional-only argument and default-value AST fields.", "Compare these AST fields with the rendered documentation signature."),
        (18, "exploration", "no_visible_failure", "internal_state", False, "A second signature inspects how defaults align across both argument groups.", "Exercise the project renderer with the same signature variants."),
        (22, "validation", "no_visible_failure", "test_assertions", False, "Python-domain tests pass with many warnings; the new positional-only default behavior is not independently established.", "Add a focused rendered-signature assertion rather than infer target coverage from the suite."),
    ],
    "sphinx-doc__sphinx-7590": [
        (54, "validation", "no_visible_failure", "test_assertions", False, "Existing C++ domain tests pass; support for the requested literal suffixes is not shown by this event.", "Parse a literal-suffix example and observe its AST and rendered signature."),
        (72, "excluded", "not_applicable", "edit_script", False, "Shell quoting prevents an edit-only Python script from running.", "Use a literal script file for the edit, then run an actual parser probe."),
        (74, "excluded", "not_applicable", "edit_script", False, "The helper applies production-code replacements; its success message is not behavior validation.", "Run targeted parser examples after the edit."),
    ],
    "sympy__sympy-18211": [
        (24, "reproduction", "symptom_observed", "exception", True, "The equation-to-set path raises the issue's unsupported-solver exception.", "Compare equation-to-set and direct solver results using the same domain."),
        (26, "exploration", "no_visible_failure", "returned_value", False, "The periodicity helper returns no period; this alone neither fixes nor identifies the reported failure.", "Observe the dispatch branch chosen when periodicity is absent."),
        (30, "exploration", "no_visible_failure", "returned_value", False, "The direct solver returns a condition set, supplying an alternative-path comparison in the same trace.", "Preserve domain assumptions when testing the equation-to-set path."),
    ],
    "sympy__sympy-23824": [
        (14, "reproduction", "symptom_observed", "assertion_and_values", True, "Two contraction orders are compared; the second reverses the leading factors and fails its assertion.", "Retain ordered factor assertions through repair verification."),
        (16, "validation", "setup_blocked", "command_error", False, "The requested pytest executable is unavailable.", "Use the repository's test command."),
        (18, "validation", "no_visible_failure", "test_assertions", False, "The repository runner passes existing gamma-matrix tests; the earlier custom reproduction still supplies distinct issue evidence.", "Check the same contraction-order reproduction after the patch."),
    ],
    "sphinx-doc__sphinx-10449": [
        (20, "exploration", "no_visible_failure", "internal_state", False, "Standard-library signature metadata is inspected, without executing the documentation renderer.", "Compare custom-class metadata with the renderer's chosen signature."),
        (22, "exploration", "no_visible_failure", "internal_state", False, "The custom class signature exposes its return annotation directly.", "Observe whether the renderer preserves or suppresses that annotation for classes."),
        (26, "exploration", "no_visible_failure", "internal_state", False, "The agent compares the raw annotation and the project's stringified form; no inaccessible observer is demonstrated.", "Validate the final rendered class documentation rather than only the metadata."),
    ],
    "pytest-dev__pytest-6197": [
        (22, "excluded", "not_applicable", "version_check", False, "A version/import-path check is environment inspection, not target reproduction.", "Use the temporary package-collection fixture for target evidence."),
        (24, "validation", "no_visible_failure", "test_assertions", False, "An existing package-skip test passes; the supplied failing-package reproduction is a separate check.", "Compare collection node IDs in the targeted package fixture."),
        (28, "reproduction", "symptom_observed", "collection_error", True, "The reproduction collects a package initializer and triggers its assertion; pytest exit code two is the reported collection regression, not a generic setup failure.", "Preserve collected node identities when comparing the repaired collector."),
    ],
    "astropy__astropy-13579": [
        (12, "reproduction", "setup_blocked", "exception", True, "Celestial-frame resolution fails before the planned sliced-coordinate observations.", "Choose compatible coordinate inputs and verify the sliced conversion executes."),
        (14, "reproduction", "symptom_observed", "values_and_internal_state", False, "After avoiding frame resolution, the probe displays a large full-versus-sliced coordinate discrepancy and slice metadata; interpretation remains single-reviewer judgment.", "Assert the intended slice-equivalence relation with explicit units and fixed coordinates."),
        (16, "exploration", "no_visible_failure", "internal_state", False, "The agent adds axis-correlation and slice-index observations on its own.", "Trace the coupled fixed-axis contribution before selecting a production change."),
    ],
}


if __name__ == "__main__":
    extracted = json.loads((CONFIG / "events.json").read_text(encoding="utf-8"))
    events = {event["event_id"]: event for trace in extracted["traces"] for event in trace["selected_candidates"]}
    annotations = []
    for instance, rows in REVIEWS.items():
        for index, intent, outcome, surface, exception, assessment, check in rows:
            event_id = instance + ":m" + str(index) + ":c0"
            if event_id not in events:
                raise ValueError("Review does not match extracted source event: " + event_id)
            annotations.append(dict(events[event_id], instance_id=instance, intent=intent,
                included=intent != "excluded", visible_outcome=outcome, observation_surface=surface,
                exception_visible=exception, evidence_support="plausible_interpretation" if instance == "astropy__astropy-13579" and index == 14 else "documented_by_log",
                assessment=assessment, missing_internal_observation="not_established",
                contrast="buggy_current_state_contrast_not_established", reference_replay_available=False,
                next_check=check, next_check_estimated_seconds=None))
    if len(annotations) != len(events) or len({item["event_id"] for item in annotations}) != len(events):
        raise ValueError("Missing or duplicated annotation")
    included = [item for item in annotations if item["included"]]
    zero_exception = [item["event_id"] for item in included if item["exception_visible"] and item["return_code"] == 0]
    context = [
        {"instance_id": "scikit-learn__scikit-learn-15100", "message_indices": [18, 19],
         "assessment": "Later context outside the event denominator: the agent sets UTF-8 output and its copied-function comparison becomes visible. This is agent recovery, not Skylla benefit."},
    ]
    output = {"schema_version": 1, "reviewer": "Single coding assistant; not independent human adjudication",
              "events_sha256": hashlib.sha256((CONFIG / "events.json").read_bytes()).hexdigest(),
              "review_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "reviewed_candidates": len(annotations), "included_runtime_events": len(included),
              "excluded_candidates": len(annotations) - len(included),
              "outcomes": dict(Counter(item["visible_outcome"] for item in included)),
              "zero_exit_with_visible_exception": zero_exception,
              "confirmed_missing_internal_observers": 0,
              "confirmation_warning": "No replay or independent review; absence of confirmed gaps is not absence of real gaps",
              "additional_context": context, "annotations": annotations}
    with (CONFIG / "audit.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(output, indent=2) + "\n")
    print(json.dumps({key: value for key, value in output.items() if key not in ("annotations", "additional_context")}, indent=2))
