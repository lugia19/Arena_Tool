"""Assembles the bundled tools folder (tools/) from local copies of the pinned releases, pre-configured so nothing in
it gets written at runtime except Oodle (copied from the game on first use, as it can't be redistributed).

Usage: python scripts/prepare_tools.py [--witchybnd DIR] [--rewwise DIR] [--texconv DIR] [--me3 DIR]
Defaults point at a local AC6_tools folder.
"""
import argparse
import json
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT, "tools")
AC6_TOOLS = r"C:\Users\lugia19\Desktop\Programs\AC6_tools"

# WitchyBND layers its settings as appsettings.json -> %APPDATA%/WitchyBND/appsettings.user.json ->
# appsettings.override.json, so this file keeps a user's own WitchyBND settings from changing our output.
WITCHY_OVERRIDE = {
    "Bnd": True,
    "Dcx": False,
    # WitchyBND's default. Fields shared by >= 80% of rows go into a <defaults> section and are left out of those
    # rows. 0 (no defaults) can't be repacked in 3.0.1: 78 of AC6's 257 params, including
    # AccountParam/CharaInitParam/NpcParam/NpcThinkParam/TalkParam, fail to convert back.
    "ParamDefaultValueThreshold": 0.8,
    "ParamCellStyle": "Attribute",
    "Recursive": False,
    "EndDelay": 0,
    "PauseOnError": False,
    "Parallel": True,
    "Offline": True,
    "TaeFolder": True,
    "Flexible": True,
    "BackupMethod": "None",
    "GitBackup": False,
}

# WitchyBND refuses to repack a regulation newer than this. AC6's paramdefs were last changed for 1.07 and still match
# 1.09.1 (every param unpacks against them; WitchyBND checks row sizes), so only the version number is stale.
REGULATION_VERSION_GATE = "1_09_1_0042L"


def prepare_witchybnd(source: str):
    target = os.path.join(TOOLS_DIR, "witchybnd")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("oo2core_*", "appsettings.override.json"))
    paramdex_zip = os.path.join(target, "Assets", "Paramdex.zip")
    if os.path.exists(paramdex_zip):  # WitchyBND would otherwise extract it into its own folder on first run
        with zipfile.ZipFile(paramdex_zip) as archive:
            archive.extractall(os.path.join(target, "Assets", "Paramdex"))
        os.remove(paramdex_zip)
    with open(os.path.join(target, "appsettings.override.json"), "w", encoding="utf-8") as f:
        json.dump(WITCHY_OVERRIDE, f, indent=2)
    with open(os.path.join(target, "Assets", "Paramdex", "AC6", "Upgrader", "version.txt"), "w", encoding="utf-8") as f:
        f.write(REGULATION_VERSION_GATE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--witchybnd", default=os.path.join(AC6_TOOLS, "WitchyBND-3.0.1"))
    parser.add_argument("--rewwise", default=os.path.join(AC6_TOOLS, "Audio", "rewwise"))
    parser.add_argument("--texconv", default=os.path.join(AC6_TOOLS, "DirectXTex"))
    parser.add_argument("--me3", default=os.path.join(AC6_TOOLS, "me3"))
    args = parser.parse_args()

    shutil.rmtree(TOOLS_DIR, ignore_errors=True)
    prepare_witchybnd(args.witchybnd)
    os.makedirs(os.path.join(TOOLS_DIR, "rewwise"))
    shutil.copy2(os.path.join(args.rewwise, "bnk2json.exe"), os.path.join(TOOLS_DIR, "rewwise"))
    os.makedirs(os.path.join(TOOLS_DIR, "texconv"))
    shutil.copy2(os.path.join(args.texconv, "texconv.exe"), os.path.join(TOOLS_DIR, "texconv"))
    shutil.copytree(os.path.join(args.me3, "bin"), os.path.join(TOOLS_DIR, "me3", "bin"))
    for name in os.listdir(args.me3):
        if name.startswith("LICENSE"):
            shutil.copy2(os.path.join(args.me3, name), os.path.join(TOOLS_DIR, "me3"))
    print(f"Tools prepared in {TOOLS_DIR}")


if __name__ == "__main__":
    main()
