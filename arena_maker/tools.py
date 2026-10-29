"""Locations of the bundled tools (see scripts/prepare_tools.py). Each wrapper checks its own version/hash."""
import os

TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")

WITCHYBND = os.path.join(TOOLS_DIR, "witchybnd", "WitchyBND.exe")
BNK2JSON = os.path.join(TOOLS_DIR, "rewwise", "bnk2json.exe")
TEXCONV = os.path.join(TOOLS_DIR, "texconv", "texconv.exe")
ME3 = os.path.join(TOOLS_DIR, "me3", "bin", "me3.exe")


def check_tools():
    missing = [path for path in (WITCHYBND, BNK2JSON, TEXCONV, ME3) if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError("Missing bundled tools:\n  " + "\n  ".join(missing))
