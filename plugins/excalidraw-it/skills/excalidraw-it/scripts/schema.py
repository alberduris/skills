"""Check the YAML a generator reads, so that a mistake in it stops the drawing with a message that names it."""


class DataError(Exception):
    """A mistake in the YAML; draw.py prints it and exits."""


def fields(value, where, required=(), optional=()):
    """The mapping at `where`, which has every required key and no key outside required and optional."""
    if not isinstance(value, dict):
        raise DataError(f"{where}: expected a mapping, got {value!r}")
    missing = [key for key in required if key not in value]
    if missing:
        raise DataError(f"{where}: missing {', '.join(missing)}")
    unknown = [str(key) for key in value if key not in required and key not in optional]
    if unknown:
        raise DataError(f"{where}: unknown {', '.join(unknown)}; it takes {', '.join([*required, *optional])}")
    return value


def number(value, where, low=None, high=None, whole=False):
    if isinstance(value, bool) or not isinstance(value, int if whole else (int, float)):
        raise DataError(f"{where}: expected {'a whole number' if whole else 'a number'}, got {value!r}")
    if low is not None and value < low:
        raise DataError(f"{where}: {value} is below {low}")
    if high is not None and value > high:
        raise DataError(f"{where}: {value} is above {high}")
    return value


def pair(value, where, **limits):
    """Two numbers written as [a, b], each checked as number() checks one."""
    if not isinstance(value, list) or len(value) != 2:
        raise DataError(f"{where}: expected [a, b], got {value!r}")
    return tuple(number(item, f"{where}[{i}]", **limits) for i, item in enumerate(value))


def choice(value, where, choices):
    """One of the choices: a color, or the id of something defined elsewhere in the YAML."""
    if value not in choices:
        raise DataError(f"{where}: {value!r} is not one of {', '.join(map(str, choices))}")
    return value


def entries(value, where, optional=False):
    """A mapping of name: value, as bars, nodes and components are written; an optional one may be left out."""
    if optional and value is None:
        return {}
    if not isinstance(value, dict) or not value:
        raise DataError(f"{where}: expected a mapping of name: value, got {value!r}")
    return value


def listed(value, where):
    """A list, as edges and links are written; left out, it is empty."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise DataError(f"{where}: expected a list, got {value!r}")
    return value
