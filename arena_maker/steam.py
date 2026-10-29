"""Locate the AC6 install through Steam's own files (registry -> libraryfolders.vdf -> appmanifest)."""
import os
import re
import winreg
from typing import Dict, List, Optional

AC6_APP_ID = "1888160"

_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|([{}])')


def parse_vdf(text: str) -> Dict:
    """Minimal parser for Valve's text KeyValues format (quoted keys/values and braces only)."""
    tokens = []
    for match in _TOKEN.finditer(text):
        if match.group(2):
            tokens.append(match.group(2))
        else:
            tokens.append(match.group(1).replace('\\\\', '\\').replace('\\"', '"'))

    def parse_block(index):
        block = {}
        while index < len(tokens) and tokens[index] != "}":
            key = tokens[index]
            if tokens[index + 1] == "{":
                value, index = parse_block(index + 2)
                index += 1  # closing brace
            else:
                value, index = tokens[index + 1], index + 2
            block[key] = value
        return block, index

    return parse_block(0)[0]


def find_steam_dir() -> Optional[str]:
    for hive, key, value in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                             (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                             (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath")):
        try:
            with winreg.OpenKey(hive, key) as reg_key:
                path = os.path.normpath(winreg.QueryValueEx(reg_key, value)[0])
        except OSError:
            continue
        if os.path.isdir(path):
            return path
    return None


def library_folders(steam_dir: str) -> List[str]:
    folders = [steam_dir]
    vdf_path = os.path.join(steam_dir, "steamapps", "libraryfolders.vdf")
    if os.path.exists(vdf_path):
        with open(vdf_path, encoding="utf-8") as f:
            data = parse_vdf(f.read()).get("libraryfolders", {})
        for entry in data.values():
            if isinstance(entry, dict) and "path" in entry:
                path = os.path.normpath(entry["path"])
                if path.lower() not in (f.lower() for f in folders):
                    folders.append(path)
    return folders


def find_game_dir(app_id: str = AC6_APP_ID) -> Optional[str]:
    """Returns the folder containing armoredcore6.exe, or None if it can't be found."""
    steam_dir = find_steam_dir()
    if not steam_dir:
        return None
    # Checking every library's appmanifest (rather than trusting the "apps" lists) skips stale library entries.
    for library in library_folders(steam_dir):
        manifest_path = os.path.join(library, "steamapps", f"appmanifest_{app_id}.acf")
        if not os.path.exists(manifest_path):
            continue
        with open(manifest_path, encoding="utf-8") as f:
            install_dir = parse_vdf(f.read()).get("AppState", {}).get("installdir")
        if not install_dir:
            continue
        game_dir = os.path.join(library, "steamapps", "common", install_dir, "Game")
        if os.path.exists(os.path.join(game_dir, "armoredcore6.exe")):
            return game_dir
    return None
