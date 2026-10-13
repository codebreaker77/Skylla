"""A separately imported installed-copy stand-in with correct behavior."""


def omitted_option(data):
    result = str(data["value"])
    return result if data.get("width") is None else result.rjust(data["width"])


def retained_state(data):
    current, reads = None, []
    for operation, value in data["operations"]:
        if operation == "write":
            current = value
        else:
            reads.append(current)
    return reads


def execution_order(data):
    closed, registered = False, False
    for operation in data["operations"]:
        if operation == "close":
            closed, registered = True, False
        elif not closed:
            registered = True
    return int(registered)


def configuration(data):
    return data.get("environment", data.get("file", "default"))
