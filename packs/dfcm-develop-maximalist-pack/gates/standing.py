ORDER = {"BUILD_BROKEN":0,"BLOCKED":1,"UNKNOWN":2,"PARTIAL_ALIVE":3,"ALIVE":4}
def compose(values):
    values = tuple(values)
    if not values:
        return "UNKNOWN"
    unknown = set(values) - set(ORDER)
    if unknown:
        raise ValueError("REFUSED[INVALID_STANDING]")
    return min(values, key=lambda value: ORDER[value])
