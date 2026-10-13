"""Original controlled faults. Inputs and specifications are in fixtures.py."""


def omitted_option(data):
    width = data.get("width")
    if width is not None:
        return str(data["value"]).rjust(width)
    # Fault: the default branch loses its result.
    str(data["value"])


def retained_state(data):
    backing, cache = {}, {}
    reads = []
    for operation, value in data["operations"]:
        if operation == "write":
            backing["key"] = value
        else:
            if "key" not in cache:
                cache["key"] = backing["key"]
            reads.append(cache["key"])
    return reads


def execution_order(data):
    closed, registered = False, False
    for operation in data["operations"]:
        if operation == "close":
            closed, registered = True, False
        else:
            registered = True
    return int(registered)


def configuration(data):
    # Fault: file configuration incorrectly wins over environment configuration.
    return data.get("file", data.get("environment", "default"))
