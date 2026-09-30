#!/usr/bin/env python3
"""Print the edit_scene_content `add` payload of a prefab piece.

Each module in ../pieces/ is one piece. Its file name is the piece id with
underscores, and it defines add_arguments(parser) and build(args).
"""
import argparse
import json

from modules import discover


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="piece", required=True, metavar="<piece>")
    for piece_id, module in discover("pieces"):
        command = commands.add_parser(
            piece_id,
            help=module.__doc__.splitlines()[0],
            description=module.__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        module.add_arguments(command)
        command.set_defaults(build=module.build)
    args = parser.parse_args()
    print(json.dumps(args.build(args), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
