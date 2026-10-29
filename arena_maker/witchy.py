"""Wrapper around a pinned WitchyBND build: batched calls, fixed settings, and Oodle taken from the game folder.

WitchyBND layers its settings as: appsettings.json (next to the exe) -> %APPDATA%/WitchyBND/appsettings.user.json
-> appsettings.override.json (next to the exe). We write the override file, so a user's own WitchyBND settings
can't change what we produce.
"""
import ctypes
import json
import os
import re
import shutil
import subprocess
import time
from ctypes import wintypes
from typing import Iterable, List, Optional
from xml.etree import ElementTree

WITCHY_VERSION = "3.0.1.0"
TPF_PARSER_VERSION = "2170000"  # What WitchyBND 3.0.1 writes into _witchy-tpf.xml manifests
OODLE_DLL = "oo2core_8_win64.dll"

OVERRIDE_SETTINGS = {
    "Bnd": True,
    "Dcx": False,
    # WitchyBND's default. Fields shared by >= 80% of rows go into a <defaults> section and are left out of those
    # rows, so XML consumers must fall back to the defaults. 0 (no defaults) can't be repacked in 3.0.1: 78 of AC6's
    # 257 params, including AccountParam/CharaInitParam/NpcParam/NpcThinkParam/TalkParam, fail to convert back.
    "ParamDefaultValueThreshold": 0.8,
    "ParamCellStyle": "Attribute",      # <row id="..." fieldName="value" .../>
    "Recursive": False,                 # Only when asked for, per call.
    "EndDelay": 0,
    "PauseOnError": False,
    "Parallel": True,
    "Offline": True,                    # No update checks.
    "TaeFolder": True,
    "Flexible": True,
    "BackupMethod": "None",
    "GitBackup": False,
}

# Windows caps command lines at 32767 chars; stay well below it when batching paths.
MAX_COMMAND_LINE = 30000

# Oodle Kraken level used when repacking. Stock files use 9; for menu/hi/01_common.tpf.dcx that takes ~50 s,
# while 4 takes ~1.5 s for a ~3% bigger file (6: 14 s, 2: 0.9 s). Measured 2026-10-29.
REPACK_COMPRESSION_LEVEL = 4


class WitchyError(RuntimeError):
    pass


# Allow for coarse filesystem timestamps when checking that an output was (re)written by this call.
MTIME_SLACK = 2.0


def _written_since(path: str, started: float) -> bool:
    return os.path.exists(path) and os.path.getmtime(path) >= started - MTIME_SLACK


def _unpacked_output_exists(path: str, started: float) -> bool:
    """Binders unpack to a folder named like the file with dots as dashes (sometimes with a suffix, e.g.
    sfxbnd_m10-ffxbnd-dcx-wffxbnd); single-file formats unpack to <file>.xml."""
    path = os.path.abspath(path)
    if _written_since(path + ".xml", started):
        return True
    parent, prefix = os.path.dirname(path), os.path.basename(path).replace(".", "-")
    return any(name.startswith(prefix) and os.path.isdir(os.path.join(parent, name))
               and _written_since(os.path.join(parent, name), started) for name in os.listdir(parent))


def _set_compression_level(unpacked_dir: str, level: int):
    """Rewrites <compressionLevel> in an unpacked binder's manifest (only Oodle-compressed binders have one)."""
    if not os.path.isdir(unpacked_dir):
        return
    for name in os.listdir(unpacked_dir):
        if not (name.startswith("_witchy") and name.endswith(".xml")):
            continue
        path = os.path.join(unpacked_dir, name)
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
        updated = re.sub(r"<compressionLevel>\d+</compressionLevel>", f"<compressionLevel>{level}</compressionLevel>", text)
        if updated != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)


def _repacked_output_exists(path: str, started: float) -> bool:
    path = os.path.abspath(path)
    if os.path.isdir(path):
        manifests = [f for f in os.listdir(path) if f.startswith("_witchy") and f.endswith(".xml")]
        if not manifests:
            return False
        root = ElementTree.parse(os.path.join(path, manifests[0])).getroot()
        # Split binders (BXF4, e.g. 00_solo.tpfbhd/.tpfbdt) name both halves instead of a single filename.
        outputs = [name for name in (root.findtext("filename"), root.findtext("bhd_filename"),
                                     root.findtext("bdt_filename")) if name]
        return bool(outputs) and all(_written_since(os.path.join(os.path.dirname(path), name), started) for name in outputs)
    return path.endswith(".xml") and _written_since(path[:-len(".xml")], started)


def file_version(path: str) -> Optional[str]:
    """The Windows file version of an exe, e.g. "3.0.1.0"."""
    version_dll = ctypes.WinDLL("version")
    size = version_dll.GetFileVersionInfoSizeW(path, None)
    if not size:
        return None
    buffer = ctypes.create_string_buffer(size)
    if not version_dll.GetFileVersionInfoW(path, 0, size, buffer):
        return None
    info = ctypes.c_void_p()
    length = wintypes.UINT()
    if not version_dll.VerQueryValueW(buffer, "\\", ctypes.byref(info), ctypes.byref(length)):
        return None
    # VS_FIXEDFILEINFO: signature, struct version, then dwFileVersionMS/LS.
    fixed = ctypes.cast(info, ctypes.POINTER(wintypes.DWORD * 4)).contents
    ms, ls = fixed[2], fixed[3]
    return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"


class Witchy:
    def __init__(self, exe_path: str, game_dir: Optional[str] = None):
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"WitchyBND not found at {exe_path}")
        version = file_version(exe_path)
        if version != WITCHY_VERSION:
            raise WitchyError(f"Expected WitchyBND {WITCHY_VERSION}, found {version} at {exe_path}")
        self.exe_path = exe_path
        exe_dir = os.path.dirname(exe_path)

        # Oodle (needed for DCX_KRAK) can't be redistributed, but every AC6 install has it.
        oodle_path = os.path.join(exe_dir, OODLE_DLL)
        if not os.path.exists(oodle_path):
            if not game_dir or not os.path.exists(os.path.join(game_dir, OODLE_DLL)):
                raise FileNotFoundError(f"{OODLE_DLL} is missing and couldn't be copied from the game folder")
            shutil.copy2(os.path.join(game_dir, OODLE_DLL), oodle_path)

        override_path = os.path.join(exe_dir, "appsettings.override.json")
        try:
            with open(override_path, encoding="utf-8") as f:
                current = json.load(f)
        except (OSError, ValueError):
            current = None
        if current != OVERRIDE_SETTINGS:
            with open(override_path, "w", encoding="utf-8") as f:
                json.dump(OVERRIDE_SETTINGS, f, indent=2)

    def _run(self, paths: Iterable[str], flags: List[str]):
        paths = [os.path.abspath(p) for p in paths]
        if not paths:
            return
        batch, batch_length = [], 0
        for path in paths:
            if batch and batch_length + len(path) + 3 > MAX_COMMAND_LINE:
                self._run_batch(batch, flags)
                batch, batch_length = [], 0
            batch.append(path)
            batch_length += len(path) + 3
        self._run_batch(batch, flags)

    def _run_batch(self, paths: List[str], flags: List[str]):
        result = subprocess.run([self.exe_path, "--silent", *flags, *paths], capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            listed = "\n  ".join(paths[:5]) + ("\n  ..." if len(paths) > 5 else "")
            raise WitchyError(f"WitchyBND failed (exit {result.returncode}) on:\n  {listed}" + (f"\n{output}" if output else ""))

    def unpack(self, *paths: str, recursive: bool = False):
        """Unpacks files next to themselves (e.g. regulation.bin -> regulation-bin/, x.param -> x.param.xml)."""
        started = time.time()
        self._run(paths, ["--unpack"] + (["--recursive"] if recursive else []))
        # WitchyBND skips files it doesn't recognize and still exits with 0, so check that output appeared.
        missing = [p for p in paths if not _unpacked_output_exists(p, started)]
        if missing:
            raise WitchyError("WitchyBND produced no output for:\n  " + "\n  ".join(missing))

    def repack(self, *paths: str, recursive: bool = False, compression_level: Optional[int] = REPACK_COMPRESSION_LEVEL):
        """Repacks unpacked folders / XML files back into the files they came from.
        compression_level overrides the Oodle level of binders (None keeps what their manifest says)."""
        for path in paths:
            self._allow_regulation_version(path)
            if compression_level is not None:
                _set_compression_level(path, compression_level)
        started = time.time()
        self._run(paths, ["--repack"] + (["--recursive"] if recursive else []))
        missing = [p for p in paths if not _repacked_output_exists(p, started)]
        if missing:
            raise WitchyError("WitchyBND produced no output for:\n  " + "\n  ".join(missing))

    # region Regulation
    # AC6's paramdefs predate some patch-added fields (e.g. ThrustersParam_NPC has flag bits the defs call padding),
    # so converting a param to XML and back can lose data. Only ever convert the params that actually get edited.
    def unpack_regulation(self, regulation_path: str, params: Iterable[str]) -> str:
        """Splits regulation.bin into .param files and converts only `params` (e.g. "ArenaParam") to XML.
        Returns the unpacked folder."""
        self.unpack(regulation_path)
        folder = os.path.join(os.path.dirname(os.path.abspath(regulation_path)), "regulation-bin")
        self.unpack(*[os.path.join(folder, name + ".param") for name in params])
        return folder

    def repack_regulation(self, folder: str, params: Iterable[str]):
        """Converts the edited `params` back from XML, then rebuilds regulation.bin next to the folder."""
        self.repack(*[os.path.join(folder, name + ".param.xml") for name in params])
        self.repack(folder)
    # endregion

    def _allow_regulation_version(self, unpacked_dir: str):
        """WitchyBND refuses to repack a regulation newer than Paramdex's Upgrader/version.txt. AC6's paramdefs were
        last changed for 1.07 and still match 1.09.1 (every param unpacks against them; WitchyBND checks row sizes),
        so only the version number is stale. Raise the gate to exactly this regulation's version, never further."""
        manifest = os.path.join(unpacked_dir, "_witchy-bnd4.xml")
        if not os.path.isfile(manifest):
            return
        root = ElementTree.parse(manifest).getroot()
        game, version = root.findtext("game"), root.findtext("version")
        if not game or not version or not version.isdigit():
            return  # Not a regulation binder.
        gate_path = os.path.join(os.path.dirname(self.exe_path), "Assets", "Paramdex", game, "Upgrader", "version.txt")
        if not os.path.exists(gate_path):
            return
        with open(gate_path, encoding="utf-8") as f:
            known = int(f.read().strip().replace("_", "").replace("L", ""))
        if known >= int(version):
            return
        digits = version.rjust(8, "0")  # e.g. 10910042 -> 1_09_1_0042L, the format Paramdex uses
        with open(gate_path, "w", encoding="utf-8") as f:
            f.write(f"{digits[:-7]}_{digits[-7:-5]}_{digits[-5:-4]}_{digits[-4:]}L")
        with open(gate_path, encoding="utf-8") as f:
            if int(f.read().strip().replace("_", "").replace("L", "")) != int(version):
                raise WitchyError(f"Couldn't raise the Paramdex regulation version in {gate_path}")


# region Manifest editing
# Unpacked binders keep a _witchy-<type>.xml manifest; files only get repacked if the manifest lists them
# (FFXBND is the exception: it packs whatever is in its subfolders).
def _manifest_path(unpacked_dir: str) -> str:
    manifests = [f for f in os.listdir(unpacked_dir) if f.startswith("_witchy") and f.endswith(".xml")]
    if len(manifests) != 1:
        raise WitchyError(f"Expected one _witchy manifest in {unpacked_dir}, found {manifests}")
    return os.path.join(unpacked_dir, manifests[0])


def _write_manifest(path: str, root: ElementTree.Element):
    ElementTree.indent(root, space="  ")
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n' + ElementTree.tostring(root, encoding="unicode") + "\n")


def add_binder_files(unpacked_dir: str, names: Iterable[str]):
    """Lists new files (already placed in the folder) in a BND4/BXF4 manifest, with the next free IDs.
    Names already listed are left alone."""
    path = _manifest_path(unpacked_dir)
    root = ElementTree.parse(path).getroot()
    if root.tag not in ("bnd4", "bxf4"):
        raise WitchyError(f"{path} is a {root.tag} manifest, not a BND4/BXF4 one")
    files = root.find("files")
    if files is None:
        files = ElementTree.SubElement(root, "files")
    listed = {f.findtext("path") for f in files.findall("file")}
    next_id = max((int(f.findtext("id")) for f in files.findall("file")), default=-1) + 1
    for name in names:
        if name in listed:
            continue
        entry = ElementTree.SubElement(files, "file")
        ElementTree.SubElement(entry, "flags").text = "Flag1"
        ElementTree.SubElement(entry, "id").text = str(next_id)
        ElementTree.SubElement(entry, "path").text = name
        listed.add(name)
        next_id += 1
    _write_manifest(path, root)


def add_tpf_textures(unpacked_dir: str, names: Iterable[str], tpf_format: str = "102"):
    """Lists new .dds files (already placed in the folder) in a TPF manifest. 102 = BC7, as the menu textures use."""
    path = _manifest_path(unpacked_dir)
    root = ElementTree.parse(path).getroot()
    if root.tag != "tpf":
        raise WitchyError(f"{path} is a {root.tag} manifest, not a TPF one")
    textures = root.find("textures")
    listed = {t.findtext("name") for t in textures.findall("texture")}
    for name in names:
        if name in listed:
            continue
        entry = ElementTree.SubElement(textures, "texture")
        ElementTree.SubElement(entry, "name").text = name
        ElementTree.SubElement(entry, "format").text = tpf_format
        ElementTree.SubElement(entry, "flags1").text = "0x00"
        listed.add(name)
    _write_manifest(path, root)


def new_single_texture_tpf(parent_dir: str, texture_name: str, tpf_format: str = "102") -> str:
    """Creates the unpacked folder + manifest for a one-texture <texture_name>.tpf.dcx (like the MENU_Decal_* and
    MENU_Archetype_* files in 00_solo). Put <texture_name>.dds in the returned folder, then repack it."""
    folder = os.path.join(parent_dir, f"{texture_name}-tpf-dcx")
    os.makedirs(folder, exist_ok=True)
    # WitchyBND picks its TPF parser by this attribute and refuses manifests without it.
    root = ElementTree.Element("tpf", {"WitchyVersion": TPF_PARSER_VERSION})
    for tag, text in (("filename", f"{texture_name}.tpf.dcx"), ("compression", "DCX_KRAK"),
                      ("compressionLevel", "9"), ("oodleCompressorType", "KRAK"), ("encoding", "0x01"),
                      ("flag2", "0x03"), ("platform", "PC")):
        ElementTree.SubElement(root, tag).text = text
    texture = ElementTree.SubElement(ElementTree.SubElement(root, "textures"), "texture")
    ElementTree.SubElement(texture, "name").text = f"{texture_name}.dds"
    ElementTree.SubElement(texture, "format").text = tpf_format
    ElementTree.SubElement(texture, "flags1").text = "0x00"
    _write_manifest(os.path.join(folder, "_witchy-tpf.xml"), root)
    return folder
# endregion
