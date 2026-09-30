#!/usr/bin/env python3
"""Run every check in ../checks/ against an Excalidraw+ scene.

One check per sin in ledger/sins.yaml, with the same id. Prints one line per
finding and, under it, the edit that fixes it, or that it is fixed by hand.
With --fix, applies every edit through the MCP and lints the scene again.
Exits 1 when a finding is left.
"""
import argparse
import json
import sys

from fetch import fetch, live_elements
from modules import discover
from write import edit

CHECKS = list(discover("checks"))


def run_checks(scene_id):
    elements = live_elements(fetch(scene_id))
    return elements, [(sin_id, finding) for sin_id, check in CHECKS for finding in check.run(elements)]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sceneId")
    parser.add_argument("--fix", action="store_true", help="apply every fix through the MCP, then lint again")
    args = parser.parse_args()

    elements, findings = run_checks(args.sceneId)
    fixable = [(sin_id, finding) for sin_id, finding in findings if finding.get("fix")]
    if args.fix and fixable:
        for sin_id, finding in fixable:
            edit(args.sceneId, finding["fix"])
            print(f"fixed {sin_id}  {finding['id']}  {finding['problem']}")
        elements, findings = run_checks(args.sceneId)
    for sin_id, finding in findings:
        print(f"{sin_id}  {finding['id']}  {finding['problem']}")
        fix = finding.get("fix")
        print(f"  fix: {json.dumps(fix, ensure_ascii=False, separators=(',', ':')) if fix else 'none, fix it by hand'}")
    if not findings:
        print(f"clean: {len(elements)} elements, {len(CHECKS)} checks")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
