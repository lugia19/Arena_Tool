"""The external tools (WitchyBND, bnk2json, texconv, ME3): where they live and how they get there.

They aren't in the repo. Players get them as a pre-configured tools.zip from the repo's releases, downloaded on first
run (see gui.py); developers can assemble the same folder with scripts/prepare_tools.py. Each wrapper still checks its
own version/hash. When the tools change: build a new zip, upload it under a new tag, and bump all three constants.
"""
import hashlib
import os
import shutil
import zipfile

TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
TOOLS_VERSION = "1"
TOOLS_URL = "https://github.com/lugia19/Arena_Tool/releases/download/tools-1/tools.zip"
TOOLS_SHA256 = "b27f5c9bfec19732bc10e40f75a19c772cba6333ab599857f7b831897c78b38c"

WITCHYBND = os.path.join(TOOLS_DIR, "witchybnd", "WitchyBND.exe")
BNK2JSON = os.path.join(TOOLS_DIR, "rewwise", "bnk2json.exe")
TEXCONV = os.path.join(TOOLS_DIR, "texconv", "texconv.exe")
ME3 = os.path.join(TOOLS_DIR, "me3", "bin", "me3.exe")


def tools_installed() -> bool:
    try:
        with open(os.path.join(TOOLS_DIR, "VERSION"), encoding="utf-8") as f:
            return f.read().strip() == TOOLS_VERSION
    except OSError:
        return False


def install_tools(zip_path: str):
    """Replaces tools/ with the contents of a downloaded tools.zip, after checking its hash."""
    with open(zip_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if digest != TOOLS_SHA256:
        raise ValueError(f"The downloaded tools.zip doesn't match the expected checksum (got {digest})")
    shutil.rmtree(TOOLS_DIR, ignore_errors=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(TOOLS_DIR)


def check_tools():
    missing = [path for path in (WITCHYBND, BNK2JSON, TEXCONV, ME3) if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError("Missing tools (start the ArenaTool window once to download them, or run "
                                "scripts/prepare_tools.py):\n  " + "\n  ".join(missing))
