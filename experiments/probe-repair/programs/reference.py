"""Separate reference implementations for controlled-fixture evaluation."""


def omitted_option(data):
    result = str(data["value"])
    return result if data.get("width") is None else result.rjust(data["width"])


def retained_state(data):
    current = None
    reads = []
    for operation, value in data["operations"]:
        if operation == "write":
            current = value
        else:
            reads.append(current)
    return reads


def execution_order(data):
    closed = False
    registrations = 0
    for operation in data["operations"]:
        if operation == "close":
            closed, registrations = True, 0
        elif not closed:
            registrations = 1
    return registrations


def configuration(data):
    for source in ("environment", "file"):
        if source in data:
            return data[source]
    return "default"
