"""Evaluator-owned microprogram cases, never passed wholesale to a policy."""

FAMILIES = {
    "omitted_option": [
        ({"value": 7}, "7"),
        ({"value": 7, "width": 1}, "7"),
        ({"value": 7, "width": 3}, "  7"),
        ({"value": 12, "width": 4}, "  12"),
    ],
    "retained_state": [
        ({"operations": [("write", 1), ("read", None), ("write", 2), ("read", None)]}, [1, 2]),
        ({"operations": [("write", 1), ("read", None)]}, [1]),
        ({"operations": [("write", 1), ("write", 2), ("read", None)]}, [2]),
        ({"operations": [("write", 3), ("read", None), ("read", None)]}, [3, 3]),
    ],
    "execution_order": [
        ({"operations": ["close", "register"]}, 0),
        ({"operations": ["register", "close"]}, 0),
        ({"operations": ["register"]}, 1),
        ({"operations": ["close"]}, 0),
    ],
    "configuration": [
        ({"file": "disk", "environment": "env"}, "env"),
        ({"file": "disk"}, "disk"),
        ({"environment": "env"}, "env"),
        ({"file": "same", "environment": "same"}, "same"),
    ],
}

CONDITIONS = (
    "adequate", "wrong_input", "wrong_observer", "wrong_source",
    "input_and_observer", "source_and_observer", "masked_result",
)


def initial_probe(condition, input_ids):
    wrong_input = condition in ("wrong_input", "input_and_observer")
    wrong_observer = condition in ("wrong_observer", "input_and_observer", "source_and_observer")
    wrong_source = condition in ("wrong_source", "source_and_observer")
    return {"input": input_ids[1 if wrong_input else 0],
            "observer": "status" if wrong_observer else "result",
            "source": "fallback" if wrong_source else "workspace"}
