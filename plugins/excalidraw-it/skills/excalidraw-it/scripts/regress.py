#!/usr/bin/env python3
"""Draw every example of generators/examples/ and compare it with the payload saved beside it, so that a change
to a generator or a shared script shows which drawings it moved.

    regress.py check           # 0 differ: no drawing moved
    regress.py save            # once the drawings look right: their payloads become the new baseline
    regress.py check c4 block  # only these types

Each example is examples/<type>/<n>.yaml, its payload <n>.json. Numbers compare to 6 decimals, so the last bit of
a float sum is no difference, and group ids without the suffix draw.py gives each drawing.
"""
import argparse
import json
import re
import sys

import yaml

from draw import drawn
from modules import SKILL_DIR, load
from schema import DataError

EXAMPLES = SKILL_DIR / "generators" / "examples"


def payload(example):
    kind = example.parent.name
    build = load(SKILL_DIR / "generators" / f"{kind.replace('-', '_')}.py").build
    try:
        return drawn(build, yaml.safe_load(example.read_text()), 0, 0)
    except DataError as error:
        return {"error": f"{kind}: {error}"}


def normal(value):
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [normal(item) for item in value]
    if isinstance(value, dict):
        return {key: [re.sub(r"-[0-9a-f]{6}$", "", group) for group in item] if key == "groupIds" else normal(item)
                for key, item in value.items()}
    return value


def first_difference(old, new):
    if isinstance(old, dict) or isinstance(new, dict):
        return f"{str(old)[:80]} -> {str(new)[:80]}"
    count = f"{len(old)} -> {len(new)} elements; " if len(old) != len(new) else ""
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b:
            keys = sorted(key for key in set(a) | set(b) if a.get(key) != b.get(key))
            return count + f"first at {i}, a {a.get('type')}: " + "; ".join(
                f"{key} {str(a.get(key))[:60]} -> {str(b.get(key))[:60]}" for key in keys[:3])
    return count + "the same up to the shorter one"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("mode", choices=("check", "save"))
    parser.add_argument("types", nargs="*", help="only these types; every type when left out")
    args = parser.parse_args()
    examples = sorted(p for p in EXAMPLES.glob("*/*.yaml") if not args.types or p.parent.name in args.types)
    differ = 0
    for example in examples:
        new, saved = payload(example), example.with_suffix(".json")
        if args.mode == "save":
            saved.write_text(json.dumps(new, ensure_ascii=False, separators=(",", ":")) + "\n")
        elif not saved.exists():
            differ += 1
            print(f"NEW {example.parent.name}/{example.stem}: no payload saved yet")
        elif normal(old := json.loads(saved.read_text())) != normal(new):
            differ += 1
            print(f"DIFF {example.parent.name}/{example.stem}: {first_difference(normal(old), normal(new))}")
    print(f"{args.mode}: {len(examples)} examples" + (f", {differ} differ" if args.mode == "check" else ""))
    sys.exit(1 if differ else 0)


if __name__ == "__main__":
    main()
