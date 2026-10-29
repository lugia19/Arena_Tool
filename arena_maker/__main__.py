"""Command line for the fight library and the build. Run `python -m arena_maker -h` for the commands."""
import argparse
import functools
import os
import time

from . import library, tools
from .base_mod import find_overlaps
from .build import PROFILE_NAME, build
from .package import launch
from .steam import find_game_dir


def print_list(lib):
    if not lib.entries:
        print("The library is empty.")
    for number, (fight, slot) in enumerate(library.library_fights(lib), 1):
        print(f"{number:3}. [{fight.tab}] {fight.name} by {fight.author}  (slot {slot})")
    print(f"Vanilla arena: {'hidden' if lib.hide_vanilla else 'shown'}")
    print(f"Base mod: {lib.base_mod or 'none'}")


def main():
    parser = argparse.ArgumentParser(prog="arena_maker")
    parser.add_argument("--data", default=library.DEFAULT_DATA_DIR, help="Library and build folder")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Show the fights in arena order")
    add = commands.add_parser("add", help="Add or update fights from folders or zips")
    add.add_argument("sources", nargs="+")
    remove = commands.add_parser("remove", help="Remove a fight")
    remove.add_argument("number", type=int)
    move = commands.add_parser("move", help="Move a fight to another place in the list")
    move.add_argument("number", type=int)
    move.add_argument("position", type=int)
    hide = commands.add_parser("hide-vanilla", help="Hide or show the stock arena fights")
    hide.add_argument("state", choices=["on", "off"])
    base = commands.add_parser("base-mod", help="Build on top of another mod's package folder ('none' to stop)")
    base.add_argument("folder")
    build_parser = commands.add_parser("build", help="Build the mod from the library")
    build_parser.add_argument("--game", help="Game folder (default: found through Steam)")
    build_parser.add_argument("--launch", action="store_true", help="Start the game with the mod afterwards")
    commands.add_parser("launch", help="Start the game with the last build")
    args = parser.parse_args()
    library.migrate_data_dir()

    lib = library.load_library(args.data)
    if args.command == "add":
        for source in args.sources:
            for message in library.import_source(lib, source):
                print(message)
    elif args.command == "remove":
        library.remove(lib, args.number - 1)
    elif args.command == "move":
        library.move(lib, args.number - 1, args.position - 1)
    elif args.command == "hide-vanilla":
        lib.hide_vanilla = args.state == "on"
        library.save_library(lib)
    elif args.command == "base-mod":
        folder = None if args.folder.lower() == "none" else os.path.abspath(args.folder)
        if folder:
            tools.check_tools()
            game_dir = find_game_dir() or lib.game_dir
            if not game_dir:
                raise SystemExit("Couldn't find ARMORED CORE VI through Steam")
            overlaps = find_overlaps(game_dir, folder)
            if overlaps:
                print("This mod changes things ArenaTool also edits or relies on, so custom fights may not work as "
                      "their authors intended:\n  " + "\n  ".join(overlaps))
                if input("Use it as the base mod anyway? [y/N] ").strip().lower() != "y":
                    return
        lib.base_mod = folder
        library.save_library(lib)
    elif args.command in ("build", "launch"):
        tools.check_tools()
        if args.command == "build":
            if not lib.entries:
                raise SystemExit("The library is empty; add fights first")
            game_dir = args.game or find_game_dir() or lib.game_dir
            if not game_dir:
                raise SystemExit("Couldn't find ARMORED CORE VI through Steam; pass --game")
            started = time.time()
            build(library.library_fights(lib), game_dir, args.data, lib.base_mod, hide_vanilla_arena=lib.hide_vanilla,
                  log=functools.partial(print, flush=True))  # Flushed, so progress shows when piped too
            print(f"Built in {time.time() - started:.0f}s")
        if args.command == "launch" or args.launch:
            launch(tools.ME3, os.path.join(args.data, PROFILE_NAME))
        return
    print_list(lib)


if __name__ == "__main__":
    main()
