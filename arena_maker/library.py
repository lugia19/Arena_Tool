"""The user's fight library: copies of imported fights plus their order and slots, in the app's data folder.

A fight is identified by author + name (from its fight.json); importing one that's already in the library replaces
it in place. Each fight gets a slot when first added, which fixes all its game IDs except the ArenaParam one (see
ids.py). Slots are never reused: a removed fight's emblem may still be on a player's AC as a decal.
"""
import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .fight import Fight, load_fight

DEFAULT_DATA_DIR = os.path.join(os.environ["APPDATA"], "lugia19", "ac6_arena_maker")
LIBRARY_FILE = "library.json"
LIBRARY_DIR = "library"


@dataclass
class Entry:
    slot: int
    author: str
    name: str


@dataclass
class Library:
    data_dir: str
    next_slot: int = 0
    hide_vanilla: bool = False
    entries: List[Entry] = field(default_factory=list)  # In arena order
    game_dir: Optional[str] = None  # Only set when Steam detection didn't find the game

    def folder(self, entry: Entry) -> str:
        return os.path.join(self.data_dir, LIBRARY_DIR, str(entry.slot))


def load_library(data_dir: str) -> Library:
    path = os.path.join(data_dir, LIBRARY_FILE)
    if not os.path.exists(path):
        return Library(data_dir)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return Library(data_dir, data["nextSlot"], data["hideVanilla"], [Entry(**entry) for entry in data["fights"]],
                   data.get("gameDir"))


def save_library(library: Library):
    data = {"nextSlot": library.next_slot, "hideVanilla": library.hide_vanilla, "gameDir": library.game_dir,
            "fights": [vars(entry) for entry in library.entries]}
    os.makedirs(library.data_dir, exist_ok=True)
    with open(os.path.join(library.data_dir, LIBRARY_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _fight_folders(folder: str) -> List[str]:
    """The folder itself if it has a fight.json, otherwise its direct subfolders that do (a pack)."""
    if os.path.isfile(os.path.join(folder, "fight.json")):
        return [folder]
    found = [os.path.join(folder, name) for name in sorted(os.listdir(folder))
             if os.path.isfile(os.path.join(folder, name, "fight.json"))]
    if not found:
        raise ValueError(f"No fight.json in {folder} or its subfolders")
    return found


def import_source(library: Library, path: str) -> List[str]:
    """Adds or updates the fights in a folder or .zip. Returns a message per fight."""
    with tempfile.TemporaryDirectory() as temp:
        if path.lower().endswith(".zip"):
            with zipfile.ZipFile(path) as archive:
                archive.extractall(temp)  # Refuses paths that would end up outside temp
            contents = os.listdir(temp)
            # A zipped folder (e.g. pack/fightA/fight.json): start inside it
            path = os.path.join(temp, contents[0]) if len(contents) == 1 and os.path.isdir(os.path.join(temp, contents[0])) else temp
        fights = [load_fight(folder) for folder in _fight_folders(path)]  # Validate everything before changing anything

        messages = []
        for fight in fights:
            entry = next((e for e in library.entries if (e.author, e.name) == (fight.author, fight.name)), None)
            if entry:
                messages.append(f"Updated {fight.name} by {fight.author}")
            else:
                entry = Entry(library.next_slot, fight.author, fight.name)
                library.next_slot += 1
                library.entries.append(entry)
                messages.append(f"Added {fight.name} by {fight.author}")
            shutil.rmtree(library.folder(entry), ignore_errors=True)
            shutil.copytree(fight.folder, library.folder(entry))
    save_library(library)
    return messages


def remove(library: Library, index: int):
    entry = library.entries.pop(index)
    shutil.rmtree(library.folder(entry), ignore_errors=True)
    save_library(library)


def move(library: Library, index: int, new_index: int):
    library.entries.insert(new_index, library.entries.pop(index))
    save_library(library)


def library_fights(library: Library) -> List[Tuple[Fight, int]]:
    """(fight, slot) in arena order, for build()."""
    return [(load_fight(library.folder(entry)), entry.slot) for entry in library.entries]
