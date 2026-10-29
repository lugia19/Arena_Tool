"""python -m arena_maker build <fight folders...> [--out DIR] [--launch]"""
import argparse
import os
import time

from . import tools
from .build import build
from .fight import load_fight
from .package import launch
from .steam import find_game_dir

DEFAULT_OUT = os.path.join(os.environ["APPDATA"], "lugia19", "ac6_arena_maker")


def main():
    parser = argparse.ArgumentParser(prog="arena_maker")
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="Build the mod from fight folders (in arena list order, weakest first)")
    build_parser.add_argument("fights", nargs="+")
    build_parser.add_argument("--out", default=DEFAULT_OUT)
    build_parser.add_argument("--game", help="Game folder (default: found through Steam)")
    build_parser.add_argument("--hide-vanilla", action="store_true", help="Remove the stock arena fights")
    build_parser.add_argument("--launch", action="store_true", help="Start the game with the mod afterwards")
    args = parser.parse_args()

    tools.check_tools()
    game_dir = args.game or find_game_dir()
    if not game_dir:
        raise SystemExit("Couldn't find ARMORED CORE VI through Steam; pass --game")
    fights = [(load_fight(folder), slot) for slot, folder in enumerate(args.fights)]  # M1: slot = position
    started = time.time()
    profile = build(fights, game_dir, args.out, hide_vanilla_arena=args.hide_vanilla)
    print(f"Built in {time.time() - started:.0f}s: {profile}")
    if args.launch:
        launch(tools.ME3, profile)


if __name__ == "__main__":
    main()
